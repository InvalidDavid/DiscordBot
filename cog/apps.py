import discord
from discord.ext import commands
from datetime import datetime, timezone  # Import timezone

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot




### PROTOTYP



    @commands.message_command(name="User Info")
    async def userinfo(self, ctx: discord.ApplicationContext, message: discord.Message):
        member = message.author

        now = datetime.now(timezone.utc) 

        account_age = (now - member.created_at).days
        server_join_age = (
            (now - member.joined_at).days
            if isinstance(member, discord.Member) and member.joined_at
            else "N/A"
        )

        roles = [role.mention for role in member.roles[1:]] if hasattr(member, 'roles') else []
        highest_role = member.top_role.mention if hasattr(member, 'top_role') and member.top_role != ctx.guild.default_role else "None"
        is_bot = "✅" if member.bot else "❌"
        is_system = "✅" if getattr(member, 'system', False) else "❌"
        status = str(getattr(member, 'status', 'N/A')).title()
        activity = (
            f"{member.activity.type.name.title()} {member.activity.name}"
            if hasattr(member, 'activity') and member.activity
            else "None"
        )
        permissions = []
        if isinstance(member, discord.Member):
            permissions = [perm for perm, value in member.guild_permissions if value]

        embed = discord.Embed(
            title=f"User Info: {member.display_name}",
            color=member.color if hasattr(member, 'color') and member.color != discord.Color.default() else discord.Color.blurple(),
            timestamp=now  
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🆔 **ID**", value=f"`{member.id}`", inline=True)
        embed.add_field(name="📛 **Username**", value=f"`{member.name}`", inline=True)
        embed.add_field(name="#️⃣ **Discriminator**", value=f"`{member.discriminator}`", inline=True)
        embed.add_field(name="🤖 **Bot**", value=is_bot, inline=True)
        embed.add_field(name="⚙️ **System User**", value=is_system, inline=True)
        embed.add_field(
            name="📅 **Account Created**",
            value=f"{discord.utils.format_dt(member.created_at, 'f')}\n({account_age} days ago)",
            inline=False
        )

        if isinstance(member, discord.Member):
            embed.add_field(
                name="📅 **Joined Server**",
                value=f"{discord.utils.format_dt(member.joined_at, 'f')}\n({server_join_age} days ago)",
                inline=False
            )
            embed.add_field(name="👑 **Highest Role**", value=highest_role, inline=True)
            embed.add_field(
                name=f"🎭 **Roles ({len(roles)})**",
                value=" ".join(roles) if roles else "None",
                inline=False
            )
            embed.add_field(
                name="🛡️ **Key Permissions**",
                value=", ".join(permissions[:10]) if permissions else "None",
                inline=False
            )

        embed.add_field(name="🟢 **Status**", value=status, inline=True)
        embed.add_field(name="🎮 **Activity**", value=activity, inline=True)

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(UserInfo(bot))
