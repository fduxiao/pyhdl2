"""
This module ensures binary operation. Since on a real-world device, each number is stored
with a fixed bit-width. The arithmetic is exactly the one in the quotient ring. This module
provides a python class of such a ring. Note that I treat every number as a `value`, i.e.,
arithmetic operations will always give a new object of that class, even if the operands are unchanged,
I will never return them.
"""

from dataclasses import dataclass
import math


@dataclass
class Shape:
    """
    This class defines the shape of a bit array
    """
    signed: bool = False
    n_bits: int = 1

    def __post_init__(self):
        # make sure n_bits is positive
        if self.n_bits < 0:
            raise ValueError("n_bits can only be positive.")
        self.modulo = 0b01 << self.n_bits
        if self.n_bits == 0:
            self.range = None
            self.min = None
            self.max = None
        # then calculate the possible range of this value
        if not self.signed:
            self.min = 0
            self.max = 0b01 << self.n_bits
            self.range = range(self.max)
            self.max -= 1
        else:
            max_value = 0b01 << (self.n_bits - 1)
            self.min = -max_value
            self.max = max_value - 1
            self.range = range(-max_value, max_value)

    def contains(self, item: int) -> bool:
        return item in self

    def __contains__(self, item: int):
        return item in self.range

    def __repr__(self):
        if self.signed:
            return f"Signed({self.n_bits})"
        else:
            return f"Unsigned({self.n_bits})"

    @classmethod
    def from_range(cls, iterable):
        """
        Calculate the shape from many possibilities.
        """
        minimal = math.inf
        maximal = -math.inf
        for k in iterable:
            minimal = min(minimal, k)
            maximal = max(maximal, k)
        if minimal >= 0:
            # all positive
            if maximal == 0 or maximal == 1:
                return Unsigned(1)
            n_bits = math.floor(math.log2(maximal)) + 1
            return Unsigned(n_bits)
        if minimal < 0:
            if minimal == -1:
                if maximal == 0 or maximal == 1:
                    return Signed(2)
                return Signed(math.ceil(math.log2(maximal + 1) + 1))

            n_bits_neg = math.ceil(math.log2(-minimal)) + 1
            if maximal <= 1:
                return Signed(n_bits_neg)
            n_bits_pos = math.ceil(math.log2(maximal + 1) + 1)
            return Signed(max(n_bits_neg, n_bits_pos))

    @classmethod
    def from_enum(cls, enum):
        return cls.from_range(map(lambda x: x.value, enum))

    @classmethod
    def from_n(cls, *args):
        return cls.from_range(args)

    def value(self, n):
        """
        You can also easily make a value from the shape
        """
        return Value(n, self)


class Signed(Shape):
    def __init__(self, n_bit: int = 1):
        super().__init__(True, n_bit)


class Unsigned(Shape):
    def __init__(self, n_bit: int = 1):
        super().__init__(False, n_bit)


