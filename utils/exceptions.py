from pathlib import Path


class SendableException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    async def send(self, ctx):
        await ctx.sendmarkdown(self.message, deletable=False)


class SpiffyPathNotFound(SendableException):
    def __init__(self, path: Path) -> None:
        super().__init__(f'< {path} does not exist! >')


class SpiffyNameNotFound(SendableException):
    def __init__(self, name: str) -> None:
        super().__init__(f'< No server by the name \'{name}\' could be found! >')


class SpiffyInvocationMissing(SendableException):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(
            f'< {path} exists, but contains no \'spiffy_invocation\' file! >'
        )


class TerminationFailed(SendableException):
    def __init__(self, servername: str) -> None:
        super().__init__(f'< Termination of {servername} failed! >')


class ServerPropertiesMissing(SendableException):
    def __init__(self, server: str) -> None:
        super().__init__(f'< {server} has no \'server.properties\' >')


class RconAuthFailure(SendableException):
    def __init__(self, server: str, details: str) -> None:
        super().__init__(f'< RCON Authentication with {server} failed, {details} >')


class RconNotEnabled(SendableException):
    def __init__(self, server: str) -> None:
        super().__init__(f'< RCON is not enabled for {server} >')


class RconLoginDetailsMissing(SendableException):
    def __init__(self, server: str) -> None:
        super().__init__(f'< {server} has no port and/or password defined for RCON >')


class RconSettingsError(SendableException):
    def __init__(self, server: str) -> None:
        super().__init__(
            f'< {server} is missing some RCON setting entries, is \'server.properties\' corrupted? >'
        )
