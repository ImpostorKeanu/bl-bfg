from bfg.shortcuts.azure import(
    getRandomResource,
    getRandomListItem,
    lookupGraphCode,
    MSOL_UNIVERSAL_CLIENT_IDS,
    ERROR_CODE_RE)
from bfg.shortcuts.http import HTTPSession
from dataclasses import dataclass, field as Field
from collections import OrderedDict
from copy import copy
import re

@dataclass
class BaseRequestProfile:

    proxies:dict = Field(default_factory=lambda: dict())
    verify_ssl:bool = False
    allow_redirects:bool = False


@dataclass
class MicrosoftOnline(BaseRequestProfile):

    session_class:object = HTTPSession
    headers:dict = Field(
        default_factory=lambda: dict(Accept='application/json'))
    method:str = 'post'
    url:str = 'https://login.microsoftonline.com'
    path:str = '/common/oauth2/token'

    body:dict = Field(
        default_factory=lambda: dict(
            client_info = 1,
            grant_type = 'password',
            scope = 'openid',
            # Input required
            client_id = None,
            # Input required (resource URL)
            resource = None,
            # Input required
            username = None,
            # Input required
            password = None))

    # Graph API
    resource_url:str = 'https://graph.microsoft.com'

    # Teams Client
    client_id:str    = '1fec8e78-bce4-4aaf-ab1b-5451cc387264'

    def authenticate(self, username:str, password:str) -> (
            bool, bool, list,):
        '''Authenticate to the Graph API.

        Args:
            username: String username to authenticate.
            password: String password to authenticate.

        Returns:
            Returns a three-elemnt tuple:
                (
                    authentication_success,
                    username_valid,
                    [str_events],
                )
        '''

        # =================
        # PREPARE A SESSION
        # =================

        session = self.session_class(headers=self.headers,
                verify_ssl=self.verify_ssl,
                allow_redirects=self.allow_redirects)
        session.proxies.update(self.proxies)

        if hasattr(self, 'user_agent'):
            self.headers.update(
                dict(user_agent=self.user_agent))

        # ==================================
        # PREPARE THE CLIENT/RESOURCE VALUES
        # ==================================

        resource_url = self.resource_url
        if resource_url == 'RANDOM':
            name, resource_url = getRandomResource()

        client_id = self.client_id
        if client_id == 'RANDOM':
            while True:
                client_id = getRandomListItem(
                    MSOL_UNIVERSAL_CLIENT_IDS)
                if client_id != '1b730954-1685-4b74-9bfd-dac224a7b894':
                    # Loop until the client_id is not PowerShell
                    break

        # ================
        # MAKE THE REQUEST
        # ================

        # Create the POST data
        data = copy(self.body)
        data.update({
            'resource':resource_url,
            'client_id':client_id,
            'username':username,
            'password':password})

        resp = session.post(url = self.url+self.path, data = data)

        # ===================
        # HANDLE THE RESPONSE
        # ===================

        # Search the response for error codes
        error_code = re.search(ERROR_CODE_RE, resp.text)
        if error_code:

            error_code = error_code.groups()[0]
            outcome, valid_account, events = \
                lookupGraphCode(resp.status_code, error_code)

            if events:
                events[0] += f' - {username}:{password}'

        else:

            if resp.status_code == 200:
                outcome, valid_account, events = (1, True,
                        ['200 OK response'],)
            else:
                outcome, valid_account, events = (-1, True,
                        ['Unhandled response event occurred'],)

        return outcome, valid_account, events

