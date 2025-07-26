import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, option
import random
import aiosqlite
from datetime import datetime

class VerifyModal(discord.ui.Modal):
    def __init__(self, bot, db, **kwargs) -> None:
        self.bot = bot
        self.db = db
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
        async with self.db.execute('SELECT role_id FROM verify WHERE guild_id = ?', (interaction.guild.id,)) as cursor:
            server = await cursor.fetchone()

        if server is None:
            await interaction.response.send_message("Für diesen Server ist keine Verifizierungsrolle hinterlegt.", ephemeral=True)
            return

        role = interaction.guild.get_role(server[0])
        if role is None:
            await interaction.response.send_message("Die Rolle existiert nicht mehr.", ephemeral=True)
            return

        if self.children[0].value == self.zahl:
            try:
                await user.add_roles(role)
                await interaction.response.send_message("Du bist nun Verifiziert.", ephemeral=True)
            except discord.errors.Forbidden:
                embed = discord.Embed(
                    color=discord.Colour.red(),
                    title="Fehler",
                    description="Ich habe keine Berechtigung, die Rolle zu vergeben oder die Rolle ist höher als meine."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Du hast die Zahl falsch eingegeben.", ephemeral=True)


class VerifyButton(discord.ui.Button):
    def __init__(self, bot, db):
        super().__init__(
            label="Verify",
            style=discord.ButtonStyle.gray,
            emoji="❓",
            custom_id="verify"
        )
        self.bot = bot
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        async with self.db.execute('SELECT role_id FROM verify WHERE guild_id = ?', (interaction.guild.id,)) as cursor:
            server = await cursor.fetchone()

        if server is None:
            await interaction.message.edit(view=None)
            return await interaction.response.send_message("Es wurde noch keine Rolle für die Verifizierung festgelegt.", ephemeral=True)

        role = interaction.guild.get_role(server[0])
        if role is None:
            return await interaction.response.send_message("Die Verifizierungsrolle existiert nicht mehr.", ephemeral=True)

        if role in user.roles:
            await interaction.response.send_message("Du bist bereits verifiziert.", ephemeral=True)
        else:
            modal = VerifyModal(self.bot, self.db)
            await interaction.response.send_modal(modal)


class VerifyText(discord.ui.Modal):
    def __init__(self, bot, db, channel_id, nfarbe, **kwargs) -> None:
        self.bot = bot
        self.db = db
        self.channel_id = channel_id
        self.nfarbe = nfarbe
        super().__init__(**kwargs, title='Verify Text Modal')

        self.add_item(discord.ui.InputText(
            label="Titel?",
            style=discord.InputTextStyle.long,
            required=True,
            min_length=3,
            value="Verify"
        ))
        self.add_item(discord.ui.InputText(
            label="Description?",
            style=discord.InputTextStyle.long,
            required=False,
            min_length=3,
            value="Verifiziere dich mit dem Button."
        ))
        self.add_item(discord.ui.InputText(
            label="Embed Footer?",
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

        if description and description.strip():
            embed = discord.Embed(
                title=title,
                description=description,
                color=self.nfarbe,
                timestamp=datetime.utcnow()
            )
        else:
            embed = discord.Embed(
                title=title,
                color=self.nfarbe,
                timestamp=datetime.utcnow()
            )

        embed.set_author(icon_url=interaction.guild.icon.url if interaction.guild.icon else None, name=interaction.guild.name)

        if footer and footer.strip():
            embed.set_footer(text=footer)

        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot, self.db))

        channel = self.bot.get_channel(self.channel_id)
        if channel is None:
            return

        await channel.send(embed=embed, view=view)


class VerifySafe(discord.ui.View):
    def __init__(self, bot, db, channel_id, nfarbe):
        super().__init__(timeout=None)
        self.bot = bot
        self.db = db
        self.channel_id = channel_id
        self.nfarbe = nfarbe
        self.message = None  # Wird nach dem Senden gesetzt

    async def set_message(self, message: discord.Message):
        self.message = message

    @discord.ui.button(label="Bestätigen", style=discord.ButtonStyle.green, row=1)
    async def callback1(self, button, interaction):
        for btn in self.children:
            btn.disabled = True
        if self.message:
            await self.message.edit(view=self)
        else:
            await interaction.message.edit(view=self)
        await interaction.response.defer()
        modal = VerifyText(self.bot, self.db, self.channel_id, self.nfarbe)
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
        self.db = None

    verify = SlashCommandGroup("verify", default_member_permissions=discord.Permissions(administrator=True),
                               guild_only=True)

    async def cog_load(self):
        # Async DB initialisieren
        self.db = await aiosqlite.connect('Data/verify.db')
        await self.db.execute('''CREATE TABLE IF NOT EXISTS verify (guild_id INTEGER PRIMARY KEY, role_id INTEGER)''')
        await self.db.commit()

        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot, self.db))
        self.bot.add_view(view)
        print('Verify System, bereitgestellt von discord.gg/paradies')

    @verify.command()
    @discord.default_permissions(administrator=True)
    async def setup(self, ctx, rolle: discord.Role):
        async with self.db.execute('SELECT * FROM verify WHERE guild_id= ?', (ctx.guild.id,)) as cursor:
            result = await cursor.fetchone()
        if result is not None:
            return await ctx.respond('Das Verify System ist bereits aktiviert!', ephemeral=True)

        await self.db.execute('INSERT INTO verify (guild_id, role_id) VALUES (?, ?)', (ctx.guild.id, rolle.id))
        await self.db.commit()
        await ctx.respond(f"Verify System ist nun aktiviert. Verifizierte Nutzer erhalten die Rolle {rolle.mention}.", ephemeral=True)

    @verify.command()
    @discord.default_permissions(administrator=True)
    async def remove(self, ctx):
        async with self.db.execute('SELECT * FROM verify WHERE guild_id= ?', (ctx.guild.id,)) as cursor:
            result = await cursor.fetchone()
        if result is None:
            return await ctx.respond('Das Verify System ist bereits deaktiviert!', ephemeral=True)

        await self.db.execute('DELETE FROM verify WHERE guild_id= ?', (ctx.guild.id,))
        await self.db.commit()
        await ctx.respond('Das Verify System ist nun deaktiviert!', ephemeral=True)
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
    if c.fetchone() is not None:
        embed = discord.Embed(
            color=discord.Colour.embed_background(),
            title="Bestätigen",
            description=f"Channel: {channel.mention}\nFarbe: {farbe}"
        )
        channel_id = channel.id
        view = VerifySafe(self.bot, channel_id, nfarbe)
        msg = await channel.send(embed=embed, view=view)
        await view.message = msg  # Message in View speichern, damit Buttons später bearbeitet werden können
        await ctx.respond("Bestätigungs-Embed wurde gesendet.", ephemeral=True)
    else:
        await ctx.respond('Verify System ist nicht aktiviert!', ephemeral=True)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        async with self.db.execute('SELECT * FROM verify WHERE guild_id = ?', (guild.id,)) as cursor:
            result = await cursor.fetchone()
        if result is not None:
            await self.db.execute('DELETE FROM verify WHERE guild_id = ?', (guild.id,))
            await self.db.commit()


def setup(bot):
    bot.add_cog(Verify(bot))
