from abc import ABC, abstractmethod

# Constants
STARTUP_NOT_SET = 0
STARTUP_ON_START = 1
STARTUP_ON_CONNECT = 2
STARTUP_MANUAL = 3

REQUIRE_NOT_SET = 0
REQUIRE_TCP_CLIENT = 1
REQUIRE_LOGGER = 2


class Module(ABC):
    """An abstract class for Dolus client modules"""

    def __init__(self) -> None:
        self.startup = STARTUP_NOT_SET
        self.require = [REQUIRE_NOT_SET]
        self.VERSION = '1.0'

    @abstractmethod
    def start(self):
        pass
