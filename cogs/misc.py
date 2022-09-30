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

        def filt(msg):
            if msg.author.bot:
                return False
            if any([msg.content.lower().startswith(x) for x in ('m!', '^', '$', '<@520282851925688321>')]):
                return False
            if len(msg.content) == 1:
                return False
            return True
        bot._filter = filt
    
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
        
        outstring = f' with a {ceiling}bc' if ceiling != float_info.max else ''
        
        await ctx.send(f'Height after {duration} ticks{outstring}:\n **{round(y, 6)}**')

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

            messages = filter(self.bot._filter, messages)
            msg = min(messages, key=lambda x: abs(target - x.created_at))

        em = discord.Embed(description=f"{msg.content}", timestamp=msg.created_at, color=msg.author.color)
        em.set_author(name=msg.author.display_name, icon_url=msg.author.display_avatar.url)
        em.description += f"\n\n[Jump to message]({msg.jump_url})"
        em.set_footer(text="#" + msg.channel.name)

        await ctx.send(embed=em)

    @quote.error
    async def err(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('wait bitch')
    
    async def asyncsearch(self, ctx, channel, target, list):
        if not isinstance(channel, discord.TextChannel) or not channel.permissions_for(ctx.guild.me).read_message_history:
            return
        msg = [message async for message in channel.history(limit=3, around=target)]
        list.extend(msg)