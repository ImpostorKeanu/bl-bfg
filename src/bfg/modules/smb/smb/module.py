
# NOTE: This module relies on the pysmb package
from smb.SMBConnection import SMBConnection
import re
import string
from random import randint,choice
from bfg.module import Module as BLModule
from bfg.args import argument

def gen_client_name(min_len=5,max_len=15):
    '''Generate a random client name.
    '''
    
    i = randint(min_len,max_len)

    return ''.join(
                [choice(string.ascii_letters+string.digits) for n in range(32)]
            )

@argument
def server_ip(name_or_flags=('--server-ip',),
        required=True,
        help='IP address of the SMB server to target. '
            'Required: %(required)s'):
    pass

@argument
def server_name(name_or_flags=('--server-name',),
        help='Server hostname. Default: %(default)s',
        default=None):
    pass

@argument
def server_port(name_or_flags=('--server-port',),
        help='Server port. Default: %(default)s',
        default=445):
    pass

@argument
def client_name(name_or_flags=('--client-name',),
        help='Client name. Default: %(default)s',
        default=None):
    pass

@argument
def default_domain(name_or_flags=('--default-domain',),
        default='WORKGROUP',
        help='Default workgroup name when domain is not provided'
            'with a username. Default: %(default)s'):
    pass

class Module(BLModule):
    '''Defining the callback
    '''

    brief_description = description = 'Target a single SMB server.'

    args = [server_ip(), server_name(), server_port(), client_name(),
            default_domain()]

    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __init__(self, server_ip, server_name, server_port,
            client_name, default_domain):
        '''Initialize the SMB Callback.
        '''

        self.server_ip = server_ip
        self.server_port = server_port
        self.default_domain = default_domain

        self.server_name = server_name if server_name else server_ip
        self.client_name = client_name if client_name else \
                gen_client_name()

    def __call__(self, username, password, *args, **kwargs):
    
        # ==================
        # PARSE THE USERNAME
        # ==================
    
        # Assume domains are passed with each username in one of three formats:
            # DOMAIN/USERNAME
            # DOMAIN\USERNAME
            # USERNAME@DOMAIN

        original_username = username
    
        if re.search(r'@',username):
            username, domain = username.split('@')
        elif re.search(r'/',username) or re.search(r'\\|\\',username):
            domain, username = re.split(r'/|\\',username)
        else:
            domain = self.default_domain

        conn = SMBConnection(username, password, self.client_name,
                self.server_name, domain=domain, use_ntlm_v2=True,
                is_direct_tcp=True)
        outcome = conn.connect(self.server_ip, self.server_port)

        # =============
        # RETURN OUTPUT
        # =============

        if outcome:
            conn.close()
            return dict(outcome=1, username=username, password=password)
        else:
            return dict(outcome=0, username=username, password=password)
