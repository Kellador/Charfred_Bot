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
                if ' '.join(proc.info['cmdline']) == argument:
                    proclist.append(proc)

        if proclist:
            return proclist
        else:
            return None


def getProcInfo(proc):
    procinfo = {}
    high = 0.0
    for _ in range(50):
        point = proc.cpu_percent(interval=0.1)
        if point > high:
            high = point
    procinfo['cpu_percent'] = high
    with proc.oneshot():
        procinfo['create_time'] = proc.create_time()
        procinfo['cmdline'] = proc.cmdline()
        procinfo['memory_full_info'] = proc.memory_full_info()
        procinfo['num_threads'] = proc.num_threads()
    return procinfo


def format_info(process, procinfo):
    memory = procinfo['memory_full_info']
    msg = [
        f'# Process Information for PID: {process.pid}:',
        ' '.join(procinfo['cmdline']),
        '',
        'Created on:',
        dt.fromtimestamp(procinfo['create_time']).strftime("%Y-%m-%d %H:%M:%S"),
        '',
        f'# CPU Utilization: {procinfo["cpu_percent"]} % (highest value over 5 seconds)',
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

    @commands.group(aliases=['quartermaster'])
    @permission_node(f'{__name__}')
    async def qm(self, ctx):
        """System resource information commands."""

        pass

    @qm.command(invoke_without_command=True)
    async def profile(self, ctx, process: ProcessConverter):
        """Get CPU and memory usage info on a process.

        The process may be specified by its PID, name, substring of its
        commandline or full commandline.

        Note: Screen processes are filtered out.

        If searching via name or commandline returns more than one process
        you will be offered an enumerated list of returned processes to pick
        from.
        """

        if process is None:
            await ctx.sendmarkdown('< No matching process found! >')
            return
        else:
            pass

        process = [proc for proc in process if not (proc.name() == 'screen')]

        if not process:
            await ctx.sendmarkdown('< No matching non-screen processes found! >')
            return

        if len(process) > 1:
            listing = [
                f'{num}: PID={proc.pid}, name={proc.name()}'
                for num, proc in enumerate(process)
            ]
            reply, _, _ = await ctx.promptinput(
                '< Multiple matching processes found! >\n\n' +
                '\n'.join(listing) +
                '\n\n< Please select which one to profile by replying with the '
                'number listed next to the process that best matches the one '
                'you are looking for. >'
            )

            if reply:
                try:
                    process = process[int(reply)]
                except (KeyError, ValueError):
                    await ctx.sendmarkdown('< Invalid choice! >')
                    return
            else:
                return
        else:
            process = process[0]

        tmpmsg = await ctx.sendmarkdown('> Profiling...')
        procinfo = await self.loop.run_in_executor(None, getProcInfo, process)
        msg = format_info(process, procinfo)
        await tmpmsg.delete()
        await ctx.sendmarkdown(msg)

    @qm.command(aliases=['chartop'])
    async def charprofile(self, ctx):
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

            tmpmsg = await ctx.sendmarkdown('> Profiling...')
            procinfo = await self.loop.run_in_executor(None, getProcInfo, process)
            msg = format_info(process, procinfo)
            await tmpmsg.delete()
            await ctx.sendmarkdown(msg)

    @qm.command(aliases=['du'])
    async def diskusage(self, ctx):
        """Get disk usage information.

        Results are color coded based on use percentage:
        orange = >80%
        white = >20%
        grey = <=20%
        """

        msg = ['# Disk Usage:', '> Device        Total     Used     Free     % Mount']
        for dev in psutil.disk_partitions():
            use = psutil.disk_usage(dev.mountpoint)
            if int(use.percent) > 80:
                prefix = '< '
                suffix = ' >'
            elif int(use.percent) < 20:
                prefix = '> '
                suffix = ''
            else:
                prefix = '  '
                suffix = ''
            msg.append(
                f'{prefix}{dev.device:10} {naturalsize(use.total):>8} {naturalsize(use.used):>8}'
                f' {naturalsize(use.free):>8} {int(use.percent):>4}% {dev.mountpoint}{suffix}'
            )
        await ctx.sendmarkdown('\n'.join(msg))

    @qm.command(aliases=['mem'])
    async def meminfo(self, ctx):
        """Get memory usage information."""

        mem = psutil.virtual_memory()
        swp = psutil.swap_memory()
        if mem.percent > 80.0:
            prefix = '< '
            suffix = ' >'
        else:
            prefix = '  '
            suffix = ''
        if swp.percent > 80.0:
            prefixs = '< '
            suffixs = ' >'
        else:
            prefixs = '  '
            suffixs = ''
        msg = [
            '# Memory Usage:',
            '>     Total   Avail.      %',
            f'{prefix} {naturalsize(mem.total):>8} {naturalsize(mem.available):>8}'
            f' {mem.percent:>5}%{suffix}',
            '\n# Swap:',
            '>    Total     Used     %',
            f'{prefixs}{naturalsize(swp.total):>8} {naturalsize(swp.used):>8} '
            f'{swp.percent:>5}%{suffixs}'
        ]
        await ctx.sendmarkdown('\n'.join(msg))


def setup(bot):
    bot.register_nodes([f'{__name__}'])
    bot.add_cog(Quartermaster(bot))
