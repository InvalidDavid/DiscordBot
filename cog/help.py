import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, Button, Select


class HelpView(View):
    def __init__(self, bot: discord.Bot, embeds):
        super().__init__(timeout=60)
        self.bot = bot
        self.embeds = embeds
        self.current_page = 0

        self.prev_button = Button(label="⬅️", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="➡️", style=discord.ButtonStyle.secondary)
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.select_menu = Select(
            placeholder="Wähle eine Kategorie...",
            options=[
                discord.SelectOption(
                    label=embed.title.split("📂 ")[1].split(" Commands")[0],
                    value=str(idx),
                    description=f"{len(embed.fields)} Befehle"
                )
                for idx, embed in enumerate(embeds)
            ]
        )
        self.select_menu.callback = self.select_category

        self.add_item(self.select_menu)
        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.update_buttons()

    async def on_timeout(self):
        try:
            for item in self.children:
                item.disabled = True

            if hasattr(self, 'message'):
                await self.message.edit(view=self)
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"Fehler beim Timeout: {e}")


    async def prev_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    async def select_category(self, interaction: discord.Interaction):
        self.current_page = int(self.select_menu.values[0])
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    def update_buttons(self):
        self.prev_button.disabled = self.current_page <= 0
        self.next_button.disabled = self.current_page >= len(self.embeds) - 1
        for option in self.select_menu.options:
            option.default = (option.value == str(self.current_page))


def is_owner_command(cmd):
    if getattr(cmd, "owner_only", False):
        return True
    if hasattr(cmd, "subcommands") and any(getattr(sub, "owner_only", False) for sub in cmd.subcommands):
        return True
    for check in getattr(cmd, "checks", []):
        if getattr(check, "__name__", "") == "predicate" and "is_owner" in repr(check):
            return True
    return False


def is_visible_command(cmd):
    if type(cmd).__name__ not in ("SlashCommand", "SlashCommandGroup"):
        return False
    if is_owner_command(cmd):
        return False
    return True


def gather_commands_recursive(cmd, prefix=""):
    cmds = []
    if not is_visible_command(cmd):
        return cmds

    current_name = f"{prefix}{cmd.name}"
    if hasattr(cmd, "subcommands") and cmd.subcommands:
        for sub in cmd.subcommands:
            cmds.extend(gather_commands_recursive(sub, prefix=current_name + " "))
    else:
        cmds.append((current_name.strip(), cmd.description or "Keine Beschreibung"))
    return cmds


class Hilfe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(name="help", description="Zeigt alle SlashCommands, die du ausführen darfst.")
    async def help_command(self, ctx: discord.ApplicationContext):
        embeds = []

        for cog_name, cog in self.bot.cogs.items():
            commands_list = getattr(cog, "get_commands", lambda: [])()
            all_cmds = []

            for cmd in commands_list:
                if not is_visible_command(cmd):
                    continue
                all_cmds.extend(gather_commands_recursive(cmd))

            if not all_cmds:
                continue

            embed = discord.Embed(
                title=f"📂 {cog_name} Commands",
                description=f"Alle Befehle aus `{cog_name}`",
                color=discord.Color.blurple()
            )

            for name, desc in all_cmds:
                embed.add_field(name=f"/{name}", value=desc, inline=False)

            embeds.append(embed)

        if not embeds:
            await ctx.respond("Keine sichtbaren Commands gefunden.", ephemeral=True)
            return

        view = HelpView(self.bot, embeds)
        msg = await ctx.respond(embed=embeds[0], view=view, ephemeral=True)
        view.message = await msg.original_response()


def setup(bot):
    bot.add_cog(Hilfe(bot))
