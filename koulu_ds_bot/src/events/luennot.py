from discord import Embed, utils
from discord.ext import commands
from ..util.time_utils import epoch_to_lecture_time

@commands.command()
async def luennot(context):
    # get channel id
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id

    # Check if channel is bound to a course
    q = ('SELECT id, title FROM courses WHERE channel_id=?', (channel_id,))
    bound_course = context.bot.database_return(q, fetch_all=False)

    if not bound_course:
        await context.send('Tätä kanavaa ei ole yhdistetty mihinkään kurssiin')
        return

    q = ('''SELECT lecture_type, start_timestamp, end_timestamp
            FROM lectures
            WHERE course_id=?
            ORDER BY start_timestamp
        ''', (bound_course[0],))
    lectures_list = context.bot.database_return(q, fetch_all=True)

    # sort lectures by types into dict
    lectures_by_type = {}
    for lecture in lectures_list:
        lecture_type = lecture[0]
        if not lectures_by_type.get(lecture_type):
            lectures_by_type[lecture_type] = [epoch_to_lecture_time(lecture[1], lecture[2])]
            continue
        lectures_by_type[lecture_type].append(epoch_to_lecture_time(lecture[1], lecture[2]))

    lectures = '\n'.join(
        [
            f'**{lecture_type}:** ' +
            ', '.join(lectures_by_type.get(lecture_type))
            for lecture_type
            in lectures_by_type
        ]
    )

    e = Embed(title=f'Luennot {bound_course[1]}', description=lectures)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(luennot)
