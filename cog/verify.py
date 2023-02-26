import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, option
import random
import sqlite3
import datetime
from datetime import datetime

db = sqlite3.connect('Data/verify.db')
c = db.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS verify (guild_id INTEGER, role_id INTEGER)''')
db.commit()

class VerifyModal(discord.ui.Modal):
    def __init__(self, bot, **kwargs) -> None:
        self.bot = bot
        self.zahl = str(random.randint(1000, 9999))
        super().__init__(**kwargs, title=f'{self.zahl}')

        self.add_item(discord.ui.InputText(
            label=f"Gib die Zahl ein: {self.zahl}",
            placeholder=f"{self.zahl}",
            required=True,
            min_length=4,
            max_length=4
        ))
    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        c.execute(f'SELECT role_id FROM verify WHERE guild_id = ?', (interaction.guild.id,))
        server = c.fetchone()
        role = interaction.guild.get_role(server[0])

        if self.children[0].value == self.zahl:
            try:
                await user.add_roles(role)
                await interaction.response.send_message("Du bist nun Verifiziert.", ephemeral=True)
            except discord.errors.Forbidden:
                embed = discord.Embed(
                    color=discord.Colour.red(),
                    title="Fehler",
                    description="Es ist ein Fehler aufgetreten. Dies kann mehrere Gründe haben. \n\n- Ich habe keine Berechtigung, die Rolle zu vergeben. \n- Die Rolle ist höher als meine. \n- Die Rolle ist höher als meine. \n\nBitte überprüfe die Berechtigungen und versuche es erneut."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Du hast die Zahl falsch eingegeben", ephemeral=True)


class VerifyButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(
            label="Verify",
            style=discord.ButtonStyle.gray,
            emoji="❓",
            custom_id="verify"
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        c.execute(f'SELECT role_id FROM verify WHERE guild_id = ?', (interaction.guild.id,))
        server = c.fetchone()
        if server is None:
            await interaction.message.edit(view=None)
            return await interaction.response.send_message("Es wurde noch keine Rolle für die Verifizierung festgelegt.", ephemeral=True)
        else:
            role = interaction.guild.get_role(server[0])
            if role in user.roles:
                await interaction.response.send_message("Du bist bereits Verifiziert.", ephemeral=True)
            else:
                modal = VerifyModal(self.bot)
                await interaction.response.send_modal(modal)

class VerifyText(discord.ui.Modal):
    def __init__(self, bot, channel_id, nfarbe, **kwargs) -> None:
        self.bot = bot
        self.channel_id = channel_id
        self.nfarbe = nfarbe
        super().__init__(**kwargs, title=f'Verify Text Modal')
        self.add_item(discord.ui.InputText(
            label=f"Titel?",
            style=discord.InputTextStyle.long,
            required=True,
            min_length=3,
            value="Verify"
        ))
        self.add_item(discord.ui.InputText(
            label=f"Description?",
            style=discord.InputTextStyle.long,
            required=False,
            min_length=3,
            value="Verifiziere dich mit dem Button."
        ))
        self.add_item(discord.ui.InputText(
            label=f"Embed Footer?",
            style=discord.InputTextStyle.short,
            required=False,
            min_length=3,
            value="©️ discord.gg/paradies"
        ))
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Der Verify Text wurde gesendet.", ephemeral=True)
        title = self.children[0].value
        description = self.children[1].value
        footer = self.children[2].value
        if description is not None:
            embed = discord.Embed(
                title=title,
                description=description,
                color=self.nfarbe,
                timestamp=datetime.utcnow()
            )
            embed.set_author(icon_url=interaction.guild.icon.url, name=interaction.guild.name)
        else:
            embed = discord.Embed(
                title=title,
                color=self.nfarbe,
                timestamp=datetime.utcnow()
            )
            embed.set_author(icon_url=interaction.guild.icon.url, name=interaction.guild.name)
        if footer is not None:
            embed.set_footer(text=footer)
        else:
            pass

        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot))
        channel = self.bot.get_channel(self.channel_id)
        await channel.send(embed=embed, view=view)


class VerifySafe(discord.ui.View):
    def __init__(self, bot, channel_id, nfarbe):
        self.bot = bot
        self.channel_id = channel_id
        self.nfarbe = nfarbe
        super().__init__(timeout=None)

    @discord.ui.button(label="Bestätigen", style=discord.ButtonStyle.green, row=1)
    async def callback1(self, button, interaction):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self, delete_after=3)
        modal = VerifyText(self.bot, self.channel_id, self.nfarbe)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, row=1)
    async def callback2(self, button, interaction):
        embed = discord.Embed(
                    color=discord.Colour.red(),
                    title="Vorgang abgebrochen..."
        )
        await interaction.response.edit_message(embed=embed, view=None, delete_after=3)


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    verify = SlashCommandGroup("verify", "Verifizierung")

    @verify.command()
    @discord.default_permissions(administrator=True)
    async def setup(self, ctx, rolle: discord.Role):

        c.execute('SELECT * FROM verify WHERE guild_id= ?', (ctx.guild.id,))
        if c.fetchone() is not None:
            return await ctx.respond('Das Verify System ist bereits Aktiviert!', ephemeral=True)

        if c.fetchone() == None:
            c.execute('INSERT INTO verify(guild_id, role_id) VALUES(?,?)', (ctx.guild.id, rolle.id))
            db.commit()
            await ctx.respond(f"Verify System ist nun Aktiviert und man erhält beim Verifizeren die Rolle {rolle.mention}.", ephemeral=True)
            return

    @verify.command()
    @discord.default_permissions(administrator=True)
    async def remove(self, ctx):
        c.execute('SELECT * FROM verify WHERE guild_id= ?', (ctx.guild.id,))
        if c.fetchone() is None:
            return await ctx.respond('Das Verify System ist bereits Deaktiviert!', ephemeral=True)
        else:
            c.execute(f'SELECT role_id FROM verify WHERE guild_id = ?', (ctx.guild.id,))
            was = c.fetchone()
            c.execute('DELETE FROM verify WHERE guild_id= ? and role_id = ?', (ctx.guild.id, was[0]))
            db.commit()
            await ctx.respond('Das Verify System ist nun Deaktiviert!', ephemeral=True)


    @verify.command()
    @discord.default_permissions(administrator=True)
    @option(name="farbe", description="Farbe des Embeds", choices=["Rot", "Blau", "Grün", "Grau", "Random"], required=False, default="Unsichtbar")
    async def send(self, ctx, channel: discord.TextChannel, farbe):
        if farbe == "Rot":
            nfarbe = discord.Colour.red()
        elif farbe == "Blau":
            nfarbe = discord.Colour.blue()
        elif farbe == "Grün":
            nfarbe = discord.Colour.green()
        elif farbe == "Grau":
            nfarbe = discord.Colour.greyple()
        elif farbe == "Random":
            nfarbe = discord.Colour.random()
        elif farbe == "Unsichtbar":
            nfarbe = discord.Colour.embed_background()

        c.execute('SELECT * FROM verify WHERE guild_id= ?', (ctx.guild.id,))
        if c.fetchone() != None:
            c.execute('SELECT role_id FROM verify WHERE guild_id= ?', (ctx.guild.id,))

            embed = discord.Embed(
                color=discord.Colour.embed_background(),
                title="Bestätigen",
                description=f"Channel: {channel.mention}\nFarbe: {farbe}"
            )
            channel_id = channel.id
            await ctx.respond(embed=embed, view=VerifySafe(self.bot, channel_id, nfarbe), ephemeral=True)
        else:
            return await ctx.respond('Verifiy System ist nicht Aktiviert!', ephemeral=True)


    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot))
        self.bot.add_view(view)
        c.execute('''CREATE TABLE IF NOT EXISTS verify (guild_id INTEGER, role_id INTEGER)''')
        db.commit()
        print('Verify System, bereitgestellt von discord.gg/paradies')


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        c.execute('SELECT guild_id, role_id FROM verify WHERE guild_id = ?', (guild.id,))
        if c.fetchone() != None:
            c.execute('SELECT guild_id, role_id FROM verify WHERE guild_id = ?', (guild.id,))
            was = c.fetchone()
            c.execute('DELETE FROM verify WHERE guild_id = ? and role_id = ?', (guild.id, was[1]))
            db.commit()
        else:
            pass


def setup(bot):
    bot.add_cog(Verify(bot))
