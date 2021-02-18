from discord.ext import commands
from discord import Embed, utils
from ..util.ics_parser import parse_events_from_ics
from ..util.time_utils import epoch_to_readable_date, gmt_plus_2

@commands.command()
async def lueics(context):
    channel_id = utils.get(context.guild.channels, name=context.channel.name).id
    # make sure channel is connected to course
    q = ('SELECT id, peppi_id FROM courses WHERE channel_id=?', (channel_id,))
    # bound_course = [id, peppi_id]
    bound_course = context.bot.database_return(q, fetch_all=False)
    if not bound_course:
        await context.send('Tähän kanavaan ei ole liitetty kurssia.')
        return

    # read attachments
    attachments = context.message.attachments

    # make sure there is attachment
    if not attachments:
        await context.send('Lisää liitetiedostoksi .ics kalenteri')
        return

    if len(attachments) > 1:
        await context.send('Useampi liitetiedosto, katsotaan ensimmäistä')

    if not attachments[0].filename.lower().endswith('.ics'):
        await context.send('Väärä tiedostomuoto')
        return

    # parse events from calendar
    ics_file = await attachments[0].read()
    events = parse_events_from_ics(ics_file)

    added_deadlines = ''
    found_deadlines = 0

    for event in events:
        if bound_course[1] in event.get('category'):
            ts = event.get('timestamp')
            ts = gmt_plus_2(ts)
            msg = event.get('msg', 'Ei tarkempaa tietoa')
            q = ('INSERT INTO deadlines(course_id, timestamp, message) VALUES(?, ?, ?)',
                (bound_course[0], ts, msg))
            added_deadlines += f'({epoch_to_readable_date(ts)}): {msg}\n\n'
            found_deadlines += 1
            context.bot.database_query(q)
            context.bot.logger.info(f'Added new deadline from ics {msg} ({epoch_to_readable_date(ts)})')

    e = Embed(
        title=f'Tiedostosta haettiin {found_deadlines} tapahtumaa',
        description=added_deadlines
    )

    await context.send(embed=e)

def setup(bot):
    bot.add_command(lueics)
