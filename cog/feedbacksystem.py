import discord
from discord.ext import commands
from discord.commands import slash_command, SlashCommandGroup, option
import datetime
from datetime import datetime

import sqlite3

db = sqlite3.connect('Data/feedback.db')
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS feedback (guild_id INTEGER, channel_id INTEGER)')
db.commit()

class FeedbackSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        c.execute('SELECT guild_id, channel_id FROM feedback WHERE guild_id = ?', (guild.id,))
        if c.fetchone() != None:
            c.execute('SELECT guild_id, channel_id FROM feedback WHERE guild_id = ?', (guild.id,))
            was = c.fetchone()
            c.execute('DELETE FROM feedback WHERE guild_id = ? and channel_id = ?', (guild.id, was[1]))
            db.commit()
        else:
            pass

    feedback = SlashCommandGroup(name='feedback', description='Feedback System')


    @feedback.command(description="Setzt den Feedback Kanal")
    async def setup(self, ctx, channel: discord.TextChannel):
        c.execute('SELECT * FROM feedback WHERE guild_id= ?', (ctx.guild.id,))
        if c.fetchone() is not None:
            return await ctx.respond('Das Feedback System ist bereits Aktiviert!', ephemeral=True)

        c.execute(' SELECT * FROM feedback WHERE guild_id=? AND channel_id=?', (ctx.guild.id, channel.id))
        if c.fetchone() == None:
            c.execute('INSERT INTO feedback(guild_id, channel_id) VALUES(?,?)', (ctx.guild.id, channel.id))
            db.commit()
            await ctx.respond(f"Feedback Channel ist nun in {channel.mention} aktiviert.", ephemeral=True)
            return



    @feedback.command(description="Deaktiviert das Feedback System")
    async def remove(self, ctx):
        c.execute('SELECT * FROM feedback WHERE guild_id= ?', (ctx.guild.id,))
        if c.fetchone() is None:
            return await ctx.respond('Das Feedback System ist bereits Deaktiviert!', ephemeral=True)
        c.execute('DELETE FROM feedback WHERE guild_id= ?', (ctx.guild.id,))
        db.commit()
        await ctx.respond('Das Feedback System ist jetzt Deaktiviert.', ephemeral=True)

    @feedback.command(description="Sendet ein Feedback")
    @option(name="bewertung", description="Positiv oder Negative Bewertung?", required=True, choices=["Positiv", "Negativ"])
    async def send(self, ctx, *, bewertung, nachricht):
        c.execute('SELECT * FROM feedback WHERE guild_id= ?', (ctx.guild.id,))
        if c.fetchone() != None:
            c.execute('SELECT channel_id FROM feedback WHERE guild_id= ?', (ctx.guild.id,))
            channel_id = c.fetchone()[0]
            channel = self.bot.get_channel(channel_id)
            await ctx.respond('Feedback wurde gesendet.', ephemeral=True)
            if bewertung == "Positiv":
                farbe = discord.Colour.green()
            elif bewertung == "Negativ":
                farbe = discord.Colour.red()
            embed = discord.Embed(description=nachricht, color=farbe, timestamp=datetime.utcnow())
            embed.set_author(name=f'{ctx.author} › {ctx.author.id}', icon_url=ctx.author.avatar.url)
            embed.set_footer(text=f'{bewertung}er Feedback')
            await channel.send(embed=embed)

        else:
            return await ctx.respond('Feedback System ist nicht Aktiviert!', ephemeral=True)

def setup(bot):
    bot.add_cog(FeedbackSystem(bot))
