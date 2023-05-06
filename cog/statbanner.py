import discord
from discord.ext import commands, tasks
from PIL import Image, ImageFont, ImageDraw

###
#
# Die Stellen wo die Texte draufgepackt auf den Bildern sind immer unterschiedlich da es auf den Format des Banners und Schrfitart / Größe varieren.
# Und bei mir sind die definitiv FALSCH xD.
#
###

class statbanner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.stats.start()

    def only_bot_and_online_user(self, m):
        return m.bot != True and m.status != discord.Status.offline

    @tasks.loop(seconds=5)
    async def stats(self):
        font = ImageFont.truetype("Data/Statbanner/font.ttf", 100)
        server = self.bot.get_guild(903725994907693096) # Server ID

        self.counter += 1
        if self.counter == 1:
            banner1 = Image.open("Data/Statbanner/banner1.png")
            banner = ImageDraw.Draw(banner1)

            banner.text(
                (475, 335), f"{server.name}", (255, 255, 255), font=font, size=50, align="center"
            )
            banner1.save("Data/Statbanner/result1.png")
            with open("Data/Statbanner/result1.png", "rb") as image:
                await server.edit(banner=image.read())

        elif self.counter == 2:
            banner2 = Image.open("Data/Statbanner/banner2.png")
            banner = ImageDraw.Draw(banner2)

            insgesamt = "{}".format(len(list(server.members)))
            online = "{}".format(len(list(server.members)) - (
                        len(list(server.members)) - len(list(filter(self.only_bot_and_online_user, server.members)))))

            banner.text(
                (166, 350), insgesamt, (255, 255, 255), font=font, size=50, align="center"
            )
            banner.text(
                (750, 350), online, (255, 255, 255), font=font, size=50, align="center"
            )
            banner2.save("Data/Statbanner/result2.png")
            with open("Data/Statbanner/result2.png", "rb") as image:
                await server.edit(banner=image.read())

        elif self.counter == 3:
            banner3 = Image.open("Data/Statbanner/banner3.png")
            banner = ImageDraw.Draw(banner3)
            boosts = "{}".format(server.premium_subscription_count)
            channels = "{}".format(len(list(server.channels)))
            voices = "{}".format(len(list(server.voice_channels)))

            banner.text(
                (100, 125), boosts, (255, 255, 255), font=font, size=50, align="center"
            )
            banner.text(
                (250, 125), channels, (255, 255, 255), font=font, size=50, align="center"
            )
            banner.text(
                (350, 125), voices, (255, 255, 255), font=font, size=50, align="center"
            )
            banner3.save("Data/Statbanner/result3.png")
            with open("Data/Statbanner/result3.png", "rb") as image:
                await server.edit(banner=image.read())

            self.counter = 0



def setup(bot):
    bot.add_cog(statbanner(bot))
