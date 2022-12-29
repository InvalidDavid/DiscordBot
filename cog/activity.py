import discord
from discord.commands import slash_command, option
from discord.ext import commands


# WICHTIG! Diese Funktion ist längst überflüssig da man schon so die Activity starten kann!

class activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        description="Starte ein Watch Together Activity",
    )
    @option(name="auswahl", description="Wähle eine Aktivität aus", required=True, choices=["YouTube", "Chess in the Park", "Poker Night", "Bobble League", "Putt Party", "Sktech Heads", "Land-io", "Blazing 8s", "SpellCast", "Letter League", "Checkers in the Park"])
    async def activity(self, ctx, auswahl):
        if ctx.author.voice != None:
            if auswahl == "YouTube":
                channel = ctx.author.voice.channel
                invite = await channel.create_activity_invite(discord.EmbeddedActivity.watch_together, max_age=600, max_uses=1, reason="Yotube")
                embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                await ctx.respond(embeds=[embed])
            elif auswahl == "Chess in the Park":
                channel = ctx.author.voice.channel
                invite = await channel.create_activity_invite(discord.EmbeddedActivity.chess_in_the_park, max_age=600, max_uses=1, reason="Chess in the Park")
                embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                await ctx.respond(embeds=[embed])
            elif auswahl == "Poker Night":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.poker_night, max_age=600, max_uses=1, reason="Poker Night")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Bobble League":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.bobble_league, max_age=600, max_uses=1, reason="Bobble League")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Putt Party":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.putt_party, max_age=600, max_uses=1, reason="Putt Party")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Sktech Heads":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.sketch_heads, max_age=600, max_uses=1, reason="Sktech Heads")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Land-io":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.land_io, max_age=600, max_uses=1, reason="Land-io")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Blazing 8s":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.blazing_8s, max_age=600, max_uses=1, reason="Blazing 8s")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "SpellCast":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.spellcast, max_age=600, max_uses=1, reason="SpellCast")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Letter League":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.letter_league, max_age=600, max_uses=1, reason="Letter League")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")

            elif auswahl == "Checkers in the Park":
                if ctx.author in ctx.guild.premium_subscribers:
                    channel = ctx.author.voice.channel
                    invite = await channel.create_activity_invite(discord.EmbeddedActivity.checkers_in_the_park, max_age=600, max_uses=1, reason="Checkers in the Park")
                    embed = discord.Embed(title=f"{auswahl} Activity",
                                  description=f"[Klicke auf den Link um die Acitivty zu starten]({invite.url})",
                                  color=discord.Colour.embed_background())
                    await ctx.respond(embeds=[embed])
                else:
                    await ctx.respond("Du musst ein Nitro Booster sein um diese Aktivität zu starten")
        else:
            await ctx.respond("Du musst in einem Voice Channel sein um eine Aktivität zu starten")

def setup(bot):
    bot.add_cog(activity(bot))
