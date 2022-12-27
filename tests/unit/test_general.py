from unittest import TestCase, main

from m_n_kappa.general import (
    curvature,
    curvature_by_points,
    strain,
    remove_duplicates,
    neutral_axis,
    position,
    positive_sign,
    negative_sign,
    interpolation,
    remove_none,
)

from decimal import Decimal


class TestCurvature(TestCase):
    def test_greater_1(self):
        self.assertGreater(
            curvature(neutral_axis_value=10, position_value=5, strain_at_position=-0.001),
            0.0,
        )

    def test_greater_2(self):
        self.assertGreater(
            curvature(neutral_axis_value=10, position_value=15, strain_at_position=0.001),
            0.0,
        )

    def test_less_1(self):
        self.assertLess(
            curvature(neutral_axis_value=10, position_value=5, strain_at_position=0.001),
            0.0,
        )

    def test_less_2(self):
        self.assertLess(
            curvature(neutral_axis_value=10, position_value=15, strain_at_position=-0.001),
            0.0,
        )

    def test_equals_1(self):
        self.assertEqual(
            curvature(neutral_axis_value=10, position_value=5, strain_at_position=-0.001),
            0.0002,
        )

    def test_equals_2(self):
        self.assertEqual(
            curvature(neutral_axis_value=10, position_value=15, strain_at_position=0.001),
            0.0002,
        )

    def test_equals_3(self):
        self.assertEqual(
            curvature(neutral_axis_value=10, position_value=5, strain_at_position=0.001),
            -0.0002,
        )

    def test_equals_4(self):
        self.assertEqual(
            curvature(neutral_axis_value=10, position_value=15, strain_at_position=-0.001),
            -0.0002,
        )

    def test_error_1(self):
        self.assertRaises(
            ZeroDivisionError,
            curvature,
            neutral_axis_value=10.0,
            position_value=10.0,
            strain_at_position=-0.001,
        )

    def test_precision(self):
        position_value = 0.0
        neutral_axis_value = 10.0
        for factor_index in range(1, 100, 1):
            strain_value = 0.1 ** float(factor_index)
            with self.subTest(strain_value):
                curvature_value = Decimal(strain_value) / (Decimal(position_value) - Decimal(neutral_axis_value))
                self.assertEqual(
                    curvature(neutral_axis_value, position_value, float(strain_value)), float(curvature_value))


class TestCurvatureByPoints(TestCase):
    def setUp(self):
        self.top_edge = 1.0
        self.bottom_edge = 2.0
        self.top_strain = 0.1
        self.bottom_strain = -0.1
        self.result = (self.bottom_strain - self.top_strain) / (
            self.bottom_edge - self.top_edge
        )

    def test_equal_1(self):
        self.assertEqual(
            curvature_by_points(
                top_edge=self.top_edge,
                bottom_edge=self.bottom_edge,
                top_strain=self.top_strain,
                bottom_strain=self.bottom_strain,
            ),
            self.result,
        )

    def test_equal_2(self):
        self.assertEqual(
            curvature_by_points(
                top_edge=self.top_edge,
                bottom_edge=self.bottom_edge,
                top_strain=(-1) * self.top_strain,
                bottom_strain=(-1) * self.bottom_strain,
            ),
            (-1) * self.result,
        )

    def test_precision(self):
        for factor_index in range(1, 100, 1):
            top_strain = 0.1 ** factor_index
            with self.subTest(top_strain):
                result = (Decimal(self.bottom_strain) - Decimal(top_strain)) / (
                    Decimal(self.bottom_edge) - Decimal(self.top_edge)
                )
                self.assertEqual(
                    curvature_by_points(
                        top_edge=self.top_edge,
                        bottom_edge=self.bottom_edge,
                        top_strain=top_strain,
                        bottom_strain=self.bottom_strain,
                    ),
                    float(result),
                )


class TestStrain(TestCase):

    def setUp(self) -> None:
        self.neutral_axis_value = 10.
        self.curvature_value = 0.001

    def test_less_1(self):
        self.assertLess(strain(self.neutral_axis_value, self.curvature_value, position_value=5), 0.0)

    def test_greater_2(self):
        self.assertGreater(strain(self.neutral_axis_value, self.curvature_value, position_value=15), 0.0)

    def test_equals_1(self):
        self.assertEqual(strain(self.neutral_axis_value, self.curvature_value, position_value=5), -0.0005)

    def test_equals_2(self):
        self.assertEqual(strain(self.neutral_axis_value, self.curvature_value, position_value=15), 0.0005)

    def test_precision(self):
        position_value = 15.
        for factor_index in range(1, 100, 1):
            curvature_value = 0.1 ** factor_index
            with self.subTest(curvature_value):
                strain_value = Decimal(curvature_value) * (Decimal(position_value) - Decimal(self.neutral_axis_value))
                self.assertEqual(strain(self.neutral_axis_value, curvature_value, position_value), float(strain_value))


