"""
This module mimic the behavior of a wire/reg, they are both modelled as a signal
"""
from enum import Enum, auto
from .value import Value, Shape


class EdgeType(Enum):
    POS = auto()
    NEG = auto()
    ANY = auto()


class EdgeCond:
    def __init__(self, signal: "Signal", edge_type: EdgeType):
        self.signal = signal
        self.edge_type = edge_type

    def __call__(self) -> bool:
        diff = self.signal - self.signal.prev
        self.signal.prev = self.signal.raw_value
        match self.edge_type:
            case EdgeType.POS:
                return diff > 0
            case EdgeType.NEG:
                return diff < 0
            case EdgeType.ANY:
                return diff != 0


class SignalMeta(type):
    """Metaclass for usages like Signal[3]"""
    default_n_bits = None

    def __getitem__(self, item: int):
        new_type = type('Signal', (Signal,), {'default_n_bits': item})
        return new_type


class Signal(metaclass=SignalMeta):
    """The signal class. """

    def __init__(self, value: int | Value = 0, n_bits=None, signed=False):
        if n_bits is None:
            n_bits = type(self).default_n_bits
        if n_bits is None:
            if signed:
                extra = -1
            else:
                extra = 0
            shape = Shape.from_n(value, extra)
        else:
            shape = Shape(signed, n_bits)
        self._value: Value = Value(value, shape=shape)
        self.prev = value

    def copy(self):
        """Copy a signal. """
        return type(self)(self._value)

    @property
    def shape(self):
        return self._value.shape

    def get_value(self):
        return self._value.value

    def set_value(self, value):
        self.prev = self._value[:]
        self._value.set_value(value)
        return self

    @property
    def posedge(self):
        return EdgeCond(self, EdgeType.POS)

    @property
    def negedge(self):
        return EdgeCond(self, EdgeType.NEG)

    def anyedge(self):
        return EdgeCond(self, EdgeType.ANY)

    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, value):
        self.set_value(value)

    def bin(self):
        return self._value.bin()

    @property
    def raw_value(self):
        return self._value

    def binary_op(self, other, func) -> Value:
        if isinstance(other, Signal):
            other = other.raw_value
        return func(self._value, other)

    # order related
    def __eq__(self, other):
        return self.binary_op(other, lambda a, b: a == b)

    def __lt__(self, other):
        return self.binary_op(other, lambda x, y: x < y)

    def __le__(self, other):
        return self.binary_op(other, lambda x, y: x <= y)

    def __gt__(self, other):
        return self.binary_op(other, lambda x, y: x > y)

    def __ge__(self, other):
        return self.binary_op(other, lambda x, y: x >= y)

    # bitwise
    def __bool__(self):
        return bool(self._value)

    def __invert__(self):
        return ~self._value

    def __and__(self, other):
        return self.binary_op(other, lambda x, y: x & y)

    def __or__(self, other):
        return self.binary_op(other, lambda x, y: x | y)

    def __xor__(self, other):
        return self.binary_op(other, lambda x, y: x ^ y)

    # arithmetics
    def __add__(self, other):
        return self.binary_op(other, lambda x, y: x + y)

    def __neg__(self):
        return -self._value

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return self.binary_op(other, lambda x, y: x * y)

    def __floordiv__(self, other):
        return self.binary_op(other, lambda x, y: x // y)

    def __mod__(self, other):
        return self.binary_op(other, lambda x, y: x % y)
