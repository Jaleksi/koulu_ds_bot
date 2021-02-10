from discord.ext import commands
from ..api.peppi import get_course_info

@commands.command()
async def kurssi(context, param=None):
    if param is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    try:
        data = get_course_info(param)
        await context.send(data['name']['valueFi'])

    except Exception as err:
        print(err)
        await context.send("Kurssia ei löytynyt")

def setup(bot):
    bot.add_command(kurssi)
