#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
from re import search
import requests
from requests.auth import HTTPDigestAuth as HDA
from bfg.shortcuts.http import HTTPModule, handleUA

class Module(HTTPModule):

    # String found to match any of those inserted here will be
    # replaced with a string literal value of ''
    blank_signatures = []

    description = brief_description = 'Generic HTTP basic digest auth'
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    @handleUA
    def __call__(self,username,password,*args,**kwargs):

        if self.blank_handler(username): username = ''
        if self.blank_handler(password): password = ''

        # http://docs.python-requests.org/en/master/user/authentication/
        resp = requests.get(self.url,
            auth=HDA(username,password),
            headers=self.headers,
            verify=self.verify_ssl,
            allow_redirects=False,
            proxies=self.proxies)
    
        # verify credentials and return outcome
        if resp.status_code == 401:
            return dict(outcome=0, username=username, password=password)
        else:
            return dict(outcome=1, username=username, password=password)
    
    def blank_handler(self,value):

        if value in self.__class__.blank_signatures:
            return True
        else:
            return False
