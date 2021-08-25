from discord.ext import commands
from discord import Embed, utils

@commands.command()
async def seuraa(context, lecture_type=None, *title):
    if lecture_type is None:
        await context.send('Anna argumenttina seurattavan luennon tyyppi-id (+ otsikko luennolle) esim. !seuraa 1324 laskari')
        return

    # join title into a string if it's multiple words
    title = ' '.join(title) if title else 'Luento'

    # get channel id
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id

    # check if channel is connected to a course
    bound_course = context.bot.db.get_course_by_channel_id(channel_id)
    if not bound_course:
        await context.send('Tähän kanavaan ei ole liitetty kurssia.')
        return

    # make sure lecture type is valid
    lectures_to_follow = context.bot.db.get_course_lectures_by_type(bound_course['id'],
                                                                    lecture_type)
    if not lectures_to_follow:
        await context.send('Kurssityyppiä ei löytynyt tälle kurssille')
        return
    
    # check if lecture type is already followed
    already_following = context.bot.db.get_course_followed_lecture_by_type(bound_course['id'],
                                                                           lecture_type)
    if already_following:
        await context.send('Luentotyyppiä seurataan jo tällä kurssilla')
        return

    context.bot.db.insert_new_followed_course(bound_course['id'], lecture_type, title)
    context.bot.logger.info(f'Following new lecturetype {lecture_type} ({title})')

    e = Embed(
        title=f'Seurataan luentotyyppiä {lecture_type} ({title})',
        description=f'Luentoja tällä luentotyypillä tulossa {len(lectures_to_follow)}'
    )

    await context.send(embed=e)


def setup(bot):
    bot.add_command(seuraa)
