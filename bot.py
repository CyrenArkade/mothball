import asyncio
import discord
from discord.ext import commands
import commandmanager as cmdmgr
import parsers
from player import Player
import json
import subprocess
import movement
from io import StringIO
from contextlib import redirect_stdout
import re

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix=';', intents=intents, help_command=None)

player_commands = cmdmgr.get_player_commands()
player_command_arguments = cmdmgr.get_player_command_args()
player_arg_aliases = cmdmgr.get_player_arg_aliases()
params = {}

msg_links = {}

def sim(input, player = None, recordhistory = False):

    if not player:
        player = Player()

    commands = parsers.separate_commands(input)

    commands_args = [single for command in commands for single in parsers.argumentatize_command(command)]

    for command in commands_args:
        command_function = player_commands[command[0]]
        dict_args, updates = parsers.dictize_args(command[1], player_command_arguments[command_function])

        command_function(player, dict_args)
    
    if recordhistory:
        return player.history_string()
    else:
        return player

@bot.command(name="s")
async def simulate(ctx, *, text):
    msg = await ctx.send(sim(text))
    msg_links.update({ctx.message.id: msg.id})

@bot.command(name='h')
async def history(ctx, *, text):
    msg = await ctx.send(sim(text, recordhistory = True))
    msg_links.update({ctx.message.id: msg.id})

@bot.event
async def on_message_edit(before, after):
    if after.id not in msg_links:
        return
    
    newcmd = after.content[3:]
    botmsg = await after.channel.fetch_message(msg_links[after.id])
    await botmsg.edit(content=sim(newcmd))

@bot.command()
async def cmd(ctx, *, text):
    if ctx.author.id not in params['admins']:
        await ctx.message.add_reaction('🤡')
        return
    
    task = subprocess.run(text , shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    await ctx.send(f'```{task.stdout}```')
    
@bot.command()
async def restart(ctx):
    if ctx.author.id not in params.get('admins', {}):
        await ctx.message.add_reaction('🤡')
        return
    
    task = subprocess.run('pm2 restart bot', shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    await ctx.send(f'```{task.stdout}```')

@bot.command()
async def py(ctx, *, text):
    if ctx.author.id not in params['admins']:
        await ctx.message.add_reaction('🤡')
        return
    
    text = text.strip('`')
    if text.startswith('py'): text = text[2:]

    text = f'async def __ex(): ' + ''.join(f'\n {l}' for l in text.split('\n'))

    f = StringIO()
    with redirect_stdout(f):
        exec(text)
        await locals()['__ex']()
    await ctx.send(f.getvalue())

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
        
        out += '\n' + str(sim(out))
        await msg.channel.send(out)
    except asyncio.TimeoutError:
        pass

with open('params.json', 'r') as input:
    params = json.load(input)
    bot.run(params['token'])