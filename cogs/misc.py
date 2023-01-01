import discord
from discord.ext import commands
from sys import float_info
from datetime import datetime, timezone
from random import random
import asyncio, typing
import math

async def setup(bot):
    await bot.add_cog(Misc(bot))

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['d'])
    async def duration(self, ctx, floor: float = 0.0, ceiling: float = float_info.max, inertia: float = 0.005, jump_boost: int = 0):

        vy = 0.42 + 0.1 * jump_boost
        y = 0
        ticks = 0

        while y > floor or vy > 0:
            y = y + vy
            if y > ceiling - 1.8:
                y = ceiling - 1.8
                vy = 0
            vy = (vy - 0.08) * 0.98
            if abs(vy) < inertia:
                vy = 0
            ticks += 1

            if ticks > 5000:
                await ctx.send('Simulation limit reached.')
                return
    
        if vy >= 0:
            await ctx.send('Impossible jump height. Too high.')
            return

        ceiling = f' {ceiling}bc' if ceiling != float_info.max else ''
        await ctx.send(f'Duration of a {floor}b{ceiling} jump:\n**{ticks} ticks**')

    @commands.command()
    async def height(self, ctx, duration: int = 12, ceiling: float = float_info.max, inertia: float = 0.005, jump_boost: int = 0):

        vy = 0.42 + jump_boost * 0.1
        y = 0

        for i in range(duration):
            y = y + vy
            if y > ceiling - 1.8:
                y = ceiling - 1.8
                vy = 0
            vy = (vy - 0.08) * 0.98
            if abs(vy) < inertia:
                vy = 0

            if i > 5000:
                await ctx.send('Simulation limit reached.')
                return
        
        outstring = f' with a {ceiling}bc' if ceiling != float_info.max else ''
        
        await ctx.send(f'Height after {duration} ticks{outstring}:\n **{round(y, 6)}**')

    @commands.command()
    async def blip(self, ctx, blips: int = 1, blip_height: float = 0.0625, init_height: float = None, init_vy: float = None, inertia: float = 0.005, jump_boost: int = 0):
        if init_height is None:
            init_height = blip_height
        if init_vy is None:
            init_vy = 0.42 + 0.1 * jump_boost
        
        blips_done = 0
        vy = init_vy
        y = init_height
        jump_ys = [init_height]
        max_heights = []
        vy_prev = 0
        i = 0

        while blips_done < blips or vy > 0:

            y += vy
            vy = (vy - 0.08) * 0.98

            if y + vy < blip_height:

                if y + vy > 0:
                    max_heights.append('Fail')
                    jump_ys.append(y + vy)
                    break
                
                jump_ys.append(y)
                vy = 0.42
                blips_done += 1
            
            if abs(vy) < inertia:
                vy = 0

            if vy_prev > 0 and vy <= 0:
                max_heights.append(y)

            if i > 5000:
                await ctx.send('Simulation limit reached.')
                return

            vy_prev = vy
            i += 1

        out = '\n'.join([
            f'Blips: {blips_done}',
            f'Blip height: {round(blip_height, 6)}',
            f'Initial y: {round(init_height, 6)}',
            f'Initial vy: {round(init_vy, 6)}',
            f'```Blip | Jumped From | Max Height'
        ])

        num_col_width = len(str(blips))
        for i in range(0, len(jump_ys)):
            num = f'{i:0{num_col_width}}'.ljust(4)
            jumped_from = f'{jump_ys[i]:<11.6f}'
            max_height = f'{max_heights[i]:<10.6f}' if type(max_heights[i]) == float else max_heights[i]
            out += (f'\n{num} | {jumped_from} | {max_height}')
        out += '```'
        
        await ctx.send(out)

    @commands.command(aliases = ['ji'])
    async def jumpinfo(self, ctx, x: float, z: float = 0.0):

        format = lambda x, p = 6: round(x, p)
        if abs(x) < 0.6:
            dx = 0.0
        else:
            dx = x - math.copysign(0.6, x)
        if abs(z) < 0.6:
            dz = 0.0
        else:
            dz = z - math.copysign(0.6, z)
        
        if dx == 0.0 and dz == 0.0:
            await ctx.send('That\'s not a jump!')
            return
        elif dx == 0.0 or dz == 0.0:
            outstring = f'**{format(max(x, z))}b** jump -> **{format(max(dx, dz))}** distance'
            await ctx.send(outstring)
            return

        distance = math.sqrt(dx**2 + dz**2)
        angle = math.degrees(math.atan(dz/dx))

        lines = [
            f'A **{format(x)}b** by **{format(z)}b** block jump:',
            f'Dimensions: **{format(dx)}** by **{format(dz)}**',
            f'Distance: **{format(distance)}** distance -> **{format(distance+0.6)}b** jump',
            f'Optimal Angle: **{angle:.3f}°**'
        ]

        await ctx.send('\n'.join(lines))

    @commands.command(aliases=['q'])
    @commands.cooldown(3, 60, type=commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    async def quote(self, ctx, msg: typing.Union[discord.Message, str] = None):
        if msg is None:
            oldest = 1609488000
            target = datetime.fromtimestamp(oldest + random() * (datetime.now(timezone.utc).timestamp() - oldest), tz=timezone.utc)

            tasks = []
            messages = []
            for channel in ctx.guild.channels:
                tasks.append(self.asyncsearch(ctx, channel, target, messages))
            await asyncio.gather(*tasks)

            messages = filter(self.quote_filter, messages)
            msg = min(messages, key=lambda x: abs(target - x.created_at))

        if self.is_poll(msg):
            src_em = msg.embeds[0]
            em = discord.Embed(description=src_em.description, timestamp=msg.created_at, color=src_em.color)
            em.set_author(name=src_em.author.name, icon_url=src_em.author.icon_url)
            em.description += f"\n\n[Jump to poll]({msg.jump_url})"
            em.set_footer(text="#" + msg.channel.name)
        else:
            em = discord.Embed(description=msg.content, timestamp=msg.created_at, color=msg.author.color)
            em.set_author(name=msg.author.display_name, icon_url=msg.author.display_avatar.url)
            em.description += f"\n\n[Jump to message]({msg.jump_url})"
            em.set_footer(text="#" + msg.channel.name)

        await ctx.send(embed=em)

    @quote.error
    async def err(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('wait bitch')
        else:
            raise error

    def quote_filter(self, msg):
        if msg.author.bot:
            if not self.is_poll(msg):
                return False
        if any([msg.content.lower().startswith(x) for x in ('m!', 'p!', '^', '$', '<@520282851925688321>')]):
            return False
        if len(msg.content) == 1:
            return False
        return True
    
    def is_poll(self, msg):
        return all([
            msg.channel.id == 794109972609761310,
            msg.author.id == 988081422839480351,
            len(msg.embeds) == 1 and msg.embeds[0].title.startswith('Poll')
        ])

    async def asyncsearch(self, ctx, channel, target, list):
        if not isinstance(channel, discord.TextChannel) or not channel.permissions_for(ctx.guild.me).read_message_history:
            return
        msg = [message async for message in channel.history(limit=3, around=target)]
        list.extend(msg)