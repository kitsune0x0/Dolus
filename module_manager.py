# Import libraries
import inspect
import logging
import Modules.module as module
import os


class ModuleManager:
    """Manages Dolus modules"""
    def __init__(self) -> None:
        self.MODULE_DIRECTORY = 'Modules'
        self.log = logging.getLogger('Dolus')

    def get_module_names(self) -> list[str]:
        """Returns a list of all module names in the modules folder"""
        module_files = os.listdir(self.MODULE_DIRECTORY)
        return [file[:-3] for file in module_files if file.endswith('.py') and file != 'module.py']

    def get_module_startups(self, module_names: list[str]) -> dict[str, None | int]:
        """Returns a dictionary of module names and their corresponding startup times"""
        module_startups = {}
        for module_name in module_names:
            # Open the module file
            with open(f'{self.MODULE_DIRECTORY}/{module_name}.py', 'r') as module_file:
                # Find self.STARTUP_TIME
                startup_time = None

                for line in module_file:
                    # Remove whitespace
                    line = line.strip()

                    # Match startup time values
                    if line.startswith('self.startup'):
                        startup_time = line.split('=')[1].strip()
                        break

                self.log.debug('Found startup time %s for module %s', startup_time, module_name)

                # Check if the startup time was found
                if startup_time is None:
                    self.log.error('Could not find startup time for module %s', module_name)
                    module_startups[module_name] = None

                # Match startup time values
                if startup_time == 'module.STARTUP_NOT_SET':
                    module_startups[module_name] = module.STARTUP_NOT_SET

                elif startup_time == 'module.STARTUP_ON_START':
                    module_startups[module_name] = module.STARTUP_ON_START

                elif startup_time == 'module.STARTUP_MANUAL':
                    module_startups[module_name] = module.STARTUP_MANUAL

                else:
                    self.log.error('Invalid startup time for module %s', module_name)
                    module_startups[module_name] = None

        return module_startups

    @staticmethod
    def convert_int_to_startup(startup_times: dict[str, None | int]) -> dict[str, None | str]:
        """Converts startup times from integers to strings"""
        converted_startup_times = {}

        for module_name, startup_time in startup_times.items():
            if startup_time == module.STARTUP_NOT_SET:
                converted_startup_times[module_name] = 'module.STARTUP_NOT_SET'

            elif startup_time == module.STARTUP_ON_START:
                converted_startup_times[module_name] = 'module.STARTUP_ON_START'

            elif startup_time == module.STARTUP_MANUAL:
                converted_startup_times[module_name] = 'module.STARTUP_MANUAL'

        return converted_startup_times

    def load_module(self, module_name: str) -> module.Module | None:
        """Loads a module from the modules folder"""
        # Import the module
        module_import = __import__(f'{self.MODULE_DIRECTORY}.{module_name}', fromlist=[module_name])
        module_class = None

        # Get the module class
        for name, obj in inspect.getmembers(module_import):
            # Check if the member is a class
            if inspect.isclass(obj):
                # Check if the class is a subclass of Module.module
                if issubclass(obj, module.Module) and obj is not module.Module:
                    # Select the class
                    module_class = obj
                    break

        if module_class is None:
            self.log.error('Could not find module class for module %s', module_name)
            return None

        # Create the module
        module_instance = module_class()

        return module_instance
