from discord.ext.commands import Bot

class KouluBot(Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
