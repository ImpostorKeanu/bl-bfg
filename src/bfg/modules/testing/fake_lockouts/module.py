from bfg.module import Module as BLModule
#from bfg.args.testing import default
from bfg.errors import LockoutError
from bfg.breakers import LockoutErrorBreakerProfile

class Module(BLModule):
    '''Fake authentication callback for testing purposes. Always raises
    LockoutError. Purpose is to verify configuration values.
    '''

    description = brief_description = 'Fake authentication module for ' \
        'training/testing. Always raises "LockoutError".'
    args= list()
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]
    verified_functional = True
    checks_lockout = True
    breaker_profiles = [LockoutErrorBreakerProfile()]

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, username, password):
        raise LockoutError('Intentional lockout event!')
