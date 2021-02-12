import time
from discord.ext import commands
from discord import Embed, utils
from ..util.time_utils import epoch_now, remove_leading_digits_from_year, timestamp_to_epoch

@commands.command()
async def deadline(context, timestamp=None, *msg):
    if timestamp is None or len(msg) == 0:
        await context.send('Anna argumenttina kurssin aika ja viesti esim. 12/4/2021 tentti')
        return

    # join message into a string if it's multiple words
    msg = ' '.join(msg)

    # check if timestamp items are separated with . or /
    delimiter = '/' if '/' in timestamp else '.'

    # check if year was given in 4 numbers, strip first 2 if it is
    timestamp = remove_leading_digits_from_year(timestamp, delimiter)

    # create time object from strings
    epoch_time = timestamp_to_epoch(timestamp, delimiter)
    now = epoch_now()

    if now > epoch_time:
        await context.send('Päivämäärä on mennyt jo. Anna vähintään huominen.')
        return

    # get channel id
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id

    # check if channel is connected to a course
    q = ('SELECT id FROM courses WHERE channel_id=?', (channel_id,))
    bound_course_id = context.bot.database_return(q, fetch_all=False)
    if not bound_course_id:
        await context.send('Tähän kanavaan ei ole liitetty kurssia.')
        return


    q = ('INSERT INTO deadlines(course_id, timestamp, message) VALUES(?, ?, ?)',
         (bound_course_id[0], epoch_time, msg))
    context.bot.database_query(q)

    e = Embed(
        title=f'Tallennettiin deadline: {msg}',
        description=f'Deadlinesta muistutetaan {timestamp} kanavalla {context.channel.name}'
    )

    await context.send(embed=e)


def setup(bot):
    bot.add_command(deadline)
