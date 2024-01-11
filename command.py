# Constants
NOT_SET = 0
INSTALL_MODULE = 1
DELETE_MODULE = 2
RUN_MODULE = 3


def convert_type(type_int: int) -> str:
    """Convert a command type to a string"""
    if type_int == NOT_SET:
        return 'NOT_SET'

    if type_int == INSTALL_MODULE:
        return 'INSTALL_MODULE'

    if type_int == DELETE_MODULE:
        return 'DELETE_MODULE'

    if type_int == RUN_MODULE:
        return 'RUN_MODULE'

    return 'UNKNOWN'


class Command:
    """A basic command to send to the client"""

    def __init__(self) -> None:
        self.type = NOT_SET
        self.module_file = ''
        self.intended_client = ''
