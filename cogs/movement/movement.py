import discord
from discord.ext import commands
import importlib
import cogs.movement.commandmanager as cmdmgr
from cogs.movement.player import Player
import cogs.movement.parsers as parsers
import cogs.movement.functions as functions
from cogs.movement.simnode import SimNode
import asyncio
from concurrent.futures import ProcessPoolExecutor

def setup(bot):
    bot.executor = ProcessPoolExecutor()
    bot.add_cog(Movement(bot))

class Movement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_commands = cmdmgr.get_player_commands()
        self.player_command_arguments = cmdmgr.get_player_command_args()
        self.player_arg_aliases = cmdmgr.get_player_arg_aliases()

        self.msg_links = {}

    def sim(self, input, player = None):

        if not player:
            player = Player()

        commands = parsers.separate_commands(input)

        commands_args = [single for command in commands for single in parsers.argumentatize_command(command)]

        for command in commands_args:
            reverse = command[0].startswith('-')
            if reverse:
                command[0] = command[0][1:]
            
            command_function = self.player_commands[command[0]]

            dict_args, updates = parsers.dictize_args(command[1], self.player_command_arguments[command_function])
            if reverse:
                dict_args.update({'reverse': True})

            command_function(player, dict_args)
        
        return player
    
    async def genericsim(self, ctx, input, continuation = None, edit = None, history = False):
        if continuation:
            parent = self.msg_links[continuation]
            player = parent.player.softcopy()
        else:
            player = Player()
        
        try:
            task = asyncio.to_thread(self.sim, input, player)
            player = await asyncio.wait_for(task, timeout=self.bot.params['sim_timeout'])
        except asyncio.TimeoutError:
            if edit:
                await edit.botmsg.edit(content='Simulation timed out.')
            else:
                await ctx.send('Simulation timed out.')
            return

        if history:
            results = player.history_string()
        else:
            results = str(player)
        
        player.clearlogs()
        
        if edit:
            await edit.botmsg.edit(content=results)
            self.msg_links[edit.msgid].player = player.softcopy()
        else:
            botmsg = await ctx.channel.send(results)
            node = SimNode(ctx.message.id, botmsg, player)
            self.msg_links.update({ctx.message.id: node})
            if continuation:
                parent.children.append(ctx.message.id)
    
    async def cog_check(self, ctx):
        if ctx.guild == 793172726767550484 and ctx.channel.id not in (793172726767550487, 794029948972826704, 880636448678764544):
            return False
        return True

    @commands.command(aliases=['sim', 's'])
    async def simulate(self, ctx, *, text):
        await self.genericsim(ctx, text)

    @commands.command(aliases=['his', 'h'])
    async def history(self, ctx, *, text):
        await self.genericsim(ctx, text, history=True)
    
    @commands.command(aliases=['t'])
    async def then(self, ctx, *, text):
        if ctx.message.reference is None or ctx.message.reference.message_id not in self.msg_links:
            await ctx.send("You must reply to a simulation command")
            return
        
        srcid = ctx.message.reference.message_id
        await self.genericsim(ctx, text, continuation = srcid)
    
    @commands.command(aliases=['th'])
    async def thenh(self, ctx, *, text):
        if ctx.message.reference is None or ctx.message.reference.message_id not in self.msg_links:
            await ctx.send("You must reply to a simulation command")
            return
        
        srcid = ctx.message.reference.message_id
        await self.genericsim(ctx, text, continuation = srcid, history = True)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.id not in self.msg_links:
            return
        
        await self.editdown(after.channel, after)
    
    async def editdown(self, channel, msg):
        text = msg.content
        history = any(text.startswith(cmd) for cmd in (';history ', ';his ', ';h ', ';thenh ', ';th '))
        text = text[text.index(' ') + 1:]

        if msg.reference:
            continuation = msg.reference.message_id
        else:
            continuation = None

        await self.genericsim(channel, text, history = history, edit = self.msg_links[msg.id], continuation = continuation)

        for childid in self.msg_links[msg.id].children:
            child = await channel.fetch_message(childid)
            await self.editdown(channel, child)