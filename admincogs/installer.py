import asyncio
import logging
from pathlib import Path
from discord.ext import commands
from utils.discoutils import sendmarkdown

log = logging.getLogger('charfred')


class Installer(commands.Cog):
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
            log.info('"git pull" executed.')
        else:
            log.warning('"git pull" failed!')
            await sendmarkdown(ctx, '< Update failed, command exited with error! >')
            return
        output = stdout.decode().strip()
        log.info(output)
        await sendmarkdown(ctx, f'# Command output:\n{output}')

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

        if self.dir in directory:
            cogrepo = Path(directory)
        else:
            cogrepo = Path(self.dir) / directory

        if not cogrepo.exists():
            log.warning(f'{cogrepo} is not a valid directory.')
            await sendmarkdown(ctx, f'< {cogrepo} is not a valid directory! >')
            return

        if not (cogrepo / '.git').exists():
            log.warning(f'{cogrepo} does not contain a git repository.')
            await sendmarkdown(ctx, f'< {cogrepo} does not contain a git repository! >')
            return

        log.info(f'Updating {directory} cogs...')
        await self._gitcmd(ctx, cogrepo, 'pull')

    @update.command(hidden=True, aliases=['saveforlater'])
    @commands.is_owner()
    async def stash(self, ctx, directory: str=None):
        """Stash local repo changes.
        """

        if directory:
            if self.dir in directory:
                repo = Path(directory)
            else:
                repo = Path(self.dir) / directory

        if not repo.exists():
            log.warning(f'{repo} is not a valid directory.')
            await sendmarkdown(ctx, f'< {repo} is not a valid directory! >')
            return

        if not (repo / '.git').exists():
            log.warning(f'{repo} does not contain a git repository.')
            await sendmarkdown(ctx, f'< {repo} does not contain a git repository! >')
            return

        log.info(f'Stashing changes in {directory}...')
        await self._gitcmd(ctx, repo, 'stash')


def setup(bot):
    bot.add_cog(Installer(bot))
