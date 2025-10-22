import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import aiosqlite
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

DB_PATH = "Data/geburstag.db"


class GeburtstagsDB:
    def __init__(self, db_name: str = DB_PATH):
        self.db_name = db_name
        self.verbindung = None

    async def verbinden(self):
        self.verbindung = await aiosqlite.connect(self.db_name)
        self.verbindung.row_factory = aiosqlite.Row
        await self.einrichten()

    async def einrichten(self):
        try:
            await self.verbindung.execute("""
                CREATE TABLE IF NOT EXISTS geburtstage (
                    benutzer_id INTEGER PRIMARY KEY,
                    server_id INTEGER DEFAULT 0,
                    geburtstags_kanal_id INTEGER DEFAULT 0,
                    geburtstags_rolle_id INTEGER DEFAULT 0,
                    embed_kanal_id INTEGER DEFAULT 0,
                    geburtstags_tag INTEGER DEFAULT 0,
                    geburtstags_monat INTEGER DEFAULT 0
                )
            """)

            await self.verbindung.execute("""
                CREATE TABLE IF NOT EXISTS geburtstags_embeds (
                    server_id INTEGER PRIMARY KEY,
                    kanal_id INTEGER,
                    nachrichten_id INTEGER
                )
            """)

            await self.verbindung.execute("""
                CREATE TABLE IF NOT EXISTS geburtstag_logs (
                    server_id INTEGER,
                    datum TEXT,
                    PRIMARY KEY (server_id, datum)
                )
            """)

            await self.verbindung.commit()
        except Exception as e:
            print(f"DB Fehler: {e}")

    async def wurde_heute_gesendet(self, server_id):
        heute = datetime.datetime.now().strftime("%Y-%m-%d")
        async with self.verbindung.execute(
            "SELECT 1 FROM geburtstag_logs WHERE server_id = ? AND datum = ?",
            (server_id, heute)
        ) as cursor:
            return await cursor.fetchone() is not None

    async def markiere_als_gesendet(self, server_id):
        heute = datetime.datetime.now().strftime("%Y-%m-%d")
        await self.verbindung.execute(
            "INSERT OR REPLACE INTO geburtstag_logs (server_id, datum) VALUES (?, ?)",
            (server_id, heute)
        )
        await self.verbindung.commit()


    async def setze_geburtstags_kanal(self, server_id, kanal_id, rollen_id, embed_kanal_id):
        await self.verbindung.execute(
            """
            INSERT OR REPLACE INTO geburtstage (
                server_id, geburtstags_kanal_id, geburtstags_rolle_id, embed_kanal_id
            ) VALUES (?, ?, ?, ?)
            """,
            (server_id, kanal_id, rollen_id, embed_kanal_id)
        )
        await self.verbindung.commit()

    async def hole_geburtstags_kanal(self, server_id):
        async with self.verbindung.execute(
                "SELECT geburtstags_kanal_id FROM geburtstage WHERE server_id = ?", (server_id,)
        ) as cursor:
            ergebnis = await cursor.fetchone()
        return ergebnis[0] if ergebnis else None

    async def hole_geburtstags_rolle(self, server_id):
        async with self.verbindung.execute(
                "SELECT geburtstags_rolle_id FROM geburtstage WHERE server_id = ?", (server_id,)
        ) as cursor:
            ergebnis = await cursor.fetchone()
        return ergebnis[0] if ergebnis else None

    async def hole_embed_kanal_id(self, server_id):
        async with self.verbindung.execute(
                "SELECT embed_kanal_id FROM geburtstage WHERE server_id = ?", (server_id,)
        ) as cursor:
            ergebnis = await cursor.fetchone()
        return ergebnis[0] if ergebnis else None

    async def setze_geburtstag(self, server_id, benutzer_id, tag, monat):
        await self.verbindung.execute(
            "INSERT OR REPLACE INTO geburtstage (benutzer_id, server_id, geburtstags_tag, geburtstags_monat) VALUES (?, ?, ?, ?)",
            (benutzer_id, server_id or 0, tag, monat)
        )
        await self.verbindung.commit()

    async def hole_geburtstag_fuer_datum(self, tag, monat):
        async with self.verbindung.execute(
                "SELECT * FROM geburtstage WHERE geburtstags_tag = ? AND geburtstags_monat = ?", (tag, monat)
        ) as cursor:
            return await cursor.fetchall()

    async def hole_kommende_geburtstage(self):
        heute = datetime.datetime.now()
        async with self.verbindung.execute(
                "SELECT benutzer_id, geburtstags_tag, geburtstags_monat FROM geburtstage WHERE geburtstags_tag > 0 AND geburtstags_monat > 0"
        ) as cursor:
            geburtstage = await cursor.fetchall()

        ergebnis = []
        for eintrag in geburtstage:
            try:
                naechster_geburtstag = datetime.datetime(
                    year=heute.year,
                    month=eintrag["geburtstags_monat"],
                    day=eintrag["geburtstags_tag"]
                )
                if naechster_geburtstag < heute:
                    naechster_geburtstag = naechster_geburtstag.replace(year=heute.year + 1)
                ergebnis.append((eintrag["benutzer_id"], naechster_geburtstag))
            except Exception:
                continue

        ergebnis.sort(key=lambda x: x[1])
        return ergebnis

    async def speichere_embed_referenz(self, server_id, kanal_id, nachrichten_id):
        await self.verbindung.execute(
            "INSERT OR REPLACE INTO geburtstags_embeds (server_id, kanal_id, nachrichten_id) VALUES (?, ?, ?)",
            (server_id, kanal_id, nachrichten_id)
        )
        await self.verbindung.commit()

    async def hole_embed_referenz(self, server_id):
        async with self.verbindung.execute(
                "SELECT kanal_id, nachrichten_id FROM geburtstags_embeds WHERE server_id = ?", (server_id,)
        ) as cursor:
            ergebnis = await cursor.fetchone()
        return (ergebnis["kanal_id"], ergebnis["nachrichten_id"]) if ergebnis else (None, None)

    async def close(self):
        if self.verbindung:
            await self.verbindung.close()


