import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone


FEHLER_SYMBOL = "❌"
SUPPORT_SERVER = "https://github.com/InvalidDavid/DiscordBot"


class FehlerHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._error_cache = {}

    @staticmethod
    async def sende_fehler_embed(ctx, titel, beschreibung, ephemeral=True):
        embed = discord.Embed(
            color=discord.Color.red(),
            title=titel,
            description=f"{FEHLER_SYMBOL} | {beschreibung}"
        )

        if isinstance(ctx, commands.Context):
            await ctx.reply(embed=embed)
        else:
            await ctx.respond(embed=embed, ephemeral=ephemeral)

    @staticmethod
    def cooldown_timestamp(seconds: float, show_absolute: bool = True) -> str:
        target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

        relative = discord.utils.format_dt(target_time, style='R')
        absolute = discord.utils.format_dt(target_time, style='F')

        return f"{relative} ({absolute})" if show_absolute else relative

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        fehler_zuordnungen = {
            commands.MissingPermissions: ("Fehlende Berechtigungen",
                                          "Ihnen fehlen Berechtigungen zur Verwendung dieses Befehls."),
            commands.TooManyArguments: ("Zu viele Argumente", "Sie haben zu viele Argumente vorgebracht."),
            commands.DisabledCommand: ("Befehl Deaktiviert", "Dieser Befehl ist derzeit deaktiviert."),
            commands.MissingAnyRole: ("Fehlende Rolle", "Dafür benötigen Sie eine bestimmte Rolle."),
            commands.MessageNotFound: ("Nicht gefunden", "Diese Meldung wurde nicht gefunden."),
            commands.MemberNotFound: ("Nicht gefunden", "Dieser Benutzer wurde nicht gefunden."),
            commands.UserNotFound: ("Nicht gefunden", "Dieser Benutzer wurde nicht gefunden."),
            commands.ChannelNotFound: ("Nicht gefunden", "Der Kanal wurde nicht gefunden."),
            commands.ChannelNotReadable: ("Fehlender Zugriff",
                                          "Ich kann die Nachrichten auf diesem Kanal nicht lesen."),
            commands.BadColourArgument: ("Nicht gefunden", "Ich konnte diese Farbe nicht finden."),
            commands.RoleNotFound: ("Nicht gefunden", "Ich habe diese Rolle nicht gefunden."),
            commands.BotMissingPermissions: ("Fehlende Berechtigungen", "Dafür benötige ich Berechtigungen."),
            commands.EmojiNotFound: ("Nicht gefunden",
                                     "Ich konnte dieses Emoji nicht finden oder ich teile keinen Server mit diesem Emoji!"),
            commands.PrivateMessageOnly: ("Kein Zugriff", "Dieser Befehl funktioniert nur in DMs."),
            commands.NoPrivateMessage: ("Kein Zugriff", "Dieser Befehl funktioniert nur auf Servern."),
            commands.NSFWChannelRequired: ("NSFW Kanal benötigt",
                                           "Sie können diesen Befehl nur in einem NSFW-Kanal ausführen."),
            commands.NotOwner: ("Fehlende Berechtigungen", "Nur der Besitzer kann diesen Befehl verwenden."),
            commands.BotMissingAnyRole: ("Fehlende Berechtigungen", "Dafür brauche ich eine bestimmte Rolle."),
            commands.PartialEmojiConversionFailure: ("Nicht gefunden", "Das ist kein Emoji.")
        }

        if isinstance(error, commands.CommandOnCooldown):
            timestamp = self.cooldown_timestamp(error.retry_after, show_absolute=True)
            await self.sende_fehler_embed(
                ctx,
                "Cooldown",
                f"Der Befehl ist auf Abklingzeit, bitte erneut {timestamp}."
            )
            return

        for fehler_typ, (titel, beschreibung) in fehler_zuordnungen.items():
            if isinstance(error, fehler_typ):
                await self.sende_fehler_embed(ctx, titel, beschreibung)
                return

        embed = discord.Embed(
            color=discord.Color.red(),
            title="Command Error",
            description=f"{FEHLER_SYMBOL} | Es ist ein Fehler aufgetreten!\nBitte melden Sie diesen Fehler im [Support Server]({SUPPORT_SERVER})."
        )
        embed.set_author(name=ctx.author)
        embed.add_field(name="Error", value=f"```py\n{error}```")
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        key = (ctx.user.id, getattr(ctx.command, 'name', 'unknown'), type(error))
        now = datetime.utcnow()

        if key in self._error_cache:
            if now - self._error_cache[key] < timedelta(seconds=10):
                return
        self._error_cache[key] = now

        if isinstance(error, commands.CommandError):
            await self.on_command_error(ctx, error)
            return

        if isinstance(error, discord.ApplicationCommandInvokeError):
            original = error.original
            if isinstance(original, commands.CommandError):
                await self.on_command_error(ctx, original)
                return

        embed = discord.Embed(
            color=discord.Color.red(),
            title="Command Error",
            description=f"{FEHLER_SYMBOL} | Es ist ein Fehler aufgetreten!\nBitte melden Sie diesen Fehler im [Support Server]({SUPPORT_SERVER})."
        )
        embed.set_author(name=ctx.user)
        embed.add_field(name="Error", value=f"```py\n{error}```")

        try:
            if not ctx.response.is_done():
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.followup.send(embed=embed, ephemeral=True)
        except discord.errors.HTTPException:
            pass


def setup(bot):
    bot.add_cog(FehlerHandler(bot))
