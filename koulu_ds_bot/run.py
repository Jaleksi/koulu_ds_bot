from src.bot import Bot
from secret import BOT_TOKEN

if __name__ == '__main__':
    bot = Bot()
    bot.run(BOT_TOKEN)
