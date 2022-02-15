from bfg.module import Module as BLModule
from bfg.args.testing import default

class Module(BLModule):
    '''Fake authentication callback for testing purposes. Accepts a
    username and password value during initialization that will be
    compared against future authentication calls.

    This effectively gives developers a mechanism by which to emulate
    an authentication event during tool development.
    '''

    description = brief_description = 'Fake authentication module for ' \
            'training/testing'
    args = default()
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __init__(self, username:str, password:str):
        '''Initialize the Fake object.

        - username - username value
        - password - password value
        '''

        self.username = username
        self.password = password

    def __call__(self, username, password):
        'Check the provided username and password values'
   
        if username == self.username and password == self.password:
            return dict(outcome=1, username=username, password=password)
        else:
            return dict(outcome=0, username=username, password=password)
