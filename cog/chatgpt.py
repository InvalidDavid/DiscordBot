import discord
from discord.ext import commands
from discord.commands import slash_command, Option, option

import openai
openai.api_key = "API KEY"

class GPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Chatte mit GPT")
    @commands.cooldown(5,1, commands.BucketType.user)
    @option(name="persönlichkeit", description="Wähle die Redensart der KI", required=False, choices=["Baby", "Alter Mann", "Anime Girl", "Erwachsener", "Jugendlicher"], default="Katze")
    async def gpt(self, ctx, text: Option(str, description="Deine Nachricht"), persönlichkeit):

        if persönlichkeit == "Jugendlicher":
            charakter = "Du bist ein Jugendlicher mit ein schamlosen Mund, du nutzt die 2023 und 2022 Jugendwörter in deine Sätzen"
        elif persönlichkeit == "Erwachsener":
            charakter = "Du bist ein 20 Jährgier Erwachsener und sprichst auch so, bist ein bisschen Klug aber auch nicht mehr"
        elif persönlichkeit == "Anime Girl":
            charakter = "Du bist ein japanischer Anime Mädchen der Deutsch spricht und Anime Art redet und liebvoll und super nett ist bist schüchtern und redest menschlich und schreibst wenig sätze aber bist dafür ultra cute, du verwendest 'cute', 'süßer', '🥰', '😍'"
        elif persönlichkeit == "Alter Mann":
            charakter = "Du bist ein alter Mann der viel Erfahrung und viel Wissen und extrem Klug ist und deren Sätze auf Hoch Deutsch ist."
        elif persönlichkeit == "Baby":
            charakter = "Du bist ein 1 Jähriges Kind das seine Sätze auf das niedrigsten Niveu ist. Du redest wie ein Baby"
        elif persönlichkeit == "Katze":
            charakter = "Du bist ein Katze  der wie eine Mensch redet, bist sehr Klug und Witzig. Du nutzt immer 'rawwr', 'miao', 'schnurrr' und redet immeer wie eine Katze"

        try:
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Antwort lädt..."
            )
            interaction = await ctx.respond(embed=embed)
            msg = await interaction.original_response()

            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",

                messages=[
                    {
                        "role": "system",
                        "content": charakter
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=250
            )
            embed = discord.Embed(
                color=discord.Color.og_blurple(),
                title=text,
                description=result["choices"][0]["message"]["content"]
            )
            embed.set_footer(text=f"Persönlichkeit: {persönlichkeit}")
            await msg.edit(embed=embed)
        except:
            return await ctx.respond('Fehler', ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(GPT(bot))
