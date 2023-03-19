import discord
from discord.ext import commands
from discord.commands import slash_command, Option, option

import openai
openai.api_key = "API KEY von CHAT GPT EINFÜGEN"


# def openai_response(message: str) -> str:      # ALTER CHATGPT CODE
#     try:
#         response = openai.Completion.create(
#             model="text-davinci-003",
#             prompt=message,
#             temperature=0,
#             max_tokens=250,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0,
#         )
#         if response.get("choices"):
#             return response.get("choices")[0]["text"]
#     except:
#         pass

class GPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author.bot:
    #         return
    #     if not message.channel.id == 1087071866977529939:
    #         return
    #     response = openai_response(message.content)
    #     embed = discord.Embed(
    #         description=response,
    #         color=discord.Colour.red()
    #     )
    #     try:
    #         await message.channel.send(embed=embed)
    #     except:
    #         return
    #         # await message.channel.send(response)


    @slash_command(description="Unterhalte dih mit GPT")
    @commands.cooldown(5,1, commands.BucketType.user)
    @option(name="redensart", description="Wähle die Redensart der KI", required=False, choices=["Kind", "Alter Mann", "Anime Girl", "Erwachsener", "Jugendlicher"], default="Katze")
    async def gpt(self, ctx, text: Option(str), redensart):
        try:
            await ctx.defer()
            if redensart == "Jugendlicher":
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",

                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein Jugendlicher mit ein schamlosen Mund, du nutzt die 2023 und 2022 Jugendwörter in deine Sätzen."
                        },
                        {"role": "user", "content": text}
                    ],
                    max_tokens=250
                )

            elif redensart == "Kind":
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",

                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein kleines Kind das seine Sätze auf das niedrigsten Niveu ist und süß redet."
                        },
                        {"role": "user", "content": text}
                    ],
                    max_tokens=250
                )

            elif redensart == "Alter Mann":
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",

                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein alter Mann der viel Erfahrung und viel Wissen und extrem Klug ist und deren Sätze auf Hoch Deutsch ist."
                        },
                        {"role": "user", "content": text}
                    ],
                    max_tokens=250
                )

            elif redensart == "Anime Girl":
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",

                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein japanischer Anime Mädchen der Deutsch spricht und Anime Art redet und liebvoll und super nett ist bist schüchtern und redest menschlich und schreibst wenig sätze aber bist dafür ultra cute, du verwendest 'cute', 'süßer', '🥰', '😍'"
                        },
                        {"role": "user", "content": text}
                    ],
                )

            elif redensart == "Erwachsener":
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",

                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein 18-20 Jährgier Erwachsener und sprichst auch so, bist ein bisschen Klug aber auch nicht mehr"
                        },
                        {"role": "user", "content": text}
                    ],
                    max_tokens=250
                )
            else:
                result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",

                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein Katze  der wie eine Mensch redet, bist sehr Klug und Witzig. Du nutzt immer 'awww', 'miao', 'schnurrr' und redet immeer wie eine Katze"
                        },
                        {"role": "user", "content": text}
                    ]
                )

            embed = discord.Embed(
                color=discord.Color.blurple(),
                title=text,
                description=result["choices"][0]["message"]["content"]
            )
            embed.set_footer(text=f"Redensart: {redensart}")
            await ctx.respond(embed=embed)
        except:
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Fehler!",
                description="Die Servern von Open-AI sind schlecht und können die Anfrage nicht schnell genug bearbeiten."
            )
            await ctx.respond(embed=embed)



def setup(bot: discord.Bot):
    bot.add_cog(GPT(bot))
