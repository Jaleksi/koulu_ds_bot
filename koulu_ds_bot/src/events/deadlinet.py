from discord import Embed
from discord.ext import commands
from ..util.time_utils import epoch_to_readable_date

@commands.command()
async def deadlinet(context):
    get_course_title = lambda x: context.bot.database_return(
        ('SELECT title FROM courses WHERE id=?', (x,)),
        fetch_all=False
    )[0]

    deadlines_list = context.bot.database_return(('SELECT * FROM deadlines',), fetch_all=True)

    deadlines = '\n'.join(
        [
            f'{get_course_title(deadline[1])} ({epoch_to_readable_date(deadline[2])}): {deadline[3]}'
            for deadline
            in deadlines_list
        ]
    )
    e = Embed(title=f'Deadlinet', description=deadlines)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(deadlinet)
