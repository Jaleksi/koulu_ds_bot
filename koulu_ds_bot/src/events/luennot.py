from discord import Embed, utils
from discord.ext import commands
from ..util.time_utils import epoch_to_lecture_time

@commands.command()
async def luennot(context):
    # get channel id
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id
    # Check if channel is bound to a course
    bound_course = context.bot.db.get_course_by_channel_id(channel_id)

    if not bound_course:
        await context.send('Tätä kanavaa ei ole yhdistetty mihinkään kurssiin')
        return

    lectures_list = context.bot.db.get_course_lectures(bound_course['id'])

    # sort lectures by types into dict
    lectures_by_type = {}
    for lecture in lectures_list:
        lecture_type = lecture['lecture_type']
        if not lectures_by_type.get(lecture_type):
            lectures_by_type[lecture_type] = [epoch_to_lecture_time(lecture['start_timestamp'],
                                                                    lecture['end_timestamp'])]
            continue
        lectures_by_type[lecture_type].append(epoch_to_lecture_time(lecture['start_timestamp'],
                                                                    lecture['end_timestamp']))

    lectures = '\n'.join(
        [
            f'**{lecture_type}:** ' +
            ', '.join(lectures_by_type.get(lecture_type))
            for lecture_type
            in lectures_by_type
        ]
    )

    e = Embed(title=f'Luennot {bound_course["title"]}', description=lectures)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(luennot)
