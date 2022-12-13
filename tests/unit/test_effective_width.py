from unittest import TestCase, main

from m_n_kappa.general import EffectiveWidths


class TestEffectiveWidths(TestCase):
    def setUp(self) -> None:
        self.membran = 1.0
        self.bending = 2.0
        self.positive_strain = 1.0
        self.negative_strain = -1.0
        self.effective_widths = EffectiveWidths(
            membran=self.membran,
            bending=self.bending,
            reinforcement_under_tension_use_membran_width=False,
            reinforcement_under_compression_use_membran_width=True,
            concrete_under_tension_use_membran_width=False,
            concrete_under_compression_use_membran_width=True,
        )

    def test_width_concrete_positive_equal(self):
        self.assertEqual(
            self.effective_widths.width("Concrete", self.positive_strain), self.bending
        )

    def test_width_concrete_positive_unequal(self):
        self.assertNotEqual(
            self.effective_widths.width("Concrete", self.positive_strain), self.membran
        )

    def test_width_concrete_negative_equal(self):
        self.assertEqual(
            self.effective_widths.width("Concrete", self.negative_strain), self.membran
        )

    def test_width_concrete_negative_unequal(self):
        self.assertNotEqual(
            self.effective_widths.width("Concrete", self.negative_strain), self.bending
        )

    def test_width_reinforcement_positive_equal(self):
        self.assertEqual(
            self.effective_widths.width("Reinforcement", self.positive_strain),
            self.bending,
        )

    def test_width_reinforcement_positive_unequal(self):
        self.assertNotEqual(
            self.effective_widths.width("Reinforcement", self.positive_strain),
            self.membran,
        )

    def test_width_reinforcement_negative_equal(self):
        self.assertEqual(
            self.effective_widths.width("Reinforcement", self.negative_strain),
            self.membran,
        )

    def test_width_reinforcement_negative_unequal(self):
        self.assertNotEqual(
            self.effective_widths.width("Reinforcement", self.negative_strain),
            self.bending,
        )

    def test__concrete_width_positive(self):
        self.assertEqual(
            self.effective_widths._concrete_width(self.positive_strain), self.bending
        )

    def test__concrete_width_negative(self):
        self.assertEqual(
            self.effective_widths._concrete_width(self.negative_strain), self.membran
        )

    def test__reinforcement_width_positive(self):
        self.assertEqual(
            self.effective_widths._concrete_width(self.positive_strain), self.bending
        )

    def test__reinforcement_width_negative(self):
        self.assertEqual(
            self.effective_widths._concrete_width(self.positive_strain), self.bending
        )

    def test_strain_input_positive(self):
        for strain in [1.0, 10.0, 100.0]:
            with self.subTest(strain):
                self.assertEqual(
                    self.effective_widths.width("Concrete", strain), self.bending
                )

    def test_strain_input_negative(self):
        for strain in [1.0, 10.0, 100.0]:
            with self.subTest(strain):
                self.assertEqual(
                    self.effective_widths.width("Concrete", strain * (-1)), self.membran
                )


if __name__ == "__main__":
    main()