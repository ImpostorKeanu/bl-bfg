#!/usr/bin/env python3

import bruteloops
from bruteloops.db_manager import *
from bruteloops.jitter import Jitter
from bruteloops.brute import BruteForcer
from bruteloops.config import Config
from bruteloops import logging
from bruteloops.logging import getLogger, GENERAL_EVENTS
from bfg import parser as modules_parser
from bfg.db_args import parser as db_parser
from yaml import load as loadYml, SafeLoader
from sys import stderr
from pathlib import Path
from sys import exit
import traceback
import argparse

FT = FLAG_TEMPLATE = '--{flag}={value}'

# ================
# GLOBAL VARIABLES
# ================

# Shared logger object
logger=None

# Database manager object
manager=None

# Shared args variables
args=None

def parseYml(f, key_checks:list=None) -> dict:
    '''Load an open YAML file into memory as a JSON object,
    ensure that each high-level key is supplied in key_checks,
    and then return the output.

    Args:
        f: Open file containing YAML content.
        key_checks: String values that should appear within the
          YAML output.

    Returns:
        dict
    '''

    key_checks = [] if not key_checks else key_checks

    values = loadYml(f, Loader=SafeLoader)

    keys = values.keys()

    for v in key_checks:

        if not v in keys:

            raise ValueError(
               f'"{v}" value must be set in the base of the '
           'YAML file.')

    return values

def get_user_input(m:str) -> str:
    '''
    Simple input loop expecting either a "y" or "n" response.
    '''

    uinput = None
    while uinput != 'y' and uinput != 'n':
        uinput = input(m)

    return uinput

