import json

from src.bot import KouluBot
from secret import BOT_TOKEN


if __name__ == '__main__':
    with open('./config.json', 'r') as json_file:
        config = json.load(json_file)

    bot = KouluBot(command_prefix=config['commandPrefix'])

    for ev in config['events']:
        try:
            bot.load_extension(f'src.events.{ev}')
            print(f'Succesfully loaded event: {ev}')
        except Exception as err:
            print(f'Failed to load event: {ev}')
            print(err)

    try:
        bot.run(BOT_TOKEN)
    except KeyboardInterrupt:
        bot.logoout()