class Value:
    """
    Let's think about all binary numbers with 4 bits, i.e., the ring Z/(2 ** 4).
    We know that 0b1111 + 0b0001 = 0b0000 in the additive group. Thus, there are two ways
    to think about the number 0b1111, whether as the remainder 2**4-1=15, or as the
    negative number (signed number) -1.

    In the implementation of this class, I will always use the positive remainder representation
    of each residual class internally. That positive representative element is stored in the variable `_value`
    and is therefore used for the ring arithmetic.

    Then a property called `value` is used to access the desired result probably with sign.

    I also implement other binary operations such as bitwise and, or, ..., and slicing through [high:low]
    in the style of verilog (closed interval).
    """

    _value: int
    shape: Shape

    def __init__(self, value=0, shape=None):
        if isinstance(value, Value):
            shape = value.shape
            value = value._value
        if shape is None:
            shape = Shape.from_n(value)
        if shape is Signed:
            shape = Shape.from_n(-1, value)
        self.shape: Shape = shape
        value %= shape.modulo
        self._value = value

    # then we make some syntax sugar

    @property
    def signed(self):
        return self.shape.signed

    @property
    def n_bits(self):
        return self.shape.n_bits

    @property
    def min(self):
        return self.shape.min

    @property
    def max(self):
        return self.shape.max

    @property
    def modulo(self):
        return self.shape.modulo

    def copy(self):
        return type(self)(self._value, self.shape)

    @property
    def raw_value(self):
        return self._value

    @property
    def value(self):
        value = self._value
        if value > self.max:
            value -= self.modulo
        return value

    @value.setter
    def value(self, value: int):
        self.set_value(value)

    def set_value(self, value: int):
        """
        to set the correct value
        """
        if isinstance(value, Value):
            value = value._value
        self._value = value % self.modulo
        return self

    def bin(self):
        value = self._value
        result = ""
        for i in range(self.n_bits):
            result += str(value & 0b1)
            value >>= 1
        return result[::-1]

    def __repr__(self):
        return f"BitArray({self.value}, shape={self.shape})"

    def get_bit(self, index: int):
        if index < 0:
            index += self.n_bits
        if index < 0 or index >= self.n_bits:
            raise IndexError(index)
        mask = 1 << index
        value = self.value & mask
        if value > 0:
            return 1
        else:
            return 0

    def set_bit(self, key, value):
        if key < 0:
            key += self.n_bits
        if key < 0 or key >= self.n_bits:
            raise IndexError(key)
        mask = 1 << key
        value = value << key
        self._value &= ~mask
        value &= mask
        self._value |= value

    def parse_slice(self, item):
        if isinstance(item, int):
            item = slice(item, item)
        stop = item.start
        if stop is None:
            stop = self.n_bits - 1
        start = item.stop
        if start is None:
            start = 0

        # now I only support step=1
        step = 1

        if start > stop:
            raise ValueError("`stop` should be larger than `start`")
        if stop > self.n_bits or start > self.n_bits:
            raise OverflowError("`start` and/or `stop` shouldn't exceed bit width")
        if start < 0:
            raise OverflowError("`start` should be positive")
        return start, stop + 1, step

    def __getitem__(self, item):
        start, stop, step = self.parse_slice(item)
        bit_width = (stop - start) // step

        result_value = 0
        value = self._value >> start
        last_bit = 0b1
        mask = 0b1
        # use shifting and masking to calculate result_value
        for i in range(start, stop, step):
            if i >= self.n_bits:
                break
            result_value |= (value & last_bit) * mask
            mask <<= 1
            value >>= step
        return Value(result_value, shape=Unsigned(bit_width))  # always unsigned

    def rev(self):
        value = self.value
        result = 0
        for i in range(self.n_bits):
            result <<= 1
            result |= value & 0b1
            value >>= 1
        return Value(result)  # always unsigned

    def __setitem__(self, key, value):
        # by setting value, we always make sure value is an unsigned value
        # even if it is negative, we will view it as a positive number.
        if isinstance(value, int):
            value = Value(value)
        shape = value.shape
        value = value._value

        start, stop, step = self.parse_slice(key)
        target_bit_width = (stop - start) // step
        if shape.n_bits > target_bit_width:
            value %= 1 << target_bit_width  # truncate overflow bits

        # shift the value
        value <<= start
        # prepare the mask
        # first tag the bits to be changed with 1
        mask = (0b01 << target_bit_width) - 1
        mask <<= start
        # then take the negation
        mask ^= self.modulo - 1

        self._value = (self.value & mask) | value

    def as_shape(self, shape: Shape):
        """
        return with the specified shape
        """
        return type(self)(self._value, shape=shape)

    def as_signed(self):
        """
        sometimes we may want to change an unsigned number to a signed. Then we can use this one
        """
        return self.as_shape(Signed(self.n_bits))

    def __bool__(self):
        return self._value == 1

    def binary_op(self, other, func):
        if isinstance(other, Value):
            other = other.value
        return Value(func(self.value, other))

    # order related
    def __eq__(self, other):
        return self.binary_op(other, lambda x, y: x == y)

    def __lt__(self, other):
        return self.binary_op(other, lambda x, y: x < y)

    def __le__(self, other):
        return self.binary_op(other, lambda x, y: x <= y)

    def __gt__(self, other):
        return self.binary_op(other, lambda x, y: x > y)

    def __ge__(self, other):
        return self.binary_op(other, lambda x, y: x >= y)

    def binary_op_raw(self, other, func):
        if isinstance(other, Value):
            other = other._value
        return Value(func(self._value, other))

    # arithmetics
    def __add__(self, other) -> "Value":
        return self.binary_op_raw(other, lambda x, y: x + y)

    def __neg__(self):
        return Value(self.modulo - self._value, shape=self.shape)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other) -> "Value":
        return self.binary_op_raw(other, lambda x, y: x * y)

    def __floordiv__(self, other) -> "Value":
        return self.binary_op_raw(other, lambda x, y: x // y)

    def __mod__(self, other) -> "Value":
        return self.binary_op(other, lambda x, y: x % y)

    # bitwise
    def __invert__(self):
        return Value(~self._value, shape=self.shape)

    def __and__(self, other):
        return self.binary_op_raw(other, lambda x, y: x & y)

    def __or__(self, other):
        return self.binary_op_raw(other, lambda x, y: x | y)

    def __xor__(self, other):
        return self.binary_op_raw(other, lambda x, y: x ^ y)
