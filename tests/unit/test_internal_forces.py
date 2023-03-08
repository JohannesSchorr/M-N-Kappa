from unittest import TestCase, main

from m_n_kappa.loading import SingleSpan, SingleLoad


class TestSingleSpanUniformLoad(TestCase):
    def setUp(self):
        self.beam_length = 10.0
        self.load = 20.0
        self.forces = SingleSpan(length=self.beam_length, uniform_load=self.load)

    def test_moment(self):
        self.assertEqual(
            self.forces.moment(0.5 * self.beam_length),
            self.load * self.beam_length**2.0 / 8.0,
        )

    def test_maximum_moment(self):
        self.assertEqual(
            self.forces.maximum_moment, self.load * self.beam_length**2.0 / 8.0
        )

    def test_transversal_shear_1(self):
        self.assertEqual(self.forces.transversal_shear(0.5 * self.beam_length), 0.0)

    def test_transversal_shear_2(self):
        self.assertEqual(
            self.forces.transversal_shear(0.0), 0.5 * self.load * self.beam_length
        )

    def test_transversal_shear_3(self):
        self.assertEqual(
            self.forces.transversal_shear(self.beam_length),
            -0.5 * self.load * self.beam_length,
        )

    def test_transversal_shear_support_left(self):
        self.assertEqual(
            self.forces.transversal_shear_support_left,
            0.5 * self.load * self.beam_length,
        )

    def test_transversal_shear_support_right(self):
        self.assertEqual(
            self.forces.transversal_shear_support_right,
            -0.5 * self.load * self.beam_length,
        )

    def test_length(self):
        self.assertEqual(self.forces.length, self.beam_length)

    def test_load(self):
        self.assertEqual(self.forces.loading, self.load * self.beam_length)


class TestSingleSpanSingleLoad(TestCase):
    def setUp(self):
        self.beam_length = 10.0
        self.load = 10.0
        self.load_position = 0.5 * self.beam_length
        self.single_load = SingleLoad(self.load_position, self.load)
        self.forces = SingleSpan(length=self.beam_length, loads=[self.single_load])

    def test_transversal_shear_support_left(self):
        self.assertEqual(self.forces.transversal_shear_support_left, 0.5 * self.load)

    def test_transversal_shear_support_right(self):
        self.assertEqual(self.forces.transversal_shear_support_right, -0.5 * self.load)

    def test_length(self):
        self.assertEqual(self.forces.length, self.beam_length)

    def test_load(self):
        self.assertEqual(self.forces.loading, self.load)

    def test_maximum_moment(self):
        self.assertEqual(
            self.forces.maximum_moment, 0.5 * self.load * self.load_position
        )

    def test_moment(self):
        self.assertEqual(
            self.forces.moment(0.5 * self.beam_length),
            0.5 * self.load * 0.5 * self.beam_length,
        )

    def test_position_of_maximum_moment(self):
        self.assertEqual(
            self.forces.positions_of_maximum_moment(), [self.load_position]
        )

    def test_position_of_maximum_deformation(self):
        self.assertEqual(
            self.forces.position_of_maximum_deformation(), self.load_position
        )


class TestSingleSpanSingleLoads(TestCase):
    """Single span with more than one single load"""

    def setUp(self) -> None:
        self.beam_length = 10.0
        self.load = 10.0
        self.load_positions = [
            1.0 / 3.0 * self.beam_length,
            2.0 / 3.0 * self.beam_length,
        ]
        self.single_loads = [
            SingleLoad(position, 0.5 * self.load) for position in self.load_positions
        ]
        self.forces = SingleSpan(length=self.beam_length, loads=self.single_loads)

    def test_transversal_shear_support_left(self):
        self.assertAlmostEqual(
            self.forces.transversal_shear_support_left, 0.5 * self.load
        )

    def test_transversal_shear_support_right(self):
        self.assertAlmostEqual(
            self.forces.transversal_shear_support_right, -0.5 * self.load
        )

    def test_length(self):
        self.assertEqual(self.forces.length, self.beam_length)

    def test_load(self):
        self.assertEqual(self.forces.loading, self.load)

    def test_positions_of_maximum_moment(self):
        self.assertListEqual(
            self.forces.positions_of_maximum_moment(), self.load_positions
        )

    def test_position_of_maximum_deformation(self):
        self.assertEqual(
            self.forces.position_of_maximum_deformation(), 0.5 * self.beam_length
        )


if __name__ == "__main__":
    main()
