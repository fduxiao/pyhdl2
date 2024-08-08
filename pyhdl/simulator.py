"""
A circuit is modelled as a discrete time series. We begin with
a certain state of wires and registers. After each time tick, we
may change the value of one wire or something else. This will cause
the change of the state. By this way, we are able to stimulate a
digital circuit.

Thus, we define a circuit as an iterator. After we call the initial
`next`, we start to record the circuit state. The first `next` is
defined as time 0, or the state in time period [0, 1].

We naturally use generators in python to make such an iterator. For
each `next` call, i.e., the yield of a generator, we make use of the
result of the `next` call. Each generator yields many `events`, which
are called during the stimulation loop. That means at each time period,
we can use the events to record the state, etc.
"""

from typing import Iterable, Any
from .event import BaseEvent


def flatten(*args, guard=lambda _: True):
    """flatten a complicated structure of events"""

    for p in args:
        if isinstance(p, tuple | list):
            yield from flatten(*p, guard=guard)
        elif guard(p):
            yield p


class Simulator:
    """
    The simulator class
    """
    def __init__(self, *iterables: Iterable[Any]):
        self.iterables = [*flatten(iterables, guard=lambda x: isinstance(x, Iterable))]
        self.time = 0

    def next(self):
        """trigger the `__next__` of each iterable"""
        events = []
        new_list = []
        for iterable in self.iterables:
            try:
                results = next(iterable)
                events.extend(flatten(results, guard=lambda x: isinstance(x, BaseEvent)))
                new_list.append(iterable)
            except StopIteration:
                continue
        self.iterables = new_list
        return events

    def run(self, duration: int = None):
        """
        run a simulation
        """
        self.time = 0
        while True:
            if duration is not None:
                if self.time >= duration:
                    break

            # next(self.iter)
            events = self.next()
            for event in flatten(events):
                event.trigger()
            self.time += 1
        self.next()
