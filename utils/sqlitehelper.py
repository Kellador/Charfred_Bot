import aiosqlite
import logging

log = logging.getLogger('charfred')


class SQLiteHelper():
    """Helper class to handle database connections and transactions.
    Supports SQLite3 via aiosqlite.
    """
    def __init__(self, bot, **opts):
        self.bot = bot
        self.loop = bot.loop
        self.db = opts.pop('database', None)
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db)
        log.info(f'DBMS connected to {self.db}.')

    async def disconnect(self):
        await self.conn.close()
        log.info('DBMS-adapter disconnected.')

    async def execute(self, command, args=None, commit=True):
        if isinstance(command, str):
            if args is None:
                cursor = await self.conn.execute(command)
            else:
                cursor = await self.conn.execute(command, args)
        else:
            cursor = await self.conn.cursor()
            for cmd in command:
                await cursor.execute(command)
        if commit:
            await self.conn.commit()
        return cursor

    async def executemany(self, command, args, commit=True):
        cursor = await self.conn.executemany(command, args)
        if commit:
            await self.conn.commit()
        return cursor

    async def fetch(self, query, args=None, amount=None):
        if args is None:
            cursor = await self.execute(query, commit=False)
        else:
            cursor = await self.execute(query, args, commit=False)
        if amount is None:
            res = await cursor.fetchall()
        elif amount == 1:
            res = await cursor.fetchone()
        else:
            res = await cursor.fetchmany(amount)
        return res

    async def fetchrow(self, query, args=None):
        res = await self.fetch(query, args, 1)
        return res

    async def fetchall(self, query, args=None):
        res = await self.fetch(query, args)
        return res
