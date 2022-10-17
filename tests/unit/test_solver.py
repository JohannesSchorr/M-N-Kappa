from unittest import TestCase, main

from m_n_kappa.solver import Newton, Bisection

data = [
    [0, 2],
    [-5, -3],
]


class TestBisection(TestCase):
    def setUp(self):
        self.solver = Bisection(data=data, target=1, variable=0)

    def test_compute(self):
        self.assertEqual(self.solver.compute(), -2.5)


class TestNewton(TestCase):
    def setUp(self):
        self.solver = Newton(data=data, target=1, variable=0)

    def test_compute(self):
        self.assertEqual(self.solver.compute(), -2.0)


if __name__ == "__main__":
    main()
