from discord import Embed
from discord.ext import commands

@commands.command()
async def poistakurssi(context, peppi_id=None):
    if peppi_id is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    try:
        q = ('SELECT id, title, channel_id FROM courses WHERE peppi_id=?', (peppi_id,))
        delete_this = context.bot.database_return(q, fetch_all=False)

        if not delete_this:
            await context.send('Kurssia ei löytynyt')
            return

        q = ('DELETE FROM courses WHERE peppi_id=?', (peppi_id,))
        context.bot.database_query(q)

        # Delete deadlines and lectures connected to the course
        for table in ['deadlines', 'lectures']:
            q = (f'DELETE FROM {table} WHERE id=?', (delete_this[0],))
            context.bot.database_query(q)

        e = Embed(title=f'Poistettiin kurssi {peppi_id} onnistuneesti', description=delete_this[1])
        await context.bot.get_channel(delete_this[2]).send(embed=e)

    except Exception as err:
        print(err)
        await context.send(f'Kurssin poistaminen epäonnistui ({err})')

def setup(bot):
    bot.add_command(poistakurssi)
