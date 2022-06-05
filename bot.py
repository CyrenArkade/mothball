import discord
from discord.ext import commands
import commandmanager as cmdmgr
import parsers
from player import Player
import json
import subprocess
import movement
import shlex
import time

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix=';', intents=intents, help_command=None)

player_commands = cmdmgr.get_player_commands()
player_command_arguments = cmdmgr.get_player_command_args()
player_arg_aliases = cmdmgr.get_player_arg_aliases()
params = {}

msg_links = {}

def sim(input, player = None):

    if not player:
        player = Player()

    commands = parsers.separate_commands(input)
    print('Step one:', commands)

    commands_args = [single for command in commands for single in parsers.argumentatize_command(command)]
    print('Step two:', commands_args)
         

    for command in commands_args:
        command_function = player_commands[command[0]]
        dict_args, updates = parsers.dictize_args(command[1], player_command_arguments[command_function])

        command_function(player, dict_args)
    
    return (player)

@bot.command(name="s")
async def simulate(ctx, *, text):
    msg = await ctx.send(sim(text))
    msg_links.update({ctx.message.id: msg.id})

@bot.event
async def on_message_edit(before, after):
    if after.id not in msg_links:
        return
    if not after.content.startswith(';s '):
        return
    
    newcmd = after.content[3:]
    botmsg = await after.channel.fetch_message(msg_links[after.id])
    await botmsg.edit(content=sim(newcmd))

@bot.command()
async def gitpull(ctx):
    if ctx.author.id not in params['admins']:
        return
    
    task = subprocess.run(['pm2', 'restart', 'bot'], shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    await ctx.send(task.stdout)

@bot.command()
async def cmd(ctx, *, text):
    if ctx.author.id not in params['admins']:
        return
    
    task = subprocess.run(shlex.split(text), shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    await ctx.send(task.stdout)
    

@bot.command()
async def restart(ctx):
    if ctx.author.id not in params.get('admins', {}):
        return
    
    task = subprocess.run(['pm2', 'restart', 'bot'], shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    await ctx.send(task.stdout)

@bot.command()
async def help(ctx):
    await ctx.send('Read the readme!\nhttps://github.com/CyrenArkade/mothball')

with open('params.json', 'r') as input:
    params = json.load(input)
    bot.run(params['token'])