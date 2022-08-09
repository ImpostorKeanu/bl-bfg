import argparse
import inspect
import re
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union
from bfg.errors import LockoutError
from bfg.breakers import (
    BaseBreaker,
    ThresholdBreakerProfile,
    LockoutErrorBreakerProfile)

class ContributorModel(BaseModel):
    '''Define contributor data structure.'''

    name: str
    additional: Optional[dict]

class ModuleAttributes(BaseModel):
    '''Attrubtes profile for all modules.'''

    brief_description: str
    'Brief description that will be displayed in the help menu.'

    description: str
    'Lengthier description that will be displayed in module help.'

    contributors: List[ContributorModel] = Field(default_factory=list)
    'List of people who contributed to module development.'

    references: List[str] = Field(default_factory=list)
    'List of string references for the module.'

    verified_functional: Optional[bool] = False
    'Boolean flag that determines if the module has been verified ' \
    'as functional.'

    checks_lockout: Optional[bool] = False
    'Determines if the module raises bfg.errors.LockoutError when ' \
    'a logic suspects that a lockout event has occurred for a ' \
    'username.'

    notes: Optional[List[str]] = Field(default_factory=list)
    'List of string notes to display.'

    breaker_profiles: Optional[
            Union[
                List[BaseBreaker],
                List[ThresholdBreakerProfile]
            ]] = Field(default_factory=list)
    'List of breakers applicable to the model.'

def bindSignatureArgs(func, src:dict) -> dict:
    '''

    Args:
        func: Function/method from which the signature will be sourced.
        src: Source dictionary that will provide values for dest.

    Returns:
        A new dictionary with argument values from src set
        in dest.

    '''

    dest = {}

    # Iterate over paramaters and values in the function's
    # signature
    for k,v in inspect.signature(func).parameters.items():

        # Skip "self" references
        if k == 'self': continue

        # Extract the user supplied value when provided
        if k in src: dest[k]=src[k]

        # Use the default value other wise
        else: dest[k]=v

    return dest
        
