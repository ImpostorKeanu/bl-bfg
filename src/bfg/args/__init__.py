import inspect
from functools import wraps
from argparse import (
    Action,
    BooleanOptionalAction,
    ArgumentParser as AP,
    _HelpAction as HA
)

def genParentArg(*args, **kwargs) -> AP:
    '''This function effectively creates a reusable argument object.

    It creates an ArgParse argument using the supplied arguments and
    bind it to an ArgumentParser object with add_help=False.
    '''

    if kwargs.get('action') == 'BoolAction':
        kwargs['action'] = BooleanOptionalAction

    parser = AP(add_help=False)
    parser.add_argument(*args, **kwargs)

    return parser

# =================
# GENERIC ARGUMENTS
# =================

def argument(f):

    @wraps(f)
    def wrapper(name_or_flags=None, **kwargs):

        if name_or_flags:
            kwargs['name_or_flags'] = name_or_flags

        spec = inspect.getfullargspec(f)
        defaults = {
            spec.args[ind]:spec.defaults[ind]
            for ind in range(0,len(spec.args))}

        defaults = defaults | kwargs

        return genParentArg(*defaults.get('name_or_flags'), **{
                k:v for k,v in defaults.items()
                if not k.startswith('__') and
                k != 'name_or_flags'})

    return wrapper

def getArgDefaults(f):

    @wraps(f)
    def wrapper(*names, invert=False):

        # Get the dictionary of default arguments
        dct = f()
    
        if not names:

            return list(dct.values())

        else:

            if invert:
                _names = [f for f in dct.keys() if not f in names]
                names = _names
                del(_names)

            values = []

            for flag in names:

                v = dct.get(flag)

                if not v:
                    raise ValueError(
                        f'Invalid argument flag requested: {flag}')

                values.append(v)

            return values

    return wrapper
