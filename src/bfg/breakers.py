'''This module defines "breaker profiles," i.e. models used to
translate between argparse arguments and a BruteLoops model.G
'''

from bruteloops.models import Breaker, ThresholdBreaker
from .errors import LockoutError
from pydantic import BaseModel, Field
from argparse import Namespace
from typing import (
    Callable,
    Union,
    List,
    Dict,
    Any,
    Iterable,
    Optional
)

class MediationHandles(BaseModel):
    '''Maps instance variable names between argparse and breaker
    profiles.
    '''

    argparse: str
    ('Argparse argument handle used to dereference from '
    'argparse.Namespace.')

    breaker: str
    ('Name of the breaker attribute to set on either BaseBreaker '
     'or BaseThresholdBreaker, depending on the type of BreakerProfile '
     'being managed')

class FromArgparseMixin:
    '''Class that provides functions to derive a Breaker instance
    from a BreakerProfile model.

    It works by referencing the MediationHandles and updating the
    breaker profile attributes with values provided by argparse.
    '''

    def namespace_update(self, namespace:Namespace):
        '''Update the breaker_kwargs attribute with values from an
        `argparse.Namespace` object.

        Args:
            namespace: Namespace derived from Argparse. Values found
              in the namespace will be used to update the object's
              breaker_kwargs instance.
        '''

        kwargs = dict()
        for aap in self.argparse_kwargs:

            # Get the new value from the namespace based on 
            # argparse name
            v = getattr(namespace, aap.handles.argparse, None)         

            if not v:
                continue

            # Set the new value to breaker_kwargs by referencing
            # the breaker handle
            setattr(self.breaker_kwargs, aap.handles.breaker, v)

    def to_breaker(self, namespace:Namespace=None) -> Union[Breaker,
            ThresholdBreaker]:
        '''Convert te BreakerProfile into a BruteLoops breaker instance.

        namespace is passed to namespace_update when non-None.

        Args:
            namespace: Namespace derived from Argparse. Values found
              in the namespace will be used to update the object's
              breaker_kwargs instance.
        '''

        if namespace:
            self.namespace_update(namespace)

        return self.bruteloops_model(
            **{
                k:getattr(self.breaker_kwargs, k) for k in
                self.bruteloops_model.__fields__.keys()
                if hasattr(self.breaker_kwargs, k)
              })

class BaseBreaker(BaseModel):
    '''Common breaker profile attributes.
    '''

    trip_msg: str
    ('Message thrown when the breaker is tripped.')

    exception_classes: List[Any]
    ('List of Exception classes to act on.')

class BaseThresholdBreaker(BaseBreaker):
    '''Breaker profile attributes for threshold breakers.
    '''

    threshold: int
    ('Count of times the breaker can be touched before tripping.')

    reset_spec: str
    ('Reset specification, which matches jitter time specifications.')

class ArgparseArgumentProfile(BaseModel):
    '''A model for inputs that will be passed to
    argparse.ArgumentParser.add_argument. It also incorporates handles
    to facilitate translation between argparse.Namespace and BruteLoops
    breaker models.
    '''

    handles: MediationHandles
    name_or_flags: List[str]
    action: Optional[Union[str, Callable]]
    nargs: Optional[int]
    const: Optional[Any]
    default: Optional[Any]
    type: Optional[Any]
    choices: Optional[list]
    required: Optional[bool]
    help: Optional[str]
    metavar: Optional[str]
    dest: Optional[str]

class ThresholdBreakerProfile(BaseModel, FromArgparseMixin):
    '''A model to represent threshold breaker profiles.
    '''

    breaker_kwargs:  BaseThresholdBreaker
    ('Threshold breaker arguments.')

    argparse_kwargs: List[ArgparseArgumentProfile]
    ('Argparse kwargs.')

    @property
    def bruteloops_model(self):
        return ThresholdBreaker

class ConnectionErrorBreakerProfile(ThresholdBreakerProfile):
    '''A profile for all ConnectionError events.

    By default, this breaker will trip when **20** connection errors
    occur in a **10 minute window**.
    '''

    breaker_kwargs: BaseThresholdBreaker = BaseThresholdBreaker(
        trip_msg='Connection error observed',
        threshold=20,
        reset_spec='10m',
        exception_classes=[ConnectionError])

    argparse_kwargs: List[ArgparseArgumentProfile] = [
        ArgparseArgumentProfile(handles=MediationHandles(
                argparse='max_connection_errors',
                breaker='threshold'),
            name_or_flags=('--max-connection-errors',),
            type=int,
            help='Maximum number of connection errors that can occur '
                'before terminating the attack. Default: %(default)s',
            default=20),
        ArgparseArgumentProfile(handles=MediationHandles(
                argparse='connection_error_reset_spec',
                breaker='reset_spec'),
            name_or_flags=('--connection-error-reset-spec',),
            help='Window of time that must pass before the count of '
                'connection errors will be reset. Default: %(default)s',
            default='10m')
        ]

class LockoutErrorBreakerProfile(ThresholdBreakerProfile):
    '''A profile for all LockoutError events.

    By default, this breaker will trip when **5** lockout errors
    occur in a **10 minute window**.
    '''

    breaker_kwargs: BaseThresholdBreaker = BaseThresholdBreaker(
        trip_msg='Lockout event observed',
        threshold=5,
        reset_spec='10m',
        exception_classes=[LockoutError])

    argparse_kwargs: List[ArgparseArgumentProfile] = [
        ArgparseArgumentProfile(handles=MediationHandles(
                argparse='max_lockout_errors',
                breaker='threshold'),
            name_or_flags=('--max-lockout-errors',),
            type=int,
            help='Maximum number of connection errors that can occur '
                'before terminating the attack. Default: %(default)s',
            default=5),
        ArgparseArgumentProfile(handles=MediationHandles(
                argparse='lockout_error_reset_spec',
                breaker='reset_spec'),
            name_or_flags=('--lockout-error-reset-spec',),
            help='Window of time that must pass before the count of '
                'lockout errors reset. Default: %(default)s',
            default='10m')
    ]