class Geburtstag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = GeburtstagsDB()
        self.db_ready = False
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.db_ready:
            await self.db.verbinden()
            self.db_ready = True

            self.scheduler.start()
            self.scheduler.add_job(
                self.check_geburtstag,
                trigger=CronTrigger(hour=0, minute=0),
                misfire_grace_time=60
            )
            await self.check_geburtstag()

    async def entferne_rolle(self, server_id: int, member_id: int, rollen_id: int):
        server = self.bot.get_guild(server_id)
        if not server:
            return

        rolle = server.get_role(rollen_id)
        member = server.get_member(member_id)
        if not rolle or not member:
            return

        try:
            await member.remove_roles(rolle, reason="Geburtstag vorbei 🎂")
            print(f"[✔] Geburtstagsrolle von {member} entfernt.")
        except discord.Forbidden:
            print(f"[⚠] Keine Berechtigung, um Rolle von {member} zu entfernen.")

    async def sicherstellen_db(self, ctx):
        if not self.db_ready:
            await ctx.respond("❌ Datenbank ist noch nicht bereit. Bitte später erneut versuchen.", ephemeral=True)
            return False
        if not self.db.verbindung:
            await self.db.verbinden()
        return True

    async def cog_unload(self):
        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        if hasattr(self, 'db'):
            await self.db.close()

    async def check_geburtstag(self):
        jetzt = datetime.datetime.now()

        for server in self.bot.guilds:
            await self.aktualisiere_geburtstags_embed(server)

            if await self.db.wurde_heute_gesendet(server.id):
                continue

            geburtstage_heute = await self.db.hole_geburtstag_fuer_datum(jetzt.day, jetzt.month)
            if not geburtstage_heute:
                continue


            kanal_id = await self.db.hole_geburtstags_kanal(server.id)
            if not kanal_id:
                continue
            kanal = server.get_channel(kanal_id)
            if not kanal:
                continue

            rollen_id = await self.db.hole_geburtstags_rolle(server.id)
            geburtstags_rolle = server.get_role(rollen_id) if rollen_id else None

            mentions = []
            for eintrag in geburtstage_heute:
                member = server.get_member(eintrag["benutzer_id"])
                if member:
                    mentions.append(member.mention)
                    if geburtstags_rolle:
                        try:
                            await member.add_roles(geburtstags_rolle, reason="Geburtstag 🎉")

                            job_id = f"remove_role_{server.id}_{member.id}"
                            if self.scheduler.get_job(job_id):
                                self.scheduler.remove_job(job_id)

                            self.scheduler.add_job(
                                self.entferne_rolle,
                                trigger='date',
                                run_date=datetime.datetime.now() + datetime.timedelta(hours=24),
                                args=[server.id, member.id, geburtstags_rolle.id],
                                id=job_id,
                                misfire_grace_time=300
                            )

                        except discord.Forbidden:
                            pass

            if mentions:
                if len(mentions) == 1:
                    text = f"## Alles Gute zum Geburtstag! 🎉\nHeute hat {mentions[0]} Geburtstag! 🥳🎂\nWir wünschen dir einen fantastischen Tag!"
                else:
                    text = f"## Alles Gute zum Geburtstag! 🎉\nHeute haben {', '.join(mentions)} Geburtstag! 🥳🎂\nWir wünschen euch fantastische Tage!"
                file = discord.File(fp="Data/geburstag.gif", filename="geburstag.gif")
                await kanal.send(text, file=file)
                await self.db.markiere_als_gesendet(server.id)

    async def aktualisiere_geburtstags_embed(self, server):
        kanal_id, nachrichten_id = await self.db.hole_embed_referenz(server.id)
        if not kanal_id or not nachrichten_id:
            return

        kanal = server.get_channel(kanal_id)
        if not kanal:
            return

        try:
            nachricht = await kanal.fetch_message(nachrichten_id)
        except discord.NotFound:
            return

        kommend = await self.db.hole_kommende_geburtstage()
        embed = discord.Embed(title="🎂 Kommende Geburtstage", color=0xff69b4)

        if not kommend:
            embed.description = "Keine Geburtstage gefunden."
        else:
            letzte_nummer = 0
            letzte_datum = None

            for benutzer_id, geburtstag in kommend[:10]:
                if letzte_datum != geburtstag.date():
                    letzte_nummer += 1
                    letzte_datum = geburtstag.date()

                mitglied = server.get_member(benutzer_id)
                name = mitglied.display_name if mitglied else str(benutzer_id)
                name2 = mitglied.name if mitglied else str(benutzer_id)
                timestamp = int(geburtstag.timestamp())
                kommend = await self.db.hole_kommende_geburtstage()
                gesamtanzahl = len(kommend) if kommend else 0
                embed.add_field(
                    name=f"{letzte_nummer}. {name} ({name2})",
                    value=f"<t:{timestamp}:R> (am <t:{timestamp}:d>)",
                    inline=False
                )
        try:
            embed.set_footer(text=f"Du kannst deinen Geburtstag unten hinzufügen | Insgesamt eingetragen: {gesamtanzahl}")
        except UnboundLocalError:
            embed.set_footer(text=f"Du kannst deinen Geburtstag unten hinzufügen | Insgesamt eingetragen: 0")
        await nachricht.edit(embed=embed, view=HinzufuegenGeburtstagView(self))

    geburtstag = SlashCommandGroup("geburtstag", "Geburtstags Befehle")
    admin = geburtstag.create_subgroup("admin", "Administrator")

    @admin.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx,
                    kanal: discord.TextChannel,
                    rolle: discord.Role,
                    embed: Option(discord.TextChannel, "Kanal für Übersicht", required=True)):
        server_id = ctx.guild.id

        await self.db.setze_geburtstags_kanal(server_id, kanal.id, rolle.id, embed.id)

        nachricht = await self.sende_kommende_geburtstage(ctx.guild, embed)
        await self.db.speichere_embed_referenz(server_id, embed.id, nachricht.id)

        await ctx.respond(
            f"✅ Setup abgeschlossen.\n"
            f"- 🎉 Geburtstagsnachrichten: {kanal.mention}\n"
            f"- 🏷️ Rolle: {rolle.mention}\n"
            f"- 📋 Übersichtskanal: {embed.mention}",
            ephemeral=True
        )

    async def sende_kommende_geburtstage(self, server, kanal):
        kommend = await self.db.hole_kommende_geburtstage()
        embed = discord.Embed(title="🎂 Kommende Geburtstage", color=0xff69b4)

        if not kommend:
            embed.description = "Keine Geburtstage gefunden."
        else:
            for i, (benutzer_id, geburtstag) in enumerate(kommend[:10], 1):
                mitglied = server.get_member(benutzer_id)
                name = mitglied.display_name if mitglied else f"{benutzer_id}"
                name2 = mitglied.name if mitglied else str(benutzer_id)
                timestamp = int(geburtstag.timestamp())
                kommend = await self.db.hole_kommende_geburtstage()
                gesamtanzahl = len(kommend) if kommend else 0
                embed.add_field(
                    name=f"{i}. {name} ({name2})",
                    value=f"<t:{timestamp}:R> (am <t:{timestamp}:d>)",
                    inline=False
                )
        try:
            embed.set_footer(text=f"Du kannst deinen Geburtstag unten hinzufügen | Insgesamt eingetragen: {gesamtanzahl}")
        except UnboundLocalError:
            embed.set_footer(text=f"Du kannst deinen Geburtstag unten hinzufügen | Insgesamt eingetragen: 0")
        return await kanal.send(embed=embed, view=HinzufuegenGeburtstagView(self))

    @geburtstag.command(name="entfernen")
    async def entfernen(self, ctx):
        if not await self.sicherstellen_db(ctx):
            await ctx.respond("DB ist noch nicht geladen, warte einen Moment noch.", ephemeral=True)
            return

        async with self.db.verbindung.execute(
                "SELECT geburtstags_tag, geburtstags_monat FROM geburtstage WHERE benutzer_id = ? AND server_id = ?",
                (ctx.user.id, ctx.guild.id if ctx.guild else 0)
        ) as cursor:
            eintrag = await cursor.fetchone()

        if not eintrag or (eintrag["geburtstags_tag"] == 0 and eintrag["geburtstags_monat"] == 0):
            await ctx.respond("❌ Du hast keinen Geburtstag eingetragen.", ephemeral=True)
            return

        await self.db.setze_geburtstag(ctx.guild.id if ctx.guild else 0, ctx.user.id, 0, 0)
        await ctx.respond("✅ Dein Geburtstag wurde entfernt.", ephemeral=True)
        if ctx.guild:
            await self.aktualisiere_geburtstags_embed(ctx.guild)


    @admin.command(name="add", description="Setzt den Geburtstag eines anderen Nutzers (Admin only)")
    @commands.has_permissions(administrator=True)
    @discord.default_permissions(manage_guild=True)
    async def add(self,ctx,
        user: Option(discord.Member, "Benutzer, dessen Geburtstag du setzen willst"),
        tag: Option(int, "Tag", min_value=1, max_value=31),
        monat: Option(int, "Monat", min_value=1, max_value=12)
    ):
        if not await self.sicherstellen_db(ctx):
            return

        if tag < 1 or tag > 31 or monat < 1 or monat > 12:
            await ctx.respond("❌ Ungültiges Datum.", ephemeral=True)
            return

        await self.db.setze_geburtstag(ctx.guild.id, user.id, tag, monat)
        try:
            await self.aktualisiere_geburtstags_embed(ctx.guild)
        except Exception as e:
            await ctx.respond(f"✅ Geburtstag gesetzt, aber Embed konnte nicht aktualisiert werden: `{e}`",
                              ephemeral=True)
            return

        await ctx.respond(
            f"✅ Geburtstag für **{user.display_name}** gesetzt auf **{tag:02d}.{monat:02d}.** Embed aktualisiert.",
            ephemeral=True)

    @admin.command(name="liste", description="Zeigt alle eingetragenen Geburtstage")
    @commands.has_permissions(administrator=True)
    async def liste(self, ctx):
        if not await self.sicherstellen_db(ctx):
            await ctx.respond("Datenbank ist nicht bereit.", ephemeral=True)
            return

        server_id = ctx.guild.id if ctx.guild else 0
        cursor = await self.db.verbindung.execute(
            "SELECT benutzer_id, geburtstags_tag, geburtstags_monat FROM geburtstage WHERE server_id = ? AND geburtstags_tag > 0 AND geburtstags_monat > 0",
            (server_id,)
        )
        daten = await cursor.fetchall()

        if not daten:
            await ctx.respond("Keine Geburtstage auf diesem Server eingetragen.", ephemeral=True)
            return

        text = ""
        for eintrag in daten:
            member = ctx.guild.get_member(eintrag['benutzer_id'])
            name = member.display_name if member else f"User ID {eintrag['benutzer_id']}"
            text += f"{name}: {eintrag['geburtstags_tag']:02d}.{eintrag['geburtstags_monat']:02d}\n"

        if len(text) > 1900:
            with open("alle_geburtstage_server.txt", "w", encoding="utf-8") as f:
                f.write(text)
            await ctx.respond(file=discord.File("alle_geburtstage_server.txt"), ephemeral=True)
        else:
            await ctx.respond(f"```{text}```", ephemeral=True)