class Module:
    '''Base Module Class

    This class serves as a template for brute force modules. It builds
    the interface subcommands by inspecting the __init__ method while
    also enforcing restrictions on the __call__ method to ensure
    BruteLoops can make authentication callbacks.

    The `__init__` Method:

    This method can be used to set static values supporting a brute
    force module. It's useful in situations when an upstream server
    needs to be targeted.

    The `__call__` Method:

    This method is called for each authentication attempt by BruteLoops
    and should check the validity of a username and password. The method
    signature must look like:

    ```
    def __call__(self, username, password, *args, **kwargs):
        success = False

        # Do authentication and update success to True if successful

        if success: return dict(outcome=1,username=username,password=password)
        else: return dict(outcome=0,username=username,password=password,
    ```

    Note the structure returned in the declaration above. The leading
    integer value determines if authentication was successful, indicating
    valid credentials: 1 means success, 0 means failure.
    '''

    brief_description = None
    'Brief description to display in the help menu.'

    description = None
    'Description of the module shown in the interface'

    contributors = list()
    'List of dictionaries describing contributors'

    references = list()
    'List of string references'

    verified_functional = False
    'Boolean determining if the module has been verified as functional.'

    notes = list()
    'List of string notes.'

    breaker_profiles = list()
    'List of breaker profiles.'

    checks_lockout = False
    ('Determines if the module raises LockoutError exceptions when '
    'lockouts are detected')

    @classmethod
    def initialize(cls, args:argparse.Namespace) -> 'Module':
        '''Initialize and return the underlying brute force module.

        Args:
          args: argparse.Namespace instance from which the module
            configurations will be derived.

        Notes:
          - Called by the primary brute.py application just before
            configuring the bruteloops.models.Config instance and
            starting the attack.
          - This method configures all breaker profiles.
          - When defined, this module calls the `__post_init__` method
            on the derived function.
        '''

        # Obtain breakers
        cls.cleanse_breaker_profiles()
        cls.breaker_profiles = [
            b.to_breaker(args) for b in cls.breaker_profiles
        ]

        # Translate the argparse arguments to a dictionary
        args = vars(args)

        # Initialize a dictionary to hold all of the necessary argument
        # to initialize the brute force module.
        dct = bindSignatureArgs(func=cls.__init__, src=args)

        # Initialize and return the module
        instance = cls(**dct)

        if hasattr(instance, '__post_init__'):

            instance.__post_init__(
                **bindSignatureArgs(
                    func=instance.__post_init__,
                    src=args))

        return instance

    @classmethod
    def validate(cls):
        '''Validates module configuration.

        Notes:
          - This is called by bfg.__init__ as the module is being
            loaded.
        '''

        # ==============================
        # VALIDATING THE __call__ METHOD
        # ==============================

        # Ensure that it's declared
        assert getattr(cls,'__call__'),('Modules must be callable. '
             'Declare a __call__ method on the module: ' \
             f'{cls.get_handle}')

        # Get a list of parameter names
        call_params = list(inspect.signature(cls.__call__).parameters \
                .keys())

        if call_params and call_params[0] == 'self':
            call_params = call_params[1:3]

        # Ensure there are two or greater params to be received
        assert len(call_params) == 2,('__call__ must receive at ' \
              'least two arguments: username, password')

        # Ensure that the first two are 'username' and 'password'
        assert ['username','password'] == call_params,('__call__ ' \
            'must receive the first two arguments as username, ' \
            f'password -- not: {call_params}')

    @classmethod
    def get_handle(cls):
        '''Return a simple string to use as a module identifier.

        Notes:
          - Format returned: protocol.module_directory_name
        '''

        return '.'.join(cls.__module__.split('.')[-3:][:2])

    @classmethod
    def cleanse_breaker_profiles(cls):
        '''Cleanse breaker profiles for modules by removing those
        that do not align with module configurations.

        This provides a method of removing breakers that are applied
        via inheritance.

        Currently, it only checks for the "checks_lockout" attribute,
        removing any breaker targeting "LockoutError" classes. This
        ensures that modules don't misleadingly appear to check for
        lockouts. This could lead an operator to assume that lockout
        events are not occurring, resulting in mass lockout scenarios.
        '''

        # ======================================
        # PREPARE MODULE ATTRIBUTES AS NECESSARY
        # ======================================
        
        for i in range(0, len(cls.breaker_profiles)):

            # ============================================
            # REMOVE LOCKOUT BREAKERS FROM INVALID MODULES
            # ============================================

            # Only modules with "checks_lockout" attribute should
            # accept this breaker profile.

            if not cls.checks_lockout and LockoutError in (cls
                    .breaker_profiles[i]
                    .breaker_kwargs
                    .exception_classes):

                # Remove from the module
                del(cls.breaker_profiles[i])

    @classmethod
    def build_interface(cls, subparsers: argparse.ArgumentParser):
        '''Use the inspect module to iterate over each parameter
        declared in __init__ and build an interface via argparse.

        Args:
          subparsers: Argparse subparsers that will receive the
            subcommand. Arguments are added to the supplied parser.
        '''

        cls.cleanse_breaker_profiles()

        # ==========================
        # VALIDATE MODULE ATTRIBUTES
        # ==========================

        attrs = ModuleAttributes(**{
            k:getattr(cls, k) for k in
            ModuleAttributes.__fields__.keys()
            if hasattr(cls, k)})

        # ==============
        # PREPARE EPILOG
        # ==============

        epilog = ''
        if attrs.contributors:

            epilog = 'Contributors:\n\n'

            for c in attrs.contributors:
                epilog += f'\n- {c.name}'
                if c.additional:
                    for k,v in c.additional.items():
                        epilog += f'\n  {k}: {v}'

                epilog += '\n'

        if attrs.references:

            epilog += f'\nReferences:\n'
            for ref in attrs.references:
                epilog += f'\n- {ref}'

        # Handle notes
        if attrs.notes:
            epilog += f'\n\nNotes:\n'
            for n in attrs.notes:
                epilog += f'\n- {n}'

        # Indicate if the module has been tested
        fstatus = 'yes' if attrs.verified_functional else 'no'
        epilog += '\n\nVerified as Functional: ' + fstatus

        # ======================
        # BUILD MODULE ARGUMENTS
        # ======================

        '''Here we create a new argparse argument parser for the command
        assoicated with the newly created module. This is how we bind
        the name that the user will refernce at the commandline, along
        with providing a mechanism to assign values to module parameters.
        '''

        parser = subparsers.add_parser(cls.get_handle(),
                description=cls.description,
                help=cls.brief_description + f' (Tested: {fstatus})',
                parents=cls.args,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=epilog)

        parser.set_defaults(module=cls)

        parser.add_argument('--database', '-db',
            required=True,
            help='Database to target.')

        # ======================
        # HANDLE MODULE BREAKERS
        # ======================

        if attrs.breaker_profiles:

            # ====================================
            # PREPARE ARGUMENT GROUP FOR INTERFACE
            # ====================================

            b_group = parser.add_argument_group(
                'Breaker Parameters',
                'Parameters that configure when breakers should be engaged. Note that '
                'all "reset_spec" parameters expect to receive a value formatted like '
                'jitter inputs, e.g. "10m" for ten minutes.')

            for bp in attrs.breaker_profiles:

                # ==============================================
                # DERIVE BREAKER ARGUMENTS FROM BREAKER PROFILES
                # ==============================================

                for v in bp.argparse_kwargs:

                    v = v.dict()
                    nof = v.pop('name_or_flags')

                    # argparse can't handle the "handles" attribute
                    del(v['handles'])

                    # Add the argument
                    b_group.add_argument(*nof, **v)

        return parser
