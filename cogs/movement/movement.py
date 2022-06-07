import discord
from discord.ext import commands
import importlib
import cogs.movement.commandmanager as cmdmgr
from cogs.movement.player import Player
import cogs.movement.parsers as parsers
import cogs.movement.functions as functions

def setup(bot):
    bot.add_cog(Movement(bot))

class Movement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_commands = cmdmgr.get_player_commands()
        self.player_command_arguments = cmdmgr.get_player_command_args()
        self.player_arg_aliases = cmdmgr.get_player_arg_aliases()

        self.msg_links = {}

    def sim(self, input, player = None, recordhistory = False):

        if not player:
            player = Player()

        commands = parsers.separate_commands(input)

        commands_args = [single for command in commands for single in parsers.argumentatize_command(command)]

        for command in commands_args:
            command_function = self.player_commands[command[0]]
            dict_args, updates = parsers.dictize_args(command[1], self.player_command_arguments[command_function])

            command_function(player, dict_args)
        
        if recordhistory:
            return player.history_string()
        else:
            return player

    @commands.command(name="s")
    async def simulate(self, ctx, *, text):
        msg = await ctx.send(self.sim(text))
        self.msg_links.update({ctx.message.id: msg.id})

    @commands.command(name='h')
    async def history(self, ctx, *, text):
        msg = await ctx.send(self.sim(text, recordhistory = True))
        self.msg_links.update({ctx.message.id: msg.id})

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.id not in self.msg_links:
            return
        
        newcmd = after.content[3:]
        botmsg = await after.channel.fetch_message(self.msg_links[after.id])
        await botmsg.edit(content=self.sim(newcmd))