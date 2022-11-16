import discord
from discord.ext import commands
import subprocess
from io import BytesIO, StringIO
from contextlib import redirect_stdout
import traceback
import textwrap
import json

async def setup(bot):
    await bot.add_cog(Admin(bot))

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.params = bot.params
        self._last_result = None
    
    async def cog_check(self, ctx):
        return ctx.author.id in self.params['admins']
    
    @commands.command()
    async def cmd(self, ctx: commands.Context, *, text: str):
        
        task = subprocess.run(text , shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        await ctx.send(f'```{task.stdout}```')
        
    @commands.command()
    async def restart(self, ctx: commands.Context, text: str = ''):
        
        if text == 'u':
            await ctx.send('Running `git pull`...')
            task = subprocess.run('git pull' , shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            await ctx.send(f'```{task.stdout}```')

        msg = await ctx.send('Restarting...')
        with open('restart.json', 'w') as restart:
            restart.write(json.dumps({'channel': msg.channel.id, 'msg': msg.id}))
        
        await self.bot.close()

    @commands.command(aliases=[';'])
    async def py(self, ctx: commands.Context, *, text: str):

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'server': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }
        env.update(globals())

        await self.interpreter(env, text, ctx)

    async def interpreter(self, env, code: str, ctx: commands.Context):
        
        code = code.strip('`')
        if code.startswith('py'): code = code[2:]

        stdout = StringIO()

        to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```\n{e.__class__.__name__}: {e}```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            out = stdout.getvalue()
            await ctx.send(f'```\n{out}{traceback.format_exc()}```')
        else:
            out = stdout.getvalue()

            result = None
            if ret is None:
                if out:
                    result = f'```\n{out}```'
                else:
                    try:
                        result = f'```\n{repr(eval(code, env))}\n```'
                    except:
                        pass
            else:
                self._last_result = ret
                result = f'```\n{out}{ret}\n```'

            if result:
                if len(str(result)) > 1950:
                    buffer = BytesIO(str(result.strip("```")).encode("utf8"))
                    await ctx.send(content="Uploaded output to file since output was too long.", file=discord.File(fp=buffer, filename='output.txt'))
                    return

                else:
                    await ctx.send(result)
            else:
                await ctx.message.add_reaction('\U0001f44d')
    
    @cmd.error
    @restart.error
    @py.error
    async def admin_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction('🤡')
