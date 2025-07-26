import discord
from discord.ext import commands

FEHLER_SYMBOL = "❌"
SUPPORT_SERVER = "kekw"


class FehlerHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def sende_fehler_embed(ctx, titel, beschreibung, ephemeral=False):
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
    def format_cooldown(sekunden):
        tage, rest = divmod(int(sekunden), 86400)
        stunden, rest = divmod(rest, 3600)
        minuten, sekunden = divmod(rest, 60)

        teile = []
        if tage:
            teile.append(f"{tage} Tage")
        if stunden:
            teile.append(f"{stunden} Stunden")
        if minuten:
            teile.append(f"{minuten} Minuten")
        if sekunden or not teile:
            teile.append(f"{sekunden} Sekunden")

        return ", ".join(teile)

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
            cooldown_zeit = self.format_cooldown(error.retry_after)
            await self.sende_fehler_embed(
                ctx,
                "Cooldown",
                f"Der Befehl ist auf Abklingzeit, bitte erneut in {cooldown_zeit}."
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
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(FehlerHandler(bot))
