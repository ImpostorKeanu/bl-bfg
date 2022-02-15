#!/usr/bin/env python3

import requests
import re
import warnings
from bfg.args import http as http_args, argument
from bfg.shortcuts.http import HTTPModule, handleUA
warnings.filterwarnings('ignore')

'''
# Notes

## Example Post Payload

The `fc` parameter is a value embedded from initial resolution of
the DEFAULT_LANDING. Must be parsed accordingly.

```
user=testo%40wc.com&password=presto&fc=w418-O1LolQa3sNuhib5s18kwLD33f7f3YulC0B3cftanOcg%5E
```

Input field from the landing HTML

<input type="hidden" id="flogin" name="flogin" value="w418-O1LolQa3sNuhib5s18kwLD33f7f3YulC0B3cftanOcg^">

## Invalid Credential Response

```
0||1||Invalid Username/Password.
```
'''

# Default user agent
DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chr' \
             'ome/58.0.3029.110 Safari/537.36'

# Path to default landing page
#   - Assigns CRSF cookie
#   - Provides value to fc POST parameter (unknown use)
DEFAULT_LANDING = '/courier/web/1000@/wmLogin.html?'

# Path to where the form is posted
DEFAULT_LOGIN   = '/courier/web/1000@/wmUtils.api'

RE_FLOGIN = re.compile('name="flogin" value="(?P<flogin>.+)"><input '\
        'type="hidden" id="logRes"')

@argument
def landing_path(name_or_flags=('--landing-path',),
        default=DEFAULT_LANDING,
        help='String path to the landing page that issues '
            'cookies/tokens.'):
    pass

@argument
def login_path(name_or_flags=('--login-path',), default=DEFAULT_LOGIN,
        help='String path to where the authentication form '
            'is to be submitted.'):
    pass

@argument
def url(name_or_flags=('--url',),
        required=True,
        help='Origin server which --landing-path and --login-path '
                'will be suffixed to. Expected format: '
                'https://www.target.com'):
    pass

class Module(HTTPModule):
    '''Callable FTP class for the Accellion FTP web interface.
    '''

    description = brief_description = 'Accellion FTP HTTP interface login module'

    args = [url(), login_path(), landing_path()]+\
        http_args.getDefaults('url', invert=True)

    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __post_init__(self, landing_path, login_path, *args, **kwargs):

        self.origin_url=self.url
        self.landing_path=landing_path
        self.login_path=login_path
        self.landing_url=f'{origin_url}{landing_path}'
        self.auth_url=f'{origin_url}{login_path}'

    @handleUA
    def __call__(self, username, password):
        '''Authentication module called for each set of credentials.
        It uses a fresh `requests.Session` object to acquire a new
        session cookie and fc value from the landing page to assure
        that server-side logic doesn't denylist a given combination of
        values due to multiple failed authentication attempts.

        - username - String username value to guess
        - password - String password value to guess
        '''

        # ====================
        # GET NECESSARY VALUES
        # ====================

        sess = requests.Session()

        # Get a CSRF-TOKEN (cookie)
        resp = sess.get(self.landing_url,self.headers)

        if resp.status_code != 200:
            raise Exception(
                    f'Server responded with non 200: {resp.status_code}')

        # Get the flogin line from the response text content
        target=None
        for line in resp.text.split('\n'):
            if line.find('name="flogin"') > 0:
                target=line
                break

        # Get the fc value for the POST request
        if target: match = re.search(RE_FLOGIN,target)

        if target == None or match == None:
            raise Exception(
                    'Failed to acquire flogin token from response body')

        # ======================
        # ATTEMPT AUTHENTICATION
        # ======================

        resp = sess.post(
                self.auth_url,
                data={'username':username,
                    'password':password,
                    'fc':match.groups()[0]},
                headers={
                        'Referer':self.landing_url,
                        'CSRF-TOKEN':resp.cookies['CSRF-TOKEN'],
                    },
                verify=self.verify_ssl
            )

        if 'Content-Type' not in resp.headers or \
                resp.headers['Content-Type'].find('text') == -1:
            raise Exception(
                    'Unknown response after authentication attempt')

        # =====================================
        # VERIFY CREDENTIALS AND RETURN OUTCOME
        # =====================================

        if resp.text.find('Invalid') > -1:
            return dict(outcome=0, username=username, password=password)
        else:
            return dict(outcome=1, username=username, password=password)
