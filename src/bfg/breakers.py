from bruteloops.models import Breaker, ThresholdBreaker
from .errors import LockoutError
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ThresholdBreakerArgs(BaseModel):
    threshold: int
    reset_spec: str

class BreakerKwargs(BaseModel):
    trip_msg: str
    threshold: int
    reset_spec: str
    exception_classes: List[Any]

class BreakerProfile(BaseModel):
    breaker_kwargs:  BreakerKwargs
    argparse_kwargs: Dict[str, Dict]


ConnectionErrorBreakerProfile = BreakerProfile(
    breaker_kwargs = dict(
        trip_msg='Too many connection errors',
        threshold=20, reset_spec='10m',
        exception_classes=[ConnectionError]),

    argparse_kwargs = dict(
        max_connection_errors=dict(
            name_or_flags=('--max-connection-errors',),
            type=int,
            help='Maximum number of connection errors that can occur '
                'before terminating the attack. Default: %(default)s',
            default=20),
        connection_error_reset_spec=dict(
            name_or_flags=('--connection-error-reset-spec',),
            help='Window of time that must pass before the count of '
                'connection errors will be reset. Default: %(default)s',
            default='10m')
    )
)

LockoutErrorBreakerProfile = BreakerProfile(
    breaker_kwargs = dict(
        trip_msg='Too many lockout events',
        threshold=5,
        reset_spec='10m',
        exception_classes=[LockoutError]),
    argparse_kwargs = dict(
        max_lockout_errors=dict(
            name_or_flags=('--max-lockout-errors',),
            type=int,
            help='Maximum number of connection errors that can occur '
                'before terminating the attack. Default: %(default)s',
            default=5),
        lockout_error_reset_spec=dict(
            name_or_flags=('--lockout-error-reset-spec',),
            help='Window of time that must pass before the count of '
                'lockout errors reset. Default: %(default)s',
            default='10m'))
)
