from unittest import TestCase, main
import math

from m_n_kappa.fitting import GaussNewton
from m_n_kappa.matrices import Vector


class TestGaussNewton(TestCase):
    def test_rosenbrock_function(self):
        """see https://en.wikipedia.org/wiki/Rosenbrock_function for details"""

        def f_1(variables: list[float, float]):
            x_1, x_2 = variables
            return 2.0**0.5 * (1.0 - x_1)

        def f_2(variables: list[float, float]):
            x_1, x_2 = variables
            return (2.0 * 100.0) ** 0.5 * (x_2 - x_1**2.0)

        functions = [f_1, f_2]
        starting_values = [0.0, -0.1]

        gn = GaussNewton(f_i=functions, x_0=starting_values)

        self.assertEqual(gn.x_i, Vector([1.0, 1.0]))

    def test_optimization_problem_1(self):
        """https://www.igpm.rwth-aachen.de/Numa/NumaMB/SS13/grUe10.pdf Example 1"""

        def f_1(variable: list[float]):
            x = variable[0]
            return math.e ** (-x * 1.0) - 0.8

        def f_2(variable: list[float]):
            x = variable[0]
            return math.e ** (-x * 2.0) - 0.5

        functions = [f_1, f_2]
        starting_values = [0.3]

        gn = GaussNewton(f_i=functions, x_0=starting_values)

        self.assertEqual(round(gn.x_i, 4), Vector([0.3056]))

    def test_optimization_problem_2(self):
        """https://www.igpm.rwth-aachen.de/Numa/NumaMB/SS13/grUe10.pdf Example 2"""

        def f(exp, result):
            def function(variables: list[float]):
                A, lamb = variables
                return A * (1 - math.e ** (-lamb * exp)) - result

            return function

        functions = [f(0.1, 1.0), f(1.0, 2.0), f(3.0, 3.0), f(5.0, 4.0)]
        starting_values = [4.0, 2.5]

        gn = GaussNewton(f_i=functions, x_0=starting_values)

        self.assertEqual(round(gn.x_i, 7), Vector([3.8605284, 0.69519100]))


if __name__ == "__main__":
    main()
