import discord
from discord.ext import commands
from discord import Message
from discord.utils import format_dt
from datetime import datetime, timezone

ansi_blue = "\u001b[2;34m"
ansi_reset = "\u001b[0m"

class Apps(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def time_ago(self, dt: datetime) -> str:
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

    @commands.message_command(name="Benutzerinfo")
    async def userinfo(self, ctx: discord.ApplicationContext, message: Message):
        member = message.author
        now = datetime.now(timezone.utc)
        created_at = member.created_at
        joined_at = getattr(member, "joined_at", None)

        user_obj = await self.bot.fetch_user(member.id)

        embed = discord.Embed(
            title=f"🔎 Benutzerinfo: {member.display_name}",
            color=member.color if hasattr(member, 'color') and member.color.value else discord.Color.blurple(),
            timestamp=now
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🆔 ID", value=f"```ansi\n{ansi_blue}{member.id}{ansi_reset}```", inline=True)
        embed.add_field(name="👤 Benutzername", value=f"```ansi\n{ansi_blue}{member.name}{ansi_reset}```", inline=True)
        embed.add_field(name="🤖 Bot", value=f"```ansi\n{ansi_blue}{'Ja' if member.bot else 'Nein'}{ansi_reset}```", inline=True)

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

        if getattr(member, "premium_since", None):
            embed.add_field(
                name="🚀 Boostet seit",
                value=f"```ansi\n{ansi_blue}{format_dt(member.premium_since, 'F')} ({self.time_ago(member.premium_since)}){ansi_reset}```",
                inline=True
            )

        if hasattr(member, "timed_out_until") and member.timed_out_until:
            embed.add_field(
                name="⏱️ Timeout aktiv bis",
                value=f"```ansi\n{ansi_blue}{format_dt(member.timed_out_until, 'F')} ({self.time_ago(member.timed_out_until)}){ansi_reset}```",
                inline=False
            )

        devices = []
        if getattr(member, "desktop_status", None) != discord.Status.offline:
            devices.append("💻 PC")
        if getattr(member, "mobile_status", None) != discord.Status.offline:
            devices.append("📱 Handy")
        if getattr(member, "web_status", None) != discord.Status.offline:
            devices.append("🌐 Website")

        if devices and not member.bot:
            embed.add_field(name="🖥️ Online auf", value=f"```ansi\n{ansi_blue}{', '.join(devices)}{ansi_reset}```", inline=True)

        embed.add_field(name="📶 Status", value=f"```ansi\n{ansi_blue}{str(member.status).capitalize()}{ansi_reset}```", inline=True)

        if member.activities:
            aktivitaetsliste = [act.name for act in member.activities if act.name]
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

        embed.set_footer(icon_url=ctx.author.display_avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Apps(bot))
