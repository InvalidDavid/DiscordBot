import discord
import os
from dotenv import load_dotenv

load_dotenv()


bot = discord.Bot(
    intents=discord.Intents.all(),
    debug_guilds=[int(guild) for guild in os.getenv("DEBUG_GUILDS", "").split(",") if guild.strip()]
)



@bot.event
async def on_ready():
    await bot.wait_until_ready()
    infos = [
        f"Pycord:    {discord.__version__}",
        f"Ping:      {round(bot.latency * 1000):,}ms",
        f"Guilds:    {len(bot.guilds):,}",
        f"Users:     {len(bot.users)}",
        f"Commands:  {len(bot.commands):,}",
    ]

    longest = max([str(i) for i in infos], key=len)
    formatter = f"<{len(longest)}"

    start_txt = "Bot is online!"
    start_txt += f"\n╔{(len(longest) + 2) * '═'}╗\n"
    for thing in infos:
        start_txt += f"║ {thing:{formatter}} ║\n"
    start_txt += f"╚{(len(longest) + 2) * '═'}╝"
    print(start_txt)

    activity = discord.Game(name="mit den Chaos")
    await bot.change_presence(status=discord.Status.online, activity=activity)


if __name__ == "__main__":
    for filename in os.listdir("cog"):
        if filename.endswith(".py"):
            cog = f"cog.{filename[:-3]}"
            try:
                bot.load_extension(cog)
                print(f"[+] Geladen: {cog}")
            except Exception as e:
                print(f"[!] Fehler beim Laden von {cog}: {e}")
            # bot.load_extension(f"cog.{filename[:-3]}")

    load_dotenv()
    bot.run(os.getenv("TOKEN"))
