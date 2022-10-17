from unittest import TestCase, main

from m_n_kappa.function import Linear, Polynominal

data = [[0, 2], [-5, -3], [4, 1]]


class TestLinear(TestCase):
    def setUp(self):
        self.func = Linear(data, variable=0, target=1)

    def test_intersection(self):
        self.assertEqual(self.func.intersection, 2.0)

    def test_slope(self):
        self.assertEqual(self.func.slope, 1.0)

    def test_derivate(self):
        self.assertEqual(self.func.derivate(None), 1.0)


class TestPolynominal(TestCase):
    def setUp(self):
        self.func = Polynominal(data, variable=0, target=1)

    def test_a(self):
        self.assertAlmostEqual(self.func.a, -0.13888, places=4)


if __name__ == "__main__":
    main()
