"""Module for installing dependcies for directory tools."""

import conda.cli as conda_client
import subprocess
import sys
import re
import os
import pkg_resources 

class PackageInstaller(object):
    """Installation of dependencies for tools."""

    def __init__(self):
        self.modules = self.define_modules()
        self.environment = self.find_environment()

    def define_modules(self):
        """Read modules list from Pipfile."""
        with open('./Pipfile') as modules:
            content = modules.read().splitlines()

        begin = [i for i, line in enumerate(content) if re.match(r'\[packages\]', line)][0] + 1
        end = [i for i, line in enumerate(content) if re.match(r'\[requires\]', line)][0] - 2

        modules = [re.search(r'.*(?=\s\=)', module)[0] for module in content[begin:end]]
        return modules

    def find_environment(self):
        """Determine if the user is using Conda or Pip for package management."""
        if os.system('conda list >/dev/null 2>&1') == 256:
            print('No Conda environment found ... installing packages via pip')
            env = 'pip'
        else:
            print('Conda environment found ... installing packages via Conda')
            env = 'conda'

        return env

    def module_check_install(self):
        """Check the local machine for installed packages; install those that aren't via Conda."""
        installed_packages = [dist.key for dist in pkg_resources.working_set] 
        for module in self.modules:
            if module not in installed_packages:
                print(module + ' not found ... will attempt to install now')

                if self.environment == 'conda':
                    conda_client.main('conda', 'install', '-y', module)

                elif self.environment == 'pip':
                    subprocess.call([sys.executable, '-m', 'pip', 'install', f'{module}'])

        print('\nModule installation complete')
