import aiomysql
import logging

log = logging.getLogger('charfred')


class DBHelper():
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

    async def disconnect(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def execute(self, command, args=None, many=False):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if many:
                    func = cursor.executemany
                else:
                    func = cursor.execute
                if args is None:
                    await func(command)
                else:
                    await func(command, args)
                log.info(cursor.description)

    async def executemany(self, command, args):
        await self.execute(command, args, True)

    async def fetch(self, query, args=None, amount=None):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                if args is None:
                    await cursor.execute(query)
                else:
                    await cursor.execute(query, args)
                if amount is None:
                    res = await cursor.fetchall()
                elif amount == 1:
                    res = await cursor.fetchone()
                else:
                    res = await cursor.fetchmany(amount)
                log.info(cursor.description)
                return res

    async def fetchrow(self, query, args=None):
        res = await self.fetch(query, args, 1)
        return res
