#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
from re import search
import requests
from bfg.args import http as http_args, argument
from bfg.shortcuts.http import HTTPModule, handleUA

@argument
def flags(name_or_flags=('--flags',),
        help='Flags POST parameter value.',
        default=0):
    pass

@argument
def forcedownlevel(name_or_flags=('--forcedownlevel',),
        type=int, default=0,
        help='Flags POST parameter value.'):
    pass

@argument
def trusted(name_or_flags=('--trusted',),
        type=int, default=0,
        help='trust POST parameter value'):
    pass

@argument
def isUTF8(name_or_flags=('--isUtf8',),
        type=int, default=1,
        help='isUTF8 POST parameter value.'):
    pass
        
class Module(HTTPModule):

    description = brief_description = 'OWA 2010 web interface'

    args = [http_args.url(), flags(), forcedownlevel(), trusted(),
            isUTF8()] + \
        http_args.getDefaults('url', invert=True)

    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __post_init__(self, flags, forcedownlevel, trusted, isUtf8,
            *args, **kwargs):

        self.flags = flags
        self.forcedownlevel = forcedownlevel
        self.trusted = trusted
        self.isUtf8 = isUtf8

    @handleUA
    def __call__(self,username,password,*args,**kwargs):
    
        # post data
        data = {
            'destination':self.url,
            'flags':self.flags,
            'forcedownlevel':self.forcedownlevel,
            'trusted':self.trusted,
            'username':username,
            'password':password,
            'isUtf8':self.isUtf8
        }
    
        # make the request
        resp = requests.post(self.url,
                data=data,
                headers=self.headers,
                verify=self.verify_ssl,
                allow_redirects=False,
                proxies=self.proxies)
    
        # verify credentials and return outcome
        if resp.status_code == 302 and resp.headers['Location'] and (
            search(r'auth\/logon\.aspx\?', resp.headers['Location'])):
            return dict(outcome=0, username=username, password=password)
        else:
            return dict(outcome=1, username=username, password=password)
