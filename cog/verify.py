import discord
from discord.ext import commands
from discord.commands import slash_command
import random

rolle = 1057946388975075338 # Eure Rolle ID hier einsetzen

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
        role = interaction.guild.get_role(rolle)

        if self.children[0].value == self.zahl:
            try:
                await user.add_roles(role)
                await interaction.response.send_message("Du bist nun Verifiziert.", ephemeral=True)
            except:
                await interaction.response.send_message("Es ist ein Fehler aufgetreten, bitte Wiederhole die Verifizierung.", ephemeral=True)
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
        role = interaction.guild.get_role(rolle)
        if role in user.roles:
            await interaction.response.send_message("Du bist bereits Verifiziert.", ephemeral=True)
        else:
            modal = VerifyModal(self.bot)
            await interaction.response.send_modal(modal)


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Verify")
    async def verifysetup(self, ctx):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot))
        await ctx.respond("Verify", view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyButton(self.bot))
        self.bot.add_view(view)

def setup(bot):
    bot.add_cog(Verify(bot))
