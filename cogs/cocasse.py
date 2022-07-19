import discord
from discord.ext import commands
import re
import asyncio

async def setup(bot):
    await bot.add_cog(Cocasse(bot))

class Cocasse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener('on_message')
    async def on_message(self, msg: discord.Message):
        if re.search(r'\[(\'.*?\'(, )?)*?\]', msg.content) and msg.author.id == 982688359069659146:
            await self.cocasse(msg)
        
        await self.bot.process_commands(msg)

    async def cocasse(self, msg: discord.Message):
        await msg.add_reaction('🔍')

        def check(reaction, user):
            return reaction.message.id == msg.id and str(reaction.emoji) == '🔍' and not user.bot

        try:
            await self.bot.wait_for('reaction_add', timeout=60, check=check)

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
            
            movement = self.bot.get_cog('Movement')
            out += '\n' + str(movement.sim(out))
            await msg.channel.send(out)
        except asyncio.TimeoutError:
            pass
