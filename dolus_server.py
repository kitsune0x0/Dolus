# Import libraries
import logger
import network
import os
import socket

# Constants
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 2016
VERSION = '1.0'


if __name__ == '__main__':
    # Remove the log file if it exists
    if os.path.exists('dolus.log'):
        os.remove('dolus.log')

    # Initialize logger
    log = logger.init_log(True, 'dolus')

    # Start the TCP server
    server = network.TCPServer(SERVER_IP, SERVER_PORT)
    server.start()
