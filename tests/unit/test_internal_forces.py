from unittest import TestCase, main

from m_n_kappa.internalforces import SingleSpan


class TestSingleSpanUniformLoad(TestCase):
    def setUp(self):
        self.beam_length = 10.0
        self.load = 20.0
        self.forces = SingleSpan(length=self.beam_length, uniform_load=self.load)

    def test_moment(self):
        self.assertEqual(
            self.forces.moment(0.5 * self.beam_length),
            self.load * self.beam_length ** (2.0) / 8.0,
        )

    def test_maximum_moment(self):
        self.assertEqual(
            self.forces.maximum_moment, self.load * self.beam_length ** (2.0) / 8.0
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
        self.forces = SingleSpan(
            length=self.beam_length, loads=[[0.5 * self.beam_length, self.load]]
        )

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
            self.forces.maximum_moment, 0.5 * self.load * 0.5 * self.beam_length
        )

    def test_moment(self):
        self.assertEqual(
            self.forces.moment(0.5 * self.beam_length),
            0.5 * self.load * 0.5 * self.beam_length,
        )


if __name__ == "__main__":
    main()
