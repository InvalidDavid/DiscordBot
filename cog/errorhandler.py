import discord
from discord.ext import commands
import math

f = "<:DP_bbye:972516085238726756>"

class error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): # Für Noramele Commands
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Ihnen fehlen Berechtigungen zur Verwendung dieses Befehls.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Zu viele Argumente",
                                  description=f"{f} | Sie haben zu viele Argumente vorgebracht.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Befehl Deaktiviert",
                                  description=f"{f} | Dieser Befehl ist derzeit deaktiviert.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Rolle",
                                  description=f"{f} | Dafür benötigen Sie eine bestimmte Rolle.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.CommandOnCooldown):
            seconds_in_day = 86400
            seconds_in_hour = 3600
            seconds_in_minute = 60

            seconds = error.retry_after

            days = seconds // seconds_in_day
            seconds = seconds - (days * seconds_in_day)

            hours = seconds // seconds_in_hour
            seconds = seconds - (hours * seconds_in_hour)

            minutes = seconds // seconds_in_minute
            seconds = seconds - (minutes * seconds_in_minute)
            if math.ceil(error.retry_after) <= 60:  # seconds
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in `{math.ceil(seconds)}` sekunden.",
                                      color=discord.Color.red())
                await ctx.reply(embed=embed)
                return

            if math.ceil(error.retry_after) <= 3600:  # minutes
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in  `{math.ceil(minutes)}` minuten und `{math.ceil(seconds)}` sekunden",
                                      color=discord.Color.red())
                await ctx.reply(embed=embed)
                return

            if math.ceil(error.retry_after) <= 86400:  # hours
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in `{math.ceil(hours)}` stunden, `{math.ceil(minutes)}` minuten und `{math.ceil(seconds)}` sekunden.",
                                      color=discord.Color.red())
                await ctx.reply(embed=embed)
                return

            if math.ceil(error.retry_after) >= 86400:  # days
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in `{math.ceil(days)}` Tage, `{math.ceil(hours)}` Stunden, `{math.ceil(minutes)}` Minuten und `{math.ceil(seconds)}` Sekunden.",
                                      color=discord.Color.red())
                await ctx.reply(embed=embed)
                return

        if isinstance(error, commands.MessageNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Diese Meldung wurde nicht gefunden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Dieser Benutzer wurde nicht gefunden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.UserNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Dieser Benutzer wurde nicht gefunden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.ChannelNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Der Kanal wurde nicht gefunden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.ChannelNotReadable):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlender Zugriff",
                                  description=f"{f} | Ich kann die Nachrichten auf diesem Kanal nicht lesen.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.BadColourArgument):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Ich konnte diese Farbe nicht finden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.RoleNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Ich habe diese Rolle nicht gefunden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Dafür benötige ich Berechtigungen.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.EmojiNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Ich konnte dieses Emoji nicht finden oder ich teile keinen Server mit diesem Emoji!")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.PrivateMessageOnly):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Kein Zugriff",
                                  description=f"{f} | Dieser Befehl funktioniert nur in DMs.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Kein Zugriff",
                                  description=f"{f} | Dieser Befehl funktioniert nur auf Servern.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.NSFWChannelRequired):
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description=f"{f} | Sie können diesen Befehl nur in einem nsfw-Kanal ausführen.",
                                  )
            embed.set_author(name=ctx.author)
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Nur der Besitzer kann diesen Befehl verwenden.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Ich bin dazu nicht berechtigt.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.BotMissingAnyRole):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechigungen",
                                  description=f"{f} | Dafür brauche ich eine bestimmte Rolle.")
            await ctx.reply(embed=embed)
            return

        else:
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Command Error",
                                  description=f"{f} | Es ist ein Fehler vorgefallen!\r\nBitte melden sie beim [Support Server]( https://discord.gg/UREwBEVmxQ ) den fehler.")
            embed.set_author(name=ctx.author)
            embed.add_field(name=f"Error", value=f"```py\r\n{error}```")
            await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error): # Für Slash Commands

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Ihnen fehlen Berechtigungen zur Verwendung dieses Befehls.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Zu viele Argumente",
                                  description=f"{f} | Sie haben zu viele Argumente vorgebracht.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Befehl Deaktiviert",
                                  description=f"{f} | Dieser Befehl ist derzeit deaktiviert.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Rolle",
                                  description=f"{f} | Dafür benötigen Sie eine bestimmte Rolle.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.CommandOnCooldown):
            seconds_in_day = 86400
            seconds_in_hour = 3600
            seconds_in_minute = 60

            seconds = error.retry_after

            days = seconds // seconds_in_day
            seconds = seconds - (days * seconds_in_day)

            hours = seconds // seconds_in_hour
            seconds = seconds - (hours * seconds_in_hour)

            minutes = seconds // seconds_in_minute
            seconds = seconds - (minutes * seconds_in_minute)
            if math.ceil(error.retry_after) <= 60:  # seconds
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in `{math.ceil(seconds)}` sekunden.",
                                      color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)
                return

            if math.ceil(error.retry_after) <= 3600:  # minutes
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in  `{math.ceil(minutes)}` minuten und `{math.ceil(seconds)}` sekunden",
                                      color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)
                return

            if math.ceil(error.retry_after) <= 86400:  # hours
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in `{math.ceil(hours)}` stunden, `{math.ceil(minutes)}` minuten und `{math.ceil(seconds)}` sekunden.",
                                      color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)
                return

            if math.ceil(error.retry_after) >= 86400:  # days
                embed = discord.Embed(title=f"Cooldown",
                                      description=f"{f} | Der Befehl ist auf Abklingzeit, bitte erneut in `{math.ceil(days)}` Tage, `{math.ceil(hours)}` Stunden, `{math.ceil(minutes)}` Minuten und `{math.ceil(seconds)}` Sekunden.",
                                      color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)
                return

        if isinstance(error, commands.MessageNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Diese Meldung wurde nicht gefunden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Dieser Benutzer wurde nicht gefunden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.UserNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Dieser Benutzer wurde nicht gefunden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.ChannelNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Der Kanal wurde nicht gefunden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.ChannelNotReadable):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlender Zugriff",
                                  description=f"{f} | Ich kann die Nachrichten auf diesem Kanal nicht lesen.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.BadColourArgument):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Ich konnte diese Farbe nicht finden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.RoleNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Ich habe diese Rolle nicht gefunden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Dafür benötige ich Berechtigungen.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.EmojiNotFound):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Ich konnte dieses Emoji nicht finden oder ich teile keinen Server mit diesem Emoji!")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.PrivateMessageOnly):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Kein Zugriff",
                                  description=f"{f} | Dieser Befehl funktioniert nur in DMs.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Kein Zugriff",
                                  description=f"{f} | Dieser Befehl funktioniert nur auf Servern.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.NSFWChannelRequired):
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description=f"{f} | Sie können diesen Befehl nur in einem nsfw-Kanal ausführen.",
                                  )
            embed.set_author(name=ctx.author)
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Nur der Besitzer kann diesen Befehl verwenden.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Ich bin dazu nicht berechtigt.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.BotMissingAnyRole):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Fehlende Berechigungen",
                                  description=f"{f} | Dafür brauche ich eine bestimmte Rolle.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.PartialEmojiConversionFailure):
            embed = discord.Embed(colour=discord.Colour.red(), title=f"Nicht gefunden",
                                  description=f"{f} | Das ist kein Emoji.")
            await ctx.respond(embed=embed, ephemeral=True)
            return
        else:
            print(error)


def setup(bot):
    bot.add_cog(error(bot))
