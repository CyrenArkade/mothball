import discord
from discord.ext import commands
from cogs.movement.player import Player
from cogs.movement.parsers import execute_string
from cogs.movement.utils import SimError, SimNode
import asyncio
from io import BytesIO

async def setup(bot):
    bot.env = {}

    await bot.add_cog(Movement(bot))

class Movement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.msg_links = {}

    def sim(self, input: str, player: Player):

        execute_string(input, [self.bot.env], player)
        
        return player
    
    async def genericsim(self, ctx: commands.Context, input, continuation = None, edit = None, history = False):
        if continuation:
            parent = self.msg_links[continuation]
            player = parent.player.softcopy()
        else:
            player = Player()
        
        errored = True
        try:
            task = asyncio.to_thread(self.sim, input, player)
            player = await asyncio.wait_for(task, timeout=self.bot.params['sim_timeout'])

            if history:
                results = player.history_string()
            else:
                results = str(player)

            errored = False

        except asyncio.TimeoutError:
            results = 'Simulation timed out.'
        except SimError as e:
            results = str(e)
        except Exception as e:
            if self.bot.params['is_dev']:
                raise e
            results = 'Something went wrong.'

        if player.macro:
            buffer = BytesIO(player.macro_csv().encode('utf8'))
            kwargs = {'content': results, 'file': discord.File(fp=buffer, filename=f'{player.macro}.csv')}
        elif len(results) > 1990:
            buffer = BytesIO(results.encode('utf8'))
            kwargs = {'content': 'Uploaded output to file since output was too long.', 'file': discord.File(fp=buffer, filename='output.txt')}
        else:
            kwargs = {'content': results}

        if errored:
            kwargs.pop('file', None)
        
        if edit:
            if 'file' in kwargs:
                kwargs['content'] = 'Cannot edit attachments.\n' + kwargs['content']
                kwargs.pop('file', None)
            await edit.botmsg.edit(**kwargs)
            self.msg_links[edit.msgid].player = player.softcopy()
        else:
            botmsg = await ctx.channel.send(**kwargs)

            node = SimNode(ctx.message.id, botmsg, player)
            self.msg_links[ctx.message.id] = node
            if continuation:
                parent.children.append(ctx.message.id)
        
        player.clearlogs()

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
        for i in range(len(text)):
            if text[i].isspace():
                text = text[i+1:]
                break

        if msg.reference:
            continuation = msg.reference.message_id
        else:
            continuation = None

        await self.genericsim(channel, text, history = history, edit = self.msg_links[msg.id], continuation = continuation)

        for childid in self.msg_links[msg.id].children:
            child = await channel.fetch_message(childid)
            await self.editdown(channel, child)