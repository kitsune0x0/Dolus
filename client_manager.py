# Import libraries
import client_info
import json
import logging
import os


class ClientManager:
    """Manage clients stored in clients.json"""

    def __init__(self) -> None:
        self.log = logging.getLogger('Dolus')

        self.clients = []
        self.clients_file = 'clients.json'

    def load_clients(self) -> None:
        """Load clients from clients.json"""
        self.clients = []

        # Check if the file is empty
        if os.path.getsize(self.clients_file) == 0:
            self.log.info('No clients to load, file is empty.')
            return

        with open(self.clients_file, 'r') as f:
            clients = json.load(f)

        for client in clients:
            client_to_load = client_info.DolusClientInfo()
            client_to_load.name = client['name']
            client_to_load.username = client['username']
            client_to_load.role = client['role']
            client_to_load.version = client['version']
            client_to_load.uuid = client['uuid']

            self.clients.append(client_to_load)

    def save_client(self, client: client_info.DolusClientInfo) -> None:
        """Save a client to clients.json"""
        self.clients.append(client)

        # TODO: Clean up function to remove duplicate code
        clients = []
        for client in self.clients:
            clients.append({
                'name': client.name,
                'username': client.username,
                'role': client.role,
                'version': client.version,
                'uuid': client.uuid
            })

        with open(self.clients_file, 'w+') as f:
            json.dump(clients, f, indent=4)

        self.log.info('Saved client %s', client.name)

    def delete_client(self, client_uuid: str) -> None:
        """Delete a client from clients.json"""
        for client in self.clients:
            if client.uuid == client_uuid:
                self.clients.remove(client)
                self.log.info('Delete client with UUID - %s', client_uuid)

        clients = []
        for client in self.clients:
            clients.append({
                'name': client.name,
                'username': client.username,
                'role': client.role,
                'version': client.version,
                'uuid': client.uuid
            })

        with open(self.clients_file, 'w+') as f:
            json.dump(clients, f, indent=4)

    def get_client(self, client_uuid: str) -> client_info.DolusClientInfo | None:
        """Get a client from clients.json"""
        for client in self.clients:
            if client.uuid == client_uuid:
                client_to_return = client_info.DolusClientInfo()
                client_to_return.name = client.name
                client_to_return.username = client.username
                client_to_return.role = client.role
                client_to_return.version = client.version
                client_to_return.uuid = client.uuid

                return client_to_return

        return None

    def check_for_mismatch(self, client: client_info.DolusClientInfo) -> bool:
        """Check if a received client info matches the saved client info"""
        client_to_check = self.get_client(client.uuid)

        if client_to_check.name != client.name:
            self.log.info('Mismatch in saved client name (%s) and received client name (%s)',
                          client_to_check.name, client.name)
            return False

        if client_to_check.username != client.username:
            self.log.info('Mismatch in saved client username (%s) and received client username (%s)',
                          client_to_check.username, client.username)
            return False

        if client_to_check.role != client.role:
            self.log.info('Mismatch in saved client role (%s) and received client role (%s)',
                          client_to_check.role, client.role)
            return False

        if client_to_check.version != client.version:
            self.log.info('Mismatch in saved client version (%s) and received client version (%s)',
                          client_to_check.version, client.version)
            return False

        return True
