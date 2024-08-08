import unittest
from pyhdl import Logger, Signal, delay, Simulator


class TestStimulator(unittest.TestCase):
    def test_simple_circuit(self):
        logger = Logger()

        def clock(signal: Signal, n=1):
            while True:
                yield from delay(n)
                logger.append(signal.value)
                signal.value = ~signal

        sig = Signal(0)
        sim = Simulator(clock(sig, 1))
        sim.run(10)

        self.assertEqual(logger, [i % 2 for i in range(10)])

        sig.value = 0
        logger.clear()
        sim = Simulator(clock(sig, 2))
        sim.run(10)
        self.assertEqual(logger, [0, 1, 0, 1, 0])


if __name__ == '__main__':
    unittest.main()
