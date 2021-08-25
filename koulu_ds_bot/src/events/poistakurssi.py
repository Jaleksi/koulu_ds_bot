from discord import Embed
from discord.ext import commands


@commands.command()
async def poistakurssi(context, peppi_id=None):
    if peppi_id is None:
        await context.send('Anna argumenttina kurssin id esim. 902150Y')
        return

    try:
        delete_this = context.bot.db.get_course_by_peppi_id(peppi_id)

        if not delete_this:
            await context.send('Kurssia ei löytynyt')
            return

        context.bot.db.delete_course_by_peppi_id(peppi_id)

        channel = context.bot.get_channel(delete_this['channel_id'])
        context.bot.logger.info(
            f'Removed course {peppi_id} from channel {channel}'
        )

        e = Embed(
            title=f'Poistettiin kurssi {peppi_id} kanavalta {channel}',
            description=delete_this['title']
        )
        await channel.send(embed=e)

    except Exception as err:
        context.bot.logger.error(err)
        await context.send(f'Kurssin poistaminen epäonnistui ({err})')
        raise

def setup(bot):
    bot.add_command(poistakurssi)
