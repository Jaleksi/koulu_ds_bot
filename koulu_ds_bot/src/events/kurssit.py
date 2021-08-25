from discord import Embed
from discord.ext import commands

@commands.command()
async def kurssit(context):
    courses_list = context.bot.db.get_all_courses()
    get_name = lambda x: context.bot.get_channel(x)
    courses = '\n'.join(
        [
            f'**{c["peppi_id"]} ({get_name(c["channel_id"])}):** {c["title"]}'
            for c
            in courses_list
        ]
    )
    e = Embed(title=f'Tallennetut kurssit', description=courses)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(kurssit)
