from bruteloops import args as blargs
import argparse

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
    credentials = manager.get_strict_credentials()

    if len(credentials) == 0:
        logger.info('No static credentials in database')
        return
    else:
        logger.info(f'Count of static credentials: {len(credentials)}')

    for r in credentials:
        print(f'{r.username.value}{args.credential_delimiter}' \
              f'{r.password.value}')

    logger.info('Strict credentials dumped')

def handle_values(args, logger, manager, associate_spray_values=True):
    '''Insert or delete values from the database.
    '''
    new_args = dict(
        as_credentials = args.as_credentials,
        insert = args.action == 'insert',
        associate_spray_values = associate_spray_values)

    for handle in ['usernames','passwords','credentials',
            'username_files','password_files','credential_files',
            'csv_files', 'credential_delimiter']:
        if hasattr(args,handle): new_args[handle] = getattr(args,handle) 

    manager.manage_db_values(**new_args, logger=logger)

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

def associate_spray_values(args, logger, manager):

    logger.info(f'Associating spray values')
    manager.associate_spray_values()

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
    description=
        'Dump scrict credentials, regardless of of status from the '
        'database. This is a means of identifying which static '
        'values have been imported and can be used to obtain a list '
        'of values to be deleted from the attack. Use the dump_valid '
        'subcommand to dump valid values, including strict records, '
        'from the database.',
    help='Dump all credential values from the database.',
    parents=[db_flag],
    add_help=False)
parser_dump_strict_credentials.add_argument('--credential-delimiter',
    default=':', help=blargs.CREDENTIAL_DELIMITER)
parser_dump_strict_credentials.set_defaults(cmd=dump_strict_credentials)

# ========================
# IMPORT VALUES SUBCOMMAND
# ========================

parser_import_values = subparsers.add_parser('import-spray-values',
    description=
        'Import username and password values into the target '
        'database. NOTE: if credential inputs are provided, they will '
        'be split into individual username and password values and '
        'imported for spraying. Use the import-credentials subcommand '
        'if you wish to import individual credentials that will be '
        'paired individualy in the database.',
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
    description=
        'Import credential values into the target database. '
        'The username to password relationship is maintained in the '
        'data meaning that individual guesses for the username to '
        'password combination will be scheduled. No additional guesses '
        'will be made for the username and the password will not be '
        'used for guesses targeting other usernames.',
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
    description=
        'Delete username and password values from the target database. '
        'NOTE: if credentials are supplied, then the username and '
        'password values are removed from the database entirely. Use '
        'the delete-credentials subcommand if you wish to delete '
        'credential records',
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
    description=
        'Delete credential values from the target database. This '
        'targets password to username relationships, but a given '
        'username or passwwill be removed from the database '
        'entirely should either no longer be associated with future '
        'guesses after the associations have been removed',
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


