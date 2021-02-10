from discord.ext import commands

@commands.command()
async def ping(context):
    await context.send("pong")


def setup(bot):
    bot.add_command(ping)

