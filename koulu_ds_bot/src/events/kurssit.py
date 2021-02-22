from discord import Embed
from discord.ext import commands

@commands.command()
async def kurssit(context):
    courses_list = context.bot.database_return(
        ('SELECT peppi_id, title, channel_id FROM courses',), fetch_all=True
    )
    get_name = lambda x: context.bot.get_channel(x)
    courses = '\n'.join([f'**{c[0]} ({get_name(c[2])}):** {c[1]}' for c in courses_list])
    e = Embed(title=f'Tallennetut kurssit', description=courses)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(kurssit)