class TestPosition(TestCase):

    def setUp(self) -> None:
        self.neutral_axis_value = 10.
        self.curvature_value = 0.002

    def test_equals_1(self):
        self.assertEqual(
            position(
                neutral_axis_value=self.neutral_axis_value,
                curvature_value=self.curvature_value,
                strain_at_position=-0.001),
            5.0,
        )

    def test_equals_2(self):
        self.assertEqual(
            position(
                neutral_axis_value=self.neutral_axis_value,
                curvature_value=self.curvature_value,
                strain_at_position=0.001),
            15.0,
        )

    def test_precision(self):
        for factor_index in range(1, 100, 1):
            strain_value = 0.1 ** factor_index
            with self.subTest(strain_value):
                position_value = Decimal(strain_value) / Decimal(self.curvature_value) + Decimal(self.neutral_axis_value)
                self.assertEqual(
                    position(
                        neutral_axis_value=self.neutral_axis_value,
                        curvature_value=self.curvature_value,
                        strain_at_position=float(strain_value)),
                    float(position_value)
                )


class TestNeutralAxis(TestCase):
    def setUp(self) -> None:
        self.curvature_value = 0.001
        self.position_value = 10.0
        self.strain_at_position = 0.0

    def test_equals_1(self):
        self.assertEqual(
            neutral_axis(
                strain_at_position=self.strain_at_position,
                curvature_value=self.curvature_value,
                position_value=self.position_value),
            10.0,
        )

    def test_precision(self):
        for factor_index in range(1, 100, 1):
            curvature_value = 0.1 ** factor_index
            print(curvature_value)
            with self.subTest(curvature_value):
                neutral_axis_value = Decimal(self.position_value )+ (Decimal(self.strain_at_position) / Decimal(curvature_value))
                self.assertEqual(
                    neutral_axis(self.strain_at_position, curvature_value, self.position_value),
                    float(neutral_axis_value)
                )

class TestRemoveDuplicates(TestCase):
    def test_equals_1(self):
        my_list = [[0.0, 1.0], [0.0, 1.0], [1.0, 2.0]]
        self.assertListEqual(remove_duplicates(my_list), [[0.0, 1.0], [1.0, 2.0]])

    def test_not_equal_1(self):
        my_list = [[0.0, 1], [1.0, 2.0], [0.0, 1]]
        self.assertNotEqual(remove_duplicates(my_list), [[0.0, 1.0], [1.0, 2.0]])


class TestPositiveSign(TestCase):

    my_list = [[0.0, 1.0], [0.0, 1.0], [1.0, 2.0]]

    def test_all_positive(self):
        self.assertListEqual(positive_sign(self.my_list), self.my_list)

    def test_all_negative(self):
        negative_list = [[(-1) * pos[0], (-1) * pos[1]] for pos in self.my_list]
        self.assertListEqual(positive_sign(negative_list), self.my_list)

    def test_partial_negative_1(self):
        negative_list = [[pos[0], (-1) * pos[1]] for pos in self.my_list]
        self.assertListEqual(positive_sign(negative_list), self.my_list)

    def test_partial_negative_2(self):
        negative_list = [[(-1) * pos[0], pos[1]] for pos in self.my_list]
        self.assertListEqual(positive_sign(negative_list), self.my_list)


class TestNegativeSign(TestCase):

    positive_list = [[0.0, 1.0], [0.0, 1.0], [1.0, 2.0]]
    negative_list = [[(-1) * pos[0], (-1) * pos[1]] for pos in positive_list]

    def test_all_positive(self):
        self.assertListEqual(negative_sign(self.positive_list), self.negative_list)

    def test_all_negative(self):
        self.assertListEqual(negative_sign(self.negative_list), self.negative_list)

    def test_partial_positive_1(self):
        negative_list = [[pos[0], (-1) * pos[1]] for pos in self.positive_list]
        self.assertListEqual(negative_sign(negative_list), self.negative_list)

    def test_partial_positive_2(self):
        negative_list = [[(-1) * pos[0], pos[1]] for pos in self.positive_list]
        self.assertListEqual(negative_sign(negative_list), self.negative_list)


class TestInterpolation(TestCase):
    def test_1(self):
        self.assertEqual(
            interpolation(position_value=1.5, first_pair=[0.0, 1.0], second_pair=[1.0, 2.0]),
            0.5,
        )


class TestRemoveNone(TestCase):
    def test_1(self):
        self.assertListEqual(
            remove_none([0.0, 0.1, None, 1.0, None, 2.0, None, None]),
            [0.1, 1.0, 2.0],
        )

    def test_2(self):
        self.assertNotEqual(remove_none([0.0, 0.1]), [0.0, 0.1])

    def test_3(self):
        self.assertListEqual(remove_none([None, None, None]), [])


if __name__ == "__main__":
    main()