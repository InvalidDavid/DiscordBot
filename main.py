import discord
import os
from dotenv import load_dotenv

bot = discord.Bot(intents=discord.Intents.all(), help_command=None, debug_guilds=[ServerID]) # discord.Bot erlaubt nur Slash Commands

@bot.event
async def on_ready():
    print('Online')
    print('Bot Name: ' + bot.user.name + ' | Bot ID: ' + str(bot.user.id) + ' | Bot Version: ' + discord.__version__)


if __name__ == "__main__":
    for filename in os.listdir("cog"):
        if filename.endswith(".py"):
            bot.load_extension(f"cog.{filename[:-3]}")
            
    load_dotenv()
    bot.run(os.getenv("TOKEN"))
