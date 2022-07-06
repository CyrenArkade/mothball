import asyncio
import discord
from discord.ext import commands
import json
import subprocess
import re

def prefix(bot, msg):
    return bot.params['prefix']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)

@bot.command()
async def help(ctx):
    await ctx.send('Read the readme!\n<https://github.com/CyrenArkade/mothball>')

@bot.event
async def on_message(msg):
    if re.search(r'\[(\'.*?\'(, )?)*?\]', msg.content) and msg.author.id == 982688359069659146:
        await cocasse(msg)
    
    await bot.process_commands(msg)

async def cocasse(msg):
    await msg.add_reaction('🔍')

    def check(reaction, user):
        return reaction.message.id == msg.id and str(reaction.emoji) == '🔍' and not user.bot

    try:
        await bot.wait_for('reaction_add', timeout=60, check=check)

        out = ''
        for match in re.findall(r'\'.*?\'', msg.content):
            match = match[1:-1]

            if 'stop' in match:
                out += 'stop'
            elif 'sneak' in match:
                out += 'sn'
            elif 'walk' in match:
                out += 'w'
            elif 'sprint' in match:
                out += 's'
            
            if '45' in match:
                out += '45'
            
            if 'back' in match:
                out += '(-1)'
            
            out += ' '
        
        movement = bot.get_cog('Movement')
        out += '\n' + str(movement.sim(out))
        await msg.channel.send(out)
    except asyncio.TimeoutError:
        pass


if __name__ == '__main__':

    with open('params.json', 'r') as input:
        params = json.load(input)
    bot.params = params

    bot.load_extension('cogs.admin.admin')
    bot.load_extension('cogs.movement.movement')
    bot.run(params['token'])