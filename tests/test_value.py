from unittest import TestCase
from pyhdl import Shape, Signed, Unsigned, Value, Signal


class TestValue(TestCase):
    def test_shape(self):
        # test n_bits calculation
        for i in range(256):
            self.assertEqual(Shape.from_n(i), Unsigned(len(bin(i)) - 2))
        # with negative values
        for i in range(256):
            self.assertEqual(Shape.from_n(-1, i), Signed(len(bin(i)) - 2 + 1))
        # from several values
        self.assertEqual(Shape.from_n(-4), Signed(3))
        self.assertTrue(-4 in Signed(3))
        self.assertEqual(Shape.from_n(-4, 4), Signed(4))
        self.assertEqual(Shape.from_n(-5), Signed(4))
        self.assertEqual(Shape.from_n(-5, 4), Signed(4))
        self.assertEqual(Shape.from_n(-8), Signed(4))
        self.assertEqual(Shape.from_n(-8, 8), Signed(5))

        for i in range(256):
            # 0 is meaningless
            i += 1
            shape = Unsigned(i)
            self.assertEqual(shape.range.start, 0)
            self.assertEqual(shape.range.stop, 2 ** i)

            shape = Signed(i)
            self.assertEqual(shape.range.start, - 2 ** (i - 1))
            self.assertEqual(shape.range.stop, 2 ** (i - 1))

    def test_get_value(self):
        reg = Value(0b1011)
        self.assertEqual(reg.n_bits, 4)
        self.assertEqual(reg.signed, False)
        self.assertEqual(reg[0], 1)
        self.assertEqual(reg[1], 1)
        self.assertEqual(reg[2], 0)
        self.assertEqual(reg[3], 1)

        reg = Value(-5)  # this should be 0b1011 as an array of length 4
        self.assertEqual(reg._value, 0b1011)
        self.assertEqual(reg.n_bits, 4)
        self.assertEqual(reg.signed, True)
        self.assertEqual(reg[0], 1)
        self.assertEqual(reg[1].bin(), "1")
        self.assertEqual(reg[2], 0)
        self.assertEqual(reg[3], 1)
        self.assertEqual(reg[:].bin(), "1011")
        self.assertEqual(reg[:1].bin(), "101")
        self.assertEqual(reg[2:1].bin(), "01")
        self.assertEqual(reg.rev().bin(), "1101")
        self.assertEqual(reg[2:], 0b011)

    def test_set_value(self):
        reg = Value(shape=Signed(8))
        reg[:] = 0b11111011
        self.assertEqual(reg, -5)
        self.assertEqual(reg._value, 0b11111011)
        reg[7:4] = -5  # 0b1011
        self.assertEqual(reg._value, 0b10111011)
        reg[3:0] = 0b11101
        self.assertEqual(reg._value, 0b10111101)
        reg[7:4] = -22  # 0b101010
        self.assertEqual(reg[7:4].as_signed(), -6)
        self.assertEqual(reg[3:0].as_signed(), -3)

    def test_arithmetic(self):
        shape = Signed(4)
        a1 = shape.value(1)
        a2 = -a1
        self.assertEqual(a2, -1)
        self.assertEqual((a1 + a2).as_shape(shape), 0)
        self.assertEqual((a1 - a2).as_shape(shape), 2)

        a1 = shape.value(0b1011)
        self.assertEqual(a1, -5)
        a2 = shape.value(0b1111)
        self.assertEqual(a2, -1)
        self.assertEqual(a1 + a2, 0b1011 + 0b1111)
        self.assertEqual((a1 + a2).as_shape(shape), -6)
        self.assertEqual((a1 + a2).as_shape(shape)._value, 10)

        self.assertEqual(~a1, 0b0100)
        self.assertEqual(~a2, 0b0000)
        self.assertEqual(a1 & a2, 0b1011)
        self.assertEqual(a1 | a2, 0b1111)
        self.assertEqual(a1 ^ a2, 0b0100)

        self.assertEqual((a1 * a2).as_shape(shape), 5)
        self.assertEqual((a1 // a2).as_shape(shape), 0)

        a1 = shape.value(0b1011)
        a2 = Value(7)
        self.assertEqual(a1 % a2, 2)

        a2 = Value(15)
        a3 = Value(4)
        self.assertEqual(a2 % a3, 3)

    def test_signal(self):
        s = Signal(4)
        self.assertEqual(s.shape.n_bits, 3)
        self.assertEqual(type(s).default_n_bits, None)

        s = Signal[8](4)
        self.assertEqual(s.shape.n_bits, 8)
        self.assertEqual(type(s).default_n_bits, 8)

        s = Signal[8](4, n_bits=6)
        self.assertEqual(s.shape.n_bits, 6)
