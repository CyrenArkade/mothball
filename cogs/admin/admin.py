import discord
from discord.ext import commands
import subprocess
from io import StringIO
from contextlib import redirect_stdout
import json

def setup(bot):
    bot.add_cog(Admin(bot))

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('params.json', 'r') as input:
            self.params = json.load(input)
    
    @commands.command()
    async def cmd(self, ctx, *, text):
        if ctx.author.id not in self.params['admins']:
            await ctx.message.add_reaction('🤡')
            return
        
        task = subprocess.run(text , shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        await ctx.send(f'```{task.stdout}```')
        
    @commands.command()
    async def restart(self, ctx):
        if ctx.author.id not in self.params.get('admins', {}):
            await ctx.message.add_reaction('🤡')
            return
        
        task = subprocess.run('pm2 restart bot', shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        await ctx.send(f'```{task.stdout}```')

    @commands.command()
    async def py(self, ctx, *, text):
        if ctx.author.id not in self.params['admins']:
            await ctx.message.add_reaction('🤡')
            return
        
        text = text.strip('`')
        if text.startswith('py'): text = text[2:]

        text = f'async def __ex(): ' + ''.join(f'\n {l}' for l in text.split('\n'))

        f = StringIO()
        with redirect_stdout(f):
            exec(text)
            await locals()['__ex']()
        await ctx.send(f.getvalue())