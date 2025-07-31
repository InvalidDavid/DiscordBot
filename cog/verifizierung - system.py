import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, option
from discord.ui import InputText, Button
import random
import sqlite3
from datetime import datetime, timezone


DB_PATH = "Data/verifizierung.db"

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# Initialize database tables
with get_db_connection() as db_conn:
    db_conn.execute('''CREATE TABLE IF NOT EXISTS verify(
                      guild_id INTEGER PRIMARY KEY,
                      role_id INTEGER
                  )''')
    db_conn.commit()


class VerifyModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, **kwargs) -> None:
        self.bot = bot
        self.code = str(random.randint(1000, 9999))
        super().__init__(**kwargs, title=f'Verifizierungscode: {self.code}')

        self.add_item(InputText(
            label="Gib den Code ein",
            placeholder="4-stelliger Code",
            style=discord.InputTextStyle.short,
            required=True,
            min_length=4,
            max_length=4
        ))

    async def callback(self, interaction: discord.Interaction):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT role_id FROM verify WHERE guild_id = ?', (interaction.guild.id,))
            result = cur.fetchone()

        if not result:
            return await interaction.response.send_message(
                "Verifizierungssystem ist nicht aktiviert.",
                ephemeral=True
            )

        role = interaction.guild.get_role(result['role_id'])
        if not role:
            return await interaction.response.send_message(
                "Verifizierungsrolle nicht gefunden.",
                ephemeral=True
            )

        if self.children[0].value == self.code:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "Erfolgreich verifiziert!",
                    ephemeral=True
                )
            except discord.Forbidden:
                embed = discord.Embed(
                    color=discord.Colour.red(),
                    title="Berechtigungsfehler",
                    description="Bot hat keine Berechtigung für diese Aktion"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            return await interaction.response.send_message(
                "Falscher Code!",
                ephemeral=True
            )


class VerifyButton(Button):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            label="Verifizieren",
            style=discord.ButtonStyle.green,
            emoji="✅",
            custom_id="verify_button"
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT role_id FROM verify WHERE guild_id = ?', (interaction.guild.id,))
            result = cur.fetchone()

        if not result:
            await interaction.message.edit(view=None)
            return await interaction.response.send_message(
                "Verifizierungssystem ist nicht aktiviert.",
                ephemeral=True
            )

        role = interaction.guild.get_role(result['role_id'])
        if role in interaction.user.roles:
            return await interaction.response.send_message(
                "Du bist bereits verifiziert!",
                ephemeral=True
            )
        else:
            modal = VerifyModal(self.bot)
            return await interaction.response.send_modal(modal)


class VerifyTextModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, channel_id: int, embed_color: discord.Color, **kwargs):
        self.bot = bot
        self.channel_id = channel_id
        self.embed_color = embed_color
        super().__init__(**kwargs, title='Verifizierung einrichten')

        self.add_item(InputText(
            label="Titel",
            style=discord.InputTextStyle.short,
            required=True,
            min_length=3,
            max_length=256,
            value="Verifizierung"
        ))

        self.add_item(InputText(
            label="Beschreibung",
            style=discord.InputTextStyle.long,
            required=False,
            min_length=3,
            max_length=4000,
            value="Klicke auf den Button zur Verifizierung"
        ))

        self.add_item(InputText(
            label="Fußzeile",
            style=discord.InputTextStyle.short,
            required=False,
            min_length=3,
            max_length=2048,
            value="Verifizierungssystem"
        ))

    async def callback(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value
        footer = self.children[2].value

        embed = discord.Embed(
            title=title,
            color=self.embed_color,
            timestamp=datetime.now(timezone.utc)
        )

        if description:
            embed.description = description

        if interaction.guild.icon:
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
        else:
            embed.set_author(name=interaction.guild.name)

        if footer:
            embed.set_footer(text=footer)

        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot))

        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message(
                f"Verifizierungsnachricht wurde in {channel.mention} gesendet.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Kanal nicht gefunden!",
                ephemeral=True
            )


