# Import libraries
import client_info
import command
import logger
import network
import pickle
import uuid


def print_help() -> None:
    """Print the help menu"""
    print('''\n~~~~~~~~~~ Dolus Agent ~~~~~~~~~~
help - Print this help menu
exit - Exit the agent
install - Install a module on a client
delete - Delete a module on a client
start - Start a module on a client\n''')


if __name__ == '__main__':
    log = logger.init_log(True)

    # Create agent info
    agent_info = client_info.DolusClientInfo()
    agent_info.name = 'Test agent'
    agent_info.username = 'test'
    agent_info.role = client_info.ROLE_AGENT
    agent_info.version = '1.0'
    agent_info.uuid = str(uuid.uuid4())

    # Connect to the server
    client = network.TCPClient('192.168.1.161', 2016)
    client.connect()

    # Send agent info
    client.send(pickle.dumps(agent_info))

    # Get server logs
    print(client.receive().decode() + '\n')

    # Get commands to send
    while 1:
        command_to_send = input('Dolus > ')

        if command_to_send == 'exit':
            break

        if command_to_send == 'help':
            print_help()
            continue

        elif command_to_send == 'install':
            c = command.Command()
            c.type = command.INSTALL_MODULE
            c.module_file = input('Module file: ')
            c.intended_client = input('Client UUID: ')

            client.send(pickle.dumps(c))
            print(client.receive().decode())

        elif command_to_send == 'delete':
            c = command.Command()
            c.type = command.DELETE_MODULE
            c.module_file = input('Module file: ')
            c.intended_client = input('Client UUID: ')

            client.send(pickle.dumps(c))
            print(client.receive().decode())

        elif command_to_send == 'start':
            c = command.Command()
            c.type = command.RUN_MODULE
            c.module_file = input('Module file: ')
            c.intended_client = input('Client UUID: ')

            client.send(pickle.dumps(c))

            while 1:
                c = input('    > ')
                client.send(c.encode())
                print(client.receive())

        else:
            print(f'Unknown command: {command_to_send}')

    client.disconnect()
