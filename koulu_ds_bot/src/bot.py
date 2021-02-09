import discord

class Bot(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, msg):
        print(f'{msg.author}: {msg.content}')