def handle_keyboard_interrupt(brute,exception):

    print()
    print('CTRL+C Captured\n')
    resp = get_user_input('Kill brute force?(y/n): ')

    if resp == 'y':
        print('Kill request received')
        print('Monitoring final processes completion')
        bf.shutdown()
        print('Exiting')
        exit()
    else:
        return 1

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Select Input Mode')

    # =====================
    # CLI INPUT SUBCOMMANDS
    # =====================

    cli_parser = subparsers.add_parser('cli')
    cli_subparsers = cli_parser.add_subparsers(title='Select Mode')

    db_sp = cli_subparsers.add_parser('manage-db',
        parents=[db_parser], add_help=False)
    db_sp.set_defaults(mode='db')

    brute_sp = cli_subparsers.add_parser('brute-force',
        parents=[modules_parser], add_help=False)

    brute_sp.set_defaults(mode='brute')
    brute_sp.add_argument('--database', '-db',
        required=True,
        help='Database to target.')

    # =====================
    # YML INPUT SUBCOMMANDS
    # =====================

    yml_parser = subparsers.add_parser('yml')
    yml_subparsers = yml_parser.add_subparsers(title='Select Mode')

    brute_yaml_sp = yml_subparsers.add_parser('brute-force')
    brute_yaml_sp.set_defaults(mode='brute-yaml')
    brute_yaml_sp.add_argument('--yaml-file', '-yml',
        required=True,
        help='YAML file containing attack configuration parameters.')

    # Parse the arguments
    args = parser.parse_args()

    # =====================
    # HANDLE YAML ARGUMENTS
    # =====================

    if args.mode == 'brute-yaml':

        # =====================
        # HANDLE THE FILE INPUT
        # =====================

        path = Path(args.yaml_file)
        if not path.exists():
            raise FileNotFoundError(
                f'YAML file not found: {args.yaml_file}')

        with path.open() as yfile:

            args = parseYml(yfile, key_checks=('brute-force','database',))
            _args = ['--database='+args['database']]
            args = args['brute']

            if not 'module' in args.keys():
                raise ValueError(
                    '"module" field must be set in the YAML file.')

            # ====================================
            # TRANSLATE YAML TO ARGPARSE ARGUMENTS
            # ====================================

            for k,v in args.items():

                if k != 'module':

                    # =============================
                    # CAPTURE A NON-MODULE ARGUMENT
                    # =============================

                    _args.append(
                        FT.format(flag=k.replace("_","-"),
                            value=v))

                else:

                    # =========================
                    # CAPTURE A MODULE ARGUMENT
                    # =========================

                    if not 'name' in v:

                        raise ValueError(
                            f'"name" field must be defined under "module".')

                    elif not 'args' in v:

                        raise ValueError(
                            f'"args" field must be defined under "module".')

                    _args.append(v['name'])
                    
                    for ik, iv in v['args'].items():

                        _args.append(
                            FT.format(
                                flag=ik.replace("_","-"),
                                value=iv))

        args = brute_sp.parse_args(_args)

    if args.mode == 'db':

        # ====================
        # HANDLE THE ARGUMENTS
        # ====================
    
        args = parser.parse_args()
        if not args.cmd:
            parser.print_help()
            exit()
    
        # =================
        # CONFIGURE LOGGING
        # =================
    
        logger = getLogger('dbmanager.py', log_level=10)
        logger.info('Initializing database manager')
    
        # =======================
        # HANDLE MISSING DATABASE
        # =======================
    
        if not Path(args.database).exists():
    
            cont = None
    
            while cont != 'y' and cont != 'n':
                
                cont = input(
                        '\nDatabase not found. Continue and create it? ' \
                        '(y/n) '
                    )
    
            if cont == 'n':
    
                logger.info('Database not found. Exiting')
                exit()
    
            print()
            logger.info(f'Creating database file: {args.database}')
    
        # ======================
        # INITIALIZE THE MANAGER
        # ======================
    
        try:
            manager = Manager(args.database)
        except Exception as e:
            logger.info('Failed to initialize the database manager')
            raise e
    
        # ======================
        # EXECUTE THE SUBCOMMAND
        # ======================
    
        logger.info(f'Executing command')
        args.cmd(args, logger, manager)
        logger.info('Execution finished. Exiting.')

    if args.mode == 'brute':

        if not hasattr(args, 'module'):
            raise Exception(
                'No attack module supplied!')

        # Initialize a BruteLoops.config.Config object
        config = Config()
    
        # Initialize the callback from the module bound to the argument
        # parser when the interface was being built
        config.authentication_callback = args.module.initialize(args)
    
        # Authentication Configurations
        config.process_count = args.process_count
        config.max_auth_tries = args.max_auth_tries
        config.stop_on_valid = args.stop_on_valid
    
        # Jitter Configurations
        config.authentication_jitter = Jitter(min=args.auth_jitter_min,
                max=args.auth_jitter_max)
        config.max_auth_jitter = Jitter(min=args.threshold_jitter_min,
                max=args.threshold_jitter_max)
    
        # Output Configurations
        config.db_file = args.database
    
        # Log destinations
        config.log_file = args.log_file
        config.log_stdout = args.log_stdout
    
        # Log Levels
        config.log_general = args.log_general
        config.log_valid = args.log_valid
        config.log_invalid = args.log_invalid
    
        # Configure an exception handler for keyboard interrupts    
        config.exception_handlers={KeyboardInterrupt:handle_keyboard_interrupt}
        
        # Always validate the configuration.
        config.validate()
       
        # Configure logging
        logger = getLogger('bfg', log_level=10)
        
        try:
        
            logger.log(GENERAL_EVENTS,'Initializing attack')
            bf = BruteForcer(config)
            bf.launch()
            logger.log(GENERAL_EVENTS,'Attack complete')
            
        except Exception as e:
        
            print()
            print('Unhandled exception occurred.\n')
            print(e)
            print(e.with_traceback(e.__traceback__))
            print(e.__traceback__.__dir__())
            print(e.__traceback__.tb_lineno)
            traceback.print_tb(e.__traceback__)
            print()
            print()
