import aiomysql
import logging

log = logging.getLogger('charfred')


class MySQLHelper():
    """Helper class to handle database connections and transactions.
    Supports MySQL via aiomysql.
    """
    def __init__(self, bot, **opts):
        self.bot = bot
        self.loop = bot.loop
        self.db = opts.pop('database', None)
        self.host = opts.pop('host', None)
        self.port = opts.pop('port', None)
        self.user = opts.pop('user', None)
        self.pw = opts.pop('password', None)
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.pw,
            db=self.db,
            loop=self.loop
        )
        log.info(f'DBMS connected to {self.db}.')

    async def disconnect(self):
        self.pool.close()
        await self.pool.wait_closed()
        log.info('DBMS-adapter disconnected.')

    def _convertplaceholders(self, query: str) -> str:
        return query.replace('?', '%s')

    async def execute(self, command, args=None, commit=True):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if isinstance(command, str):
                    command = self._convertplaceholders(command)
                    if args is None:
                        await cursor.execute(command)
                    else:
                        await cursor.execute(command, args)
                else:
                    for cmd in command:
                        cmd = self._convertplaceholders(cmd)
                        await cursor.execute(cmd)
                if commit:
                    await connection.commit()
                log.info(cursor.description)
                return cursor

    async def executemany(self, command: str, args, commit=True):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                command = self._convertplaceholders(command)
                await cursor.executemany(command, args)
                if commit:
                    await connection.commit()
                log.info(cursor.description)
                return cursor

    async def fetch(self, query: str, args=None, amount=None):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                query = self._convertplaceholders(query)
                if args is None:
                    await cursor.execute(query, commit=False)
                else:
                    await cursor.execute(query, args, commit=False)
                if amount is None:
                    res = await cursor.fetchall()
                elif amount == 1:
                    res = await cursor.fetchone()
                else:
                    res = await cursor.fetchmany(amount)
                log.info(cursor.description)
                return res

    async def fetchrow(self, query: str, args=None):
        res = await self.fetch(query, args, 1)
        return res

    async def fetchall(self, query: str, args=None):
        res = await self.fetch(query, args)
        return res
