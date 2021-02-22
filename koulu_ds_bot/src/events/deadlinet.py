from discord import Embed, utils
from discord.ext import commands
from ..util.time_utils import epoch_to_readable_date

@commands.command()
async def deadlinet(context):
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id
    
    # check if channel is connected to a course
    q = ('SELECT id FROM courses WHERE channel_id=?', (channel_id,))
    bound_course_id = context.bot.database_return(q, fetch_all=False)
    # if channel is not connected to a course, get all deadlines
    # otherwise get only deadlines on that course
    # query returns [(title, timestamp, message)...]
    if not bound_course_id:
        q = ('''SELECT courses.title, deadlines.timestamp, deadlines.message
                FROM deadlines
                INNER JOIN courses ON deadlines.course_id=courses.id
                ORDER BY timestamp''',)
        deadlines_list = context.bot.database_return(q, fetch_all=True)
    else:
        q = ('''SELECT courses.title, deadlines.timestamp, deadlines.message
                FROM deadlines
                INNER JOIN courses ON deadlines.course_id=courses.id
                WHERE courses.channel_id=?
                ORDER BY deadlines.timestamp''', (channel_id,))
        deadlines_list = context.bot.database_return(q, fetch_all=True)

    deadlines = '\n'.join(
        [
            f'**{deadline[0]} ({epoch_to_readable_date(deadline[1])}):** {deadline[2]}'
            for deadline
            in deadlines_list
        ]
    )
    e = Embed(title=f'Deadlinet', description=deadlines)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(deadlinet)
