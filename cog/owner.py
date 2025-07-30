import os
import discord
from discord.ext import commands

COG_PATH = "cog"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_autocomplete(self, ctx: discord.AutocompleteContext):
        files = [f[:-3] for f in os.listdir(COG_PATH) if f.endswith(".py")]
        return [f for f in files if ctx.value.lower() in f.lower()][:25]


    owner = discord.SlashCommandGroup("owner", "owner")

    @owner.command(name="reload", description="Lade ein Cog neu")
    @commands.is_owner()
    async def reload_cog(
        self,
        ctx: discord.ApplicationContext,
        cog_name: discord.Option(str, "Wähle ein Cog", autocomplete=cog_autocomplete)
    ):
        await ctx.defer(ephemeral=True)

        extension = f"{COG_PATH}.{cog_name}"

        try:
            self.bot.reload_extension(extension)
            await ctx.respond(f"✅ Cog `{cog_name}` erfolgreich neu geladen!", ephemeral=True)
        except commands.ExtensionNotLoaded:
            try:
                self.bot.load_extension(extension)
                await ctx.respond(f"⚡ Cog `{cog_name}` war nicht geladen und wurde jetzt geladen.", ephemeral=True)
            except Exception as e:
                await ctx.respond(f"❌ Fehler beim Laden von `{cog_name}`:\n```{e}```", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Fehler beim Reload von `{cog_name}`:\n```{e}```", ephemeral=True)


def setup(bot):
    bot.add_cog(Admin(bot))
