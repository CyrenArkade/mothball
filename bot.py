import asyncio
import discord
from discord.ext import commands
import json
import re
import os

class Mothball(commands.Bot):
    async def setup_hook(self):

        if os.path.isfile('restart.json'):
            with open('restart.json', 'r') as restart:
                info = json.load(restart)
                channel = await self.fetch_channel(info['channel'])
                msg = await channel.fetch_message(info['msg'])
                await msg.edit(content='Restarting...   Restarted!')
            os.remove('restart.json')
        
        await self.load_extension('cogs.admin')
        await self.load_extension('cogs.movement.movement')

def command_prefix(bot, msg: discord.Message):
    return bot.params['prefix']

intents = discord.Intents.all()
bot = Mothball(command_prefix=command_prefix, intents=intents, help_command=None)

@bot.command()
async def help(ctx):
    await ctx.send('Read the readme!\n<https://github.com/CyrenArkade/mothball>')

async def main():
    async with bot:
        await bot.start(bot.params['token'])

if __name__ == '__main__':

    with open('params.json', 'r') as input:
        params = json.load(input)
    bot.params = params

    asyncio.run(main())