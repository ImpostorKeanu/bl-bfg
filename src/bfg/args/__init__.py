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
    '''Read the signature of the decorated function and use the defined
    parameters to produce an argparse.ArgumentParser object that can
    be implemented in the `args` parameter of a BFG module.
    '''

    @wraps(f)
    def wrapper(*name_or_flags, **kwargs):

        if name_or_flags:
            kwargs['name_or_flags'] = name_or_flags

        # =======================================
        # OBTAIN DEFAULTS FROM DECORATED FUNCTION
        # =======================================

        spec = inspect.getfullargspec(f)
        defaults = {
            spec.args[ind]:spec.defaults[ind]
            for ind in range(0,len(spec.args))}
        defaults = defaults | kwargs

        # ==============================================
        # CONSTRUCT AND RETURN THE ArgumentParser OBJECT
        # ==============================================

        return genParentArg(*defaults.get('name_or_flags'), **{
                k:v for k,v in defaults.items()
                if not k.startswith('__') and
                k != 'name_or_flags'})

    return wrapper

def getArgDefaults(f):

    @wraps(f)
    def wrapper(*names, invert=False):
        '''Accept a dictionary of `argparse.ArgumentParser` objects
        organized by string names.

        When a list of `names` is supplied, only argument names in
        that list will be returned.

        Should `names`  be supplied and the `invert` argument is
        `True`, then all parameters that do not appear in `names`
        are returned.
        '''

        # Get the dictionary of default arguments
        dct = f()
    
        if not names:

            # Return all the values
            return list(dct.values())

        else:

            if invert:

                # Get flags that do not appear in the list of names
                names = [f for f in dct.keys() if not f in names]

            values = []

            for flag in names:

                v = dct.get(flag)

                if not v:
                    raise ValueError(
                        f'Unknown argument requested: {flag}')

                values.append(v)

            return values

    return wrapper
