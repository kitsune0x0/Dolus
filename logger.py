# Import libraries
import logging
import os
from logging import Logger


class DolusLogger(logging.Logger):
    """Dolus custom logger"""
    def __init__(self, name: str, level=logging.NOTSET):
        super().__init__(name, level)

    def d_info(self, msg, *args, **kwargs):
        # Ignore this function if the logger is set to debug
        if self.level == logging.DEBUG:
            return

        # Call the original info function
        super().info(msg, *args, **kwargs)


def init_log(debug: bool = False, file_name: str = None) -> Logger:
    """Initialize logging for Dolus"""
    # Set logging level
    log_level = logging.DEBUG if debug else logging.INFO

    # Create logger
    logging.setLoggerClass(DolusLogger)
    logger = logging.getLogger('Dolus')
    logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s', '%m/%d/%Y %I:%M:%S %p')
    console_handler.setFormatter(formatter)

    # Create file handler
    if file_name is not None:
        # Add file handler
        file_handler = logging.FileHandler(f'{file_name}.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add console handler to logger
    logger.addHandler(console_handler)

    return logger
