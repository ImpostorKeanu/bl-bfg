import argparse
import inspect
import re
        
class Module:

    '''# Base Module Class

    This class serves as a template for brute force modules within this
    example directory. It builds the interface subcommands by
    inspecting the __init__ method while also enforcing restrictions on
    the __call__ method to ensure BruteLoops can make authentication
    callbacks.

    # The __init__ Method

    This method can be used to set static values supporting a brute
    force module. It's useful in situations when an upstream server
    needs to be targeted.

    # The __call__ Method

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

    # Name for the module that'll be shown in logging
    name = None

    # Brief description to display in the help menu
    brief_description = None

    # Description of the module that'll be shown in the interface
    description = None

    @classmethod
    def initialize(cls, args):
        '''Initialize and return the underlying brute force module.
        '''

        # Translate the argparse arguments to a dictionary
        args = vars(args)

        # Initialize a dictionary to hold all of the necessary argument
        # to initialize the brute force module.
        dct = {}

        # Take each argparse value and add it to the dictionary
        for k,v in inspect.signature(cls.__init__).parameters.items():

            # Skip "self" references
            if k == 'self': continue

            # Extract the user supplied value when provided
            if k in args: dct[k]=args[k]

            # Use the default value other wise
            else: dct[k]=v

        # Initialize and return the module
        return cls(**dct)

    @classmethod
    def validate(cls):

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
        '''
        return '.'.join(cls.__module__.split('.')[-3:][:2])

    @classmethod
    def build_interface(cls,
            subparsers: 'Argparse subparsers that will receive the subcommand') \
                    -> argparse.ArgumentParser:
        '''Use the inspect module to iterate over each parameter
        declared in __init__ and build an interface via argparse.
        '''

        # =====================
        # INITIALIZE THE PARSER
        # =====================
        '''Here we create a new argparse argument parser for the command
        assoicated with the newly created module. This is how we bind
        the name that the user will refernce at the commandline, along
        with providing a mechanism to assign values to module parameters.
        '''

        epilog = None
        if hasattr(cls, 'contributors'):
            epilog = 'Module Contributors:\n\n'

            if not isinstance(cls.contributors, list):

                raise ValueError(
                    'Module contributors must be a list of dictionary '
                    f'values, not {type(cls.contributors)}')

            for cont in cls.contributors:

                if not isinstance(cont, dict):

                    raise ValueError(
                        'contributor records must be dictionaries, '
                        f'not {type(cont)}')

                name = cont.get('name')
                additional = cont.get('additional')

                if not name:

                    raise ValueError(
                        'contributor records must have a "name" field')

                epilog += f'- {name}'

                if additional:

                    if not isinstance(additional, dict):

                        raise ValueError(
                            'additional field of contributor records '
                            f'must be a dict, not {type(additional)}')

                    for k,v in additional.items():

                        epilog += f'\n  {k}: {v}'

        parser = subparsers.add_parser(cls.get_handle(),
                description=cls.description,
                help=cls.brief_description,
                parents=cls.args,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=epilog)

        parser.set_defaults(module=cls)

        parser.add_argument('--database', '-db',
            required=True,
            help='Database to target.')

        return parser
