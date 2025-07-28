import discord
from discord import Option, Embed
from discord.commands import SlashCommandGroup,option
from discord.ext import commands
import sqlite3
from typing import List, Tuple, Optional
import datetime
import asyncio
import io



class TicketDatenbank:
    def __init__(self, db_name: str = "Data/ticket.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            thread_id INTEGER NOT NULL,
            ersteller_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'offen',
            kategorie TEXT NOT NULL,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            geschlossen_am TIMESTAMP NULL,
            geschlossen_von INTEGER NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_einstellungen (
            guild_id INTEGER PRIMARY KEY,
            support_rolle_id INTEGER NULL,
            transkript_channel_id INTEGER NULL,
            ticket_channel_id INTEGER NULL,
            log_channel_id INTEGER NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_kategorien (
            guild_id INTEGER NOT NULL,
            kategorie_name TEXT NOT NULL,
            beschreibung TEXT NOT NULL,
            PRIMARY KEY (guild_id, kategorie_name)
        )
        """)
        self.conn.commit()

    def ticket_erstellen(self, guild_id: int, thread_id: int, ersteller_id: int, kategorie: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO tickets (guild_id, thread_id, ersteller_id, kategorie)
        VALUES (?, ?, ?, ?)
        """, (guild_id, thread_id, ersteller_id, kategorie))
        self.conn.commit()
        return cursor.lastrowid

    def ticket_schliessen(self, ticket_id: int, geschlossen_von: int):
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE tickets 
        SET status = 'geschlossen', 
            geschlossen_am = CURRENT_TIMESTAMP,
            geschlossen_von = ?
        WHERE ticket_id = ?
        """, (geschlossen_von, ticket_id))
        self.conn.commit()

    def get_ticket(self, thread_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM tickets 
        WHERE thread_id = ? AND status = 'offen'
        """, (thread_id,))
        return cursor.fetchone()

    def get_benutzer_tickets(self, guild_id: int, benutzer_id: int) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM tickets 
        WHERE guild_id = ? AND ersteller_id = ? AND status = 'offen'
        """, (guild_id, benutzer_id))
        return cursor.fetchall()

    def update_einstellungen(self, guild_id: int, support_rolle_id: int = None,
                           transkript_channel_id: int = None, ticket_channel_id: int = None,
                           log_channel_id: int = None):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO ticket_einstellungen 
        (guild_id, support_rolle_id, transkript_channel_id, ticket_channel_id, log_channel_id)
        VALUES (?, ?, ?, ?, ?)
        """, (guild_id, support_rolle_id, transkript_channel_id, ticket_channel_id, log_channel_id))
        self.conn.commit()

    def get_einstellungen(self, guild_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM ticket_einstellungen 
        WHERE guild_id = ?
        """, (guild_id,))
        return cursor.fetchone()

    def kategorie_hinzufuegen(self, guild_id: int, name: str, beschreibung: str):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO ticket_kategorien 
        (guild_id, kategorie_name, beschreibung)
        VALUES (?, ?, ?)
        """, (guild_id, name, beschreibung))
        self.conn.commit()

    def kategorie_entfernen(self, guild_id: int, name: str):
        cursor = self.conn.cursor()
        cursor.execute("""
        DELETE FROM ticket_kategorien 
        WHERE guild_id = ? AND kategorie_name = ?
        """, (guild_id, name))
        self.conn.commit()

    def get_kategorien(self, guild_id: int) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM ticket_kategorien 
        WHERE guild_id = ?
        """, (guild_id,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()

async def autocomplete_kategorienliste(self, ctx: discord.AutocompleteContext):
    guild_id = ctx.interaction.guild_id
    query = ctx.value.lower()

    kategorien = self.db.get_kategorien(guild_id)
    return [
               name for _, name, _ in kategorien
               if query in name.lower()
           ][:25]



class TicketKategorieView(discord.ui.View):
    def __init__(self, db, settings, categories, create_ticket_callback):
        super().__init__(timeout=None)
        self.db = db
        self.settings = settings
        self.categories = categories
        self.create_ticket_callback = create_ticket_callback

        self.add_item(TicketKategorieSelect(db, settings, categories, create_ticket_callback))



class TicketKategorieSelect(discord.ui.Select):
    def __init__(self, db, settings, categories, create_ticket_callback):
        options = [
            discord.SelectOption(
                label=category[1],
                description=category[2],
                value=category[1]
            ) for category in categories
        ]
        super().__init__(
            placeholder="Wähle eine Kategorie",
            options=options,
            min_values=1,
            max_values=1
        )
        self.db = db
        self.settings = settings
        self.create_ticket_callback = create_ticket_callback

    async def callback(self, interaction: discord.Interaction):
        await self.create_ticket_callback(interaction, self.settings, self.values[0])
        self.view.clear_items()
        message = await interaction.original_response()
        await message.edit(view=self.view, delete_after=10)




class TicketErstellenView(discord.ui.View):
    def __init__(self, bot, db):
        super().__init__(timeout=None)
        self.bot = bot
        self.db = db

        button = discord.ui.Button(
            label="Ticket erstellen",
            style=discord.ButtonStyle.primary,
            custom_id="ticket_erstellen_button",
            emoji="🎫"
        )
        button.callback = self.button_callback
        self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        try:
            if not interaction.guild:
                return await interaction.response.send_message(
                    "❌ Dieser Befehl kann nur in einem Server verwendet werden.",
                    ephemeral=True
                )


            settings = self.db.get_einstellungen(interaction.guild.id)
            if not settings:
                return await interaction.response.send_message(
                    "❌ Das Ticket-System wurde auf diesem Server noch nicht eingerichtet.",
                    ephemeral=True
                )


            categories = self.db.get_kategorien(interaction.guild.id)
            if not categories:
                return await interaction.response.send_message(
                    "❌ Es sind keine Ticket-Kategorien konfiguriert.",
                    ephemeral=True
                )

            else:
                view = TicketKategorieView(self.db, settings, categories, self._create_ticket)
                await interaction.response.send_message(
                    "Bitte wähle eine Kategorie:",
                    view=view,
                    ephemeral=True
                )

        except Exception as e:
            print(f"Error in button callback: {e}")
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(
                        "❌ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut.",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "❌ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut.",
                        ephemeral=True
                    )
            except Exception as e2:
                print(f"Error handling error: {e2}")


    async def _create_ticket(self, interaction: discord.Interaction, settings: Tuple, kategorie_name: str):
        try:
            await interaction.response.defer(ephemeral=True)

            guild = interaction.guild
            member = interaction.user

            existing_tickets = self.db.get_benutzer_tickets(guild.id, member.id)
            if existing_tickets:
                await interaction.followup.send(
                    f"❌ Du hast bereits ein offenes Ticket: <#{existing_tickets[0][2]}>",
                    ephemeral=True
                )
                return

            ticket_channel = guild.get_channel(settings[3])
            if not ticket_channel:
                await interaction.followup.send("❌ Ticket-Channel nicht gefunden!", ephemeral=True)
                return



            thread = await ticket_channel.create_thread(
                name=f"Ticket-{member.display_name}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )

            await thread.add_user(member)
            support_role = guild.get_role(settings[1])
            if support_role:
                for support_member in support_role.members:
                    try:
                        await thread.add_user(support_member)
                    except discord.HTTPException:
                        continue

            ticket_id = self.db.ticket_erstellen(guild.id, thread.id, member.id, kategorie_name)

            embed = discord.Embed(
                title=f"Ticket #{ticket_id} - {kategorie_name}",
                description=(
                    f"Hallo {member.mention},\n"
                    f"Dein privates Ticket wurde erstellt. Bitte beschreibe dein Anliegen so genau wie möglich.\n"
                    f"Das Support-Team wird sich bald bei dir melden.\n"
                    f"**Kategorie:** {kategorie_name}\n"
                    f"**Erstellt am:** {discord.utils.format_dt(datetime.datetime.now(), 'f')}"
                ),
                color=discord.Color.blue()
            )

            await thread.send(
                content=f"{member.mention} {support_role.mention if support_role else ''}",
                embed=embed,
                view=TicketManagementView(self.bot, self.db)
            )

            await interaction.followup.send(
                f"✅ Dein privates Ticket wurde erstellt: {thread.mention}",
                ephemeral=True
            )

            log_channel = guild.get_channel(settings[4]) if settings[4] else None
            if log_channel:
                log_embed = discord.Embed(
                    title="📥 Neues Ticket erstellt",
                    color=discord.Color.green(),
                    description=(
                        f"**Ticket-ID:** #{ticket_id}\n"
                        f"**Benutzer:** {member.mention} ({member.id})\n"
                        f"**Kategorie:** {kategorie_name}\n"
                        f"**Thread:** {thread.mention}"
                    )
                )
                await log_channel.send(embed=log_embed)
            else:
                return
        except Exception as e:
            print(f"Error creating ticket: {e}")
            try:
                await interaction.followup.send("❌ Fehler beim Erstellen des Tickets.", ephemeral=True)
            except Exception as e2:
                print(f"Error sending error message: {e2}")


class TicketManagementView(discord.ui.View):
    def __init__(self, bot, db):
        super().__init__(timeout=None)
        self.bot = bot
        self.db = db

        button = discord.ui.Button(
            label="Schließen",
            style=discord.ButtonStyle.red,
            custom_id="ticket_schliessen_button",
            emoji="🔒"
        )
        button.callback = self.close_ticket
        self.add_item(button)

    async def close_ticket(self, interaction: discord.Interaction):
        ticket = self.db.get_ticket(interaction.channel.id)
        if not ticket:
            await interaction.response.send_message("❌ Dies ist kein gültiges Ticket.", ephemeral=True)
            return

        settings = self.db.get_einstellungen(interaction.guild.id)
        member = interaction.guild.get_member(ticket[3])

        if not (interaction.user.guild_permissions.administrator or
                (settings and interaction.user.get_role(settings[1])) or
                interaction.user.id == ticket[3]):
            await interaction.response.send_message(
                "❌ Du hast keine Berechtigung, dieses Ticket zu schließen.",
                ephemeral=True
            )
            return

        confirm_view = discord.ui.View()
        confirm_button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label="Bestätigen",
            custom_id=f"confirm_close_{interaction.channel.id}"
        )
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="Abbrechen",
            custom_id=f"cancel_close_{interaction.channel.id}"
        )
        confirm_view.add_item(confirm_button)
        confirm_view.add_item(cancel_button)

        embed = discord.Embed(
            title="Ticket wirklich schließen?",
            description="Möchtest du dieses Ticket wirklich schließen?",
            color=discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=embed,
            view=confirm_view,
            ephemeral=True
        )

        message = await interaction.original_response()

        def check(i: discord.Interaction):
            return i.user == interaction.user and i.message.id == message.id

        try:
            confirm_interaction = await self.bot.wait_for(
                "interaction",
                check=check,
                timeout=30.0
            )

            for child in confirm_view.children:
                child.disabled = True

            try:
                await message.edit(view=confirm_view)
                await message.delete(delay=5.0)
            except discord.NotFound:
                pass

            if f"confirm_close_{interaction.channel.id}" in confirm_interaction.data["custom_id"]:
                await self._finalize_close(interaction, ticket, settings, member)
            else:
                await confirm_interaction.response.send_message(
                    "✅ Ticket-Schließung abgebrochen.",
                    ephemeral=True
                )

        except asyncio.TimeoutError:
            for child in confirm_view.children:
                child.disabled = True
            try:
                await message.edit(view=confirm_view)
                await message.delete(delay=5.0)
            except discord.NotFound:
                pass

            await interaction.followup.send(
                "❌ Zeitüberschreitung. Ticket wurde nicht geschlossen.",
                ephemeral=True
            )

    async def _finalize_close(self, interaction, ticket, settings, member):
        messages = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(f"{message.author.display_name} ({message.author.id}): {message.content}")

        transcript = "\n".join(messages)

        transcript_file = discord.File(
            io.BytesIO(transcript.encode("utf-8")),
            filename=f"transcript-{ticket[0]}.txt"
        )

        # transcript_channel = interaction.guild.get_channel(settings[2]) if settings else None
        #if transcript_channel:
         #   await transcript_channel.send(
          #      content=f"📄 Transkript für Ticket #{ticket[0]} ({ticket[4]})",
            #    file=transcript_file
           # )

        self.db.ticket_schliessen(ticket[0], interaction.user.id)

        thread = interaction.channel
        await thread.edit(
            name=f"geschlossen-{thread.name}",
            archived=True,
            locked=True
        )

        try:
            erstellt_am = discord.utils.format_dt(datetime.datetime.fromisoformat(ticket[6]), 'f')
        except (ValueError, IndexError):
            erstellt_am = "Unbekannt"


        embed = discord.Embed(
            title=f"Ticket #{ticket[0]} geschlossen",
            description=(
                f"Das Ticket wurde von {interaction.user.mention} geschlossen.\n"
                f"**Ersteller:** {member.mention if member else 'Unbekannt'}\n"
                f"**Erstellt am:** {erstellt_am}\n"
                f"**Geschlossen am:** {discord.utils.format_dt(datetime.datetime.now(), 'f')}"
            ),
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, file=transcript_file)

        self.stop()

        if settings[4]:
            log_channel = interaction.guild.get_channel(settings[4])
            if log_channel:
                log_embed = discord.Embed(
                    title="Ticket geschlossen",
                    color=discord.Color.red(),
                    description=(
                        f"**Ticket-ID:** #{ticket[0]}\n"
                        f"**Geschlossen von:** {interaction.user.mention} ({interaction.user.id})\n"
                        f"**Ersteller:** {member.mention if member else 'Unbekannt'} ({ticket[3]})\n"
                        f"**Thread:** {interaction.channel.mention}"
                    )
                )
                await log_channel.send(embed=log_embed, file=transcript_file)


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TicketDatenbank()
        self.bot.loop.create_task(self.initialize_views())

    async def initialize_views(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(TicketErstellenView(self.bot, self.db))
        self.bot.add_view(TicketManagementView(self.bot, self.db))

    ticket = SlashCommandGroup("ticket", "Ticket-System Befehle")

    @ticket.command(name="setup", description="Richtet das Ticket-System ein")
    @commands.has_permissions(administrator=True)
    async def setup_ticket(
            self,
            ctx,
            support_rolle: Option(discord.Role, "Rolle für Support-Mitglieder"),
            transkript_channel: Option(discord.TextChannel, "Channel für Transkripte"),
            ticket_channel: Option(discord.TextChannel, "Channel für Ticket-Threads"),
            log_channel: Option(discord.TextChannel, "Channel für Logs", required=False)
    ):
        self.db.update_einstellungen(
            ctx.guild.id,
            support_rolle.id,
            transkript_channel.id,
            ticket_channel.id,
            log_channel.id if log_channel else None
        )

        embed = Embed(
            title="✅ Ticket-System erfolgreich eingerichtet",
            color=discord.Color.green(),
            description=f"""
            **Support-Rolle:** {support_rolle.mention}
            **Transkript-Channel:** {transkript_channel.mention}
            **Ticket-Channel:** {ticket_channel.mention}
            **Log-Channel:** {log_channel.mention if log_channel else 'Keiner'}
            """
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @ticket.command(name="nachricht", description="Erstellt ein Ticket-Panel")
    @commands.has_permissions(administrator=True)
    async def create_panel(
            self,
            ctx,
            titel: Option(str, "Titel des Panels", default="Support-Ticket System"),
            beschreibung: Option(str, "Beschreibung des Panels",
                                 default="Klicke auf den Button unten, um ein Ticket zu erstellen."),
            farbe: Option(str, "Farbe als Hex-Code (z.B. #ff0000)", default="#5865F2"),
            button_text: Option(str, "Button-Text", default="Ticket erstellen"),
            button_emoji: Option(str, "Button-Emoji", required=False)
    ):
        try:
            color = int(farbe.lstrip("#"), 16)
        except ValueError:
            color = discord.Color.blue()

        embed = Embed(
            title=titel,
            description=beschreibung,
            color=color
        )

        view = TicketErstellenView(self.bot, self.db)
        button = view.children[0]
        button.label = button_text
        if button_emoji:
            button.emoji = button_emoji

        await ctx.send(embed=embed, view=view)
        await ctx.respond("✅ Panel erfolgreich erstellt!", ephemeral=True)

    @ticket.command(name="kategorien_hinzufuegen", description="Fügt eine Ticket-Kategorie hinzu")
    @commands.has_permissions(administrator=True)
    async def add_kategorie(
        self,
        ctx,
        name: Option(str, "Name der Kategorie"),
        beschreibung: Option(str, "Beschreibung der Kategorie")
    ):
        kategorien = self.db.get_kategorien(ctx.guild.id)

        if len(kategorien) >= 7:
            await ctx.respond("❌ Es dürfen maximal **7 Kategorien** existieren.", ephemeral=True)
            return

        if any(k[1].lower() == name.lower() for k in kategorien):
            await ctx.respond(f"⚠️ Kategorie **{name}** existiert bereits.", ephemeral=True)
            return

        self.db.kategorie_hinzufuegen(ctx.guild.id, name, beschreibung)
        await ctx.respond(f"✅ Kategorie **{name}** wurde hinzugefügt.", ephemeral=True)


    @ticket.command(name="kategorien_entfernen", description="Entfernt eine Ticket-Kategorie")
    @option("name", description="Name der Kategorie", autocomplete=autocomplete_kategorienliste)
    @commands.has_permissions(administrator=True)
    async def remove_kategorie(self, ctx, name: str):
        kategorien = [k[1] for k in self.db.get_kategorien(ctx.guild.id)]
        if name not in kategorien:
            await ctx.respond(f"❌ Kategorie **{name}** existiert nicht.", ephemeral=True)
            return

        self.db.kategorie_entfernen(ctx.guild.id, name)
        await ctx.respond(f"🗑️ Kategorie **{name}** wurde entfernt.", ephemeral=True)



    @ticket.command(name="kategorien_liste", description="Zeigt alle Ticket-Kategorien")
    @commands.has_permissions(administrator=True)
    async def list_kategorien(self, ctx):
        kategorien = self.db.get_kategorien(ctx.guild.id)
        if not kategorien:
            await ctx.respond("⚠️ Keine Kategorien vorhanden.", ephemeral=True)
            return

        msg = "\n".join([f"• **{name}** – {beschreibung}" for _, name, beschreibung in kategorien])
        await ctx.respond(f"📋 **Ticket-Kategorien:**\n{msg}", ephemeral=True)




def setup(bot):
    bot.add_cog(TicketSystem(bot))
