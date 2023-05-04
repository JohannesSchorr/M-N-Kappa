from unittest import TestCase, main
import math

from m_n_kappa.matrices import Matrix, Vector, LinearEquationsSystem, Jacobian


class TestVector(TestCase):
    def setUp(self) -> None:
        self.vector_1 = Vector([0, 1])
        self.vector_2 = Vector([2, 3])

    def test_append(self):
        self.assertEqual(self.vector_1.append(self.vector_2), Matrix([[0, 2], [1, 3]]))

    def test_add(self):
        self.assertEqual(self.vector_1 + self.vector_2, Vector([2, 4]))
        
    def test_subtract(self):
        self.assertEqual(self.vector_1 - self.vector_2, Vector([-2, -2]))

    def test_scalar_product(self):
        self.assertEqual(self.vector_1.scalar_product(self.vector_2), 3.0)

    def test_scalar_product_with_itself(self):
        self.assertEqual(self.vector_1.scalar_product(self.vector_1), 1.0)

    def test_multiply_scalar(self):
        self.assertEqual(self.vector_1.multiply_scalar(2.0), Vector([0.0, 2.0]))
    
    def test_tensor_product(self):
        self.assertEqual(
            self.vector_1.tensor_product(self.vector_2), 
            Matrix([[0, 0], [2, 3]])
        )

class TestMatrix(TestCase):
    def setUp(self):
        self.matrix_1 = Matrix([[0, 1, 2], [3, 4, 5]])
        self.matrix_2 = Matrix([[1, -3, 2], [1, 2, 7]])
        self.matrix_3 = Matrix([[3, 2, 1], [1, 0, 2]])
        self.matrix_4 = Matrix([[1, 2], [0, 1], [4, 0]])
        self.matrix_5 = Matrix([[0, 3, 5], [2, 1, -1]])
        self.matrix_6 = Matrix([[3, 2], [1, 2], [2, 2]])
        self.vector_1 = Vector([1, 2])
        self.matrix_7 = Matrix([[12, -51, 4], [6, 167, -68], [-4, 24, -41]])
        self.matrix_8 = Matrix([[3, 5], [0, 2], [0, 0], [4, 5]])
        self.matrix_9 = Matrix([[6, 5, 0], [5, 1, 4], [0, 4, 3]])

    def test_transpose(self):
        self.assertEqual(self.matrix_1.transpose(), Matrix([[0, 3], [1, 4], [2, 5]]))

    def test_multiply_float(self):
        self.assertEqual(
            self.matrix_2.multiply_by(5), Matrix([[5, -15, 10], [5, 10, 35]])
        )

    def test_multiply_vector(self):
        self.assertEqual(
            self.matrix_2.multiply_by(Vector([1, 2, 3])), Vector([1.0, 26.0])
        )

    def test_multiply_matrix(self):
        self.assertEqual(
            self.matrix_3.multiply_by(self.matrix_4), Matrix([[7, 8], [9, 2]])
        )

    def test_add(self):
        self.assertEqual(
            self.matrix_2.add(self.matrix_5), Matrix([[1, 0, 7], [3, 3, 6]])
        )

    def test_subtract(self):
        self.assertEqual(
            self.matrix_2.subtract(self.matrix_5), Matrix([[1, -6, -3], [-1, 1, 8]])
        )

    def test_orthonormal_triangular(self):
        round_value = 13
        q, t = self.matrix_7.orthonormal_triangular()
        q = round(q, round_value)
        t = round(t, round_value)
        self.assertEqual(
            q,
            round(
                Matrix(
                    [
                        [6 / 7, -69 / 175, -58 / 175],
                        [3 / 7, 158 / 175, 6 / 175],
                        [-2 / 7, 6 / 35, -33 / 35],
                    ]
                ),
                round_value,
            ),
        )
        self.assertEqual(t, Matrix([[14, 21, -14], [0, 175, -70], [0, 0, 35]]))

    def test_append(self):
        self.assertEqual(
            self.matrix_1.append(self.vector_1), Matrix([[0, 1, 2, 1], [3, 4, 5, 2]])
        )

    def test_gram_schmidt(self):
        self.assertEqual(
            round(self.matrix_7._gram_schmidt()[0], 10),
            round(
                Matrix(
                    [
                        [6 / 7, -69 / 175, -58 / 175],
                        [3 / 7, 158 / 175, 6 / 175],
                        [-2 / 7, 6 / 35, -33 / 35],
                    ]
                ),
                10,
            ),
        )

    def test_modified_gram_schmidt(self):
        self.assertEqual(
            round(self.matrix_7._gram_schmidt_modified()[0], 10),
            round(
                Matrix(
                    [
                        [6 / 7, -69 / 175, -58 / 175],
                        [3 / 7, 158 / 175, 6 / 175],
                        [-2 / 7, 6 / 35, -33 / 35],
                    ]
                ),
                10,
            ),
        )
        
    def test_givens_2(self):
        """see https://de.wikipedia.org/wiki/Givens-Rotation#QR-Zerlegung-mittels-Givens-Rotationen"""
        q, r = self.matrix_8._givens()
        self.assertEqual(
            q, 
            Matrix([[3/5, 4/(5*5**0.5), 0, -8/(5*5**0.5)], 
                    [0, 2/(5**0.5), 0, 1/(5**0.5)], 
                    [0, 0, 1, 0], 
                    [4/5, -3/(5*5**0.5), 0, 6/(5*5**0.5)]])
        )
        self.assertEqual(
            round(r, 15), 
            Matrix(
                [[5, 7], [0, 5**0.5], [0, 0], [0, 0]]
            )
        )
    
    def test_givens_3(self):
        """see https://en.wikipedia.org/wiki/Givens_rotation#Triangulization"""
        q, r = self.matrix_9._givens()
        self.assertEqual(
            round(r, 4),
            Matrix([[7.8102, 4.4813, 2.5607], [0, 4.6817, 0.9664], [0, 0, -4.1843]])
        )
        self.assertEqual(
            round(q, 4), 
            Matrix([[0.7682, 0.3327, 0.5470], 
                    [0.6402, -0.3992, -0.6564], 
                    [0.0, 0.8544, -0.5196]])
        )
        


