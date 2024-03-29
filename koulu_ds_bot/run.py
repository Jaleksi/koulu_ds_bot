import json

from src.bot import KouluBot
from secret import BOT_TOKEN


if __name__ == '__main__':
    # Read config file
    with open('./config.json', 'r') as json_file:
        config = json.load(json_file)

    # init and run bot
    bot = KouluBot(config)
    bot.run(BOT_TOKEN)