class VerifyConfirmationView(discord.ui.View):
    def __init__(self, bot: commands.Bot, channel_id: int, embed_color: discord.Color):
        super().__init__(timeout=180)
        self.bot = bot
        self.channel_id = channel_id
        self.embed_color = embed_color

    @discord.ui.button(label="Bestätigen", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = VerifyTextModal(self.bot, self.channel_id, self.embed_color)
        await interaction.response.send_modal(modal)
        
        for child in self.children:
            child.disabled = True
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            color=discord.Colour.red(),
            title="Abgebrochen"
        )
        await interaction.response.edit_message(embed=embed, view=None, delete_after=5)


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    verify = SlashCommandGroup(
        name="verifizierung",
        description="Verifizierungssystem verwalten",
        default_member_permissions=discord.Permissions(administrator=True)
    )

    @verify.command()
    @discord.default_permissions(administrator=True)
    async def setup(self, ctx: discord.ApplicationContext, role: discord.Role):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT role_id FROM verify WHERE guild_id = ?', (ctx.guild.id,))
            if cur.fetchone():
                return await ctx.respond(
                    'Verifizierungssystem ist bereits aktiviert!',
                    ephemeral=True
                )

            cur.execute('INSERT INTO verify(guild_id, role_id) VALUES(?, ?)',
                       (ctx.guild.id, role.id))
            conn.commit()

        return await ctx.respond(
            f"Verifizierung aktiviert! Benutzer erhalten {role.mention} nach Verifizierung.",
            ephemeral=True
        )

    @verify.command()
    @discord.default_permissions(administrator=True)
    async def remove(self, ctx: discord.ApplicationContext):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT role_id FROM verify WHERE guild_id = ?', (ctx.guild.id,))
            if not cur.fetchone():
                return await ctx.respond(
                    'Verifizierungssystem ist nicht aktiviert!',
                    ephemeral=True
                )

            cur.execute('DELETE FROM verify WHERE guild_id = ?', (ctx.guild.id,))
            conn.commit()

        return await ctx.respond(
            'Verifizierungssystem wurde deaktiviert!',
            ephemeral=True
        )

    @verify.command()
    @discord.default_permissions(administrator=True)
    @option(
        name="channel",
        description="Kanal für die Verifizierungsnachricht",
        channel_types=[discord.ChannelType.text]
    )
    @option(
        name="farbe",
        description="Farbe des Embeds",
        choices=["Red", "Blue", "Green", "Grey", "Random", "Invisible"],
        default="Invisible"
    )
    async def send(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel,
        farbe: str
    ):
        farben = {
            "Red": discord.Colour.red(),
            "Blue": discord.Colour.blue(),
            "Green": discord.Colour.green(),
            "Grey": discord.Colour.greyple(),
            "Random": discord.Colour.random(),
            "Invisible": discord.Colour.embed_background()
        }
        embed_farbe = farben.get(farbe, discord.Colour.embed_background())

        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT role_id FROM verify WHERE guild_id = ?', (ctx.guild.id,))
            if not cur.fetchone():
                return await ctx.respond(
                    'Verifizierungssystem ist nicht aktiviert! Nutze zuerst /verify setup.',
                    ephemeral=True
                )

        embed = discord.Embed(
            color=discord.Colour.embed_background(),
            title="Bestätigung",
            description=f"**Kanal:** {channel.mention}\n**Farbe:** {farbe}\n\nKlicke auf Bestätigen um fortzufahren."
        )

        return await ctx.respond(
            embed=embed,
            view=VerifyConfirmationView(self.bot, channel.id, embed_farbe),
            ephemeral=True
        )





    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot))
        self.bot.add_view(view)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        with get_db_connection() as conn:
            conn.execute('DELETE FROM verify WHERE guild_id = ?', (guild.id,))
            conn.commit()


def setup(bot):
    bot.add_cog(Verify(bot))
