import discord
from discord.ext import commands
import commandmanager as cmdmgr
import parsers
import movement
from player import Player
import json
import asyncio

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix=';', intents=intents)

player_commands = cmdmgr.get_player_commands()
player_command_arguments = cmdmgr.get_player_command_args()
player_arg_aliases = cmdmgr.get_player_arg_aliases()

def sim(input, player = Player()):

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
    await ctx.send(sim(text))


with open('params.json', 'r') as input:
    params = json.load(input)
    bot.run(params['token'])