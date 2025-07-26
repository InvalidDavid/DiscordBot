import discord
from discord.ext import commands
import math

ERROR_EMOJI = "<:DP_bbye:972516085238726756>"

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _format_cooldown(self, seconds: float) -> str:
        """Formatiert Cooldown in Tage, Stunden, Minuten, Sekunden."""
        seconds = int(math.ceil(seconds))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} {'Tag' if days == 1 else 'Tage'}")
        if hours > 0:
            parts.append(f"{hours} {'Stunde' if hours == 1 else 'Stunden'}")
        if minutes > 0:
            parts.append(f"{minutes} {'Minute' if minutes == 1 else 'Minuten'}")
        if seconds > 0:
            parts.append(f"{seconds} {'Sekunde' if seconds == 1 else 'Sekunden'}")
        return ", ".join(parts)

    async def _send_error_embed(self, ctx, title: str, description: str, ephemeral: bool = False):
        embed = discord.Embed(title=title, description=f"{ERROR_EMOJI} | {description}", color=discord.Color.red())
        # Je nach ctx Typ: respond (Slash), reply (Prefix)
        if hasattr(ctx, "respond"):  # Slash Command Kontext
            await ctx.respond(embed=embed, ephemeral=ephemeral)
        else:
            await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self._handle_error(ctx, error)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        await self._handle_error(ctx, error, ephemeral=True)

    async def _handle_error(self, ctx, error, ephemeral=False):
        # Mögliche Fehler zusammenfassen, um Duplikate zu vermeiden
        if isinstance(error, commands.MissingPermissions):
            await self._send_error_embed(ctx, "Fehlende Berechtigungen", "Ihnen fehlen Berechtigungen zur Verwendung dieses Befehls.", ephemeral)
            return

        if isinstance(error, commands.TooManyArguments):
            await self._send_error_embed(ctx, "Zu viele Argumente", "Sie haben zu viele Argumente vorgebracht.", ephemeral)
            return

        if isinstance(error, commands.DisabledCommand):
            await self._send_error_embed(ctx, "Befehl deaktiviert", "Dieser Befehl ist derzeit deaktiviert.", ephemeral)
            return

        if isinstance(error, commands.MissingAnyRole):
            await self._send_error_embed(ctx, "Fehlende Rolle", "Dafür benötigen Sie eine bestimmte Rolle.", ephemeral)
            return

        if isinstance(error, commands.CommandOnCooldown):
            cooldown_str = self._format_cooldown(error.retry_after)
            await self._send_error_embed(ctx, "Cooldown", f"Der Befehl ist auf Abklingzeit, bitte erneut in {cooldown_str}.", ephemeral)
            return

        not_found_errors = (
            commands.MessageNotFound,
            commands.MemberNotFound,
            commands.UserNotFound,
            commands.ChannelNotFound,
            commands.RoleNotFound,
            commands.EmojiNotFound,
            commands.PartialEmojiConversionFailure,
        )
        if isinstance(error, not_found_errors):
            await self._send_error_embed(ctx, "Nicht gefunden", "Das gesuchte Element wurde nicht gefunden.", ephemeral)
            return

        if isinstance(error, commands.ChannelNotReadable):
            await self._send_error_embed(ctx, "Fehlender Zugriff", "Ich kann die Nachrichten auf diesem Kanal nicht lesen.", ephemeral)
            return

        if isinstance(error, commands.BadColourArgument):
            await self._send_error_embed(ctx, "Ungültige Farbe", "Ich konnte diese Farbe nicht finden.", ephemeral)
            return

        if isinstance(error, commands.BotMissingPermissions):
            await self._send_error_embed(ctx, "Fehlende Berechtigungen", "Dafür benötige ich Berechtigungen.", ephemeral)
            return

        if isinstance(error, commands.PrivateMessageOnly):
            await self._send_error_embed(ctx, "Kein Zugriff", "Dieser Befehl funktioniert nur in DMs.", ephemeral)
            return

        if isinstance(error, commands.NoPrivateMessage):
            await self._send_error_embed(ctx, "Kein Zugriff", "Dieser Befehl funktioniert nur auf Servern.", ephemeral)
            return

        if isinstance(error, commands.NSFWChannelRequired):
            await self._send_error_embed(ctx, "NSFW-Kanal erforderlich", "Sie können diesen Befehl nur in einem NSFW-Kanal ausführen.", ephemeral)
            return

        if isinstance(error, commands.NotOwner):
            await self._send_error_embed(ctx, "Fehlende Berechtigungen", "Nur der Besitzer kann diesen Befehl verwenden.", ephemeral)
            return

        if isinstance(error, commands.BotMissingAnyRole):
            await self._send_error_embed(ctx, "Fehlende Berechtigungen", "Dafür brauche ich eine bestimmte Rolle.", ephemeral)
            return

        # Unbekannte Fehler — ausführliche Meldung nur in Prefix-Commands sichtbar, bei Slash ephemeral False wegen Support-Server
        if not ephemeral:
            embed = discord.Embed(
                title="Unbekannter Fehler",
                description=f"{ERROR_EMOJI} | Ein unerwarteter Fehler ist aufgetreten. Bitte melde ihn im Support Server.\n```py\n{error}```",
                color=discord.Color.red()
            )
            embed.set_author(name=str(ctx.author))
            await ctx.reply(embed=embed)
        else:
            # Slash Commands: Einfach Loggen, keine Details senden (Sicherheitsgründe)
            print(f"[SlashCommand Error] {error}")

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
