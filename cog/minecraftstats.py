import requests
import discord
from discord.ext import commands
from discord.commands import slash_command, option

class mc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    @option(name="auswahl", description="Wähle eine Option", required=True, choices=["Java", "Bedrock"])
    async def minecraftstats(self, ctx, auswahl, ip):
        try:
            if auswahl == "Bedrock":
                api = requests.get(f"https://api.mcsrvstat.us/bedrock/2/{ip}")
                data = api.json()

                if data["online"] == True:
                    text = f"Online"
                elif data["online"] == False:
                    text = "Offline"
                try:
                   embed = discord.Embed(
                    color=discord.Colour.embed_background(),
                    title="Minecraft Server Stats",
                    description=f"Status: {text}\nIP: {data['ip']}\nPort: {data['port']}\nVersion: {data['version']}\nSoftware: {data['software']}\nSpieler: {data['players']['online']}/{data['players']['max']}"
             )
                   await ctx.respond(embed=embed)
                except:
                    embed = discord.Embed(
                        color=discord.Colour.embed_background(),
                        title="Minecraft Server Stats",
                        description=f"Status: {text}\nIP: {data['ip']}\nPort: {data['port']}"
                    )
                    await ctx.respond(embed=embed)


            elif auswahl == "Java":
                api = requests.get(f"https://api.mcsrvstat.us/2/{ip}")
                data = api.json()

                if data["online"] == True:
                    text = f"Online"
                elif data["online"] == False:
                    text = "Offline"

                embed = discord.Embed(
                    color=discord.Colour.embed_background(),
                    title="Minecraft Server Stats",
                  description=f"Status: {text}\nIP: {data['ip']}\nPort: {data['port']}\nVersion: {data['version']}\nSoftware: {data['software']}\nSpieler: {data['players']['online']}/{data['players']['max']}"
             )
                await ctx.respond(embed=embed)
        except:
            await ctx.respond("Server nicht gefunden", ephemeral=True)


def setup(bot):
    bot.add_cog(mc(bot))
