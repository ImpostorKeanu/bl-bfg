from bfg.defaults import *
from random import randint
import re

# Compiled regex to match the keys of ERROR_CODES
#ERROR_CODE_RE = re.compile('.+(AADSTS[0-9]{5,})')
ERROR_CODE_RE = re.compile('.+(AADSTS[0-9]+)')

def lookupCode(status_code:int, error_code:str) -> (int, bool, [str]):
    '''Accept an HTTP status code and Azure error code to determine
    the outcome of an authentication request.

    Args:
        status_code: HTTP status code of the request.
        error_code: Azure error code parsed from the HTTP response.

    Returns:
        A tuple of values that can be used to craft the return
        value for BruteLoops:

        (
          int determining if authentication was successful
          bool determining if the username is valid
          [str] a list of log events
        )
    '''

    message = f'[{error_code}] - '

    if status_code == 200 or error_code in VALID_CODES:

        # =================
        # VALID CREDENTIALS
        # =================

        message += f'VALID CREDENTIALS - REASON - '

        if error_code in VALID_CODES:
            message += ERROR_CODES[error_code]
        else:
            message += 'No graph reason, indiciative of active/' \
                'accessible account'

        return CRED_VALID, USERNAME_VALID, [message]

    elif error_code == 'AADSTS50053':

        # =======================================
        # ACCOUNT VALID, BUT SMARTLOCK IS ENGAGED
        # =======================================

        message += 'INVALID CREDENTIALS - ' \
            f'Smart Lock - Will ' \
            'attempt credentials during next iteration.'

        return CRED_FAILED, USERNAME_VALID, [message]

    elif error_code == 'AADSTS50034':

        # ============
        # UNKNOWN USER
        # ============

        message += 'User does not exist.'

        return CRED_FAILED, USERNAME_INVALID, [message]

    elif error_code == 'AADSTS50056':

        # =======================================
        # GOOD USER, BUT NO PASSWORD SET FOR USER
        # =======================================

        message += 'User exists but does not have a password in ' \
            'Azure AD'

        return CRED_FAILED, USERNAME_VALID, [message]

    elif error_code == 'AADSTS80014':

        # ====================================
        # GOOD USER, PASSTHROUGH TIME EXCEEDED
        # ====================================

        message += 'User exists but pass-through time exceeded.'

        return CRED_FAILED, USERNAME_VALID, [message]

    elif error_code in VALID_USERNAME_CODES:

        # =======================================
        # PASSWORD INVALID, BUT USERNAME IS VALID
        # =======================================

        return CRED_INVALID, USERNAME_VALID, None

    elif error_code in FATAL_CODES:

        # =============================
        # SOMETHING WENT TERRIBLY WRONG
        # =============================

        raise Exception(
            f'Graph Error Code: {error_code}: ' \
            f'{ERROR_CODES.get(error_code)}')

    else:

        # =============================
        # SOMETHING WENT....EVEN WORSE?
        # =============================

        message += 'Unhandled Azure AD error code!'
        return CRED_FAILED, True, [message]

def getRandomListItem(lst:list):
    '''Return a random element from lst.

    Args:
        lst: List to pull an element from.
    '''

    llen = len(lst)

    if llen == 0:
        raise ValueError(
            'lst must have at least one element')
    elif llen ==1:
        return lst[0]

    return lst[randint(0,len(lst)-1)]

def getRandomDictKey(dct:dict):
    '''Return a random key from the dictionary.

    Args:
        dct: Dictionary to pull a random key from.
    '''

    keys = list(dct.keys())
    return getRandomListItem(keys)

def getRandomClientID() -> (str, str, str):
    '''Get a random client ID from CIDS.

    Returns:
        (client, tag, client_id)
    '''

    client = getRandomDictKey(CIDS)
    tag = getRandomDictKey(CIDS[client])

    return client, tag, getRandomListItem(CIDS[client][tag])

def getRandomResource() -> (str, str):
    '''Get a random resource from RESOURCES and return the name along
    with the URL.

    Returns:
        (resource_name, resource_url,)
    '''

    name = getRandomDictKey(RESOURCES)
    return name, RESOURCES[name]

# A list of code values known to be associated with responses for
# valid credentials
VALID_CODES = [
    'AADSTS50014',
    'AADSTS50055',
    'AADSTS50057',
    'AADSTS50072',
    'AADSTS50074',
    'AADSTS50076',
    'AADSTS50079',
    'AADSTS50129',
    'AADSTS50131',
    'AADSTS50144',
    'AADSTS50158',
    'AADSTS53000',
    'AADSTS53001',
    'AADSTS53004',
    'AADSTS80012',
    'AADSTS90072',
    'AADSTS90094',
    'AADSTS50158',
]

VALID_USERNAME_CODES = [
    'AADSTS50126',
    'AADSTS50053',
    'AADSTS50056',
    'AADSTS80014',
]

# A list of cade values that should throw an exception when detected

FATAL_CODES = [
    'ADSTS20001',
    'AADSTS20012',
    'AADSTS20033',
    'AADSTS40008',
    'AADSTS40009',
    'AADSTS40010',
    'AADSTS40015',
    'AADSTS50000',
    'AADSTS50005',
    'AADSTS50008',
    'AADSTS50020',
    'AADSTS50128',
    'AADSTS50180',
    'AADSTS51001',
    'AADSTS90023',
    'AADSTS90024',
    'AADSTS530032',
    'AADSTS700016',
    'AADSTS9002313'
]

