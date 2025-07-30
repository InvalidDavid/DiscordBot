import discord
from discord import Option, Embed
from discord.commands import SlashCommandGroup,option
from discord.ext import commands
import sqlite3
from typing import List, Tuple, Optional
import datetime
import asyncio
import io
import json # fuer den embed

DB_PATH = "Data/ticket.db"


class TicketDatenbank:
    def __init__(self, db_name: str = DB_PATH):
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


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_panels (
            guild_id INTEGER PRIMARY KEY,
            embed_json TEXT NOT NULL,
            message_id INTEGER NULL
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


        self.conn.commit()

    def save_panel(self, guild_id: int, embed: discord.Embed, message_id: int = None):
        try:
            embed_dict = embed.to_dict()
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ticket_panels 
                (guild_id, embed_json, message_id)
                VALUES (?, ?, ?)
            """, (guild_id, json.dumps(embed_dict), message_id))
            self.conn.commit()
        except Exception as e:
            print(f"Fehler beim Speichern des Embeds: {e}")

    def load_panel(self, guild_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT embed_json, message_id FROM ticket_panels WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        if result:
            try:
                embed_dict = json.loads(result[0])
                return discord.Embed.from_dict(embed_dict), result[1]
            except Exception as e:
                print(f"[Fehler beim Laden des Embeds] {e}")
        return None, None


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
                await message.edit(view=None)
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
    kategorie = ticket.create_subgroup("kategorie", description="Kategorie der Ticket")

    @ticket.command(name="einstellungen", description="Ändert die Ticket-System Einstellungen")
    @commands.has_permissions(administrator=True)
    async def ticket_einstellungen(self, ctx):
        settings = self.db.get_einstellungen(ctx.guild.id)
        if not settings:
            return await ctx.respond(
                "❌ Das Ticket-System wurde noch nicht eingerichtet! Bitte verwende zuerst `/ticket setup`.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🎛️ Ticket-Einstellungen",
            description="Wähle unten aus, was du bearbeiten möchtest.",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="Aktuelle Einstellungen",
            value=(
                f"**Support-Rolle:** {f'<@&{settings[1]}>' if settings[1] else '❌ Nicht gesetzt'}\n"
                f"**Transkript-Channel:** {f'<#{settings[2]}>' if settings[2] else '❌ Nicht gesetzt'}\n"
                f"**Ticket-Channel:** {f'<#{settings[3]}>' if settings[3] else '❌ Nicht gesetzt'}\n"
                f"**Log-Channel:** {f'<#{settings[4]}>' if settings[4] else '❌ Nicht gesetzt'}"
            ),
            inline=False
        )

        view = EinstellungenAuswahlView(self.db, ctx.guild.id, ctx.user, self.bot)
        msg = await ctx.respond(embed=embed, view=view, ephemeral=True)
        view.message = await msg.original_response()

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

    @ticket.command(name="nachricht", description="Sendet das aktuelle Ticket-Panel")
    @commands.has_permissions(administrator=True)
    async def send_panel(self, ctx):
        settings = self.db.get_einstellungen(ctx.guild.id)
        if not settings or not settings[3]:
            return await ctx.respond("❌ Konfiguriere zuerst einmal mit `/ticket setup`!", ephemeral=True)

        channel = ctx.guild.get_channel(settings[3])
        if not channel:
            return await ctx.respond("❌ Konfiguriere zuerst einmal mit `/ticket setup`!", ephemeral=True)

        embed, message_id = self.db.load_panel(ctx.guild.id)
        if not embed:
            embed = discord.Embed(
                title="🎫 Ticket-System",
                description="Klicke unten um ein Ticket zu erstellen",
                color=discord.Color.blue()
            )

        view = TicketErstellenView(self.bot, self.db)
        msg = await channel.send(embed=embed, view=view)
        self.db.save_panel(ctx.guild.id, embed, msg.id)
        self.bot.add_view(view, message_id=msg.id)

        return await ctx.respond(f"✅ Panel wurde in {channel.mention} gesendet!", ephemeral=True)

    @ticket.command(name="embed", description="Bearbeitet das Ticket-Panel Embed")
    @commands.has_permissions(administrator=True)
    async def edit_embed(self, ctx):

        embed_data = self.db.load_panel(ctx.guild.id)

        embed = embed_data[0] if embed_data and embed_data[0] else None

        if embed is None:
            embed = discord.Embed(
                title="🎫 Ticket-System",
                description="Klicke unten um ein Ticket zu erstellen",
                color=discord.Color.blue()
            )

        view = EmbedBuilderView(self.db, ctx.guild.id)
        await ctx.respond("✍️ Bearbeite das Ticket-Panel:", embed=embed, view=view, ephemeral=True)

    @kategorie.command(name="hinzufuegen", description="Fügt eine Ticket-Kategorie hinzu")
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


    @kategorie.command(name="entfernen", description="Entfernt eine Ticket-Kategorie")
    @option("name", description="Name der Kategorie", autocomplete=autocomplete_kategorienliste)
    @commands.has_permissions(administrator=True)
    async def remove_kategorie(self, ctx, name: str):
        kategorien = [k[1] for k in self.db.get_kategorien(ctx.guild.id)]
        if name not in kategorien:
            await ctx.respond(f"❌ Kategorie **{name}** existiert nicht.", ephemeral=True)
            return

        self.db.kategorie_entfernen(ctx.guild.id, name)
        await ctx.respond(f"🗑️ Kategorie **{name}** wurde entfernt.", ephemeral=True)



    @kategorie.command(name="liste", description="Zeigt alle Ticket-Kategorien")
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


class TicketErstellenButton(discord.ui.Button):
    def __init__(self, bot, db):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Ticket erstellen",
            custom_id="persistent:ticket_create",
            emoji="🎫"
        )
        self.bot = bot
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        settings = self.db.get_einstellungen(interaction.guild.id)
        if not settings:
            return await interaction.response.send_message(
                "❌ Ticket-System wurde noch nicht eingerichtet!",
                ephemeral=True
            )

        ticket_channel = interaction.guild.get_channel(settings[3])
        if not ticket_channel:
            return await interaction.response.send_message(
                "❌ Ticket-Channel nicht gefunden!",
                ephemeral=True
            )

        categories = self.db.get_kategorien(interaction.guild.id)
        if not categories:
            return await interaction.response.send_message(
                "❌ Keine Kategorien verfügbar!",
                ephemeral=True
            )

        thread = await ticket_channel.create_thread(
            name=f"Ticket-{interaction.user.display_name}",
            type=discord.ChannelType.private_thread
        )

        await thread.add_user(interaction.user)
        support_role = interaction.guild.get_role(settings[1])
        if support_role:
            for member in support_role.members:
                try:
                    await thread.add_user(member)
                except:
                    continue

        ticket_id = self.db.ticket_erstellen(
            interaction.guild.id,
            thread.id,
            interaction.user.id,
            "Allgemein"
        )

        embed = discord.Embed(
            title=f"Ticket #{ticket_id}",
            description=f"Hallo {interaction.user.mention},\n\n"
                        "Bitte beschreibe dein Anliegen.\n"
                        "Das Support-Team wird sich bald bei dir melden.",
            color=discord.Color.blue()
        )

        view = EmbedBuilderView(self.db, interaction.guild.id)
        await thread.send(
            content=f"{interaction.user.mention} {support_role.mention if support_role else ''}",
            embed=embed,
            view=view
        )

        return await interaction.response.send_message(
            f"✅ Ticket wurde erstellt: {thread.mention}",
            ephemeral=True
        )


class CreateEmbedBuilderButton(discord.ui.Button):
    def __init__(self, db, guild_id):
        super().__init__(label="Embed erstellen", style=discord.ButtonStyle.green, emoji="🖋️")
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Default Title", description="Default Description", color=discord.Color.blue())
        builder_view = EmbedBuilderView(self.db, self.guild_id, embed)
        await interaction.response.send_message("✍️ Bearbeite dein Embed unten:", embed=embed, view=builder_view, ephemeral=True)


class SaveEmbedButton(discord.ui.Button):
    def __init__(self, db, guild_id):
        super().__init__(style=discord.ButtonStyle.green, label="Speichern")
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        self.db.save_panel(self.guild_id, embed)

        await interaction.response.edit_message(
            content="✅ Embed wurde gespeichert!",
            embed=embed,
            view=None
        )




class EmbedBuilderView(discord.ui.View):
    def __init__(self, db, guild_id: int, has_saved_embed: bool = False):
        super().__init__(timeout=600)
        self.db = db
        self.guild_id = guild_id
        self.add_item(Dropdown())
        self.add_item(SaveEmbedButton(db, guild_id))
        self.add_item(ResetEmbedButton())


    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        await interaction.response.send_message(
            "❌ Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
            ephemeral=True
        )
        print(f"Error in {item}: {error}")

class SendEmbedButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Senden",
            custom_id="send_embed_button",
            emoji="📨"
        )

    async def callback(self, interaction: discord.Interaction):
        settings = self.view.db.get_einstellungen(interaction.guild.id)
        if not settings:
            return await interaction.response.send_message(
                "❌ Ticket-System nicht eingerichtet!",
                ephemeral=True
            )

        support_role = interaction.guild.get_role(settings[1])
        if not (interaction.user.guild_permissions.administrator or
                (support_role and support_role in interaction.user.roles)):
            return await interaction.response.send_message(
                "❌ Nur Support-Mitglieder können Embeds senden!",
                ephemeral=True
            )

        embed = interaction.message.embeds[0]
        await interaction.channel.send(embed=embed)

        return await interaction.response.send_message(
            "✅ Embed wurde gesendet!",
            ephemeral=True
        )




class Send(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Send",
            style=discord.enums.ButtonStyle.green,
            custom_id="interaction:send",
            emoji="✉️"
        )

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        channel = interaction.channel
        if len(message.embeds) == 0 and not message.content:
            return await interaction.response.send_message("Was willst du bitte senden", ephemeral=True)
        if len(message.embeds) == 0:
            await channel.send(content=message.content)
        else:
            embed = message.embeds[0]
            final = embed.copy()

            if message.content:
                await channel.send(embed=embed,content=message.content)
            else:
                await channel.send(embed=embed)
        return await interaction.response.send_message("Gesendet", ephemeral=True)


async def check_embed(embed, checker):
    list = embed.to_dict()
    list_fields = len(list['fields'])
    if checker == "":
        if list_fields <= 0:
            if len(list) < 4:
                return False
    return True

class ResetEmbedButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="Zurücksetzen",
            emoji="🗑️"
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Ticket-System",
            description="Klicke unten um ein Ticket zu erstellen",
            color=discord.Color.blue()
        )
        view = EmbedBuilderView(self.view.db, self.view.guild_id)
        await interaction.response.edit_message(embed=embed, view=view)


class content(discord.ui.Modal):
    def __init__(self, label, placeholder, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder
        self.value = value

        self.add_item(discord.ui.InputText(
            required=False,
            max_length=1999,
            label=label,
            placeholder=placeholder,
            value=value,
            style=discord.InputTextStyle.long
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        await interaction.response.edit_message(content=self.children[0].value)

class author(discord.ui.Modal):
    def __init__(self, label, placeholder, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder
        self.value = value

        self.add_item(discord.ui.InputText(
            required=False,
            max_length=200,
            label=label,
            placeholder=placeholder,
            value=value,
            style=discord.InputTextStyle.short
        ))
        self.add_item(discord.ui.InputText(
            required=True,
            max_length=200,
            label="Author Icon",
            placeholder="Author Icon Here...",
            value=value,
            style=discord.InputTextStyle.short
        ))
        self.add_item(discord.ui.InputText(
            required=True,
            max_length=200,
            label="Author URL",
            placeholder="Author URL Here...",
            value=value,
            style=discord.InputTextStyle.short
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        embed = message.embeds[0]
        check = await check_embed(embed, self.children[0].value)
        if check is False:
            return await interaction.response.send_message("Es muss midnesten ein feld vorhanden sein")

        # embed.set_author(name=self.children[0].value,url=self.children[2].value,icon_url=self.children[1].value)

        embeds = []
        if not len(message.embeds) == 2 or len(message.embeds[1].fields) == 0:
            embeds.append(embed)
            embed2 = discord.Embed(description=f"Settings", color=discord.Color.yellow())
            if self.children[0].value == "":
                embed2.add_field(name="Author", value="default author")
            else:
                embed2.add_field(name="Author", value=self.children[0].value)

            link_aiu = self.children[1].value
            if link_aiu.find('http://') == 0 or link_aiu.find('https://') == 0:
                embed2.add_field(name="Author Icon URL", value=self.children[1].value)

            else:
                embed2.add_field(name="Author Icon URL", value="https://www.pleaseenteravaildurladress.com/")

            link_au = self.children[2].value
            if link_au.find('http://') == 0 or link_au.find('https://') == 0:
                embed2.add_field(name="Author URL", value=self.children[2].value)
            else:
                embed2.add_field(name="Author URL", value="https://www.pleaseenteravaildurladress.com/")
            embeds.append(embed2)
        else:
            embeds.append(embed)
            embed2 = message.embeds[1]
            current_fields = embed2.fields.copy()
            field_list = []
            for field in current_fields:
                field_list.append(field.name)
                if field.name == "Author":
                    embed2.remove_field(embed2.fields.index(field))
                    if not self.children[0].value == "":
                        embed2.add_field(name="Author", value=self.children[0].value)
                elif field.name == "Author Icon URL":
                    embed2.remove_field(embed2.fields.index(field))
                    if not self.children[0].value == "":
                        link_aiu2 = self.children[1].value
                        if link_aiu2.find('http://') == 0 or link_aiu2.find('https://') == 0:
                            embed2.add_field(name="Author Icon URL", value=self.children[1].value)
                        else:
                            embed2.add_field(name="Author Icon URL",
                                             value="https://www.pleaseenteravaildurladress.com/")
                elif field.name == "Author URL":
                    embed2.remove_field(embed2.fields.index(field))
                    if not self.children[0].value == "":
                        link_au2 = self.children[2].value
                        if link_au2.find('http://') == 0 or link_au2.find('https://') == 0:
                            embed2.add_field(name="Author URL", value=self.children[2].value)
                        else:
                            embed2.add_field(name="Author URL", value="https://www.pleaseenteravaildurladress.com/")

            if not "Author" in field_list or not "Author URL" in field_list or not "Author Icon URL" in field_list:
                if self.children[0].value == "":
                    embed2.add_field(name="Author", value="default author")
                else:
                    embed2.add_field(name="Author", value=self.children[0].value)

                link_aiut = self.children[1].value
                if link_aiut.find('http://') == 0 or link_aiut.find('https://') == 0:
                    embed2.add_field(name="Author Icon URL", value=self.children[1].value)
                else:
                    embed2.add_field(name="Author Icon URL", value="https://www.pleaseenteravaildurladress.com/")

                link_aut = self.children[2].value
                if link_aut.find('http://') == 0 or link_aut.find('https://') == 0:
                    embed2.add_field(name="Author URL", value=self.children[2].value)
                else:
                    embed2.add_field(name="Author URL", value="https://www.pleaseenteravaildurladress.com/")

            embeds.append(embed2)

        return await interaction.response.edit_message(embeds=embeds)


class title(discord.ui.Modal):
    def __init__(self, label, placeholder, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder
        self.value = value

        self.add_item(discord.ui.InputText(
            required=False,
            max_length=50,
            label=label,
            placeholder=placeholder,
            value=value,
            style=discord.InputTextStyle.short
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message

        embed = message.embeds[0]
        check = await check_embed(embed, self.children[0].value)
        if check is False:
            return await interaction.response.send_message("Es muss midnesten ein feld vorhanden sein")
        try:

            embed.title = self.children[0].value
        except:
            pass

        embeds = []
        if len(message.embeds) == 2:
            embeds.append(embed)
            embeds.append(message.embeds[1])
        else:
            embeds.append(embed)

        return await interaction.response.edit_message(embeds=embeds)


class description(discord.ui.Modal):
    def __init__(self, label, placeholder, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder
        self.value = value

        self.add_item(discord.ui.InputText(
            required=False,
            max_length=500,
            label=label,
            placeholder=placeholder,
            value=value,
            style=discord.InputTextStyle.long
        ))

    async def callback(self, interaction: discord.Interaction):
        # variablen = ["UserID","UserTag","Username","UserAvatarURL","UserBannerURL","UserCreateAT","UserJoined","Members","GuildID","Guildname","GuildIcon","GuildBannert"]
        # variable_set = set(variablen)
        text = self.children[0].value
        # for variable in re.findall(r'{(.*?)}', text):
        #     if variable not in variable_set:
        #         text = text.replace("{" + variable + "}", "#####")
        message = interaction.message
        embed = message.embeds[0]
        check = await check_embed(embed, text)
        if check is False:
            return await interaction.response.send_message("Es muss midnesten ein feld vorhanden sein")
        try:
            embed.description = text
        except:
            pass

        embeds = []
        if len(message.embeds) == 2:
            embeds.append(embed)
            embeds.append(message.embeds[1])
        else:
            embeds.append(embed)

        return await interaction.response.edit_message(embeds=embeds)



class footer(discord.ui.Modal):
    def __init__(self, label, placeholder, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder
        self.value = value

        self.add_item(discord.ui.InputText(
            required=False,
            max_length=50,
            label=label,
            placeholder=placeholder,
            value=value,
            style=discord.InputTextStyle.short
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        embed = message.embeds[0]
        check = await check_embed(embed, self.children[0].value)
        if check is False:
            return await interaction.response.send_message("Es muss midnesten ein feld vorhanden sein")
        try:
            embed.set_footer(text=self.children[0].value)
        except:
            pass

        embeds = []
        if len(message.embeds) == 2:
            embeds.append(embed)
            embeds.append(message.embeds[1])
        else:
            embeds.append(embed)

        return interaction.response.edit_message(embeds=embeds)


class color(discord.ui.Modal):
    def __init__(self, label, placeholder, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder
        self.value = value

        self.add_item(discord.ui.InputText(
            required=False,
            max_length=6,
            min_length=6,
            label=label,
            placeholder=placeholder,
            value=value,
            style=discord.InputTextStyle.short
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        embed = message.embeds[0]
        check = await check_embed(embed, self.children[0].value)
        if check is False:
            return await interaction.response.send_message("Es muss midnesten ein feld vorhanden sein")
        try:
            farbe = f"0x{self.children[0].value}"
            embed.colour = discord.Colour(int(farbe, 16))
        except:
            pass

        embeds = []
        if len(message.embeds) == 2:
            embeds.append(embed)
            embeds.append(message.embeds[1])
        else:
            embeds.append(embed)

        return await interaction.response.edit_message(embeds=embeds)


class field_add(discord.ui.Modal):
    def __init__(self, dropdown, label, placeholder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropdown = dropdown
        self.label = label
        self.placeholder = placeholder

        self.add_item(discord.ui.InputText(
            required=True,
            max_length=2000,
            label=label,
            placeholder=placeholder,
            style=discord.InputTextStyle.short
        ))

        self.add_item(discord.ui.InputText(
            required=True,
            max_length=2000,
            label="Field Value",
            placeholder="Field Value Here...",
            style=discord.InputTextStyle.long
        ))

        self.add_item(discord.ui.InputText(
            required=True,
            max_length=2000,
            min_length=4,
            label="Field Inline",
            placeholder="Field Inline Here... (true or false)",
            value="false",
            style=discord.InputTextStyle.short
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        embed = message.embeds[0]

        if self.children[2].value == "true" or "false":
            if len(embed.fields) == 24:
                return await interaction.response.send_message(
                    "Du Kannst nicht mehr als 25 Felder zu deinem Embed Hinzufügen", ephemeral=True)
            else:
                embed.add_field(name=self.children[0].value, value=self.children[1].value,
                                inline=self.children[2].value)
        else:
            embed.add_field(name=self.children[0].value, value=self.children[1].value)

        embeds = []
        if len(message.embeds) == 2:
            embeds.append(embed)
            embeds.append(message.embeds[1])
        else:
            embeds.append(embed)

        return await interaction.response.edit_message(embeds=embeds)


class field_remove(discord.ui.Modal):
    def __init__(self, label, placeholder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.placeholder = placeholder

        self.add_item(discord.ui.InputText(
            required=True,
            max_length=2,
            label=label,
            placeholder=placeholder,
            style=discord.InputTextStyle.short
        ))

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        embed = message.embeds[0]
        if len(embed.fields) == 0:
            return await interaction.response.send_message("Du kannst keine Felder entfernen, da keine Felder da sind", ephemeral=True)
        else:
            if len(embed.fields) == 0:
                return await interaction.response.send_message(
                    "Du Kannst nicht mehr Felder entfernen, weil keine da sind", ephemeral=True)
            if len(embed.fields) > int(self.children[0].value):
                embed.fields.pop(int(self.children[0].value))
            else:
                return await interaction.response.send_message(
                    "Beachte, das die Zähung der Felder bei 0 beginnt also 0, 1, 2, ...", ephemeral=True)

        embeds = []
        if len(message.embeds) == 2:
            embeds.append(embed)
            embeds.append(message.embeds[1])
        else:
            embeds.append(embed)

        return await interaction.response.edit_message(embeds=embeds)


options = [
            discord.SelectOption(label="Inhalt",  emoji="✍️", value="content"),
            discord.SelectOption(label="Autor",  emoji="🗣️", value="author"),
            discord.SelectOption(label="Titel",  emoji="📣", value="title"),
            discord.SelectOption(label="Beschreibung",  emoji="📜",
                                 value="description"),
            discord.SelectOption(label="Fußzeile", emoji="📓", value="footer"),
            discord.SelectOption(label="Farbe", emoji="🎨", value="color"),
            discord.SelectOption(label="Timestamp",  emoji="⏰", value="timestamp"),
            discord.SelectOption(label="Embed hinzufuegen",  emoji="➕", value="field_add"),
            discord.SelectOption(label="Embed entfernen",  emoji="➖",
                                 value="field_remove"),
        ]

class Dropdown(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Feld auswählen",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="interaction:Dropdown",
        )

    async def callback(self, interaction: discord.Interaction):
        not_embed = "Du musst ein Embed hinzufügen, um diese Funktion nutzen zu können!"
        if "content" in interaction.data['values']:
            message = interaction.message
            modal = content(label="Inhalt", placeholder="Inhalt hier...", value=message.content,
                            title="Neues Embed: Inhalt")
            return await interaction.response.send_modal(modal)
        elif "author" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]
            if embed.author is None:
                modal = author(label="Autor", placeholder="Autor hier...", value="", title="Neues Embed: Autor")
            else:
                modal = author(label="Autor", placeholder="Autor hier...", value=embed.author.name,
                               title="Neues Embed: Autor")
            return await interaction.response.send_modal(modal)

        elif "title" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]

            if embed.title is None:
                modal = title(label="Titel", placeholder="Titel hier...", value="", title="Neues Embed: Titel")
            else:
                modal = title(label="Titel", placeholder="Titel hier...", value=embed.title, title="Neues Embed: Titel")
            await interaction.response.send_modal(modal)

        elif "description" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]

            if embed.description is None:
                modal = description(label="Beschreibung", placeholder="Beschreibung hier...", value="",
                                    title="Neues Embed: Beschreibung")
            else:
                modal = description(label="Beschreibung", placeholder="Beschreibung hier...", value=embed.description,
                                    title="Neues Embed: Beschreibung")
            return await interaction.response.send_modal(modal)

        elif "footer" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]
            if embed.footer is None:
                modal = footer(label="Fußzeile", placeholder="Fußzeile hier...", value="", title="Neues Embed: Fußzeile")
            else:
                modal = footer(label="Fußzeile", placeholder="Fußzeile hier...", value=embed.footer.text,
                               title="Neues Embed: Fußzeile")
            return await interaction.response.send_modal(modal)

        elif "color" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]
            if embed.colour is None:
                modal = color(label="Farbe", placeholder="Farbe (HEX) hier...", value="", title="Neues Embed: Farbe")
            else:
                rgb = embed.colour.to_rgb()
                hex_code = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                modal = color(label="Farbe", placeholder="Farbe (HEX) hier...", value=hex_code[1:],
                              title="Neues Embed: Farbe")
            return await interaction.response.send_modal(modal)

        elif "timestamp" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]

            if embed.timestamp:
                embed.timestamp = None
            else:
                embed.timestamp = datetime.datetime.utcnow()

            embeds = []
            if len(message.embeds) == 2:
                embeds.append(embed)
                embeds.append(message.embeds[1])
            else:
                embeds.append(embed)

            return await interaction.response.edit_message(embeds=embeds)

        elif "field_add" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]
            modal = field_add(self, label="Feldname", placeholder="Feldname hier...", title="Neues Embed: Feld hinzufügen")
            return await interaction.response.send_modal(modal)

        elif "field_remove" in interaction.data['values']:
            message = interaction.message
            if not message.embeds:
                return await interaction.response.send_message(not_embed, ephemeral=True)
            embed = message.embeds[0]
            if len(embed.fields) == 1:
                embed.fields.pop(0)
                embeds = []
                if len(message.embeds) == 2:
                    embeds.append(embed)
                    embeds.append(message.embeds[1])
                else:
                    embeds.append(embed)

                return await interaction.response.edit_message(embeds=embeds)
            modal = field_remove(label="Feldnummer (Zählung beginnt bei 0)", placeholder="Feldnummer hier...",
                                 title="Neues Embed: Feld entfernen")
            return await interaction.response.send_modal(modal)
        elif not interaction.response.is_done():
            view = discord.ui.View()
            view.add_item(Dropdown())
            message = interaction.message

            if message:
                await interaction.response.edit_message(view=view)
            else:
                await interaction.response.send_message(view=view)


class EinstellungenAuswahlView(discord.ui.View):
    def __init__(self, db, guild_id, user, bot):
        super().__init__(timeout=60)
        self.db = db
        self.guild_id = guild_id
        self.user = user
        self.bot = bot
        self.add_item(EinstellungenDropdown(db, guild_id, user, bot))
        self.add_item(FertigButton(user))
        self.add_item(AbbrechenButton(user))

    async def on_timeout(self):
        try:
            for item in self.children:
                item.disabled = True
            await self.message.edit(content="⏰ Zeit abgelaufen.", view=self)
        except:
            pass

class EinstellungenDropdown(discord.ui.Select):
    def __init__(self, db, guild_id, user, bot):
        self.db = db
        self.guild_id = guild_id
        self.user = user
        self.bot = bot

        options = [
            discord.SelectOption(label="Support-Rolle", value="support", emoji="🛠️"),
            discord.SelectOption(label="Transkript-Channel", value="transcript", emoji="📄"),
            discord.SelectOption(label="Ticket-Channel", value="ticket", emoji="🎫"),
            discord.SelectOption(label="Log-Channel", value="log", emoji="📋")
        ]
        super().__init__(
            placeholder="Wähle eine Einstellung...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("Nicht dein Menü.", ephemeral=True)

        value = self.values[0]
        if value == "support":
            button = SupportRolleButton(self.db, self.guild_id)
        elif value == "transcript":
            button = TranskriptChannelButton(self.db, self.guild_id)
        elif value == "ticket":
            button = TicketChannelButton(self.db, self.guild_id)
        elif value == "log":
            button = LogChannelButton(self.db, self.guild_id)
        else:
            return await interaction.response.send_message("Ungültige Auswahl.", ephemeral=True)

        return await button.callback(interaction)

class FertigButton(discord.ui.Button):
    def __init__(self, user):
        super().__init__(label="Fertig", style=discord.ButtonStyle.green, row=1)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("Nur der ursprüngliche Benutzer kann das abschließen.", ephemeral=True)

        return await interaction.response.edit_message(content="✅ Einstellungen abgeschlossen.", view=None)


class SupportRolleButton(discord.ui.Button):
    def __init__(self, db, guild_id):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Support-Rolle",
            custom_id=f"settings_support_{guild_id}",
            row=0
        )
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class RoleSelect(discord.ui.Select):
            def __init__(self, db, guild_id, user, roles):
                self.db = db
                self.guild_id = guild_id
                self.user = user
                options = [
                    discord.SelectOption(label=role.name, value=str(role.id))
                    for role in roles if not role.is_default()
                ][:25]
                super().__init__(
                    placeholder="Wähle eine Support-Rolle",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, select_interaction: discord.Interaction):
                if select_interaction.user != self.user:
                    return await select_interaction.response.send_message(
                        "Nur der ursprüngliche Benutzer kann diese Auswahl treffen.",
                        ephemeral=True
                    )

                role_id = int(self.values[0])
                current = self.db.get_einstellungen(self.guild_id)
                self.db.update_einstellungen(
                    self.guild_id,
                    role_id,
                    current[2],
                    current[3],
                    current[4]
                )

                return await select_interaction.response.edit_message(
                    content=f"✅ Support-Rolle wurde auf <@&{role_id}> gesetzt.",
                    view=None
                )

        view = discord.ui.View(timeout=60)
        view.add_item(RoleSelect(self.db, self.guild_id, interaction.user, interaction.guild.roles))
        await interaction.followup.send("Wähle eine Support-Rolle aus:", view=view, ephemeral=True)


class TranskriptChannelButton(discord.ui.Button):
    def __init__(self, db, guild_id):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Transkript-Channel",
            custom_id=f"settings_transcript_{guild_id}",
            row=0
        )
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class TranscriptSelect(discord.ui.Select):
            def __init__(self, db, guild_id, user, channels):
                self.db = db
                self.guild_id = guild_id
                self.user = user
                options = [
                    discord.SelectOption(label=channel.name, value=str(channel.id))
                    for channel in channels
                ][:25]
                super().__init__(
                    placeholder="Wähle einen Transkript-Channel",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, select_interaction: discord.Interaction):
                if select_interaction.user != self.user:
                    return await select_interaction.response.send_message(
                        "Nur der ursprüngliche Benutzer kann diese Auswahl treffen.",
                        ephemeral=True
                    )

                channel_id = int(self.values[0])
                current = self.db.get_einstellungen(self.guild_id)
                self.db.update_einstellungen(
                    self.guild_id,
                    current[1],
                    channel_id,
                    current[3],
                    current[4]
                )

                return await select_interaction.response.edit_message(
                    content=f"✅ Transkript-Channel wurde auf <#{channel_id}> gesetzt.",
                    view=None
                )

        view = discord.ui.View(timeout=60)
        view.add_item(TranscriptSelect(self.db, self.guild_id, interaction.user, interaction.guild.text_channels))
        await interaction.followup.send("Wähle einen Transkript-Channel aus:", view=view, ephemeral=True)



class TicketChannelButton(discord.ui.Button):
    def __init__(self, db, guild_id):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Ticket-Channel",
            custom_id=f"settings_ticket_{guild_id}",
            row=1
        )
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class TicketSelect(discord.ui.Select):
            def __init__(self, db, guild_id, user, channels):
                self.db = db
                self.guild_id = guild_id
                self.user = user
                options = [
                    discord.SelectOption(label=channel.name, value=str(channel.id))
                    for channel in channels
                ][:25]
                super().__init__(
                    placeholder="Wähle einen Ticket-Channel",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, select_interaction: discord.Interaction):
                if select_interaction.user != self.user:
                    return await select_interaction.response.send_message(
                        "Nur der ursprüngliche Benutzer kann diese Auswahl treffen.",
                        ephemeral=True
                    )

                channel_id = int(self.values[0])
                current = self.db.get_einstellungen(self.guild_id)
                self.db.update_einstellungen(
                    self.guild_id,
                    current[1],
                    current[2],
                    channel_id,
                    current[4]
                )

                return await select_interaction.response.edit_message(
                    content=f"✅ Ticket-Channel wurde auf <#{channel_id}> gesetzt.",
                    view=None
                )

        view = discord.ui.View(timeout=60)
        view.add_item(TicketSelect(self.db, self.guild_id, interaction.user, interaction.guild.text_channels))
        await interaction.followup.send("Wähle einen Ticket-Channel aus:", view=view, ephemeral=True)



class LogChannelButton(discord.ui.Button):
    def __init__(self, db, guild_id):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Log-Channel",
            custom_id=f"settings_log_{guild_id}",
            row=1
        )
        self.db = db
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class ChannelSelect(discord.ui.Select):
            def __init__(self, db, guild_id, user, channels):
                self.db = db
                self.guild_id = guild_id
                self.user = user

                options = [
                    discord.SelectOption(label=channel.name, value=str(channel.id))
                    for channel in channels
                ][:25]

                super().__init__(
                    placeholder="Wähle einen Log-Channel",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, select_interaction: discord.Interaction):
                if select_interaction.user != self.user:
                    return await select_interaction.response.send_message(
                        "Nur der ursprüngliche Benutzer kann diese Auswahl treffen.",
                        ephemeral=True
                    )

                channel_id = int(self.values[0])
                current = self.db.get_einstellungen(self.guild_id)
                self.db.update_einstellungen(
                    self.guild_id,
                    current[1],  # support role
                    current[2],  # transcript channel
                    current[3],  # ticket channel
                    channel_id
                )

                return await select_interaction.response.edit_message(
                    content=f"✅ Log-Channel wurde auf <#{channel_id}> gesetzt.",
                    view=None
                )

        view = discord.ui.View(timeout=60)
        view.add_item(ChannelSelect(self.db, self.guild_id, interaction.user, interaction.guild.text_channels))
        await interaction.followup.send("Wähle einen Log-Channel aus:", view=view, ephemeral=True)



class AbbrechenButton(discord.ui.Button):
    def __init__(self, user):
        super().__init__(label="Abbrechen", style=discord.ButtonStyle.red, row=1)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("Nicht dein Vorgang.", ephemeral=True)

        return await interaction.response.edit_message(content="❌ Einstellungen abgebrochen.", view=None)
