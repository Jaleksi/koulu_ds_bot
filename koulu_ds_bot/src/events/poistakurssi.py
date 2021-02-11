from discord import Embed
from discord.ext import commands

@commands.command()
async def poistakurssi(context, param=None):
    if param is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    try:
        q = f'SELECT title, channel FROM courses WHERE id="{param}"'
        delete_this = context.bot.database_return(q, fetch_all=False)

        if not delete_this:
            await context.send('Kurssia ei löytynyt')
            return

        q = f'DELETE FROM courses WHERE id="{param}"'
        context.bot.database_query(q)
        e = Embed(title=f'Poistettiin kurssi {param} onnistuneesti', description=delete_this[0])
        
        await context.bot.get_channel(delete_this[1]).send(embed=e)

    except Exception as err:
        print(err)
        await context.send(f'Kurssin poistaminen epäonnistui ({err})')

def setup(bot):
    bot.add_command(poistakurssi)