ERROR_CODES = \
{'AADSTS1000000': 'UserNotBoundError - The Bind API requires the Azure '
                  'AD user to also authenticate with an external IDP, '
                  "which hasn't happened yet.",
 'AADSTS1000002': 'BindCompleteInterruptError - The bind completed '
                  'successfully, but the user must be informed.',
 'AADSTS120000': 'PasswordChangeIncorrectCurrentPassword',
 'AADSTS120002': 'PasswordChangeInvalidNewPasswordWeak',
 'AADSTS120003': 'PasswordChangeInvalidNewPasswordContainsMemberName',
 'AADSTS120004': 'PasswordChangeOnPremComplexity',
 'AADSTS120005': 'PasswordChangeOnPremSuccessCloudFail',
 'AADSTS120008': 'PasswordChangeAsyncJobStateTerminated - A '
                 'non-retryable error has occurred.',
 'AADSTS120011': 'PasswordChangeAsyncUpnInferenceFailed',
 'AADSTS120012': 'PasswordChangeNeedsToHappenOnPrem',
 'AADSTS120013': 'PasswordChangeOnPremisesConnectivityFailure',
 'AADSTS120014': 'PasswordChangeOnPremUserAccountLockedOutOrDisabled',
 'AADSTS120015': 'PasswordChangeADAdminActionRequired',
 'AADSTS120016': 'PasswordChangeUserNotFoundBySspr',
 'AADSTS120018': 'PasswordChangePasswordDoesnotComplyFuzzyPolicy',
 'AADSTS120020': 'PasswordChangeFailure',
 'AADSTS120021': 'PartnerServiceSsprInternalServiceError',
 'AADSTS130004': "NgcKeyNotFound - The user principal doesn't have the "
                 'NGC ID key configured.',
 'AADSTS130005': 'NgcInvalidSignature - NGC key signature verified '
                 'failed.',
 'AADSTS130006': 'NgcTransportKeyNotFound - The NGC transport key '
                 "isn't configured on the device.",
 'AADSTS130007': 'NgcDeviceIsDisabled - The device is disabled.',
 'AADSTS130008': 'NgcDeviceIsNotFound - The device referenced by the '
                 "NGC key wasn't found.",
 'AADSTS135010': 'KeyNotFound',
 'AADSTS140000': 'InvalidRequestNonce - Request nonce is not provided.',
 'AADSTS140001': 'InvalidSessionKey - The session key is not valid.',
 'AADSTS16000': 'SelectUserAccount - This is an interrupt thrown by '
                'Azure AD, which results in UI that allows the user to '
                'select from among multiple valid SSO sessions. This '
                'error is fairly common and may be returned to the '
                'application if prompt=none is specified.',
 'AADSTS16001': "UserAccountSelectionInvalid - You'll see this error "
                'if the user clicks on a tile that the session select '
                'logic has rejected. When triggered, this error allows '
                'the user to recover by picking from an updated list '
                'of tiles/sessions, or by choosing another account. '
                'This error can occur because of a code defect or race '
                'condition.',
 'AADSTS16002': 'AppSessionSelectionInvalid - The app-specified SID '
                'requirement was not met.',
 'AADSTS16003': 'SsoUserAccountNotFoundInResourceTenant - Indicates '
                "that the user hasn't been explicitly added to the "
                'tenant.',
 'AADSTS165900': 'InvalidApiRequest - Invalid request.',
 'AADSTS17003': "CredentialKeyProvisioningFailed - Azure AD can't "
                'provision the user key.',
 'AADSTS20001': "WsFedSignInResponseError - There's an issue with your "
                'federated Identity Provider. Contact your IDP to '
                'resolve this issue.',
 'AADSTS20012': "WsFedMessageInvalid - There's an issue with your "
                'federated Identity Provider. Contact your IDP to '
                'resolve this issue.',
 'AADSTS20033': "FedMetadataInvalidTenantName - There's an issue with "
                'your federated Identity Provider. Contact your IDP to '
                'resolve this issue.',
 'AADSTS220450': 'UnsupportedAndroidWebViewVersion - The Chrome '
                 'WebView version is not supported.',
 'AADSTS220501': 'InvalidCrlDownload',
 'AADSTS221000': 'DeviceOnlyTokensNotSupportedByResource - The '
                 'resource is not configured to accept device-only '
                 'tokens.',
 'AADSTS240001': "BulkAADJTokenUnauthorized - The user isn't "
                 'authorized to register devices in Azure AD.',
 'AADSTS240002': "RequiredClaimIsMissing - The id_token can't be used "
                 'as urn:ietf:params:oauth:grant-type:jwt-bearer '
                 'grant.',
 'AADSTS40008': "OAuth2IdPUnretryableServerError - There's an issue "
                'with your federated Identity Provider. Contact your '
                'IDP to resolve this issue.',
 'AADSTS40009': "OAuth2IdPRefreshTokenRedemptionUserError - There's an "
                'issue with your federated Identity Provider. Contact '
                'your IDP to resolve this issue.',
 'AADSTS40010': "OAuth2IdPRetryableServerError - There's an issue with "
                'your federated Identity Provider. Contact your IDP to '
                'resolve this issue.',
 'AADSTS40015': "OAuth2IdPAuthCodeRedemptionUserError - There's an "
                'issue with your federated Identity Provider. Contact '
                'your IDP to resolve this issue.',
 'AADSTS50000': "TokenIssuanceError - There's an issue with the "
                'sign-in service. Open a support ticket to resolve '
                'this issue.',
 'AADSTS50001': 'InvalidResource - The resource is disabled or does '
                "not exist. Check your app's code to ensure that you "
                'have specified the exact resource URL for the '
                'resource you are trying to access.',
 'AADSTS50002': 'NotAllowedTenant - Sign-in failed because of a '
                "restricted proxy access on the tenant. If it's your "
                'own tenant policy, you can change your restricted '
                'tenant settings to fix this issue.',
 'AADSTS50003': 'MissingSigningKey - Sign-in failed because of a '
                'missing signing key or certificate. This might be '
                'because there was no signing key configured in the '
                'app. Check out the resolutions outlined at '
                '../manage-apps/application-sign-in-problem-federated-sso-gallery.md#certificate-or-key-not-configured. '
                'If you still see issues, contact the app owner or an '
                'app admin.',
 'AADSTS50005': 'DevicePolicyError - User tried to log in to a device '
                "from a platform that's currently not supported "
                'through Conditional Access policy.',
 'AADSTS50006': 'InvalidSignature - Signature verification failed '
                'because of an invalid signature.',
 'AADSTS50007': 'PartnerEncryptionCertificateMissing - The partner '
                'encryption certificate was not found for this app. '
                'Open a support ticket with Microsoft to get this '
                'fixed.',
 'AADSTS50008': 'InvalidSamlToken - SAML assertion is missing or '
                'misconfigured in the token. Contact your federation '
                'provider.',
 'AADSTS50010': 'AudienceUriValidationFailed - Audience URI validation '
                'for the app failed since no token audiences were '
                'configured.',
 'AADSTS50011': 'InvalidReplyTo - The reply address is missing, '
                'misconfigured, or does not match reply addresses '
                'configured for the app.  As a resolution ensure to '
                'add this missing reply address to the Azure Active '
                'Directory application or have someone with the '
                'permissions to manage your application in Active '
                'Directory do this for you.',
 'AADSTS50012': 'AuthenticationFailed - Authentication failed for one '
                'of the following reasons:The subject name of the '
                'signing certificate is not authorizedA matching '
                'trusted authority policy was not found for the '
                'authorized subject nameThe certificate chain is not '
                'validThe signing certificate is not validPolicy is '
                'not configured on the tenantThumbprint of the signing '
                'certificate is not authorizedClient assertion '
                'contains an invalid signature',
 'AADSTS50013': 'InvalidAssertion - Assertion is invalid because of '
                "various reasons - The token issuer doesn't match the "
                'api version within its valid time range -expired '
                '-malformed - Refresh token in the assertion is not a '
                'primary refresh token.',
 'AADSTS50014': "GuestUserInPendingState - The user's redemption is in "
                'a pending state. The guest user account is not fully '
                'created yet.',
 'AADSTS50015': 'ViralUserLegalAgeConsentRequiredState - The user '
                'requires legal age group consent.',
 'AADSTS50017': 'CertificateValidationFailed - Certification '
                'validation failed, reasons for the following '
                'reasons:Cannot find issuing certificate in trusted '
                'certificates listUnable to find expected '
                'CrlSegmentCannot find issuing certificate in trusted '
                'certificates listDelta CRL distribution point is '
                'configured without a corresponding CRL distribution '
                'pointUnable to retrieve valid CRL segments because of '
                'a timeout issueUnable to download CRLContact the '
                'tenant admin.',
 'AADSTS50020': 'UserUnauthorized - Users are unauthorized to call '
                'this endpoint.',
 'AADSTS50027': 'InvalidJwtToken - Invalid JWT token because of the '
                "following reasons:doesn't contain nonce claim, sub "
                'claimsubject identifier mismatchduplicate claim in '
                'idToken claimsunexpected issuerunexpected audiencenot '
                'within its valid time range token format is not '
                'properExternal ID token from issuer failed signature '
                'verification.',
 'AADSTS50029': 'Invalid URI - domain name contains invalid '
                'characters. Contact the tenant admin.',
 'AADSTS50032': 'WeakRsaKey - Indicates the erroneous user attempt to '
                'use a weak RSA key.',
 'AADSTS50033': 'RetryableError - Indicates a transient error not '
                'related to the database operations.',
 'AADSTS50034': 'UserAccountNotFound - To sign into this application, '
                'the account must be added to the directory.',
 'AADSTS50042': 'UnableToGeneratePairwiseIdentifierWithMissingSalt - '
                'The salt required to generate a pairwise identifier '
                'is missing in principle. Contact the tenant admin.',
 'AADSTS50043': 'UnableToGeneratePairwiseIdentifierWithMultipleSalts',
 'AADSTS50048': 'SubjectMismatchesIssuer - Subject mismatches Issuer '
                'claim in the client assertion. Contact the tenant '
                'admin.',
 'AADSTS50049': 'NoSuchInstanceForDiscovery - Unknown or invalid '
                'instance.',
 'AADSTS50050': 'MalformedDiscoveryRequest - The request is malformed.',
 'AADSTS50053': 'IdsLocked - The account is locked because the user '
                'tried to sign in too many times with an incorrect '
                'user ID or password.',
 'AADSTS50055': 'InvalidPasswordExpiredPassword - The password is '
                'expired.',
 'AADSTS50056': 'Invalid or null password -Password does not exist in '
                'store for this user.',
 'AADSTS50057': 'UserDisabled - The user account is disabled. The '
                'account has been disabled by an administrator.',
 'AADSTS50058': 'UserInformationNotProvided - This means that a user '
                "is not signed in. This is a common error that's "
                'expected when a user is unauthenticated and has not '
                'yet signed in.If this error is encouraged in an SSO '
                'context where the user has previously signed in, this '
                'means that the SSO session was either not found or '
                'invalid.This error may be returned to the application '
                'if prompt=none is specified.',
 'AADSTS50059': 'MissingTenantRealmAndNoUserInformationProvided - '
                'Tenant-identifying information was not found in '
                'either the request or implied by any provided '
                'credentials. The user can contact the tenant admin to '
                'help resolve the issue.',
 'AADSTS50061': 'SignoutInvalidRequest - The sign-out request is '
                'invalid.',
 'AADSTS50064': 'CredentialAuthenticationError - Credential validation '
                'on username or password has failed.',
 'AADSTS50068': 'SignoutInitiatorNotParticipant - Sign out has failed. '
                'The app that initiated sign out is not a participant '
                'in the current session.',
 'AADSTS50070': 'SignoutUnknownSessionIdentifier - Sign out has '
                'failed. The sign out request specified a name '
                "identifier that didn't match the existing session(s).",
 'AADSTS50071': 'SignoutMessageExpired - The logout request has '
                'expired.',
 'AADSTS50072': 'UserStrongAuthEnrollmentRequiredInterrupt - User '
                'needs to enroll for second factor authentication '
                '(interactive).',
 'AADSTS50074': 'UserStrongAuthClientAuthNRequiredInterrupt - Strong '
                'authentication is required and the user did not pass '
                'the MFA challenge.',
 'AADSTS50076': 'UserStrongAuthClientAuthNRequired - Due to a '
                'configuration change made by the admin, or because '
                'you moved to a new location, the user must use '
                'multi-factor authentication to access the resource. '
                'Retry with a new authorize request for the resource.',
 'AADSTS50079': 'UserStrongAuthEnrollmentRequired - Due to a '
                'configuration change made by the administrator, or '
                'because the user moved to a new location, the user is '
                'required to use multi-factor authentication.',
 'AADSTS50085': 'Refresh token needs social IDP login. Have user try '
                'signing-in again with username -password',
 'AADSTS50086': 'SasNonRetryableError',
 'AADSTS50087': 'SasRetryableError - The service is temporarily '
                'unavailable. Try again.',
 'AADSTS50089': 'Flow token expired - Authentication Failed. Have the '
                'user try signing-in again with username -password.',
 'AADSTS50097': 'DeviceAuthenticationRequired - Device authentication '
                'is required.',
 'AADSTS50099': 'PKeyAuthInvalidJwtUnauthorized - The JWT signature is '
                'invalid.',
 'AADSTS50105': 'EntitlementGrantsNotFound - The signed in user is not '
                'assigned to a role for the signed in app. Assign the '
                'user  to the app. For more '
                'information:../manage-apps/application-sign-in-problem-federated-sso-gallery.md#user-not-assigned-a-role.',
 'AADSTS50107': 'InvalidRealmUri - The requested federation realm '
                'object does not exist. Contact the tenant admin.',
 'AADSTS50120': 'ThresholdJwtInvalidJwtFormat - Issue with JWT header. '
                'Contact the tenant admin.',
 'AADSTS50124': 'ClaimsTransformationInvalidInputParameter - Claims '
                'Transformation contains invalid input parameter. '
                'Contact the tenant admin to update the policy.',
 'AADSTS50125': 'PasswordResetRegistrationRequiredInterrupt - Sign-in '
                'was interrupted because of a password reset or '
                'password registration entry.',
 'AADSTS50126': 'InvalidUserNameOrPassword - Error validating '
                'credentials due to invalid username or password.',
 'AADSTS50127': 'BrokerAppNotInstalled - User needs to install a '
                'broker app to gain access to this content.',
 'AADSTS50128': 'Invalid domain name - No tenant-identifying '
                'information found in either the request or implied by '
                'any provided credentials.',
 'AADSTS50129': 'DeviceIsNotWorkplaceJoined - Workplace join is '
                'required to register the device.',
 'AADSTS50131': 'ConditionalAccessFailed - Indicates various '
                'Conditional Access errors such as bad Windows device '
                'state, request blocked due to suspicious activity, '
                'access policy, or security policy decisions.',
 'AADSTS50132': 'SsoArtifactInvalidOrExpired - The session is not '
                'valid due to password expiration or recent password '
                'change.',
 'AADSTS50133': 'SsoArtifactRevoked - The session is not valid due to '
                'password expiration or recent password change.',
 'AADSTS50134': 'DeviceFlowAuthorizeWrongDatacenter - Wrong data '
                'center. To authorize a request that was initiated by '
                'an app in the OAuth 2.0 device flow, the authorizing '
                'party must be in the same data center where the '
                'original request resides.',
 'AADSTS50135': 'PasswordChangeCompromisedPassword - Password change '
                'is required due to account risk.',
 'AADSTS50136': 'RedirectMsaSessionToApp - Single MSA session '
                'detected.',
 'AADSTS50139': 'SessionMissingMsaOAuth2RefreshToken - The session is '
                'invalid due to a missing external refresh token.',
 'AADSTS50140': 'KmsiInterrupt - This error occurred due to "Keep me '
                'signed in" interrupt when the user was signing-in. '
                'Open a support ticket with Correlation ID, Request '
                'ID, and Error code to get more details.',
 'AADSTS50143': 'Session mismatch - Session is invalid because user '
                'tenant does not match the domain hint due to '
                'different resource. Open a support ticket with '
                'Correlation ID, Request ID, and Error code to get '
                'more details.',
 'AADSTS50144': "InvalidPasswordExpiredOnPremPassword - User's Active "
                'Directory password has expired. Generate a new '
                'password for the user or have the user use the '
                'self-service reset tool to reset their password.',
 'AADSTS50146': 'MissingCustomSigningKey - This app is required to be '
                'configured with an app-specific signing key. It is '
                'either not configured with one, or the key has '
                'expired or is not yet valid.',
 'AADSTS50147': 'MissingCodeChallenge - The size of the code challenge '
                'parameter is not valid.',
 'AADSTS50155': 'DeviceAuthenticationFailed - Device authentication '
                'failed for this user.',
 'AADSTS50158': 'ExternalSecurityChallenge - External security '
                'challenge was not satisfied.',
 'AADSTS50161': 'InvalidExternalSecurityChallengeConfiguration - '
                'Claims sent by external provider is not enough or '
                'Missing claim requested to external provider.',
 'AADSTS50166': 'ExternalClaimsProviderThrottled - Failed to send the '
                'request to the claims provider.',
 'AADSTS50168': 'ChromeBrowserSsoInterruptRequired - The client is '
                'capable of obtaining an SSO token through the Windows '
                '10 Accounts extension, but the token was not found in '
                'the request or the supplied token was expired.',
 'AADSTS50169': 'InvalidRequestBadRealm - The realm is not a '
                'configured realm of the current service namespace.',
 'AADSTS50170': 'MissingExternalClaimsProviderMapping - The external '
                'controls mapping is missing.',
 'AADSTS50177': 'ExternalChallengeNotSupportedForPassthroughUsers - '
                'External challenge is not supported for passthrough '
                'users.',
 'AADSTS50178': 'SessionControlNotSupportedForPassthroughUsers - '
                'Session control is not supported for passthrough '
                'users.',
 'AADSTS50180': 'WindowsIntegratedAuthMissing - Integrated Windows '
                'authentication is needed. Enable the tenant for '
                'Seamless SSO.',
 'AADSTS50187': 'DeviceInformationNotProvided - The service failed to '
                'perform device authentication.',
 'AADSTS50196': 'LoopDetected - A client loop has been detected. Check '
                'the app’s logic to ensure that token caching is '
                'implemented, and that error conditions are handled '
                'correctly.  The app has made too many of the same '
                'request in too short a period, indicating that it is '
                'in a faulty state or is abusively requesting tokens.',
 'AADSTS50197': 'ConflictingIdentities - The user could not be found. '
                'Try signing in again.',
 'AADSTS50199': 'CmsiInterrupt - For security reasons, user '
                'confirmation is required for this request.  Because '
                'this is an "interaction_required" error, the client '
                'should do interactive auth.  This occurs because a '
                'system webview has been used to request a token for a '
                'native application - the user must be prompted to ask '
                'if this was actually the app they meant to sign into. '
                'To avoid this prompt, the redirect URI should be part '
                'of the following safe list: '
                'http://https://msauth://(iOS only)msauthv2://(iOS '
                'only)chrome-extension:// (desktop Chrome browser '
                'only)',
 'AADSTS51000': 'RequiredFeatureNotEnabled - The feature is disabled.',
 'AADSTS51001': 'DomainHintMustbePresent - Domain hint must be present '
                'with on-premises security identifier or on-premises '
                'UPN.',
 'AADSTS51004': 'UserAccountNotInDirectory - The user account doesn’t '
                'exist in the directory.',
 'AADSTS51005': 'TemporaryRedirect - Equivalent to HTTP status 307, '
                'which indicates that the requested information is '
                'located at the URI specified in the location header. '
                'When you receive this status, follow the location '
                'header associated with the response. When the '
                'original request method was POST, the redirected '
                'request will also use the POST method.',
 'AADSTS51006': 'ForceReauthDueToInsufficientAuth - Integrated Windows '
                'authentication is needed. User logged in using a '
                'session token that is missing the Integrated Windows '
                'authentication claim. Request the  user to log in '
                'again.',
 'AADSTS52004': 'DelegationDoesNotExistForLinkedIn - The user has not '
                'provided consent for access to LinkedIn resources.',
 'AADSTS53000': 'DeviceNotCompliant - Conditional Access policy '
                'requires a compliant device, and the device is not '
                'compliant. The user must enroll their device with an '
                'approved MDM provider like Intune.',
 'AADSTS53001': 'DeviceNotDomainJoined - Conditional Access policy '
                'requires a domain joined device, and the device is '
                'not domain joined. Have the user use a domain joined '
                'device.',
 'AADSTS53002': 'ApplicationUsedIsNotAnApprovedApp - The app used is '
                'not an approved app for Conditional Access. User '
                'needs to use one of the apps from the list of '
                'approved apps to use in order to get access.',
 'AADSTS53003': 'BlockedByConditionalAccess - Access has been blocked '
                'by Conditional Access policies. The access policy '
                'does not allow token issuance.',
 'AADSTS530032': 'BlockedByConditionalAccessOnSecurityPolicy - The '
                 'tenant admin has configured a security policy that '
                 'blocks this request. Check the security policies '
                 'that are defined on the tenant level to determine if '
                 'your request meets the policy requirements.',
 'AADSTS53004': 'ProofUpBlockedDueToRisk - User needs to complete the '
                'multi-factor authentication registration process '
                'before accessing this content. User should register '
                'for multi-factor authentication.',
 'AADSTS54000': 'MinorUserBlockedLegalAgeGroupRule',
 'AADSTS65001': 'DelegationDoesNotExist - The user or administrator '
                'has not consented to use the application with ID X. '
                'Send an interactive authorization request for this '
                'user and resource.',
 'AADSTS65004': 'UserDeclinedConsent - User declined to consent to '
                'access the app. Have the user retry the sign-in and '
                'consent to the app',
 'AADSTS65005': 'MisconfiguredApplication - The app required resource '
                'access list does not contain apps discoverable by the '
                'resource or The client app has requested access to '
                'resource, which was not specified in its required '
                'resource access list or Graph service returned bad '
                'request or resource not found. If the app supports '
                'SAML, you may have configured the app with the wrong '
                'Identifier (Entity). Try out the resolution listed '
                'for SAML using the link below: '
                'https://docs.microsoft.com/azure/active-directory/application-sign-in-problem-federated-sso-gallery#no-resource-in-requiredresourceaccess-list',
 'AADSTS650052': 'The app needs access to a service ("{name}") that '
                 'your organization "{organization}" has not '
                 'subscribed to or enabled. Contact your IT Admin to '
                 'review the configuration of your service '
                 'subscriptions.',
 'AADSTS67003': 'ActorNotValidServiceIdentity',
 'AADSTS70000': 'InvalidGrant - Authentication failed. The refresh '
                'token is not valid. Error may be due to the following '
                'reasons:Token binding header is emptyToken binding '
                'hash does not match',
 'AADSTS700005': 'InvalidGrantRedeemAgainstWrongTenant - Provided '
                 'Authorization Code is intended to use against other '
                 'tenant, thus rejected. OAuth2 Authorization Code '
                 'must be redeemed against same tenant it was acquired '
                 'for (/common or /{tenant-ID} as appropriate)',
 'AADSTS70001': 'UnauthorizedClient - The application is disabled.',
 'AADSTS7000112': 'UnauthorizedClientApplicationDisabled - The '
                  'application is disabled.',
 'AADSTS700016': 'UnauthorizedClient_DoesNotMatchRequest - The '
                 "application wasn't found in the directory/tenant. "
                 'This can happen if the application has not been '
                 'installed by the administrator of the tenant or '
                 'consented to by any user in the tenant. You might '
                 'have misconfigured the identifier value for the '
                 'application or sent your authentication request to '
                 'the wrong tenant.',
 'AADSTS70002': 'InvalidClient - Error validating the credentials. The '
                'specified client_secret does not match the expected '
                'value for this client. Correct the client_secret and '
                'try again. For more info, see Use the authorization '
                'code to request an access token.',
 'AADSTS700020': 'InteractionRequired - The access grant requires '
                 'interaction.',
 'AADSTS7000215': 'Invalid client secret is provided. Developer error '
                  '- the app is attempting to sign in without the '
                  'necessary or correct authentication parameters.',
 'AADSTS700022': 'InvalidMultipleResourcesScope - The provided value '
                 "for the input parameter scope isn't valid because it "
                 'contains more than one resource.',
 'AADSTS7000222': 'InvalidClientSecretExpiredKeysProvided - The '
                  'provided client secret keys are expired. Visit the '
                  'Azure portal to create new keys for your app, or '
                  'consider using certificate credentials for added '
                  'security: https://aka.ms/certCreds',
 'AADSTS700023': 'InvalidResourcelessScope - The provided value for '
                 "the input parameter scope isn't valid when request "
                 'an access token.',
 'AADSTS70003': 'UnsupportedGrantType - The app returned an '
                'unsupported grant type.',
 'AADSTS70004': 'InvalidRedirectUri - The app returned an invalid '
                'redirect URI. The redirect address specified by the '
                'client does not match any configured addresses or any '
                'addresses on the OIDC approve list.',
 'AADSTS70005': 'UnsupportedResponseType - The app returned an '
                'unsupported response type due to the following '
                "reasons:response type 'token' is not enabled for the "
                "appresponse type 'id_token' requires the 'OpenID' "
                'scope -contains an unsupported OAuth parameter value '
                'in the encoded wctx',
 'AADSTS70007': 'UnsupportedResponseMode - The app returned an '
                'unsupported value of response_mode when requesting a '
                'token.',
 'AADSTS70008': 'ExpiredOrRevokedGrant - The refresh token has expired '
                'due to inactivity. The token was issued on XXX and '
                'was inactive for a certain amount of time.',
 'AADSTS70011': 'InvalidScope - The scope requested by the app is '
                'invalid.',
 'AADSTS70012': 'MsaServerError - A server error occurred while '
                'authenticating an MSA (consumer) user. Try again. If '
                'it continues to fail, open a support ticket ',
 'AADSTS70016': 'AuthorizationPending - OAuth 2.0 device flow error. '
                'Authorization is pending. The device will retry '
                'polling the request.',
 'AADSTS70018': 'BadVerificationCode - Invalid verification code due '
                'to User typing in wrong user code for device code '
                'flow. Authorization is not approved.',
 'AADSTS70019': 'CodeExpired - Verification code expired. Have the '
                'user retry the sign-in.',
 'AADSTS75001': 'BindingSerializationError - An error occurred during '
                'SAML message binding.',
 'AADSTS75003': 'UnsupportedBindingError - The app returned an error '
                'related to unsupported binding (SAML protocol '
                'response cannot be sent via bindings other than HTTP '
                'POST).',
 'AADSTS75005': 'Saml2MessageInvalid - Azure AD doesn’t support the '
                'SAML request sent by the app for SSO.',
 'AADSTS7500514': 'A supported type of SAML response was not found. '
                  "The supported response types are 'Response' (in XML "
                  "namespace 'urn:oasis:names:tc:SAML:2.0:protocol') "
                  "or 'Assertion' (in XML namespace "
                  "'urn:oasis:names:tc:SAML:2.0:assertion'). "
                  'Application error - the developer will handle this '
                  'error.',
 'AADSTS7500529': 'The value ‘SAMLId-Guid’ is not a valid SAML ID - '
                  'Azure AD uses this attribute to populate the '
                  'InResponseTo attribute of the returned response. ID '
                  'must not begin with a number, so a common strategy '
                  'is to prepend a string like "id" to the string '
                  'representation of a GUID. For example, '
                  'id6c1c178c166d486687be4aaf5e482730 is a valid ID.',
 'AADSTS75008': 'RequestDeniedError - The request from the app was '
                'denied since the SAML request had an unexpected '
                'destination.',
 'AADSTS75011': 'NoMatchedAuthnContextInOutputClaims - The '
                'authentication method by which the user authenticated '
                "with the service doesn't match requested "
                'authentication method.',
 'AADSTS75016': 'Saml2AuthenticationRequestInvalidNameIDPolicy - SAML2 '
                'Authentication Request has invalid NameIdPolicy.',
 'AADSTS80001': 'OnPremiseStoreIsNotAvailable - The Authentication '
                'Agent is unable to connect to Active Directory. Make '
                'sure that agent servers are members of the same AD '
                'forest as the users whose passwords need to be '
                'validated and they are able to connect to Active '
                'Directory.',
 'AADSTS80002': 'OnPremisePasswordValidatorRequestTimedout - Password '
                'validation request timed out. Make sure that Active '
                'Directory is available and responding to requests '
                'from the agents.',
 'AADSTS80005': 'OnPremisePasswordValidatorUnpredictableWebException - '
                'An unknown error occurred while processing the '
                'response from the Authentication Agent. Retry the '
                'request. If it continues to fail, open a support '
                'ticket to get more details on the error.',
 'AADSTS80007': 'OnPremisePasswordValidatorErrorOccurredOnPrem - The '
                "Authentication Agent is unable to validate user's "
                'password. Check the agent logs for more info and '
                'verify that Active Directory is operating as '
                'expected.',
 'AADSTS80010': 'OnPremisePasswordValidationEncryptionException - The '
                'Authentication Agent is unable to decrypt password.',
 'AADSTS80012': 'OnPremisePasswordValidationAccountLogonInvalidHours - '
                'The users attempted to log on outside of the allowed '
                'hours (this is specified in AD).',
 'AADSTS80013': 'OnPremisePasswordValidationTimeSkew - The '
                'authentication attempt could not be completed due to '
                'time skew between the machine running the '
                'authentication agent and AD. Fix time sync issues.',
 'AADSTS81004': 'DesktopSsoIdentityInTicketIsNotAuthenticated - '
                'Kerberos authentication attempt failed.',
 'AADSTS81005': 'DesktopSsoAuthenticationPackageNotSupported - The '
                'authentication package is not supported.',
 'AADSTS81006': 'DesktopSsoNoAuthorizationHeader - No authorization '
                'header was found.',
 'AADSTS81007': 'DesktopSsoTenantIsNotOptIn - The tenant is not '
                'enabled for Seamless SSO.',
 'AADSTS81009': 'DesktopSsoAuthorizationHeaderValueWithBadFormat - '
                "Unable to validate user's Kerberos ticket.",
 'AADSTS81010': 'DesktopSsoAuthTokenInvalid - Seamless SSO failed '
                "because the user's Kerberos ticket has expired or is "
                'invalid.',
 'AADSTS81011': 'DesktopSsoLookupUserBySidFailed - Unable to find user '
                "object based on information in the user's Kerberos "
                'ticket.',
 'AADSTS81012': 'DesktopSsoMismatchBetweenTokenUpnAndChosenUpn - The '
                'user trying to sign in to Azure AD is different from '
                'the user signed into the device.',
 'AADSTS90002': "InvalidTenantName - The tenant name wasn't found in "
                'the data store. Check to make sure you have the '
                'correct tenant ID.',
 'AADSTS90004': 'InvalidRequestFormat - The request is not properly '
                'formatted.',
 'AADSTS90005': 'InvalidRequestWithMultipleRequirements - Unable to '
                'complete the request. The request is not valid '
                "because the identifier and login hint can't be used "
                'together.',
 'AADSTS90006': 'ExternalServerRetryableError - The service is '
                'temporarily unavailable.',
 'AADSTS90007': 'InvalidSessionId - Bad request. The passed session ID '
                "can't be parsed.",
 'AADSTS90008': 'TokenForItselfRequiresGraphPermission - The user or '
                "administrator hasn't consented to use the "
                'application. At the minimum, the application requires '
                'access to Azure AD by specifying the sign-in and read '
                'user profile permission.',
 'AADSTS90009': 'TokenForItselfMissingIdenticalAppIdentifier - The '
                'application is requesting a token for itself. This '
                "scenario is supported only if the resource that's "
                'specified is using the GUID-based application ID.',
 'AADSTS90010': 'NotSupported - Unable to create the algorithm.',
 'AADSTS90012': 'RequestTimeout - The requested has timed out.',
 'AADSTS90013': 'InvalidUserInput - The input from the user is not '
                'valid.',
 'AADSTS90014': 'MissingRequiredField - This error code may appear in '
                'various cases when an expected field is not present '
                'in the credential.',
 'AADSTS90015': 'QueryStringTooLong - The query string is too long.',
 'AADSTS90016': "MissingRequiredClaim - The access token isn't valid. "
                'The required claim is missing.',
 'AADSTS90019': 'MissingTenantRealm - Azure AD was unable to determine '
                'the tenant identifier from the request.',
 'AADSTS90022': 'AuthenticatedInvalidPrincipalNameFormat - The '
                'principal name format is not valid, or does not meet '
                'the expected name[/host][@realm] format. The '
                'principal name is required, host and realm are '
                'optional and may be set to null.',
 'AADSTS90023': 'InvalidRequest - The authentication service request '
                'is not valid.',
 'AADSTS9002313': 'InvalidRequest - Request is malformed or invalid. - '
                  'The issue here is because there was something wrong '
                  'with the request to a certain endpoint. The '
                  'suggestion to this issue is to get a fiddler trace '
                  'of the error occurring and looking to see if the '
                  'request is actually properly formatted or not.',
 'AADSTS90024': 'RequestBudgetExceededError - A transient error has '
                'occurred. Try again.',
 'AADSTS90033': 'MsodsServiceUnavailable - The Microsoft Online '
                'Directory Service (MSODS) is not available.',
 'AADSTS90036': 'MsodsServiceUnretryableFailure - An unexpected, '
                'non-retryable error from the WCF service hosted by '
                'MSODS has occurred. Open a support ticket to get more '
                'details on the error.',
 'AADSTS90038': 'NationalCloudTenantRedirection - The specified tenant '
                "'Y' belongs to the National Cloud 'X'. Current cloud "
                "instance 'Z' does not federate with X. A cloud "
                'redirect error is returned.',
 'AADSTS900382': 'Confidential Client is not supported in Cross Cloud '
                 'request.',
 'AADSTS90043': 'NationalCloudAuthCodeRedirection - The feature is '
                'disabled.',
 'AADSTS90051': 'InvalidNationalCloudId - The national cloud '
                'identifier contains an invalid cloud identifier.',
 'AADSTS90055': 'TenantThrottlingError - There are too many incoming '
                'requests. This exception is thrown for blocked '
                'tenants.',
 'AADSTS90056': 'BadResourceRequest - To redeem the code for an access '
                'token, the app should send a POST request to the '
                '/token endpoint. Also, prior to this, you should '
                'provide an authorization code and send it in the POST '
                'request to the /token endpoint. Refer to this article '
                'for an overview of OAuth 2.0 authorization code flow: '
                '../azuread-dev/v1-protocols-oauth-code.md. Direct the '
                'user to the /authorize endpoint, which will return an '
                'authorization_code. By posting a request to the '
                '/token endpoint, the user gets the access token. Log '
                'in the Azure portal, and check App registrations > '
                'Endpoints to confirm that the two endpoints were '
                'configured correctly.',
 'AADSTS90072': 'PassThroughUserMfaError - The external account that '
                "the user signs in with doesn't exist on the tenant "
                "that they signed into; so the user can't satisfy the "
                'MFA requirements for the tenant. The account must be '
                'added as an external user in the tenant first. Sign '
                'out and sign in with a different Azure AD user '
                'account.',
 'AADSTS90081': 'OrgIdWsFederationMessageInvalid - An error occurred '
                'when the service tried to process a WS-Federation '
                'message. The message is not valid.',
 'AADSTS90082': 'OrgIdWsFederationNotSupported - The selected '
                "authentication policy for the request isn't currently "
                'supported.',
 'AADSTS90084': 'OrgIdWsFederationGuestNotAllowed - Guest accounts '
                "aren't allowed for this site.",
 'AADSTS90085': 'OrgIdWsFederationSltRedemptionFailed - The service is '
                'unable to issue a token because the company object '
                "hasn't been provisioned yet.",
 'AADSTS90086': 'OrgIdWsTrustDaTokenExpired - The user DA token is '
                'expired.',
 'AADSTS90087': 'OrgIdWsFederationMessageCreationFromUriFailed - An '
                'error occurred while creating the WS-Federation '
                'message from the URI.',
 'AADSTS90090': 'GraphRetryableError - The service is temporarily '
                'unavailable.',
 'AADSTS90091': 'GraphServiceUnreachable',
 'AADSTS90092': 'GraphNonRetryableError',
 'AADSTS90093': 'GraphUserUnauthorized - Graph returned with a '
                'forbidden error code for the request.',
 'AADSTS90094': 'AdminConsentRequired - Administrator consent is '
                'required.',
 'AADSTS90099': "The application '{appId}' ({appName}) has not been "
                "authorized in the tenant '{tenant}'. Applications "
                'must be authorized to access the customer tenant '
                'before partner delegated administrators can use them. '
                'Provide pre-consent or execute the appropriate '
                'Partner Center API to authorize the application.',
 'AADSTS90100': 'InvalidRequestParameter - The parameter is empty or '
                'not valid.',
 'AADSTS901002': "AADSTS901002: The 'resource' request parameter is "
                 'not supported.',
 'AADSTS90101': "InvalidEmailAddress - The supplied data isn't a valid "
                'email address. The email address must be in the '
                'format someone@example.com.',
 'AADSTS90102': 'InvalidUriParameter - The value must be a valid '
                'absolute URI.',
 'AADSTS90107': 'InvalidXml - The request is not valid. Make sure your '
                "data doesn't have invalid characters.",
 'AADSTS90114': 'InvalidExpiryDate - The bulk token expiration '
                'timestamp will cause an expired token to be issued.',
 'AADSTS90117': 'InvalidRequestInput',
 'AADSTS90119': 'InvalidUserCode - The user code is null or empty.',
 'AADSTS90120': 'InvalidDeviceFlowRequest - The request was already '
                'authorized or declined.',
 'AADSTS90121': 'InvalidEmptyRequest - Invalid empty request.',
 'AADSTS90123': "IdentityProviderAccessDenied - The token can't be "
                'issued because the identity or claim issuance '
                'provider denied the request.',
 'AADSTS90124': 'V1ResourceV2GlobalEndpointNotSupported - The resource '
                'is not supported over the /common or /consumers '
                'endpoints. Use the /organizations or tenant-specific '
                'endpoint instead.',
 'AADSTS90125': "DebugModeEnrollTenantNotFound - The user isn't in the "
                'system. Make sure you entered the user name '
                'correctly.',
 'AADSTS90126': 'DebugModeEnrollTenantNotInferred - The user type is '
                "not supported on this endpoint. The system can't "
                "infer the user's tenant from the user name.",
 'AADSTS90130': 'NonConvergedAppV2GlobalEndpointNotSupported - The '
                'application is not supported over the /common or '
                '/consumers endpoints. Use the /organizations or '
                'tenant-specific endpoint instead.'}

