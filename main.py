import discord
import os
from dotenv import load_dotenv

bot = discord.Bot(intents=discord.Intents.all(), help_command=None, debug_guilds=[ServerID]) # discord.Bot erlaubt nur Slash Commands

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    infos = [
        f"Pycord:    {discord.__version__}",
        f"Ping:      {round(bot.latency * 1000):,}ms",
        f"Guilds:    {len(bot.guilds):,}",
        f"Users:     {len(bot.users)}",
        f"Commands:  {len(bot.commands):,}",
        f"Bot Owner: {(await bot.application_info()).owner}"
    ]

    longest = max([str(i) for i in infos], key=len)
    formatter = f"<{len(longest)}"

    start_txt = "Bot is online!"
    start_txt += f"\n╔{(len(longest) + 2) * '═'}╗\n"
    for thing in infos:
        start_txt += f"║ {thing:{formatter}} ║\n"
    start_txt += f"╚{(len(longest) + 2) * '═'}╝"
    print(start_txt)

if __name__ == "__main__":
    for filename in os.listdir("cog"):
        if filename.endswith(".py"):
            bot.load_extension(f"cog.{filename[:-3]}")
            
    load_dotenv()
    print('Support: https://discord.gg/paradies\nCredits: https://youtu.be/Bb2hrOIhi40')
    bot.run(os.getenv("TOKEN"))
