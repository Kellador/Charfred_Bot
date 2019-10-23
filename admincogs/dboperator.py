import logging
from discord.ext import commands
from utils.discoutils import sendmarkdown

log = logging.getLogger('charfred')


class DBOperator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.cfg = bot.cfg
        self.db = None

    def _load_dbmsadapter(self, dbms):
        if dbms == 'sqlite':
            from utils.sqlitehelper import SQLiteHelper
            try:
                self.db = SQLiteHelper(self.bot, db=self.cfg['dbcredentials']['db'])
            except KeyError:
                log.error('Database credentials not found!')
                log.error('Database adapter could not be loaded.')
            else:
                self.loop.create_task(self.db.connect())
        elif dbms == 'mysql':
            from utils.mysqlhelper import MySQLHelper
            try:
                dbcfg = self.cfg['dbcredentials']
                self.db = MySQLHelper(
                    self.bot,
                    db=dbcfg['db'],
                    host=dbcfg['host'],
                    port=dbcfg['port'],
                    user=dbcfg['user'],
                    pw=dbcfg['password']
                )
            except KeyError:
                log.error('Database credentials not found!')
                log.error('Database adapter could not be loaded.')
            else:
                self.bot.db = self.db
                self.loop.create_task(self.db.connect())
        else:
            log.warning('Specified DBMS not supported!')

    @commands.group(invoke_without_command=True, hidden=True,
                    aliases=['db', 'datbase'])
    @commands.is_owner()
    async def database(self, ctx):
        """Database admin commands.

        This returns whether or not a DBMS adapter is loaded,
        if no subcommand was given.
        """

        if self.db:
            log.info(f'{self.db.__name__} database adapter is currently loaded.')
            await sendmarkdown(ctx, f'# {self.db.__name__} adapter is currently loaded.')
        else:
            log.info('No database adapter loaded.')
            await sendmarkdown(ctx, '< No database adapter loaded. >')

    @database.command(hidden=True)
    @commands.is_owner()
    async def connect(self, ctx, *args):
        """Attempts to load the database adapter and connect to the database.

        Required arguments are, in order:
        DBMS to use, database name
        (also, if using MySQL):
        host, port, user and password
        """
        creds = ['dbms', 'db', 'host', 'port', 'user', 'password']
        for (key, value) in zip(creds, args):
            self.cfg['dbcredentials'][key] = value
        await self.cfg.save()

        if self.db is None and args is None:
            log.warning('No DBMS specified and none configured, abort!')
            await sendmarkdown(ctx, '< No DBMS specified or preconfigured. >')
            return
        elif self.db is None:
            self._load_dbmsadapter(args[0])
        else:
            log.warning('Database adapter already loaded.')
            await sendmarkdown(ctx, '> Database adapter already loaded.')
        await self.db.connect()
        log.info('Database adapter loaded and connected.')
        await sendmarkdown(ctx, '# Database adapter loaded and connected.')

    @database.command(hidden=True)
    @commands.is_owner()
    async def execute(self, ctx, command, *args):
        """Runs a given sql command, no return information,
        use query instead if you want to fetch data.

        A variable number of arguments can be given.
        Please use qmark style (question marks) for your
        variable placeholders.
        """

        if self.db is None or isinstance(self.db, str):
            log.warning('No database adapter loaded, abort!')
            await sendmarkdown(ctx, '< No database adapter laoded, abort command! >')
            return

        log.info(f'Executing command: {command}')
        if args:
            await self.db.execute(command, args)
        else:
            await self.db.execute(command)


def setup(bot):
    if 'dbcredentials' not in bot.cfg:
        bot.cfg['dbcredentials'] = {
            'db': None,
            'host': None,
            'port': None,
            'user': None,
            'password': None
        }
        bot.cfg._save()
    bot.add_cog(DBOperator(bot))
