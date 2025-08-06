import discord
from discord.ext import commands
from discord import Message
from discord.utils import format_dt
from datetime import datetime, timezone

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

        account_age = self.time_ago(created_at)
        join_age = self.time_ago(joined_at) if joined_at else "Nicht verfügbar"

        user_obj = await self.bot.fetch_user(member.id)

        embed = discord.Embed(
            title=f"🔎 Benutzerinfo: {member.display_name}",
            description=f"[Profil anzeigen](https://discord.com/users/{member.id})",
            color=member.color if hasattr(member, 'color') and member.color.value else discord.Color.blurple(),
            timestamp=now
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="👤 Benutzername", value=f"`{member.name}`", inline=True)
        embed.add_field(name="🤖 Bot", value="✅ Ja" if member.bot else "❌ Nein", inline=True)

        embed.add_field(
            name="📅 Konto erstellt am",
            value=f"{format_dt(created_at, 'f')} ({account_age})",
            inline=False
        )

        if isinstance(member, discord.Member) and joined_at:
            embed.add_field(
                name="📥 Server beigetreten am",
                value=f"{format_dt(joined_at, 'f')} ({join_age})",
                inline=False
            )

        if member.premium_since:
            embed.add_field(
                name="🚀 Boostet seit",
                value=f"{format_dt(member.premium_since, 'f')} ({self.time_ago(member.premium_since)})",
                inline=True
            )

        if hasattr(member, "timed_out_until") and member.timed_out_until:
            embed.add_field(
                name="⏱️ Timeout aktiv bis",
                value=f"{format_dt(member.timed_out_until, 'f')} ({self.time_ago(member.timed_out_until)})",
                inline=False
            )

        devices = []
        if member.desktop_status != discord.Status.offline:
            devices.append("💻 Desktop")
        if member.mobile_status != discord.Status.offline:
            devices.append("📱 Mobil")
        if member.web_status != discord.Status.offline:
            devices.append("🌐 Web")

        if devices:
            embed.add_field(name="🖥️ Online auf", value=", ".join(devices), inline=True)

        embed.add_field(name="📶 Status", value=str(member.status).capitalize(), inline=True)

        if member.activities:
            aktivitätsliste = []
            for act in member.activities:
                if act.name:
                    aktivitätsliste.append(f"{act.name}")
            embed.add_field(name="🎮 Aktivität(en)", value=", ".join(aktivitätsliste), inline=False)

        if user_obj.accent_color:
            embed.add_field(name="🎨 Profilfarbe", value=f"`#{user_obj.accent_color.value:06X}`", inline=True)

        if user_obj.banner:
            embed.set_image(url=user_obj.banner.url)

        embed.set_footer(icon_url=ctx.author.display_avatar.url)

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Apps(bot))
