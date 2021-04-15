import logging
import asyncio
from json import loads, JSONDecodeError
from discord.ext import commands
from utils import permission_node

log = logging.getLogger(f'charfred.{__name__}')


class StreamServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.server = None
        self.cfg = bot.cfg
        self.handlers = {}
        self.loop.create_task(self._start_server())

    @property
    def running(self) -> bool:
        """Status property, indicating whether the
        stream server is running or not.

        Returns
        -------
        bool
            True when server is available and serving.
        """

        if self.server and self.server.is_serving():
            return True
        else:
            return False

    def cog_unload(self):
        if self.server:
            log.info('Closing server.')
            self.server.close()

            self.loop.create_task(self.server.wait_closed())

    async def _start_server(self):
        if self.running:
            log.info('Server already running!')
        else:
            try:
                port = self.cfg['streamserverport']
            except KeyError:
                log.warning('No port configured!')
                return

            self.server = await asyncio.start_server(
                self._connection_handler,
                '127.0.0.1',
                port,
                loop=self.loop
            )
            log.info('Server started.')

    def _close_server(self, wait=True):
        if self.server:
            log.info('Closing server.')
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
        log.info(f'New connection established with {peer}.')

        handshake = await reader.readline()
        if not handshake:
            log.warning(f'No handshake recieved from {peer},'
                        ' dropping connection.')
            writer.close()
            return

        try:
            handshake = loads(handshake)
            is_handshake = handshake['type'] == 'handshake'
        except JSONDecodeError:
            log.warning(f'Recieved non-json data from {peer},'
                        ' dropping connection.')
            writer.close()
            return
        except KeyError:
            log.warning(f'Malformed handshake recieved from {peer},'
                        ' dropping connection.')
            writer.close()
            return

        if is_handshake:
            try:
                handler = handshake['handler']
            except KeyError:
                log.warning(f'{peer} did not specify a handler,'
                            ' dropping connection.')
                writer.close()
                return

            if handler in self.handlers:
                self.loop.create_task(self.handlers[handler](reader, writer, handshake))
            else:
                log.warning(f'Handler "{handler}" specified by {peer} is unknown,'
                            ' dropping connection.')
                writer.close()
                return
        else:
            log.warning(f'Initial data from {peer} was not a handshake,'
                        ' dropping connection.')
            writer.close()
            return

    def register_handler(self, handler: str, func) -> None:
        """Registers a new connection handler.

        Parameters
        ----------
        handler : str
            name of the handler
        func : Callable[[asyncio.StreamReader, asyncio.StreamWriter, str], None]
            handler callable
        """

        log.info(f'Registering {handler}.')
        self.handlers[handler] = func

    def unregister_handler(self, handler: str) -> None:
        """Unregister a known connection handler.

        Parameters
        ----------
        handler : str
            name of the handler
        """

        if handler in self.handlers:
            log.info(f'Unregistering {handler}.')
            del self.handlers[handler]
        else:
            log.info(f'{handler} is not registered.')

    async def _serverstatus(self):
        if self.running:
            return '# Stream Server is up.'
        else:
            return '< Stream server is down! >'

    @commands.group(invoke_without_command=True)
    @permission_node(f'{__name__}')
    async def streamserver(self, ctx):
        """Stream server commands.

        Returns whether or not the server is up.
        """

        msg = await self._serverstatus()
        await ctx.sendmarkdown(msg)

    @streamserver.command()
    @permission_node(f'{__name__}')
    async def start(self, ctx):
        """Start the stream server."""

        await self._start_server()
        msg = await self._serverstatus()
        await ctx.sendmarkdown(msg)

    @streamserver.command()
    @permission_node(f'{__name__}')
    async def stop(self, ctx):
        """Stop the stream server."""

        self._close_server(wait=False)
        await self.server.wait_closed()
        msg = await self._serverstatus()
        await ctx.sendmarkdown(msg)

    @streamserver.command()
    @permission_node(f'{__name__}.setport')
    async def setport(self, ctx, port: int):
        """Set the port the stream server should listen on."""

        self.cfg['streamserverport'] = port
        await self.cfg.save()
        await ctx.sendmarkdown('# Port saved!')

    @streamserver.command()
    @permission_node(f'{__name__}.disable')
    async def disable(self, ctx):
        """Disable the stream server by stopping it and removing
        the configured port, preventing the server from
        launching again.

        Useful in case you want to unload the cog and not have the
        server start up when you load it up again.
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
