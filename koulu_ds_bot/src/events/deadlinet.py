from discord import Embed, utils
from discord.ext import commands
from ..util.time_utils import epoch_to_readable_date

@commands.command()
async def deadlinet(context):
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id
    bound_course = context.bot.db.get_course_by_channel_id(channel_id)

    # if channel is not connected to a course, get all deadlines
    # otherwise get only deadlines on that course
    if not bound_course:
        deadlines_list = context.bot.db.get_all_deadlines()
    else:
        deadlines_list = context.bot.db.get_course_deadlines(bound_course[0])

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
