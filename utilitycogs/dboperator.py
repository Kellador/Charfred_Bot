import logging
from asyncio import wait_for, TimeoutError
from discord.ext import commands

log = logging.getLogger(f'charfred.{__name__}')


class DBOperator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.cfg = bot.cfg
        self.db = None
        self.queryresult = None
        if self.cfg['dbcredentials']:
            self.loop.create_task(self._connect())

    async def _connect(self):
        log.info('Creating database connection pool.')
        self.bot.db = self.db = await asyncpg.create_pool(**self.cfg['dbcredentials'])
        await self._createtables()

    async def _disconnect(self):
        log.info('Closing database connection pool...')
        try:
            await wait_for(self.db.close(), 60, loop=self.loop)
        except TimeoutError:
            log.critical('Database connection pool closing timed out!')
        else:
            log.info('Database connection pool closed.')

    async def _createtables(self):
        async with self.db.acquire() as con:
            for (cog, tablecmd) in self.cfg['dbtables']:
                await con.execute(tablecmd)
                log.info(f'Created table for {cog} using: {tablecmd}')

    def cog_unload(self):
        if self.db:
            self.loop.create_task(self._disconnect())

    @commands.group(invoke_without_command=True, hidden=True,
                    aliases=['db', 'datbase'])
    @commands.is_owner()
    async def database(self, ctx):
        """Database admin commands.

        This returns whether or not a database connection pool
        exists, if no subcommand was given.
        It is not a guarantee for the pool being usable.
        """

        if self.db:
            await ctx.sendmarkdown('> Connection pool available.')
        else:
            await ctx.sendmarkdown('> No connection pool available.')

    @database.command(hidden=True)
    @commands.is_owner()
    async def connect(self, ctx):
        """Creates a connection pool and creates tables.

        Make sure database credentials are saved in the bot
        configs first. You can use the 'database credentials'
        group of commands for this.
        """

        if self.db:
            await ctx.sendmarkdown('> Connection pool already established!')
        else:
            await self._connect()
            await ctx.sendmarkdown('# Connection pool established, '
                                   'pre-configured tables created.')

    @database.command(hidden=True)
    @commands.is_owner()
    async def execute(self, ctx, command, *args):
        """Runs a given sql command,
        use query instead if you want to fetch data.

        A variable number of arguments can be given via $n notation.
        """

        async with self.db.acquire() as con:
            if args:
                stat = await con.execute(command, *args)
            else:
                stat = await con.execute(command)
        log.info(stat)
        await ctx.sendmarkdown(stat)

    @database.command(hidden=True)
    @commands.is_owner()
    async def query(self, ctx, query, *args):
        """Runs a given sql query and caches returned Record list,
        use execute instead if you do not want to fetch any data.

        Cached Record list can be accessed with the `record read`
        subcommand.
        """

        async with self.db.acquire() as con:
            if args:
                rec = await con.fetch(query, args)
            else:
                rec = await con.fetch(query)
        self.queryresult = rec
        log.info(f'# Query cached with {len(rec)} rows!')
        await ctx.sendmarkdown(f'# Query cached with {len(rec)} rows!')

    @database.group(invoke_without_command=False, hidden=True)
    @commands.is_owner()
    async def record(self, ctx):
        pass

    @record.command(hidden=True)
    @commands.is_owner()
    async def read(self, ctx):
        """TODO
        """

        pass

    @database.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def credentials(self, ctx):
        """Database credentials commands.

        Returns the currently saved credentials,
        if no subcommand is given.
        """

        out = []
        for k, v in self.cfg['dbcredentials']:
            out.append(f'{k}: {v}')
        if out:
            out.insert(0, '# Saved credentials:\n\n')
            log.info('\n'.join(out))
            await ctx.sendmarkdown('\n'.join(out))
        else:
            log.info('< No credentials saved! >')
            await ctx.sendmarkdown('< No credentials saved! >')

    @credentials.command(hidden=True)
    @commands.is_owner()
    async def set(self, ctx, *args):
        """Save given credentials to bot config.
        """

        creds = ['database', 'host', 'port', 'user', 'password']
        self.cfg['dbcredentials'] = {}
        for (k, v) in zip(creds, args):
            self.cfg['dbcredentials'][k] = v
        await self.cfg.save()
        log.info('Credentials saved!')
        await ctx.sendmarkdown('> Credentials saved, '
                               'hope you entered them correctly!')


try:
    import asyncpg
except ImportError:
    log.error('Could not import asyncpg, dboperator not loaded!')

    def setup(bot):
        pass
else:
    def setup(bot):
        if 'dbcredentials' not in bot.cfg:
            bot.cfg['dbcredentials'] = {}
            bot.cfg._save()
        if 'dbtables' not in bot.cfg:
            bot.cfg['dbtables'] = {}
            bot.cfg._save()
        bot.add_cog(DBOperator(bot))
