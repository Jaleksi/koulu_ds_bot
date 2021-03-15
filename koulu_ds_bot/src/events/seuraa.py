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
    q = ('SELECT id FROM courses WHERE channel_id=?', (channel_id,))
    bound_course_id = context.bot.database_return(q, fetch_all=False)
    if not bound_course_id:
        await context.send('Tähän kanavaan ei ole liitetty kurssia.')
        return

    # make sure lecture type is valid
    q = ('''SELECT id
            FROM lectures
            WHERE lecture_type=?
            AND course_id=?
         ''', (lecture_type, bound_course_id[0]))
    lectures_to_follow = context.bot.database_return(q, fetch_all=True)
    if not lectures_to_follow:
        await context.send('Kurssityyppiä ei löytynyt tälle kurssille')
        return
    
    # check if lecture type is already followed
    q = ('SELECT id FROM followed_lecture_types WHERE lecture_type=? AND course_id=?', (lecture_type, bound_course_id[0]))
    already_following = context.bot.database_return(q, fetch_all=False)
    if already_following:
        await context.send('Luentotyyppiä seurataan jo tällä kurssilla')
        return

    # insert new type to table
    q = ('INSERT INTO followed_lecture_types(lecture_type, course_id, title) VALUES(?, ?, ?)',
         (lecture_type, bound_course_id[0], title))
    context.bot.database_query(q)

    context.bot.logger.info(f'Following new lecturetype {lecture_type} ({title})')

    e = Embed(
        title=f'Seurataan luentotyyppiä {lecture_type} ({title})',
        description=f'Luentoja tällä luentotyypillä tulossa {len(lectures_to_follow)}'
    )

    await context.send(embed=e)


def setup(bot):
    bot.add_command(seuraa)
