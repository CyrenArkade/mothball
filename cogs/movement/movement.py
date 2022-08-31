import discord
from discord.ext import commands
from cogs.movement.functions import commands_by_name
from cogs.movement.player import Player
import cogs.movement.parsers as parsers
from cogs.movement.util import SimError, SimNode
import asyncio
from io import BytesIO
import logging

async def setup(bot):
    await bot.add_cog(Movement(bot))

class Movement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.msg_links = {}

    def sim(self, input: str, player: Player = None):

        if not player:
            player = Player()

        commands = parsers.separate_commands(input)

        commands_args = [single for command in commands for single in parsers.argumentatize_command(command)]

        command: str
        args: list[str]
        for command, args in commands_args:
            reverse = command.startswith('-')
            if reverse:
                command = command[1:]
            
            try:
                command_function = commands_by_name[command]
            except:
                raise SimError(f'Command `{command}` not found')

            dict_args = parsers.dictize_args(command_function, args)
            if reverse:
                dict_args.update({'reverse': True})

            command_function(player, dict_args)
        
        return player
    
    async def genericsim(self, ctx: commands.Context, input, continuation = None, edit = None, history = False):
        if continuation:
            parent = self.msg_links[continuation]
            player = parent.player.softcopy()
        else:
            player = Player()
        
        try:
            task = asyncio.to_thread(self.sim, input, player)
            player = await asyncio.wait_for(task, timeout=self.bot.params['sim_timeout'])

            if history:
                results = player.history_string()
            else:
                results = str(player)

        except asyncio.TimeoutError:
            results = 'Simulation timed out.'
        except SimError as e:
            results = str(e)
        except:
            results = 'Something went wrong.'
        
        player.clearlogs()
        
        if edit:

            if len(results) > 1990:
                buffer = BytesIO(results.encode("utf8"))
                await edit.botmsg.edit(content="Uploaded output to file since output was too long.", file=discord.File(fp=buffer, filename='output.txt'))
            else:
                await edit.botmsg.edit(content=results)

            await edit.botmsg.edit(content=results)
            self.msg_links[edit.msgid].player = player.softcopy()
        else:

            if len(results) > 1990:
                buffer = BytesIO(results[3:-3].encode("utf8"))
                botmsg = await ctx.channel.send(content="Uploaded output to file since output was too long.", file=discord.File(fp=buffer, filename='output.txt'))
            else:
                botmsg = await ctx.channel.send(results)

            node = SimNode(ctx.message.id, botmsg, player)
            self.msg_links.update({ctx.message.id: node})
            if continuation:
                parent.children.append(ctx.message.id)
    
    async def cog_check(self, ctx: commands.Context):
        if ctx.guild.id == 793172726767550484 and ctx.channel.id not in (793172726767550487, 794029948972826704, 880636448678764544):
            return False
        return True

    @commands.command(aliases=['sim', 's'])
    async def simulate(self, ctx: commands.Context, *, text: str):
        await self.genericsim(ctx, text)

    @commands.command(aliases=['his', 'h'])
    async def history(self, ctx: commands.Context, *, text: str):
        await self.genericsim(ctx, text, history=True)
    
    @commands.command(aliases=['t'])
    async def then(self, ctx: commands.Context, *, text: str):
        if ctx.message.reference is None or ctx.message.reference.message_id not in self.msg_links:
            await ctx.send("You must reply to a simulation command")
            return
        
        srcid = ctx.message.reference.message_id
        await self.genericsim(ctx, text, continuation = srcid)
    
    @commands.command(aliases=['th'])
    async def thenh(self, ctx: commands.Context, *, text: str):
        if ctx.message.reference is None or ctx.message.reference.message_id not in self.msg_links:
            await ctx.send("You must reply to a simulation command")
            return
        
        srcid = ctx.message.reference.message_id
        await self.genericsim(ctx, text, continuation = srcid, history = True)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
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