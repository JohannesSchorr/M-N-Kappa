from unittest import TestCase, main

from m_n_kappa.solver import Newton, Bisection


class TestBisection(TestCase):
    def setUp(self):
        self.data = [
            [0, 2],
            [-5, -3],
        ]
        self.solver = Bisection(data=self.data, target=1, variable=0)

    def test_compute(self):
        self.assertEqual(self.solver.compute(), -2.5)


class TestNewtonLinear(TestCase):
    def setUp(self):
        self.data = [
            [0, 2],
            [-5, -3],
        ]
        self.solver = Newton(data=self.data, target=1, variable=0)

    def test_minimum_variable(self):
        self.assertEqual(self.solver.minimum_variable, -5)

    def test_maximum_variable(self):
        self.assertEqual(self.solver.maximum_variable, 0.0)

    def test_compute(self):
        self.assertEqual(self.solver.compute(), -2.0)


class TestNewtonPolynomial(TestCase):
    def setUp(self):
        self.data = [
            [2, 4],
            [0, 2],
            [-5, -3],
            [-10, -5],
            [4, 6],
        ]
        self.solver = Newton(data=self.data, target=1, variable=0)

    def test_compute(self):
        self.assertEqual(self.solver.compute(), -2.0)


class TestNewtonPolynomial2(TestCase):
    def setUp(self):
        self.data = [
            {"axial_force": 407764.9041884129, "neutral_axis_value": 0.0},
            {
                "axial_force": 882758.2291958473,
                "neutral_axis_value": 18.836874779570994,
            },
            {
                "axial_force": -4232634.547079985,
                "neutral_axis_value": 214.3652445143822,
            },
        ]
        self.solver = Newton(
            data=self.data, variable="neutral_axis_value", target="axial_force"
        )

    def test_minimum_variable(self):
        self.assertEqual(self.solver.minimum_variable, 0.0)

    def test_compute(self):
        self.assertAlmostEqual(self.solver.compute(), 107.182, places=2)


class TestPassingGenerator(TestCase):
    def setUp(self):
        self.data_list = [
            [0, 2],
            [-5, -3],
        ]
        self.data = (point for point in self.data_list)
        #self.solver = Bisection(data=self.data, target=1, variable=0)

    #def test_compute(self):
    #    self.assertEqual(self.solver.compute(), -2.5)


if __name__ == "__main__":
    main()