# Client ID Source: https://github.com/Gerenios/AADInternals/blob/master/AccessToken_utils.ps1#L11
# Parsed Structure: {client:{tag:ID}}

COMMON_CLIENT_IDS = CIDS = \
{'aad_account': {'https://account.activedirectory.windowsazure.com': ['0000000c-0000-0000-c000-000000000000']},
 'aadconnectv2': {'AADConnectv2': ['6eb59a73-39b2-4c23-a70f-e2e3ce8965b1']},
 'aadrm': {'AADRM': ['90f610bf-206d-4950-b61d-37fa6fd1b224']},
 'aadsync': {'AzureADSync': ['cb1056e2-e479-49de-ae31-7812af012ed8']},
 'az': {'AADJCSP': ['b90d5b8f-5503-4153-b545-b31cecfaece2'],
        'AADPinredemptionclient': ['06c6433f-4fb8-4670-b2cd-408938296b8e'],
        'AZPowerShellModule': ['1950a258-227b-4e31-a9cf-717495945fc2'],
        'AppleInternetAccounts': ['f8d98a96-0999-43f5-8af3-69971c7bb423'],
        'AuthenticatorAppresource:ff9ebd75-fe62-434a-a6ce-b3f0a8592eaf': ['4813382a-8fa7-425e-ab75-3b753aab3abb'],
        'AzureAndroidApp': ['0c1307d4-29d6-4389-a11c-5cbe7f65d7fa'],
        'IntuneMAMclientresource:https://intunemam.microsoftonline.com': ['6c7e8096-f593-4d72-807f-a5f86dcc9c77'],
        'Microsoft.AAD.BrokerPluginresource:https://cs.dds.microsoft.com': ['6f7e0f60-9401-4f5b-98e2-cf15bd5fd5e3'],
        'MicrosoftAADCloudAP': ['38aa3b87-a06d-4817-b275–7a316988d93b'],
        'MicrosoftAuthenticationBroker(AzureMDMclient)': ['29d9ed98-a469-4536-ade2-f981bc1d605e'],
        'MicrosoftExchangeRESTAPIBasedPowershell': ['fb78d390-0c51-40cd-8e17-fdbfab77341b'],
        'Microsoft_AAD_RegisteredApps': ['18ed3507-a475-4ccb-b669-d66bc9f2a36e'],
        'Office365Management(mobileapp)': ['00b41c95-dab0-4487-9791-b9d2c32c80f2'],
        'SPOManagementShell': ['9bc3ab49-b65d-410a-85ad-de819febfddc'],
        'Teamsclient': ['1fec8e78-bce4-4aaf-ab1b-5451cc387264'],
        'WindowsConfigurationDesigner(WCD)': ['de0853a1-ab20-47bd-990b-71ad5077ac7b'],
        'code-try-0': ['7f59a773-2eaf-429c-a059-50fc5bb28b44'],
        'https://mysignins.microsoft.com': ['19db86c3-b2b9-44cc-b339-36da233a3be2']},
 'azure_mgmt': {'WindowsAzureServiceManagementAPI': ['84070985-06ea-473d-82fe-eb82b4011c9d']},
 'azureadmin': {'AzureAdminwebui': ['c44b4083-3bb0-49c1-b47d-974e53cbdf3c']},
 'azuregraphclientint': {'MicrosoftAzureGraphClientLibrary2.1.9Internal': ['7492bca1-9461-4d94-8eb8-c17896c61205']},
 'dynamicscrm': {'DynamicsCRM': ['00000007-0000-0000-c000-000000000000']},
 'exo': {'EXORemotePowerShell': ['a0c73c16-a7e3-4564-9a95-2bdf47383716']},
 'graph_api': {'MSGraphAPI': ['1b730954-1685-4b74-9bfd-dac224a7b894']},
 'msmamservice': {'MSMAMServiceAPI': ['27922004-5251-4030-b22d-91ecd9a37ea4']},
 'o365exo': {'ExchangeOnline': ['00000002-0000-0ff1-ce00-000000000000']},
 'o365spo': {'SharePointOnline': ['00000003-0000-0ff1-ce00-000000000000']},
 'o365suiteux': {'O365SuiteUX': ['4345a7b9-9a63-4910-a426-35363201d503']},
 'office': {'Office,ref.https://docs.microsoft.com/en-us/office/dev/add-ins/develop/register-sso-add-in-aad-v2': ['d3590ed6-52b3-4102-aeff-aad2292ab01c']},
 'office_mgmt': {'OfficeManagementAPIEditorhttps://manage.office.com': ['389b1b32-b5d5-43b2-bddc-84ce938d6737']},
 'office_online': {'OutlookOnlineAdd-inApp': ['bc59ab01-8403-45c6-8796-ac3ef710b3e3']},
 'office_online2': {'SharePointOnlineClient': ['57fb890c-0dab-4253-a5e0-7188c88b2bb4']},
 'onedrive': {'OneDriveSyncEngine': ['ab9b8c07-8f02-4f72-87fa-80105867a763']},
 'patnerdashboard': {'Partnerdashboard(missingonletter?)': ['4990cffe-04e8-4e8b-808a-1175604b879']},
 'powerbi_contentpack': {'PowerBIcontentpack': ['2a0c3efa-ba54-4e55-bdc0-770f9e39e9ee']},
 'pta': {'Pass-throughauthentication': ['cb1056e2-e479-49de-ae31-7812af012ed8']},
 'sara': {'MicrosoftSupportandRecoveryAssistant(SARA)': ['d3590ed6-52b3-4102-aeff-aad2292ab01c']},
 'skype': {'Skype': ['d924a533-3729-4708-b3e8-1d2445af35e3']},
 'synccli': {'Syncclient': ['1651564e-7ce4-4d99-88be-0a65050d8dc3']},
 'teams': {'Teams': ['1fec8e78-bce4-4aaf-ab1b-5451cc387264']},
 'teamswebclient': {'Teamswebclient': ['5e3ce6c0-2b1f-4285-8d4b-75ee78787346']},
 'webshellsuite': {'Office365ShellWCSS-Client': ['89bee1f7-5e6e-4d8a-9f3d-ecd601259da7']},
 'www': {'Officeportal': ['00000006-0000-0ff1-ce00-000000000000']}}