class HinzufuegenGeburtstagView(discord.ui.View):
    def __init__(self, geburtstags_cog):
        super().__init__(timeout=None)
        self.geburtstags_cog = geburtstags_cog

    @discord.ui.button(label="🎂 Geburtstag hinzufügen", style=discord.ButtonStyle.success,
                       custom_id="geburtstag_hinzufuegen_button")
    async def hinzufuegen_geburtstag(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.geburtstags_cog.sicherstellen_db(interaction):
            await interaction.response.send_message("Datenbank noch nicht bereit, bitte später versuchen.",
                                                    ephemeral=True)
            return
        try:
            await interaction.response.send_modal(HinzufuegenGeburtstagModal(self.geburtstags_cog))
        except Exception:
            pass


class HinzufuegenGeburtstagModal(discord.ui.Modal):
    def __init__(self, geburtstags_cog):
        super().__init__(title="Füge deinen Geburtstag hinzu")
        self.geburtstags_cog = geburtstags_cog
        self.add_item(discord.ui.InputText(label="Tag", custom_id="tag", min_length=1, max_length=2))
        self.add_item(discord.ui.InputText(label="Monat", custom_id="monat", min_length=1, max_length=2))

    async def callback(self, interaction):
        try:
            tag = int(self.children[0].value)
            monat = int(self.children[1].value)
            assert 1 <= tag <= 31 and 1 <= monat <= 12
        except Exception:
            await interaction.response.send_message("❌ Ungültiges Datum.", ephemeral=True)
            return

        await self.geburtstags_cog.db.setze_geburtstag(
            interaction.guild.id if interaction.guild else 0,
            interaction.user.id,
            tag,
            monat
        )
        await interaction.response.send_message(
            f"✅ Dein Geburtstag wurde auf **{tag}.{monat}** gesetzt!\n"
            f"Mit `/geburtstag entfernen` kannst du dich aus Datenbank entfernen.",
            ephemeral=True
        )

        if interaction.guild:
            await self.geburtstags_cog.aktualisiere_geburtstags_embed(interaction.guild)


def setup(bot):
    bot.add_cog(Geburtstag(bot))
