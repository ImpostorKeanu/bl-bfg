
from logging import getLogger, INFO
from bfg.args import argument, getArgDefaults

getLogger('urllib3.connectionpool').setLevel(INFO)

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 ' \
        'Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko' \
        ') Chrome/85.0.4183.121 Mobile Safari/537.36'

@getArgDefaults
def getDefaults():
    return DEFAULTS

@argument
def url(name_or_flags=('--url',),
        required=True,
        help='The URL to target. Required: %(required)s'):
    pass

@argument
def proxies(name_or_flags=('--proxies',),
        required=False,
        nargs='+',
        help='Space delimited proxies to use. Each value should '
            'be in URL format, prefixed with the target HTTP protocol. '
            'If you\'re using an HTTPS application through Burp, '
            'for instance, then you would need to prefix the target '
            'application URL with "https:", e.g. '
            'https:http://localhost:8080. If the proxy is Socks5, then '
            'it becomes https:socks5://localhost:1080. Required: '
            '%(required)s'):
    pass

@argument
def headers(name_or_flags=('--headers',),
        required=False,
        help='Space delimited static HTTP headers to pass along to '
            'each request. Note that each header must be formatted '
            'as follows: "Header: value". Required: %(required)s'):
    pass

@argument
def verify_ssl(name_or_flags=('--verify-ssl',),
        action='BoolAction',
        default=False,
        help='Determines if SSL certificate verification occurs. '
            'Default: %(default)s'):
    pass

@argument
def user_agent(name_or_flags=('--user-agent',),
        default=DEFAULT_USER_AGENT,
        help='User-Agent string value. Default: %(default)s'):
    pass

@argument
def allow_redirects(name_or_flags=('--allow-redirects',),
        action='BoolAction',
        default=False,
        help='Determines if redirects should be followed. '
            'Default: %(default)s'):
    pass

URL = url()
PROXIES = proxies()
HEADERS = headers()
VERIFY_SSL = verify_ssl()
USER_AGENT = user_agent()
ALLOW_REDIRECTS = allow_redirects()

DEFAULTS = {
    'url':URL,
    'proxies':PROXIES,
    'headers':HEADERS,
    'verify_ssl':VERIFY_SSL,
    'user_agent':USER_AGENT,
    'allow_redirects':ALLOW_REDIRECTS,
}



