from discord.ext import commands
from discord import Embed, utils
from ..api.peppi import get_course_info
from ..util.time_utils import epoch_now

@commands.command()
async def uusikurssi(context, peppi_id=None, channel_name=None):
    '''
        context (discord.ext.commands.Context object): given automatically
        peppi_id (str): user-given id for course
        channel_name (str): channel to bound course to, if None bound to channel it was sent from
    '''
    if peppi_id is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    if channel_name is None:
        channel_name = context.channel.name
    
    # get channel id (int) with given channel name (str)
    channel_id = utils.get(context.guild.channels, name=channel_name).id

    # Check if course is already in database
    q = ('SELECT * FROM courses WHERE peppi_id=?', (peppi_id,))
    duplicates = context.bot.database_return(q, fetch_all=True)
    if duplicates:
        await context.send('Kurssi on jo lisätty')
        return

    # fetch course data
    try:
        data = get_course_info(peppi_id)
    except IndexError:
        await context.send('Kurssia ei löytynyt')
        return

    course_title = data['name']['valueFi']

    q = ('INSERT INTO courses(peppi_id, title, channel_id) VALUES(?, ?, ?)',
         (peppi_id, course_title, channel_id))
    new_entry_id = context.bot.database_query(q)


    # add lecture times to db
    lectures = parse_lecture_times(data)
    for lecture in lectures:
        q = ('INSERT INTO lectures(course_id, start_timestamp, end_timestamp, location) VALUES(?, ?, ?, ?)',
             (new_entry_id, lecture['start'], lecture['end'], lecture['loc']))
        context.bot.database_query(q)

    e = Embed(
        title=f'Yhdistettiin kurssi {peppi_id} onnistuneesti kanavaan {channel_name}',
        description=course_title + f'\n Tulevia luentoja löytyi {len(lectures)} kpl'
    )
    await context.bot.get_channel(channel_id).send(embed=e)


def parse_lecture_times(data):
    lectures = []
    now = epoch_now()
    for lecture in data['reservations']:
        # ignore passed lectures.
        # data has 3 trailing zeroes.
        lecture_start = int(lecture['startTime'] / 1000)
        if now > lecture_start:
            continue

        lectures.append({
            'start': lecture_start,
            'end': lecture['endTime'],
            'loc': lecture['location']
        })

    return lectures


def setup(bot):
    bot.add_command(uusikurssi)
