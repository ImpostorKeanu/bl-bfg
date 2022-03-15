from bfg.defaults import *
from random import randint
from bfg.errors import ModuleError
import re
from .error_codes import *
from .client_resources import *

# Compiled regex to match the keys of ERROR_CODES
#ERROR_CODE_RE = re.compile('.+(AADSTS[0-9]{5,})')
ERROR_CODE_RE = re.compile('.+(AADSTS[0-9]+)')

def lookupGraphCode(status_code:int, error_code:str) -> (int, bool, [str]):
    '''Accept an HTTP status code and Azure error code to determine
    the outcome of an authentication request.

    Args:
        status_code: HTTP status code of the request.
        error_code: Azure error code parsed from the HTTP response.

    Returns:
        A tuple of values that can be used to craft the return
        value for BruteLoops:

        (
          int determining if authentication was successful
          bool determining if the username is valid
          [str] a list of log events
        )
    '''

    message = f'[{error_code}] - '

    if status_code == 200 or error_code in VALID_CODES:

        # =================
        # VALID CREDENTIALS
        # =================

        message += f'VALID CREDENTIALS - REASON - '

        if error_code in VALID_CODES:
            message += ERROR_CODES[error_code]
        else:
            message += 'No reason, HTTP 200 status is indiciative of ' \
                'active/accessible account'

        return CRED_VALID, USERNAME_VALID, [message]

    elif error_code == 'AADSTS50053':

        # =======================================
        # ACCOUNT VALID, BUT SMARTLOCK IS ENGAGED
        # =======================================

        message += 'INVALID CREDENTIALS - ' \
            f'Smart Lock - Will ' \
            'attempt credentials during next iteration.'

        return CRED_FAILED, USERNAME_VALID, [message]

    elif error_code == 'AADSTS50034':

        # ============
        # UNKNOWN USER
        # ============

        message += 'User does not exist.'

        return CRED_FAILED, USERNAME_INVALID, [message]

    elif error_code == 'AADSTS90019':

        # =====================
        # NO TENANT INFORMATION
        # =====================

        message += 'No tenant-identifying information supplied in ' \
            'the authentication data, e.g. domain name.'

        return CRED_FAILED, USERNAME_INVALID, [message]

    elif error_code == 'AADSTS50056':

        # =======================================
        # GOOD USER, BUT NO PASSWORD SET FOR USER
        # =======================================

        message += 'User exists but does not have a password in ' \
            'Azure AD'

        return CRED_FAILED, USERNAME_VALID, [message]

    elif error_code == 'AADSTS80014':

        # ====================================
        # GOOD USER, PASSTHROUGH TIME EXCEEDED
        # ====================================

        message += 'User exists but pass-through time exceeded.'

        return CRED_FAILED, USERNAME_VALID, [message]

    elif error_code in VALID_USERNAME_CODES:

        # =======================================
        # PASSWORD INVALID, BUT USERNAME IS VALID
        # =======================================

        return CRED_INVALID, USERNAME_VALID, None

    elif error_code in FATAL_CODES:

        # =============================
        # SOMETHING WENT TERRIBLY WRONG
        # =============================

        raise Exception(
            f'Graph Error Code: {error_code}: ' \
            f'{ERROR_CODES.get(error_code)}')

    else:

        # =============================
        # SOMETHING WENT....EVEN WORSE?
        # =============================

        message += 'Unhandled Azure AD error code'
        if error_code in ERROR_CODES:
            message += '-> {}'.format(ERROR_CODES[error_code])

        return CRED_FAILED, True, [message]

def getRandomListItem(lst:list):
    '''Return a random element from lst.

    Args:
        lst: List to pull an element from.
    '''

    llen = len(lst)

    if llen == 0:
        raise ValueError(
            'lst must have at least one element')
    elif llen ==1:
        return lst[0]

    return lst[randint(0,len(lst)-1)]

def getRandomDictKey(dct:dict):
    '''Return a random key from the dictionary.

    Args:
        dct: Dictionary to pull a random key from.
    '''

    keys = list(dct.keys())
    return getRandomListItem(keys)

def getRandomClientID() -> (str, str, str):
    '''Get a random client ID from CIDS.

    Returns:
        (client, tag, client_id)
    '''

    client = getRandomDictKey(CIDS)
    tag = getRandomDictKey(CIDS[client])

    return client, tag, getRandomListItem(CIDS[client][tag])

def getRandomResource() -> (str, str):
    '''Get a random resource from RESOURCES and return the name along
    with the URL.

    Returns:
        (resource_name, resource_url,)
    '''

    name = getRandomDictKey(RESOURCES)
    return name, RESOURCES[name]

