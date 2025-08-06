import discord
from discord.ext import commands
from discord.utils import format_dt
from discord.commands import SlashCommandGroup
from datetime import datetime, timezone, timedelta
import psutil
import platform

ansi_blue = "\u001b[2;34m"
ansi_reset = "\u001b[0m"

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.now(timezone.utc)

    def format_timedelta(self, delta: timedelta) -> str:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"🗓️ {days}d ⏰ {hours}h ⏳ {minutes}m ⏲️ {seconds}s"

    def time_ago(self, dt: datetime) -> str:
        if dt is None:
            return "Nicht verfügbar"
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        seconds = int(delta.total_seconds())

        if seconds < 60:
            return f"vor {seconds} Sekunden"
        elif seconds < 3600:
            return f"vor {seconds // 60} Minuten"
        elif seconds < 86400:
            return f"vor {seconds // 3600} Stunden"
        elif seconds < 2592000:
            return f"vor {seconds // 86400} Tagen"
        elif seconds < 31536000:
            return f"vor {seconds // 2592000} Monaten"
        else:
            return f"vor {seconds // 31536000} Jahren"


    info = SlashCommandGroup("info", "Informationen")

    @info.command(name="user", description="Zeigt detaillierte Informationen über einen Benutzer.")
    async def user(self, ctx: discord.ApplicationContext, user: discord.Member = None):
        if user is None:
            user = ctx.author

        now = datetime.now(timezone.utc)
        created_at = user.created_at
        joined_at = getattr(user, "joined_at", None)

        user_obj = await self.bot.fetch_user(user.id)

        embed = discord.Embed(
            title=f"🔎 Benutzerinfo: {user.display_name}",
            color=user.color if hasattr(user, 'color') and user.color.value else discord.Color.blurple(),
            timestamp=now
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="🆔 ID", value=f"```ansi\n{ansi_blue}{user.id}{ansi_reset}```", inline=True)
        embed.add_field(name="👤 Benutzername", value=f"```ansi\n{ansi_blue}{user.name}{ansi_reset}```", inline=True)
        embed.add_field(name="🤖 Bot", value=f"```ansi\n{ansi_blue}{'Ja' if user.bot else 'Nein'}{ansi_reset}```", inline=True)

        embed.add_field(
            name="📅 Konto erstellt am",
            value=f"{format_dt(created_at, 'F')} ({format_dt(created_at, 'R')})",
            inline=False
        )

        if joined_at:
            embed.add_field(
                name="📥 Server beigetreten am",
                value=f"{format_dt(joined_at, 'F')} ({format_dt(joined_at, 'R')})",
                inline=False
            )

        if getattr(user, "premium_since", None):
            embed.add_field(
                name="🚀 Boostet seit",
                value=f"```ansi\n{ansi_blue}{format_dt(user.premium_since, 'F')} ({self.time_ago(user.premium_since)}){ansi_reset}```",
                inline=True
            )

        if hasattr(user, "timed_out_until") and user.timed_out_until:
            embed.add_field(
                name="⏱️ Timeout aktiv bis",
                value=f"```ansi\n{ansi_blue}{format_dt(user.timed_out_until, 'F')} ({self.time_ago(user.timed_out_until)}){ansi_reset}```",
                inline=False
            )

        devices = []
        if getattr(user, "desktop_status", None) != discord.Status.offline:
            devices.append("💻 PC")
        if getattr(user, "mobile_status", None) != discord.Status.offline:
            devices.append("📱 Handy")
        if getattr(user, "web_status", None) != discord.Status.offline:
            devices.append("🌐 Website")

        if devices and not user.bot:
            embed.add_field(name="🖥️ Online auf", value=f"```ansi\n{ansi_blue}{', '.join(devices)}{ansi_reset}```", inline=True)

        embed.add_field(name="📶 Status", value=f"```ansi\n{ansi_blue}{str(user.status).capitalize()}{ansi_reset}```", inline=True)

        if user.activities:
            aktivitaetsliste = [act.name for act in user.activities if act.name]
            if aktivitaetsliste:
                embed.add_field(name="🎮 Aktivität(en)",
                                value=f"```ansi\n{ansi_blue}{', '.join(aktivitaetsliste)}{ansi_reset}```",
                                inline=False)

        if user_obj.accent_color:
            embed.add_field(name="🎨 Profilfarbe",
                            value=f"```ansi\n{ansi_blue}#{user_obj.accent_color.value:06X}{ansi_reset}```",
                            inline=True)

        if user_obj.banner:
            embed.set_image(url=user_obj.banner.url)

        embed.set_footer(text=f"Angefragt von {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.respond(embed=embed)

    @info.command(description="Stats zum Server.")
    async def server(self, ctx: discord.ApplicationContext):
        guild = ctx.guild
        icon_url = guild.icon.url if guild.icon else None
        banner_url = guild.banner.url if guild.banner else None
        splash_url = guild.splash.url if guild.splash else None

        text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len(guild.categories)
        bot_count = len([m for m in guild.members if m.bot])
        humans = guild.member_count - bot_count

        embed = discord.Embed(
            title=f"📊 Serverinformationen zu: `{guild.name}`",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )

        if icon_url:
            embed.set_thumbnail(url=icon_url)
        if banner_url:
            embed.set_image(url=banner_url)

        embed.add_field(name="👑 Owner", value=f"```ansi\n{ansi_blue}{guild.owner}{ansi_reset}```", inline=False)
        embed.add_field(name="👥 Mitglieder", value=f"```ansi\n{ansi_blue}{humans}{ansi_reset}```", inline=True)
        embed.add_field(name="🤖 Bots", value=f"```ansi\n{ansi_blue}{bot_count}{ansi_reset}```", inline=True)
        embed.add_field(name="🆔 Server ID", value=f"```ansi\n{ansi_blue}{guild.id}{ansi_reset}```", inline=False)
        embed.add_field(name="📅 Erstellt", value=format_dt(guild.created_at, style='F') + f" ({format_dt(guild.created_at, style='R')})", inline=False)

        embed.add_field(name="📝 Text-Kanäle", value=f"```ansi\n{ansi_blue}{text_channels}{ansi_reset}```", inline=True)
        embed.add_field(name="🔊 Voice-Kanäle", value=f"```ansi\n{ansi_blue}{voice_channels}{ansi_reset}```", inline=True)
        embed.add_field(name="💠 Kategorien", value=f"```ansi\n{ansi_blue}{categories}{ansi_reset}```", inline=True)

        embed.add_field(name="🎭 Rollen", value=f"```ansi\n{ansi_blue}{len(guild.roles)}{ansi_reset}```", inline=True)
        embed.add_field(name="😄 Emojis", value=f"```ansi\n{ansi_blue}{len(guild.emojis)}{ansi_reset}```", inline=True)
        embed.add_field(name="🎟️ Sticker", value=f"```ansi\n{ansi_blue}{len(guild.stickers)}{ansi_reset}```", inline=True)

        if guild.afk_channel:
            embed.add_field(name="💤 AFK", value=f"```ansi\n{ansi_blue}{guild.afk_channel.name} ({guild.afk_timeout // 60} min){ansi_reset}```", inline=True)

        embed.add_field(name="🚀 Boosts", value=f"```ansi\n{ansi_blue}Level {guild.premium_tier} • {guild.premium_subscription_count or 0} Boosts{ansi_reset}```", inline=True)

        if splash_url:
            embed.add_field(name="🌊 Einladungshintergrund", value=f"```ansi\n{ansi_blue}Splash ansehen: {splash_url}{ansi_reset}```", inline=True)

        embed.set_footer(text=f"Angefragt von {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.respond(embed=embed)

    @info.command(name="bot", description="Detaillierte Informationen über den Bot.")
    async def bot_info(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        now = datetime.now(timezone.utc)
        uptime = now - self.start_time

        process = psutil.Process()
        cpu_percent = psutil.cpu_percent(interval=0.5)
        ram_usage_mb = process.memory_info().rss / 1024 / 1024
        python_version = platform.python_version()
        discord_py_version = discord.__version__

        guild_count = len(self.bot.guilds)
        user_count = len(set(self.bot.get_all_members()))

        created_at = self.bot.user.created_at if self.bot.user else None
        created_str = "Nicht verfügbar" if not created_at else f"{format_dt(created_at, 'F')} ({format_dt(created_at, 'R')})"

        embed = discord.Embed(
            title="🤖 Bot-Informationen",
            description=f"# [GitHub](https://github.com/InvalidDavid/DiscordBot)",
            color=discord.Color.blurple(),
            timestamp=now
        )

        embed.add_field(
            name="🆔 Bot ID",
            value=f"```ansi\n{ansi_blue}{self.bot.user.id if self.bot.user else 'N/A'}{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="📛 Bot Name",
            value=f"```ansi\n{ansi_blue}{self.bot.user}{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="📅 Bot erstellt am",
            value=f"{created_str}",
            inline=False
        )
        embed.add_field(
            name="🕰️ Bot Uptime",
            value=(
                f"```ansi\n{ansi_blue}{self.format_timedelta(uptime)}{ansi_reset}```"
                f"Letzter Neustart: {format_dt(self.start_time, 'F')} ({format_dt(self.start_time, 'R')})"
            ),
            inline=False
        )
        embed.add_field(
            name="💻 CPU-Auslastung",
            value=f"```ansi\n{ansi_blue}{cpu_percent:.1f}%{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="🧠 RAM-Verbrauch",
            value=f"```ansi\n{ansi_blue}{ram_usage_mb:.2f} MB{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="🐍 Python Version",
            value=f"```ansi\n{ansi_blue}{python_version}{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="📦 Py-cord Version",
            value=f"```ansi\n{ansi_blue}{discord_py_version}{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="👥 Server",
            value=f"```ansi\n{ansi_blue}{guild_count}{ansi_reset}```",
            inline=True
        )
        embed.add_field(
            name="👤 Benutzer (gesamt)",
            value=f"```ansi\n{ansi_blue}{user_count}{ansi_reset}```",
            inline=True
        )
        embed.set_footer(text=f"Angefragt von {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.respond(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
