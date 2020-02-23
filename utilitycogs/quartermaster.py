import logging
import psutil
from datetime import datetime as dt
from humanize import naturalsize
from discord.ext import commands
from utils.discoutils import permission_node

log = logging.getLogger('charfred')


class ProcessConverter(commands.Converter):
    """Converter to turn an argument into a psutil Process
    instance.

    This tries to find the process in the following order:
    1. Lookup process via pid, if given argument is an integer.
    2. These are checked in sequence for every process:
    2a. Lookup process assuming argument is the name.
    2b. Lookup process assuming argument is commandline substring.
    2c. Lookup process assuming argument is full commandline.
    3. Return None if no matching process was found.
    """

    async def convert(self, ctx, argument):
        try:
            proc = psutil.Process(int(argument))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        except ValueError:
            pass
        else:
            return proc

        proclist = []  # Account for non-unique arguments.
        for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
            if proc.info['name'] == argument:
                proclist.append(proc)
            if proc.info['cmdline']:
                if argument in proc.info['cmdline']:
                    proclist.append(proc)
                if ''.join(proc.info['cmdline']) == argument:
                    proclist.append(proc)

        if proclist:
            return proclist
        else:
            return None


def getProcInfo(proc):
    procinfo = proc.as_dict(attrs=[
        'cpu_percent', 'create_time', 'cmdline',
        'memory_full_info', 'num_threads'
    ])
    return procinfo


def format_info(process, procinfo):
    memory = procinfo['memory_full_info']
    msg = [
        f'# Process Information for PID: {process.info["pid"]}:',
        procinfo['cmdline'],
        '\n',
        'Created on:',
        dt.fromtimestamp(procinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S"),
        '\n',
        f'# CPU Utilization: {procinfo["cpu_percent"]} %',
        f'# Number of Threads: {procinfo["num_threads"]}',
        f'# Memory usage: {naturalsize(memory.rss)}',
        f'# Virtual Memory Size: {naturalsize(memory.vms)}',
        f'# Unique Set Size: {naturalsize(memory.uss)}',
        f'# Swap: {naturalsize(memory.swap)}'
    ]
    msg = '\n'.join(msg)
    return msg


class Quartermaster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop

    @commands.group(invoke_without_command=True)
    @permission_node(f'{__name__}')
    async def profile(self, ctx, process: ProcessConverter):
        """Get CPU and memory usage info on a process.

        The process may be specified by its PID, name, substring of its
        commandline or full commandline.

        If searching via name or commandline returns more than one process
        you will be offered an enumerated list of returned processes to pick
        from.
        """

        if process is None:
            await ctx.sendmarkdown('< No matching process found! >')
        else:
            pass

        procinfo = await self.loop.run_in_executor(None, getProcInfo, process)
        msg = format_info(process, procinfo)
        await ctx.sendmarkdown(msg)

    @profile.command(aliases=['charfred'])
    async def char(self, ctx):
        """Get CPU and memory usage info on Charfred."""

        try:
            process = psutil.Process()
        except psutil.NoSuchProcess:
            log.critical('QM: Well this shouldn\'t be possible...')
            await ctx.sendmarkdown('< Can\'t find my own process! >')
        except psutil.AccessDenied:
            log.warning('QM: Access denied!')
            await ctx.sendmarkdown('< psutil failed with "access denied"! >')
        else:
            procinfo = await self.loop.run_in_executor(None, getProcInfo, process)
            msg = format_info(process, procinfo)
            await ctx.sendmarkdown(msg)


def setup(bot):
    bot.register_nodes([f'{__name__}'])
    bot.add_cog(Quartermaster(bot))
