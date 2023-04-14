import discord
from discord.commands import slash_command, Option
from discord.ext import commands
import os
import random
import aiohttp
import asyncpraw

# Credits an: https://youtu.be/Bb2hrOIhi40 bzw. Coding Keks
# API_KEY in die .env Datei einfügen.

# Credits gehen an Codingkeks / tibue99, Video: https://youtu.be/X0k48ergGq4

class MemeButton(discord.ui.View):
    def __init__(self, msg, thema, user):
        self.msg = msg # Ist dazu da damit der Bot weißt welche Nachricht er bearbeiten soll
        self.thema = thema
        self.user = user
        super().__init__(timeout=30)

    async def on_timeout(self):
        for children in self.children:
            children.disabled = True
        await self.msg.edit(view=self)


    @discord.ui.button(label="Anderer Meme", style=discord.ButtonStyle.gray, custom_id="MemeButton", emoji="💀")
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user != interaction.user:
            return await interaction.response.send_message("Du hast nicht diesen Meme aufgerufen.", ephemeral=True)
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="Meme lädt..."
        )
        interaction = await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()

        id = os.getenv("reddit_id") # Hier werden die Daten aus der .env Datei geladen, bitte nicht vergessen die zu erstellen
        secret = os.getenv("reddit_secret")
        password = os.getenv("reddit_password")
        async with asyncpraw.Reddit(
            client_id=id,
            client_secret=secret,
            password=password,
            user_agent=''
        ) as reddit:
            subreddit = await reddit.subreddit(self.thema)
            hot = subreddit.hot(limit=25)

            all_posts = []
            async for post in hot:
                if not post.is_video:
                    all_posts.append(post)

            random_post = random.choice(all_posts)

            embed = discord.Embed(
                title=random_post.title,
                color=discord.Color.blurple()
            )
            embed.set_image(url=random_post.url)
            embed.set_author(name=f"{interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"r/{random_post.subreddit} | 👍 {random_post.score} | 💬 {random_post.num_comments} | 📥 {random_post.num_crossposts}", icon_url="https://cdn-icons-png.flaticon.com/512/2504/2504934.png")
            await msg.edit(embed=embed, view=MemeButton(self.msg, self.thema, self.user))

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Sende Memes und wähle dein Thema aus")
    async def meme(self, ctx, thema: Option(str, description="Wähle dein Thema aus", required=False, default="ich_iel")):
        try:
            embed = discord.Embed(
                color=discord.Color.blurple(),
                title="Meme lädt..."
            )
            interaction = await ctx.respond(embed=embed)
            msg = await interaction.original_response()

            id = os.getenv("reddit_id")
            secret = os.getenv("reddit_secret")
            password = os.getenv("reddit_password")
            async with asyncpraw.Reddit(
                    client_id=id,
                    client_secret=secret,
                    password=password,
                    user_agent=''
            ) as reddit:
                subreddit = await reddit.subreddit(thema)
                hot = subreddit.hot(limit=25)

                all_posts = []
                async for post in hot:
                    if not post.is_video:
                        all_posts.append(post)

                random_post = random.choice(all_posts)

                embed = discord.Embed(
                    title=random_post.title,
                    color=discord.Color.blurple()
                )
                embed.set_image(url=random_post.url)
                embed.set_author(name=f"{interaction.user}", icon_url=interaction.user.display_avatar.url)
                embed.set_footer(
                    text=f"r/{random_post.subreddit} | 👍 {random_post.score} | 💬 {random_post.num_comments} | 📥 {random_post.num_crossposts}",
                    icon_url="https://cdn-icons-png.flaticon.com/512/2504/2504934.png")
                user = ctx.author
                await msg.edit(embed=embed, view=MemeButton(msg, thema, user))
        except:
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Dieses Thema existiert nicht."
            )
            await msg.edit(embed=embed)

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
