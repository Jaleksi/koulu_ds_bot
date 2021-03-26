from discord import Embed, utils
from discord.ext import commands


@commands.command()
async def poistaseuraus(context, lecture_type=None):
    if lecture_type is None:
        await context.send('Anna argumenttina luentotyyppi id esim. 283777')
        return

    channel_id = utils.get(context.guild.channels, name=context.channel.name).id
    bound_course = context.bot.db.get_course_by_channel_id(channel_id)
    if not bound_course:
        await context.send('Tähän kanavaan ei ole liitetty kurssia')
        return

    delete_this = context.bot.db.get_course_followed_lecture_by_type(bound_course[0], lecture_type)

    if not delete_this:
        await context.send('Seurattua luentotyyppiä ei löytynyt')
        return
    context.bot.db.delete_followed_lecture(delete_this[0])
    context.bot.logger.info(f'Stopped following course type {lecture_type} ({delete_this[3]})')

    e = Embed(
        title='Poistettiin luentotyypin seuranta',
        description=f'**{lecture_type}**: {delete_this[3]}'
    )
    await context.send(embed=e)


def setup(bot):
    bot.add_command(poistaseuraus)
