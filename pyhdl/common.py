"""
This module contains some common circuits.
"""
from .signal import Signal


def delay(n: int):
    """Delay n ticks. """
    for i in range(n):
        yield


def xtal(signal: Signal, low=None, high=None, period=None, phase=0):
    """
    A crystal clock oscillator, generating high/low signals periodically.
    This circuit will first generate a signal with value 0 followed by
    value 1. Their duration are specified by `low` and `high`. The sum of
    them should be the period of the oscillator, which also means the possible
    values of `phase`. We divide one period into (`low` + `high`) parts, indexed
    from 0 to (period-1). They are called the phase of the oscillator. Sometimes,
    we may not start with the `low` value. Thus, we need the phase to specify
    the start point.

    :param signal: output signal
    :param low: duration of low
    :param high: duration of high
    :param period: period
    :param phase: the
    """
    if low is high is period is None:
        raise ValueError("You have to specify at least one of `low`, `high`, `period`.")
    if period is None:
        if low is None:
            low = high
        if high is None:
            high = low
        period = low + high
    else:
        # period is not None
        if low is None:
            if high is None:
                low = period // 2
        high = period - low

    phase %= period

    def do_xtal():
        while True:
            signal.value = 0
            yield from delay(low)
            signal.value = 1
            yield from delay(high)
    gen = do_xtal()
    for i in range(phase):
        next(gen)
    return gen