RESOURCES = \
{'aad_graph_api': 'https://graph.windows.net',
 'ms_graph_api': 'https://graph.microsoft.com',
 'azure_mgmt_api': 'https://management.azure.com',
 'windows_net_mgmt_api': 'https://management.core.windows.net/',
 'cloudwebappproxy': 'https://proxy.cloudwebappproxy.net/registerapp',
 'officeapps': 'https://officeapps.live.com',
 'outlook': 'https://outlook.office365.com',
 'webshellsuite': 'https://webshell.suite.office.com',
 'sara': 'https://api.diagnostics.office.com',
 'office_mgmt': 'https://manage.office.com',
 'msmamservice': 'https://msmamservice.api.application',
 'spacesapi': 'https://api.spaces.skype.com'}

# ==============================================
# CLIENT IDS KNOWN TO WORK WITH ANY RESOURCE URL
# ==============================================

MSOL_UNIVERSAL_CLIENT_IDS = \
['1b730954-1685-4b74-9bfd-dac224a7b894', 
  '90f610bf-206d-4950-b61d-37fa6fd1b224',
  'a0c73c16-a7e3-4564-9a95-2bdf47383716',
  'd924a533-3729-4708-b3e8-1d2445af35e3',
  '00000006-0000-0ff1-ce00-000000000000',
  '00000003-0000-0ff1-ce00-000000000000',
  '00000002-0000-0ff1-ce00-000000000000',
  '00000007-0000-0000-c000-000000000000',
  '4345a7b9-9a63-4910-a426-35363201d503',
  'cb1056e2-e479-49de-ae31-7812af012ed8',
  'c44b4083-3bb0-49c1-b47d-974e53cbdf3c',
  'cb1056e2-e479-49de-ae31-7812af012ed8',
  '89bee1f7-5e6e-4d8a-9f3d-ecd601259da7',
  '1fec8e78-bce4-4aaf-ab1b-5451cc387264',
  'd3590ed6-52b3-4102-aeff-aad2292ab01c',
  '57fb890c-0dab-4253-a5e0-7188c88b2bb4',
  'bc59ab01-8403-45c6-8796-ac3ef710b3e3',
  '2a0c3efa-ba54-4e55-bdc0-770f9e39e9ee',
  '0000000c-0000-0000-c000-000000000000',
  'd3590ed6-52b3-4102-aeff-aad2292ab01c',
  '389b1b32-b5d5-43b2-bddc-84ce938d6737',
  'ab9b8c07-8f02-4f72-87fa-80105867a763',
  '27922004-5251-4030-b22d-91ecd9a37ea4',
  '5e3ce6c0-2b1f-4285-8d4b-75ee78787346',
  '1950a258-227b-4e31-a9cf-717495945fc2',
  'f8d98a96-0999-43f5-8af3-69971c7bb423',
  '7f59a773-2eaf-429c-a059-50fc5bb28b44',
  '9bc3ab49-b65d-410a-85ad-de819febfddc',
  '19db86c3-b2b9-44cc-b339-36da233a3be2',
  '00b41c95-dab0-4487-9791-b9d2c32c80f2',
  '29d9ed98-a469-4536-ade2-f981bc1d605e',
  '6f7e0f60-9401-4f5b-98e2-cf15bd5fd5e3',
  '0c1307d4-29d6-4389-a11c-5cbe7f65d7fa',
  '6c7e8096-f593-4d72-807f-a5f86dcc9c77',
  '4813382a-8fa7-425e-ab75-3b753aab3abb',
  '1fec8e78-bce4-4aaf-ab1b-5451cc387264',
  'de0853a1-ab20-47bd-990b-71ad5077ac7b',
  'b90d5b8f-5503-4153-b545-b31cecfaece2',
  'fb78d390-0c51-40cd-8e17-fdbfab77341b',
  '18ed3507-a475-4ccb-b669-d66bc9f2a36e']
