import discord
from discord.ext import commands
import subprocess
from io import BytesIO, StringIO
from contextlib import redirect_stdout
import io
import traceback
import textwrap

def setup(bot):
    bot.add_cog(Admin(bot))

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.params = bot.params
    
    async def cog_check(self, ctx):
        return ctx.author.id in self.params['admins']
    
    @commands.command()
    async def cmd(self, ctx, *, text):
        
        task = subprocess.run(text , shell=True, text=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        await ctx.send(f'```{task.stdout}```')
        
    @commands.command()
    async def restart(self, ctx):
        
        task = subprocess.run('pm2 restart mothball' , shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        await ctx.send(f'```{task.stdout}```')

    @commands.command()
    async def py(self, ctx, *, text):
        
        text = text.strip('`')
        if text.startswith('py'): text = text[2:]

        text = f'async def __ex(): ' + ''.join(f'\n {l}' for l in text.split('\n'))

        f = StringIO()
        with redirect_stdout(f):
            exec(text)
            await locals()['__ex']()
        await ctx.send(f.getvalue())

    @commands.group(pass_context=True, invoke_without_command=True)
    async def py2(self, ctx, *, msg):

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

        await self.interpreter(env, msg, ctx)

    async def interpreter(self, env, code, ctx):
        body = self.cleanup_code(code)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

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
                        result = f'```\n{repr(eval(body, env))}\n```'
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
                await ctx.send("```\n```")
    
    @cmd.error
    @restart.error
    @py.error
    async def admin_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction('🤡')
