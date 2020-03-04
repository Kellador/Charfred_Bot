import logging
import asyncio
from concurrent.futures import CancelledError
from discord.ext import commands
from utils import permission_node

log = logging.getLogger('charfred')


class StreamServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.server = None
        self.cfg = bot.cfg
        self.handlers = {}
        self.loop.create_task(self._start_server())

    @property
    def running(self):
        if self.server and self.server.sockets:
            return True
        else:
            return False

    def cog_unload(self):
        if self.server:
            log.info('StreamServ: Closing server.')
            self.server.close()

            self.loop.create_task(self.server.wait_closed())

    async def _start_server(self):
        if self.running:
            log.info('StreamServ: Server already running!')
        else:
            try:
                port = self.cfg['streamserverport']
            except KeyError:
                log.warning('StreamServ: No port configured!')
                return

            self.server = await asyncio.start_server(
                self._connection_handler,
                '127.0.0.1',
                port,
                loop=self.loop
            )
            log.info('StreamServ: Server started.')

    def _close_server(self, wait=True):
        if self.server:
            log.info('StreamServ: Closing server.')
            self.server.close()

            if wait:
                self.loop.create_task(self.server.wait_closed())

    async def _connection_handler(self, reader, writer):
        """Handles the initial handshake upon recieving a new connection,
        and checks if a handler is registered for recieving said handshake.

        If a handler is found, reader and writer are handed off to it,
        if not the connection is dropped.

        The handler recieving reader and writer is responsible for when
        the connection is closed, outside of the server itself closing.
        """

        peer = str(writer.get_extra_info('peername'))
        log.info(f'StreamServ: New connection established with {peer}.')

        handshake = await reader.readline()
        if not handshake:
            log.warning(f'StreamServ: No handshake recieved from {peer},'
                        ' dropping connection.')
            writer.close()
            return

        handshake = handshake.decode()
        if handshake in self.handlers:
            self.loop.create_task(self.handlers[handshake](reader, writer))
        else:
            log.warning(f'StreamServ: No handler available for {handshake},'
                        ' dropping connection.')
            writer.close()
            return

    def register_handshake(self, handshake, handler):
        """Register a handshake and accompanying handler.

        The handshake must be a string.

        The handler must accept only a StreamReader and StreamWriter
        object and should implement some form of connection closing logic.
        """

        if handshake in self.handlers:
            log.info(f'StreamServ: {handshake} already registered.')
        else:
            log.info(f'StreamServ: Registering {handshake}.')
            self.handlers[handshake] = handler

    def unregister_handshake(self, handshake):
        """Unregisters a handshake and accompanying handler."""

        if handshake in self.handlers:
            log.info(f'StreamServ: Unregistering {handshake}.')
            del self.handlers[handshake]
        else:
            log.info(f'StreamServ: {handshake} is not registered.')

    async def _serverstatus(self):
        if self.running:
            await ctx.sendmarkdown('# Stream Server is up.')
        else:
            await ctx.sendmarkdown('< Stream server is down! >')

    @command.group(invoke_without_command=True)
    @permission_node(f'{__name__}')
    async def streamserver(self, ctx):
        """Stream server commands.

        Returns whether or not the server is up.
        """

        await self._serverstatus()

    @streamserver.command()
    async def start(self, ctx):
        """Starts the stream server."""

        await self._start_server()
        await self._serverstatus()

    @streamserver.command()
    async def stop(self, ctx):
        """Stops the stream server."""

        self._close_server(wait=False)
        await self.server.wait_closed()
        await self._serverstatus()

    @streamserver.command()
    @permission_node(f'{__name__}.setport')
    async def setport(self, ctx, port: int):
        """Sets the port the stream server should use."""

        self.cfg['streamserverport'] = port
        await self.cfg.save()

    @streamserver.command()
    @permission_node(f'{__name__}.disable')
    async def disable(self, ctx):
        """Disables the stream server by stopping it and removing
        the configured port, essentially stopping the server from
        launching again.

        Not sure why you'd want to do this, unloading the cog would
        be the better option.
        """

        self._close_server(wait=False)
        del self.cfg['streamserverport']
        await self.cfg.save()
        await self.server.wait_closed()
        await ctx.sendmarkdown('# Stream server disabled, port removed '
                               'from config!')


def setup(bot):
    permission_nodes = ['', 'setport', 'disable']
    bot.register_nodes([f'{__name__}.{node}' if node else f'{__name__}'
                        for node in permission_nodes])
    bot.add_cog(StreamServer(bot))
