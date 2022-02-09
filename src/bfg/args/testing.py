from bfg.args import argument

@argument
def username(name_or_flags=('--username',),
        required=True,
        help='Username value to test against.'):
    pass

@argument
def password(name_or_flags=('--password',),
        required=True,
        help='Password value to test against.'):
    pass

def default():

    return [username(), password()]
