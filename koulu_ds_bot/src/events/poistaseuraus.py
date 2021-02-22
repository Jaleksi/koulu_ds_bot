from discord import Embed
from discord.ext import commands


@commands.command()
async def poistaseuraus(context, lecture_type=None):
    if lecture_type is None:
        await context.send('Anna argumenttina luentotyyppi id esim. 283777')
        return

    try:
        q = ('''SELECT
                    followed_lecture_types.id,
                    followed_lecture_types.title,
                    courses.channel_id
                FROM
                    followed_lecture_types
                INNER JOIN
                    courses
                ON
                    courses.id=followed_lecture_types.course_id
                WHERE
                    followed_lecture_types.lecture_type=?
             ''', (lecture_type,))
        delete_this = context.bot.database_return(q, fetch_all=False)

        if not delete_this:
            await context.send('Seurattua luentotyyppiä ei löytynyt')
            return

        q = ('DELETE FROM followed_lecture_types WHERE id=?', (delete_this[0],))
        context.bot.database_query(q)
        context.bot.logger.info(f'Stopped following course type {lecture_type} ({delete_this[1]})')

        e = Embed(
            title='Poistettiin luentotyypin seuranta',
            description=f'**{lecture_type}**: {delete_this[1]}'
        )
        await context.bot.get_channel(delete_this[2]).send(embed=e)

    except Exception as err:
        context.bot.logger.error(err)
        await context.send(f'Seurauksen poistaminen epäonnistui ({err})')

def setup(bot):
    bot.add_command(poistaseuraus)
