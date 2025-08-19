import os
import random
import discord
from discord.ext import commands, tasks
from discord.commands import slash_command
import asyncpraw
import time
import datetime
import pytz
from datetime import datetime
from dotenv import load_dotenv
import aiohttp

load_dotenv()

ansi_blue = "\u001b[2;34m"
ansi_reset = "\u001b[0m"

mond_phase = {
    "New Moon": "Neumond",
    "Waxing Crescent": "Zunehmende Mondsichel",
    "First Quarter": "Erstes Viertel",
    "Waxing Gibbous": "Zunehmender Mond",
    "Full Moon": "Vollmond",
    "Waning Gibbous": "Abnehmender Mond",
    "Last Quarter": "Letztes Viertel",
    "Waning Crescent": "Abnehmende Mondsichel"
}



class MemeView(discord.ui.View):
    def __init__(self, cog, posts, author, cooldown=2, timeout=60):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.posts = posts
        self.author = author
        self.cooldown = cooldown
        self.last_click = 0
        self.message = None

        self.next_meme_button = discord.ui.Button(
            label="Nächstes Meme",
            style=discord.ButtonStyle.primary,
            emoji="🔄"
        )
        self.next_meme_button.callback = self.next_meme_callback
        self.add_item(self.next_meme_button)

        self.reddit_link_button = discord.ui.Button(
            label="Auf Reddit ansehen",
            style=discord.ButtonStyle.link,
            emoji="🔗",
            url="https://reddit.com"
        )
        self.add_item(self.reddit_link_button)

    async def send_new_meme(self, interaction):
        if not self.posts:
            self.posts = self.cog.cached_posts.copy()
            if not self.posts:
                await interaction.response.send_message("Keine neuen Memes gefunden.", ephemeral=True)
                return

        post = random.choice(self.posts)
        self.posts.remove(post)

        post_age_hours = (datetime.utcnow() - datetime.utcfromtimestamp(post.created_utc)).total_seconds() / 3600
        post_age_str = f"{int(post_age_hours)}h alt"

        footer_text = (
            f"👍 {post.ups} | 💬 {post.num_comments} | "
            f"Author: {post.author} | "
            f"{post_age_str}"
        )

        embed = discord.Embed(title=post.title, color=discord.Color.blurple())
        embed.set_image(url=post.url)
        embed.set_footer(text=footer_text)

        self.reddit_link_button.url = f"https://reddit.com{post.permalink}"

        await interaction.response.edit_message(embed=embed, view=self)

    async def next_meme_callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("Nur der Befehlsersteller kann diesen Button nutzen.", ephemeral=True)
            return

        now = time.time()
        if now - self.last_click < self.cooldown:
            await interaction.response.send_message(f"Bitte warte {self.cooldown} Sekunden zwischen den Klicks.", ephemeral=True)
            return
        self.last_click = now

        new_view = MemeView(self.cog, self.posts.copy(), self.author, cooldown=self.cooldown, timeout=60)
        new_view.message = self.message

        await new_view.send_new_meme(interaction)

    async def on_timeout(self):
        self.next_meme_button.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception as e:
                print(f"[ERROR] Timeout edit failed: {e}")

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cached_posts = []
        self.cache_refresh.start()

        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    def cog_unload(self):
        self.cache_refresh.cancel()

    @tasks.loop(minutes=5)
    async def cache_refresh(self):
        try:
            subreddit = await self.reddit.subreddit("ich_iel")
            hot = subreddit.hot(limit=50)

            posts = []
            async for post in hot:
                if not post.is_video:
                    posts.append(post)

            self.cached_posts = posts
        except Exception as e:
            print(f"[ERROR] Reddit API Exception: {e}")

    @cache_refresh.before_loop
    async def before_cache_refresh(self):
        await self.bot.wait_until_ready()

    @slash_command()
    async def meme(self, ctx):
        await ctx.defer()

        if not self.cached_posts:
            await ctx.respond("Momentan keine Memes verfügbar, bitte später versuchen.")
            return

        view = MemeView(self, self.cached_posts.copy(), ctx.author, cooldown=2, timeout=60)
        first_post = random.choice(view.posts)
        view.posts.remove(first_post)

        post_age_hours = (datetime.utcnow() - datetime.utcfromtimestamp(first_post.created_utc)).total_seconds() / 3600
        post_age_str = f"{int(post_age_hours)}h alt"

        footer_text = (
            f"👍 {first_post.ups} | 💬 {first_post.num_comments} | "
            f"Author: {first_post.author} | "
            f"{post_age_str}"
        )

        embed = discord.Embed(title=first_post.title, color=discord.Color.blurple())
        embed.set_image(url=first_post.url)
        embed.set_footer(text=footer_text)

        view.reddit_link_button.url = f"https://reddit.com{first_post.permalink}"

        await ctx.respond(embed=embed, view=view)
        view.message = await ctx.interaction.original_response()

    @slash_command(name="wetter", description="Zeigt das detaillierte Wetter einer Stadt an")
    async def wetter(self, ctx, stadt: discord.Option(str, "Gib den Stadtnamen ein"), unsichtbar: discord.Option(str, "Nachricht unsichtbar für andere?", choices=["Ja", "Nein"], default="Ja")):
        nachricht = True if unsichtbar.lower() == "ja" else False
        await ctx.defer(ephemeral=nachricht)

        url = f"http://wttr.in/{stadt}?format=j1&lang=de"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.respond(f"❌ Konnte Wetter für `{stadt}` nicht abrufen.", ephemeral=True)
                    return
                data = await resp.json()

        try:
            current = data.get("current_condition", [{}])[0]
            weather_desc = current.get("lang_de", [{"value": "N/A"}])[0].get("value", "N/A")
            temp_c = current.get("temp_C", "N/A")
            feels_like_c = current.get("FeelsLikeC", "N/A")
            humidity = current.get("humidity", "N/A")
            wind_kph = current.get("windspeedKmph", "N/A")
            wind_dir = current.get("winddir16Point", "N/A")
            uv_index = current.get("uvIndex", "N/A")
            pressure = current.get("pressure", "N/A")
            cloudcover = current.get("cloudcover", "N/A")

            astronomy = data.get("weather", [{}])[0].get("astronomy", [{}])[0]
            sunrise_raw = astronomy.get("sunrise", "N/A")
            sunset_raw = astronomy.get("sunset", "N/A")

            if sunrise_raw != "N/A":
                sunrise_utc = datetime.strptime(sunrise_raw, "%I:%M %p")
                today = datetime.now(pytz.utc).date()
                sunrise_utc = datetime.combine(today, sunrise_utc.time()).replace(tzinfo=pytz.utc)
                sunrise_berlin = sunrise_utc.astimezone(pytz.timezone("Europe/Berlin"))
                sunrise = sunrise_berlin.strftime("%H:%M")

            if sunset_raw != "N/A":
                sunset_utc = datetime.strptime(sunset_raw, "%I:%M %p")
                today = datetime.now(pytz.utc).date()
                sunset_utc = datetime.combine(today, sunset_utc.time()).replace(tzinfo=pytz.utc)
                sunset_berlin = sunset_utc.astimezone(pytz.timezone("Europe/Berlin"))
                sunset = sunset_berlin.strftime("%H:%M")

            moon_phase_raw = astronomy.get("moon_phase", "N/A")
            moon_phase = mond_phase.get(moon_phase_raw, moon_phase_raw)

            wetter_stunden = data.get("weather", [{}])[0].get("hourly", [])
            wetter_morgen = wetter_stunden[1] if len(wetter_stunden) > 1 else {}
            wetter_nachmittag = wetter_stunden[3] if len(wetter_stunden) > 3 else {}
            wetter_abend = wetter_stunden[5] if len(wetter_stunden) > 5 else {}

            def make_hourly_str(h):
                desc = h.get("lang_de", [{"value": "N/A"}])[0].get("value", "N/A")
                return (
                    f"Temperatur: {h.get('tempC', 'N/A')} °C\n"
                    f"Regenchance: {h.get('chanceofrain', 'N/A')} %\n"
                    f"Wind: {h.get('windspeedKmph', 'N/A')} km/h {h.get('winddir16Point', 'N/A')}\n"
                    f"Wetter: {desc}"
                )

            def make_day_summary(d):
                return (
                    f"Min: {d.get('mintempC', 'N/A')} °C\n"
                    f"Max: {d.get('maxtempC', 'N/A')} °C\n"
                    f"Regenwahrscheinlichkeit: {d.get('daily_chance_of_rain', 'N/A')} %"
                )

            warnungen = data.get("alerts", [])
            warnung_text = "\n".join([alert.get("desc", "Warnung ohne Beschreibung") for alert in
                                      warnungen]) if warnungen else "Keine aktuellen Warnungen."

            heute = data.get("weather", [{}])[0]
            morgen = data.get("weather", [{}])[1] if len(data.get("weather", [])) > 1 else {}
            uebermorgen = data.get("weather", [{}])[2] if len(data.get("weather", [])) > 2 else {}

            embed = discord.Embed(
                title=f"Wetter in {stadt}",
                description=f"## **{weather_desc}**",
                color=discord.Color.blue()
            )

            embed.add_field(name="🌡 Temperatur",
                            value=f"```ansi\n{ansi_blue}{temp_c} °C (Gefühlt: {feels_like_c} °C){ansi_reset}\n```",
                            inline=True)
            embed.add_field(name="💧 Luftfeuchtigkeit",
                            value=f"```ansi\n{ansi_blue}{humidity} %{ansi_reset}\n```", inline=True)
            embed.add_field(name="🌬 Wind",
                            value=f"```ansi\n{ansi_blue}{wind_kph} km/h {wind_dir}{ansi_reset}\n```", inline=True)
            embed.add_field(name="☀ UV-Index",
                            value=f"```ansi\n{ansi_blue}{uv_index}{ansi_reset}\n```", inline=True)
            embed.add_field(name="📊 Luftdruck",
                            value=f"```ansi\n{ansi_blue}{pressure} hPa{ansi_reset}\n```", inline=True)
            embed.add_field(name="☁ Bewölkung",
                            value=f"```ansi\n{ansi_blue}{cloudcover} %{ansi_reset}\n```", inline=True)
            embed.add_field(name="🌅 Sonnenaufgang",
                            value=f"```ansi\n{ansi_blue}{sunrise} Uhr{ansi_reset}\n```", inline=True)
            embed.add_field(name="🌇 Sonnenuntergang",
                            value=f"```ansi\n{ansi_blue}{sunset} Uhr{ansi_reset}\n```", inline=True)
            embed.add_field(name="🌕 Mondphase",
                            value=f"```ansi\n{ansi_blue}{moon_phase}{ansi_reset}\n```", inline=True)

            embed.add_field(name="🌄 Tagesverlauf Morgen (6-9 Uhr)",
                            value=f"```ansi\n{ansi_blue}{make_hourly_str(wetter_morgen)}{ansi_reset}\n```", inline=True)
            embed.add_field(name="🏞 Tagesverlauf Nachmittag (12-15 Uhr)",
                            value=f"```ansi\n{ansi_blue}{make_hourly_str(wetter_nachmittag)}{ansi_reset}\n```",
                            inline=True)
            embed.add_field(name="🌆 Tagesverlauf Abend (18-21 Uhr)",
                            value=f"```ansi\n{ansi_blue}{make_hourly_str(wetter_abend)}{ansi_reset}\n```", inline=True)

            embed.add_field(name="📅 Heute",
                            value=f"```ansi\n{ansi_blue}{make_day_summary(heute)}{ansi_reset}\n```", inline=True)
            embed.add_field(name="📅 Morgen",
                            value=f"```ansi\n{ansi_blue}{make_day_summary(morgen)}{ansi_reset}\n```", inline=True)
            embed.add_field(name="📅 Übermorgen",
                            value=f"```ansi\n{ansi_blue}{make_day_summary(uebermorgen)}{ansi_reset}\n```", inline=True)

            embed.add_field(name="⚠ Aktuelle Warnungen",
                            value=f"```ansi\n{ansi_blue}{warnung_text}{ansi_reset}\n```", inline=False)

            embed.set_footer(text=f"Daten von wttr.in")

            await ctx.respond(embed=embed, ephemeral=nachricht)
        except Exception as e:
            await ctx.respond(f"❌ Fehler beim Verarbeiten der Wetterdaten: {e}", ephemeral=True)


def setup(bot):
    bot.add_cog(Random(bot))
