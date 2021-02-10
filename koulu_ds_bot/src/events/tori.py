from discord import Embed
from discord.ext import commands

@commands.command()
async def tori(context):
    e = Embed()
    e.set_image(url='https://kamerat.oulunkaupunki.fi/Kauppatori/picture1.jpg')
    await context.send(embed=e)


def setup(bot):
    bot.add_command(tori)

