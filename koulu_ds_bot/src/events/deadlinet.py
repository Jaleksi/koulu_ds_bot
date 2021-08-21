from discord import Embed, utils
from discord import File as DFile
from discord.ext import commands
from ..util.time_utils import epoch_to_readable_date, days_until
from ..util.deadline_image import create_image

@commands.command()
async def deadlinet(context, *args):
    # TODO: Make sure course is not already connected to some channel
    # TODO: Should bounding course to main channel (yleinen) be disallowed?
    # TODO: Add argument to get deadlines within some limit (eg. days=30
    #       would return deadlines that are within 30 days from now)

    channel_id = utils.get(context.guild.channels, name=context.channel.name).id
    bound_course = context.bot.db.get_course_by_channel_id(channel_id)
    return_as_image = '--kuva' in args
    return_all_deadlines = '--kaikki' in args

    # if channel is not connected to a course, get all deadlines
    # otherwise get only deadlines on that course
    if not bound_course or return_all_deadlines:
        deadlines_list = context.bot.db.get_all_deadlines()
    else:
        deadlines_list = context.bot.db.get_course_deadlines(bound_course[0])

    if not deadlines_list:
        await context.send("Ei tallennettuja deadlineja")
        return

    if return_as_image:
        deadlines = [
            {
                'course': deadline[0],
                'date': epoch_to_readable_date(deadline[1]),
                'title': deadline[2],
                'days_until': days_until(deadline[1])
            }
            for deadline
            in deadlines_list
        ]
        try:
            deadline_img = DFile(create_image(deadlines), filename='deadlinet.png')
            await context.send('', file=deadline_img)
        except Exception as err:
            await context.send(f'Kuvan luominen epäonnistui: {err}')
        return

    else:
        deadlines = '\n'.join(
            [
                f'**{deadline[0]} ({epoch_to_readable_date(deadline[1])}):** {deadline[2]}'
                for deadline
                in deadlines_list
            ]
        )
        e = Embed(title=f'Deadlinet', description=deadlines[:2048])
        await context.send(embed=e)

def setup(bot):
    bot.add_command(deadlinet)
