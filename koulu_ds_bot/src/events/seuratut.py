from discord import Embed, utils
from discord.ext import commands

@commands.command()
async def seuratut(context):
    # get channel id
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id

    # Check if channel is bound to a course
    q = ('SELECT id, title FROM courses WHERE channel_id=?', (channel_id,))
    bound_course = context.bot.database_return(q, fetch_all=False)

    if not bound_course:
        await context.send('Tätä kanavaa ei ole yhdistetty mihinkään kurssiin')
        return

    q = ('''SELECT
                lecture_type,
                title
            FROM
                followed_lecture_types
            WHERE course_id=?
        ''', (bound_course[0],))

    followed_lecturetypes_list = context.bot.database_return(q, fetch_all=True)

    followed_lecturetypes = '\n'.join(
        [
            f'**{followed[0]}**: {followed[1]}'
            for followed
            in followed_lecturetypes_list
        ]
    )

    e = Embed(title=f'Seuratut luentotyypit {bound_course[1]}', description=followed_lecturetypes)
    await context.send(embed=e)

def setup(bot):
    bot.add_command(seuratut)
