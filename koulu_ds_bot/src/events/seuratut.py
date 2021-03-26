from discord import Embed, utils
from discord.ext import commands

@commands.command()
async def seuratut(context):
    # get channel id
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id

    # Check if channel is bound to a course
    bound_course = context.bot.db.get_course_by_channel_id(channel_id)

    if not bound_course:
        await context.send('Tätä kanavaa ei ole yhdistetty mihinkään kurssiin')
        return

    followed_lecturetypes_list = context.bot.db.get_course_followed_lectures(bound_course[0])

    followed_lecturetypes = '\n'.join(
        [
            f'**{followed[1]}**: {followed[3]}'
            for followed
            in followed_lecturetypes_list
        ]
    )

    e = Embed(title=f'Seuratut luentotyypit {bound_course[2]}', description=followed_lecturetypes)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(seuratut)
