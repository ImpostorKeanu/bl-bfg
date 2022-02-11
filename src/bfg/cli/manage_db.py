from bruteloops import args as blargs
from logging import getLogger
import argparse

logger = getLogger('bfg.db_cmd')

def dump_valid(args, logger, manager):
    '''Write valid credentials to stdout
    '''

    logger.info('Dumping valid credentials')

    credentials = manager.get_valid_credentials() or []

    if len(credentials) == 0:
        logger.info('No valid credentials in database')
        return
    else:
        logger.info(f'Count of valid credentials: {len(credentials)}')

    for r in manager.get_valid_credentials():
        print(f'{r.username.value}:{r.password.value}')

    logger.info('Credentials dumped')

def dump_strict_credentials(args, logger, manager):
    '''Dump strict credentials from the database to stdout
    '''

    logger.info('Dumping static credentials')
    credentials = manager.get_strict_credentials(args.credential_delimiter)

    if len(credentials) == 0:
        logger.info('No static credentials in database')
        return
    else:
        logger.info(f'Count of static credentials: {len(credentials)}')

    for r in credentials:
        print(f'{r.username.value}{args.credential_delimiter}' \
              f'{r.password}')

    logger.info('Strict credentials dumped')


def handle_values(args, logger, manager):
    '''Insert or delete values from the database.
    '''

    new_args = {'as_credentials':args.as_credentials,
            'insert':args.action == 'insert'}

    for handle in ['usernames','passwords','credentials',
            'username_files','password_files','credential_files',
            'csv_files']:
        if hasattr(args,handle): new_args[handle] = getattr(args,handle) 

    manager.manage_db_values(**new_args)

def prioritize_values(args, logger, manager):
    '''Prioritize or unprioritize values
    '''

    new_args = {'prioritize':args.prioritize}

    for handle in ['usernames','passwords']:
        if hasattr(args,handle): new_args[handle] = getattr(args,handle)

    manager.manage_priorities(**new_args)

def disable_usernames(args, logger, manager):

    logger.info(f'Disabling usernames: {args.usernames}')
    manager.disable_username_records(container=args.usernames)

def enable_usernames(args, logger, manager):

    logger.info(f'Enabling usernames: {args.usernames}')
    manager.enable_username_records(container=args.usernames)

db_flag = argparse.ArgumentParser()
db_flag.add_argument('--database', '-db', help='Database to target.',
    required=True)

# Default parser
parser = argparse.ArgumentParser(
        description='Manage BruteLoops input databases',
        add_help=False)

parser.set_defaults(cmd=handle_values,action=None)
subparsers = parser.add_subparsers(
        title='Database Management',
        description='Manage the attack database.',
        help='Subcommands:')

# =================================
# DUMP VALID CREDENTIALS SUBCOMMAND
# =================================

parser_dump_valid = subparsers.add_parser('dump-valid',
        description='Dump valid credentials from the database',
        help='Dump valid credentials from the database',
        parents=[db_flag],
        add_help=False)
parser_dump_valid.set_defaults(cmd=dump_valid)

# ==================================
# DUMP STRICT CREDENTIALS SUBCOMMAND
# ==================================

parser_dump_strict_credentials = subparsers.add_parser(
        'dump-credential-values',
        description='Dump scrict credentials, regardless of ' \
                'of status from the database. This is a mean' \
                's of identifying which static values have b' \
                'een imported and can be used to obtain a li' \
                'st of values to be deleted from the attack.' \
                ' Use the dump_valid subcommand to dump vali' \
                'values, including strict records, from the ' \
                'database.',
        help='Dump all credential values from the database.',
        parents=[db_flag],
        add_help=False)
parser_dump_strict_credentials.add_argument(
        '--credential-delimiter',
        default=':',
        help='Character delimiting the username to password valu' \
             'e. Default: ":"')
parser_dump_strict_credentials.set_defaults(
        cmd=dump_strict_credentials)

# ========================
# IMPORT VALUES SUBCOMMAND
# ========================

