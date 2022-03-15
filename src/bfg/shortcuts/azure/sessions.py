from copy import copy
from .request_profiles import MicrosoftOnline
from bfg.shortcuts.http import HTTPSession

MSOL_DEFAULTS = MicrosoftOnline()
class MSOLSession(HTTPSession):
    '''MSOL session with pre-populated HTTP headers.
    '''

    def __init__(self, headers:dict=MSOL_DEFAULTS.headers,
            *args, **kwargs):

        super().__init__(headers=headers, *args, **kwargs)
