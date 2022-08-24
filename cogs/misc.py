import discord
from discord.ext import commands
from sys import float_info

async def setup(bot):
    await bot.add_cog(Misc(bot))

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['d'])
    async def duration(self, ctx, floor: float = 0.0, ceiling: float = float_info.max, jump_boost: int = 1, inertia: float = 0.005):

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
        
        outstring = f' {ceiling}bc' if ceiling != float_info.max else ''
        
        await ctx.send(f'Duration of a {floor:+.1f}b{outstring} jump:\n\n**{ticks} ticks**')

    async def height(self, ctx, duration: int = 12, ceiling: float = float_info.max, jump_boost: int = 1, inertia: float = 0.005):

        vy = 0.42 + jump_boost * 0.1
        y = 0

        for i in range(duration - 1):
            y = y + vy
            if y > ceiling - 1.8:
                y = ceiling - 1.8
                vy = 0
            vy = (vy - 0.08) * 0.98
            if abs(vy) < inertia:
                vy = 0
            print(i + 2, y)
        
        outstring = f' with a {ceiling}bc' if ceiling != float_info.max else ''
        
        await ctx.send(f'Height after {duration} ticks{outstring}:\n\n **{round(y, 6)}**')