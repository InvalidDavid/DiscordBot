import discord
from discord.commands import slash_command, Option
from discord.ext import commands
import os
import random
import aiohttp

# Credits an: https://youtu.be/Bb2hrOIhi40 bzw. Coding Keks
# API_KEY in die .env Datei einfügen.

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def hug(self, ctx, member: Option(discord.Member, required=True)):
        user = member
        key = os.getenv("API_KEY")

        params = {
            "q": "hug",
            "key": key,
            "limit": "10",
            "client_key": "discord_bot",
            "media_filter": "gif"
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://tenor.googleapis.com/v2/search", params=params) as r:
                data = await r.json()
        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']
        embed = discord.Embed(
            title=f"{ctx.author.name} umarmt {user.name}!",
            color=discord.Color.embed_background()
       )
        embed.set_image(url=url)
        await ctx.respond(embed=embed)


    @slash_command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def punch(self, ctx, member: Option(discord.Member, required=True)):
        user = member
        key = os.getenv("API_KEY")

        params = {
            "q": "punch",
            "key": key,
            "limit": "10",
            "client_key": "discord_bot",
            "media_filter": "gif"
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://tenor.googleapis.com/v2/search", params=params) as r:
                data = await r.json()
        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']
        embed = discord.Embed(
            title=f"{ctx.author.name} puncht {user.name}!",
            color=discord.Color.embed_background()
       )
        embed.set_image(url=url)
        await ctx.respond(embed=embed)


    @slash_command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def love(self, ctx, member: Option(discord.Member, required=True)):
        user = member
        key = os.getenv("API_KEY")

        params = {
            "q": "love",
            "key": key,
            "limit": "10",
            "client_key": "discord_bot",
            "media_filter": "gif"
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://tenor.googleapis.com/v2/search", params=params) as r:
                data = await r.json()
        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']
        embed = discord.Embed(
            title=f"{ctx.author.name} liebt {user.name}!",
            color=discord.Color.embed_background()
       )
        embed.set_image(url=url)
        await ctx.respond(embed=embed)

    @slash_command(description="Sende Kekse in Chat")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def keks(self, ctx):
        key = os.getenv("API_KEY")

        params = {
            "q": "keks",
            "key": key,
            "limit": "10",
            "client_key": "discord_bot",
            "media_filter": "gif"
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://tenor.googleapis.com/v2/search", params=params) as r:
                data = await r.json()
        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']
        embed = discord.Embed(
            title="Keks",
            color=discord.Color.embed_background()
        )
        embed.set_image(url=url)
        embed.set_footer(text=f"Angefordert von {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Test(bot))
