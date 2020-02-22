import asyncio
import logging
from pathlib import Path
from discord.ext import commands

log = logging.getLogger('charfred')


class GitOperator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dir = bot.dir
        self.loop = bot.loop
        self.cfg = bot.cfg

    async def _gitcmd(self, ctx, path, cmd):
        proc = await asyncio.create_subprocess_exec(
            'git',
            '-C',
            f'{path}',
            cmd,
            loop=self.loop,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            log.info(f'"git {cmd}" executed.')
        else:
            log.warning(f'"git {cmd}" failed!')
            await ctx.sendmarkdown('< Command failed, exited with error! >')
            return
        output = stdout.decode().strip()
        log.info(output)
        await ctx.sendmarkdown(f'# Command output:\n{output}')

    async def _validate(self, repo, ctx=None):
        if not repo.exists():
            log.warning(f'{repo} is not a valid directory.')
            if ctx:
                await ctx.sendmarkdown(f'< {repo} is not a valid directory! >')
            return False

        if not (repo / '.git').exists():
            log.warning(f'{repo} does not contain a git repository.')
            if ctx:
                await ctx.sendmarkdown(f'< {repo} does not contain a git repository! >')
            return False

        return True

    def _convertfullsubpath(self, directory):
        if self.dir in directory:
            repo = Path(directory)
        else:
            repo = Path(self.dir) / directory
        return repo

    @commands.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def update(self, ctx):
        """Updates Charfred.

        Really it just runs git pull on the base repo.
        """

        log.info('Updating Charfred...')
        await self._gitcmd(ctx, self.dir, 'pull')

    @update.command(hidden=True, name='cogs', aliases=['extension'])
    @commands.is_owner()
    async def updatecogs(self, ctx, directory):
        """Updates cogs, given the directory name.

        The given directory name can either be the full path to the cog repo,
        or just the path from the base Charfred repo to the cog repo, so basically:
        Full path to cog repo - Path to Charfred repo, since cog repos always
        need to be subdirectories of the base repo.
        """

        repo = self._convertfullsubpath(directory)

        valid = await self._validate(repo, ctx)
        if valid:
            log.info(f'Updating {directory} cogs...')
            await self._gitcmd(ctx, repo, 'pull')

    @update.command(hidden=True, aliases=['stashlocal'])
    @commands.is_owner()
    async def stash(self, ctx, directory: str=None):
        """Stash local repo changes.
        """

        if directory:
            repo = self._convertfullsubpath(directory)
        else:
            repo = Path(directory)

        valid = await self._validate(repo, ctx)
        if valid:
            log.info(f'Stashing changes in {directory}...')
            await self._gitcmd(ctx, repo, 'stash')

    @commands.group(hidden=True)
    @commands.is_owner()
    async def git(self, ctx):
        """Git command group.
        """

        pass


def setup(bot):
    bot.add_cog(GitOperator(bot))
