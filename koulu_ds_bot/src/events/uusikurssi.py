from discord.ext import commands
from discord import Embed
from ..api.peppi import get_course_info

@commands.command()
async def uusikurssi(context, param=None):
    if param is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    # Check if course is already in database
    q = f'SELECT * FROM kurssit WHERE id="{param}"'
    duplicates = context.bot.database_return(q, fetch_all=True)
    if duplicates:
        await context.send('Kurssi on jo lisätty')
        return

    # fetch course data
    try:
        data = get_course_info(param)
    except IndexError:
        await context.send('Kurssia ei löytynyt')
        return

    course_title = data['name']['valueFi']

    q = f'INSERT INTO kurssit(id, title) VALUES("{param}", "{course_title}")'
    context.bot.database_query(q)

    e = Embed(title=f'Lisättiin kurssi {param} onnistuneesti', description=course_title)
    await context.send(embed=e)


def setup(bot):
    bot.add_command(uusikurssi)
