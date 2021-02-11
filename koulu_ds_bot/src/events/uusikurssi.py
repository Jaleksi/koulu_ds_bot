from discord.ext import commands
from discord import Embed, utils
from ..api.peppi import get_course_info

@commands.command()
async def uusikurssi(context, course_id=None, channel_name=None):
    '''
        context (discord.ext.commands.Context object): given automatically
        course_id (str): user-given id for course
        channel_name (str): channel to bound course to, if None bound to channel it was sent from
    '''
    if course_id is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    if channel_name is None:
        channel_name = context.channel.name
    
    # get channel id (int) with given channel name (str)
    channel_id = utils.get(context.guild.channels, name=channel_name).id

    # Check if course is already in database
    q = f'SELECT * FROM courses WHERE id="{course_id}"'
    duplicates = context.bot.database_return(q, fetch_all=True)
    if duplicates:
        await context.send('Kurssi on jo lisätty')
        return

    # fetch course data
    try:
        data = get_course_info(course_id)
    except IndexError:
        await context.send('Kurssia ei löytynyt')
        return

    course_title = data['name']['valueFi']

    q = f'INSERT INTO courses(id, title, channel) VALUES("{course_id}", "{course_title}", "{channel_id}")'
    context.bot.database_query(q)

    e = Embed(
        title=f'Yhdistettiin kurssi {course_id} onnistuneesti kanavaan {channel_name}',
        description=course_title
    )

    await context.bot.get_channel(channel_id).send(embed=e)


def setup(bot):
    bot.add_command(uusikurssi)
