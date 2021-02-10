from discord import Embed
from discord.ext import commands

@commands.command()
async def poistakurssi(context, param=None):
    if param is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    try:
        q = f'SELECT title FROM kurssit WHERE id="{param}"'
        desc_of_deleted = context.bot.database_return(q, fetch_all=False)

        if not desc_of_deleted:
            await context.send('Kurssia ei löytynyt')
            return

        q = f'DELETE FROM kurssit WHERE id="{param}"'
        context.bot.database_query(q)
        e = Embed(title=f'Poistettiin kurssi {param} onnistuneesti', description=desc_of_deleted[0])
        await context.send(embed=e)

    except Exception as err:
        print(err)
        await context.send(f'Kurssin poistaminen epäonnistui ({err})')

def setup(bot):
    bot.add_command(poistakurssi)