class AzureManagementAPI(MicrosoftOnline):
    '''An authentication profile for the Azure Management API.

    It inherits from the MicrosoftOnline profile because
    the same URL and path are hit during authentication but
    the payload differs as it requires a specific resource_url
    and client_id value.
    '''

    body:dict = Field(
        default_factory=lambda: dict(
            client_info = 1,
            grant_type = 'password',
            scope = 'openid',
            # Input required
            username = None,
            # Input required
            password = None,
            resource_url = 'https://management.core.windows.net',
            client_id = '1950a258-227b-4e31-a9cf-717495945fc2'))

    def mfaCheck(self, username:str, password:str) -> (bool, str,):

        session = self.session_class(headers=self.headers,
                verify_ssl=self.verify_ssl,
                allow_redirects=self.allow_redirects)
        session.proxies.update(self.proxies)

        data = copy(self.body)

        data.update(dict(
            username = username,
            password = password))

        resp = self.post(url=self.url+self.path, data=data)

        if resp.status_code == 200:

            return (False,
                'Azure Service Management API should be '
                'accessible. "Az" PowerShell module shoud work, '
                'too',)

        else:

            return (True,
                'Azure Service Management API appears to require '
                'MFA.',)

@dataclass
class O365WebPortal(BaseRequestProfile):
    '''O365 Web Portal

    There are three stages of authentication in this profile:

        1. Stage 1 (S1) acquires cookies and POST body parameters
           for Stage 2 (S2), specifically the originalRequest and
           flowToken values.
        2. S2 POSTS the values to MSOL.
        3. Stage 3 (S3) POSTS the authentication form to MSOL.

    It's possible to infer if MFA is required based on cookies
    from S3. If the "ESTSAUTH" cookie is present, auth things
    are golden.
    '''

    session_class:object = HTTPSession

    s1_url:str = 'https://outlook.office365.com'
    s1_method:str = 'get'
    s1_regexes:OrderedDict = Field(
        default_factory = lambda: OrderedDict(
            partial_ctx = \
                re.compile('urlLogin":"(?P<partial_ctx>.*?)"'),
            ctx = \
                re.compile('ctx=(?P<ctx>.*?)"'),
            flow_token = \
                re.compile('sFT":"(?P<flow_token>.*?)"')))

    s2_url:str = 'https://login.microsoftonline.com'
    s2_path:str = '/common/GetCredentialType?mkt=en=US'
    s2_method:str = 'post'
    s2_body:dict = Field(
        default_factory = lambda: dict(
            username = None,
            isOtherIdpSupported = False,
            checkPhones = False,
            isRemoteNGCSupported = True,
            isCookieBannerShown = False,
            isFidoSupported = True,
            # Input Required (ctx)
            originalRequest = None,
            country = "US",
            forceotclogin = False,
            isExternalFederationDisallowed = False,
            isRemoteConnectSupported = False,
            federationFlags = 0,
            isSignup = False,
            # Input Required (FlowToken)
            flowToken = None,
            isAccessPassSupported = True))

    s2_url:str = 'https://login.microsoftonline.com'
    s3_path:str = '/common/login'
    s3_method:str = 'post'
    s3_body:dict = Field(
        default_factory=lambda: dict(
            i13 = 0,
            # Input Required (username)
            login = None,
            # Input Required (username)
            loginfmt = None,
            type = 11,
            LoginOptions = 3,
            lrt = '',
            lrtPartition = '',
            hisRegion = '',
            hisScaleUnit = '',
            # Input Required (password)
            passwd = None,
            ps = 2,
            psRNGCDefaultType = '',
            psRNGCEntropy = '',
            psRNGCSLK = '',
            canary = '',
            # Input Required (ctx)
            ctx = None,
            hpgrequestid = '',
            # Input Required (FlowToken)
            flowToken = None,
            NewUser = 1,
            FoundMSAs = '',
            fspost = 0,
            i21 = 0,
            CookieDisclosure = 0,
            IsFidoSupported = 1,
            isSignupPost = 0,
            i2 = 1,
            i17 = '',
            i18 = '',
            i19 = '198733'))

    # Cookie name that will match on this indicates
    # valid authentication.
    cookie_signature:str = 'ESTAUTH'

    # Content match on this indicates no MFA
    no_mfa_signature:str = 'Stay signed in'

    # Content match on this indicates MFA is enforced
    mfa_enforced_signature:str = 'Verify your identity'

    def mfaCheck(self, username:str, password:str) -> (bool, str,):
        '''

        Notes:

            - All requests should supply the same session tokens, i.e.
              the same session object should be used across all
              requests.
        '''

        # ======= STAGE 1 =======

        session = self.session_class(headers=self.headers,
            verify_ssl = self.verify_ssl,
            allow_redirects = self.allow_redirects)
        session.proxies.update(self.proxies)

        resp = session.get(self.s1_url)

        if resp.status_code != 200:

            return (None,
                'Initial request resulted in a non-200 response code '
                f'({resp.status_code}).',)

        # ====================
        # PARSE STAGE 2 VALUES
        # ====================

        # Parse out the CTX value
        match = re.match(
            self.s1_regexes['partial_ctx'],
            resp.text)

        if not match:

            return (None,
                'Failed to get initial originalRequest (partial_ctx) '
                'value for stage 2 request.',)

        ctx = match.groups()[0]

        match = re.match(
            self.s1_regexes['ctx'],
            ctx)

        if not match:

            return (None,
                'Failed to get initial originalRequest (ctx) value '
                'for stage 2 request.',)

        ctx = match.groups()[0]

        # Parse out the flowToken value
        match = re.match(
            self.s1_regexes['flow_token'],
            resp.text)

        if not match:

            return (None,
                'Failed to get initial flowToken value for stage 2 '
                'request.',)

        flow_token = match.groups()[0]

        # ======= STAGE 2 =======

        body = copy(self.s2_body)

        body.update(dict(
            originalRequest = ctx,
            flowToken = flow_token))

        resp = session.post(
            url = self.s2_url+self.s2_path,
            data = body)

        # ======= STAGE 3 =======

        s3_body = copy(self.body)
        s3_body.update(dict(
            login = username,
            loginfmt = username,
            passwd = password,
            ctx = ctx,
            flowToken = flow_token))

        resp = session.post(
            url = self.url+self.s3_path,
            data = self.s3_body)

        # =============
        # VERIFY STATUS
        # =============
        '''
        - Authentication was successful if an ESTAUTH cookie was
          issued by the server.
        - The following strings indicate if MFA is enforced:
          - "Stay signed in" - MFA is not enforced.
          - "Verify your identity" - MFA isenforced.
        '''

        auth_success, cookies = False, ''
        for name, cookie in resp.cookies.items():

            if name.find(self.cookie_signature) > -1:

                auth_success = True

            if cookies: cookies += ' '

            cookies += '{name}: {value}'.format(
                name=name,
                value=cookie)

        if not auth_success:

            # ===================
            # INVALID CREDENTIALS
            # ===================

            return (None,
                'Authentication failed to return the ESTSAUTH '
                'cookie when verifying MFA for O365 Web Portal.')

        if resp.text.find(self.no_mfa_signature) > -1:

            # =========================
            # MFA NOT ENFORCED RESPONSE
            # =========================

            return (False,
                'MFA does not appear to be enforced. Log in with your '
                'browser at https://login.microsoftonline.com. - '
                f'COOKIES - {cookies}')

        elif resp.text.find(self.mfa_enforced_signature) > -1:

            # =====================
            # MFA ENFORCED RESPONSE
            # =====================

            return (True,
                'MFA appears to be enforced for this account.')

        else:

            # =======
            # FAILURE
            # =======

            return (None,
                'Failed to verify MFA for account.')

class O365WebPortalMobile(O365WebPortal):
    '''O365 web portal with Android UA.
    '''

    user_agent:str = ('Mozilla/5.0 (Linux; Android 6.0; '
        'Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/85.0.4183.121 Mobile Safari/53'
        '7.36')

class Microsoft365ActiveSync:
    '''Microsoft 365 Active Sync authentication profile.
    '''

    method:str = 'post'
    url:str = 'https://outlook.office365.com'
    path:str = '/Microsoft-Server-ActiveSync'
    success_status_code:int = 505

    def mfaCheck(self, username:str, password:str) -> (bool, str,):

        resp = self.get(self.url+self.path,
                auth=HTTPBasicAuth(username, password))

        if resp.status_code == 505:

            return (False,
                'MFA is not enforced on Microsoft 365 ActiveSync. '
                '-- NOTE: use the Windows Mail app to connect to '
                'this service!',)

        else:

            return (True, 'Login to ActiveSync failed.',)
