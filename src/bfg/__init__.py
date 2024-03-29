from bruteloops.args import *
from . import yaml_models
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from importlib import import_module
import inspect

# Get the base modules directory
base=Path(Path(inspect.getfile(inspect.currentframe())).parent \
        .absolute().__str__()+'/modules')

# Enumerate each valid module file to import
files = sorted([
    f for f in base.glob('**/*.py')
    if f.is_file() and not f.name.startswith('_')
])

# Initialize an argument parser object
parser = argparse.ArgumentParser(
        description='Example program that makes use of BruteLoops. ' \
                'Select a brute force module and input database to ' \
                'perform a highly configurable brute force attack a'
                'gainst a target service.',
        parents=[gp,jp,op],
        add_help=False)

# Initialize the subparsers object
subparsers = parser.add_subparsers(title='Brute Force Modules',
        help='Brute Modules Help',
        description='Select a brute force module below. Pass the ' \
                '--help flag to the module to get help related to' \
                ' module-level parameters.')

# ===========================
# LOAD MODULES AS SUBCOMMANDS
# ===========================

for f in files:

    try:

        # Create the name for the module and subcommand
        name = '.'.join(str(f.absolute()).split('/')[-3:]).strip('.py')

        # Import the module
        module = import_module('bfg.modules.'+name)

        # Validate the module and build the interface components
        module.Module.validate()
        module.Module.build_interface(subparsers)

    except Exception as e:

        # =============================
        # CLEANLY HANDLE FAILED MODULES
        # =============================

        print(
            'Failed to load module: {file}\n'
            'Reason:\n\n{error}\n\n'.format(
                file=f,
                error=e))
