# Import libraries
import socket

# Constants
ROLE_NOT_SET = 0
ROLE_TARGET = 1
ROLE_AGENT = 2


class DolusClientInfo:
    """A class to hold information about a Dolus client"""

    def __init__(self) -> None:
        self.name = ''
        self.username = ''
        self.role = ROLE_NOT_SET
        self.version = ''
        self.uuid = ''

    def __get_role_name(self) -> str:
        if self.role == ROLE_NOT_SET:
            return 'Not set'

        elif self.role == ROLE_TARGET:
            return 'Target'

        elif self.role == ROLE_AGENT:
            return 'Agent'

        else:
            return 'Unknown'

    def __str__(self) -> str:
        return (f'{{name: {self.name}, username: {self.username}, role: {self.__get_role_name()},'
                f' version: {self.version}, uuid: {self.uuid}}}')


class DolusClient:
    """A class to hold information and the connection with a Dolus client"""

    def __init__(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        self.conn = conn
        self.addr = addr
        self.info = DolusClientInfo()