parser_import_values = subparsers.add_parser('import-spray-values',
            description='Import username and password values ' \
                    'into the target database. NOTE: if crede' \
                    'ntial inputs are provided, they will be ' \
                    'split into individual username and passw' \
                    'ord values and imported for spraying. Us' \
                    'the import-credentials subommand if you ' \
                    'wish to import individual credentials th' \
                    'at will be paired individualy in the dat' \
                    'base.',
            help='Import values into the target database',
            parents=[db_flag, blargs.input_parser,blargs.credential_parser],
            add_help=False)
parser_import_values.set_defaults(as_credentials=False, action='insert')

# =============================
# IMPORT CREDENTIALS SUBCOMMAND
# =============================
# TODO: TEST ME

parser_import_credentials = subparsers.add_parser(
        'import-credential-values',
        description='Import credential values into the target' \
                ' database. The username to password relations' \
                'hip is maintained in the data meaning t' \
                'hat individual guesses for the username to p' \
                'assword combination will be scheduled. No ad' \
                'ditional guesses will be made for the userna' \
                'me and the password will not be used for gue' \
                'sses targeting other usernames.',
        help='Import credential pairs into the target database',
        parents=[db_flag, blargs.credential_parser],
        add_help=False)
parser_import_credentials.set_defaults(as_credentials=True,
        action='insert')

# ========================
# DELETE VALUES SUBCOMMAND
# ========================
# TODO: TEST ME; PAY ATTENTION TO CASCADING DELETIONS

parser_delete_values = subparsers.add_parser('delete-spray-values',
            description='Delete username and password values ' \
                    'from the target database. NOTE: if crede' \
                    'ntials are supplied, then the username a' \
                    'nd password values are removed from the ' \
                    'database entirely. Use the delete-creden' \
                    'tials subcommand if you wish to delete c' \
                    'redential records',
            help='Delete values from the target database',
            parents=[db_flag,blargs.input_parser,blargs.credential_parser],
            add_help=False)
parser_delete_values.set_defaults(as_credentials=False, action='delete')

# =============================
# DELETE CREDENTIALS SUBCOMMAND
# =============================
# TODO: TEST ME

parser_delete_credentials = subparsers.add_parser(
        'delete-credential-values',
        description='Delete credential values from the target' \
                'database. This targets password to username ' \
                'relationships, but a given username or passw' \
                'will be removed from the database entirely s' \
                'hould either no longer be associated with fu' \
                'ture guesses after the associations have bee' \
                'n removed',
        help='Delete credential pairs from the target database',
        parents=[db_flag, blargs.credential_parser],
        add_help=False)
parser_delete_credentials.set_defaults(as_credentials=True,
        action='delete')

# ============================
# PRIORITIZE VALUES SUBCOMMAND
# ============================

parser_prioritize_values = subparsers.add_parser(
        'prioritize-values',
        description='Prioritize username/password values',
        help='Prioritize username/password values',
        parents=[db_flag, blargs.stp],
        add_help=False)
parser_prioritize_values.set_defaults(
        cmd=prioritize_values)

# ==================================
# DISABLE USERNAME VALUES SUBCOMMAND
# ==================================

parser_disable_usernames = subparsers.add_parser(
    'disable-usernames',
    description='Disable usernames, removing them from further'
        'guesses.',
    help='Stop guessing of target usernames.',
    parents=[db_flag],
    add_help=False)
parser_disable_usernames.set_defaults(cmd=disable_usernames)

parser_disable_usernames.add_argument('--usernames', '-u',
    help='Usernames to disable.',
    required=True,
    nargs='+')

# =================================
# ENABLE USERNAME VALUES SUBCOMMAND
# =================================

parser_enable_usernames = subparsers.add_parser(
    'enable-usernames',
    description='Enable usernames, allowing them to be targeted'
        'guesses.',
    help='Resume guessing of target usernames.',
    parents=[db_flag],
    add_help=False)
parser_enable_usernames.set_defaults(cmd=enable_usernames)

parser_enable_usernames.add_argument('--usernames', '-u',
    help='Usernames to enable.',
    required=True,
    nargs='+')