class TestLinearEquationSystem(TestCase):
    def test_solve_dr_decomposition_1(self):
        self.matrix_1 = Matrix([[1, -1], [1, -5]])
        self.constants_1 = Vector([-7, -23])
        lgs = LinearEquationsSystem(self.matrix_1, self.constants_1)
        self.assertEqual(round(lgs.solve(), 14), Vector([-3.0, 4.0]))

    def test_solve_decomposition__2(self):
        self.matrix_2 = Matrix([[12, 11], [16, -7]])
        self.constants_2 = Vector([18, -2])
        lgs = LinearEquationsSystem(self.matrix_2, self.constants_2)
        self.assertEqual(lgs.solve(), Vector([0.4, 1.2]))

    def test_solve_decomposition__3(self):
        self.matrix_3 = Matrix([[4, -2, 1], [-1, 3, 4], [5, -1, 3]])
        self.constants_3 = Vector([15, 15, 26])
        lgs = LinearEquationsSystem(self.matrix_3, self.constants_3)
        self.assertEqual(round(lgs.solve(), 12), Vector([2, -1, 5]))

class TestJacobian(TestCase): 
    
    def setUp(self) -> None:
        def f_1(variables : list): 
            x, y, z = variables
            return x**2 + y**2 + z * math.sin(x)
        
        def f_2(variables: list):
            x, y, z = variables
            return z**2 + z * math.sin(y)
        
        self.functions = [f_1, f_2]
        self.variables_1 = Vector([1, 1, 1])
        
    def test_jacobian_build_forward(self):
        rounding_value = 7  # -> 8 leads to error
        self.assertEqual(
            round(Jacobian(self.functions, self.variables_1), rounding_value), 
            round(Matrix([[2.5403023058681398, 2, 0.8414709848078965], [0, 0.5403023058681398, 2.8414709848078965]]), rounding_value)
        )
        
    def test_jacobian_build_backward(self):
        rounding_value = 7  # -> 8 leads to error
        self.assertEqual(
            round(Jacobian(self.functions, self.variables_1, differentiation_type='b'), rounding_value), 
            round(Matrix([[2.5403023058681398, 2, 0.8414709848078965], [0, 0.5403023058681398, 2.8414709848078965]]), rounding_value)
        )
    
    def test_jacobian_build_center(self):
        rounding_value = 7  # -> 8 leads to error
        self.assertEqual(
            round(Jacobian(self.functions, self.variables_1, differentiation_type='c'), rounding_value), 
            round(Matrix([[2.5403023058681398, 2, 0.8414709848078965], [0, 0.5403023058681398, 2.8414709848078965]]), rounding_value)
        )
    

if __name__ == "__main__":
    main()
