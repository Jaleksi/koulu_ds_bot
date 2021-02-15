from discord.ext import commands

@commands.command()
async def ping(context):
    context.bot.logger.info(f'{context.message.author} called ping command')
    await context.send("pong")

def setup(bot):
    bot.add_command(ping)
