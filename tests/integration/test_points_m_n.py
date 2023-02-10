from m_n_kappa import (
    Steel,
    Rectangle,
    Crosssection,
)
from m_n_kappa.points import MNByStrain

from unittest import TestCase, main

same_sign = 'difference of axial forces at minimum and maximum strain have same sign'


class TestMNByStrainElastic(TestCase):

    def setUp(self):
        self.steel = Steel()
        self.rectangle = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section = self.steel + self.rectangle
        self.cross_section = Crosssection([self.section])

    def test_positive_axial_force(self):
        self.axial_force = 10.0
        self.strain = (self.axial_force / self.rectangle.area) / self.steel.E_a
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertAlmostEqual(
            self.m_n_by_strain.strain, self.strain, 5
        )

    def test_negative_axial_force(self):
        self.axial_force = -10.0
        self.strain = (self.axial_force / self.rectangle.area) / self.steel.E_a
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertAlmostEqual(
            self.m_n_by_strain.strain, self.strain, 5
        )


class TestMNByStrainPlastic(TestCase):

    def setUp(self) -> None:
        self.f_y = 100
        self.failure_strain = 0.15
        self.steel = Steel(f_y=self.f_y, failure_strain=self.failure_strain)
        self.rectangle = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section = self.steel + self.rectangle
        self.cross_section = Crosssection([self.section])

    def test_positive_axial_force_in_elastic(self):
        self.axial_force = 10.0
        self.strain = (self.axial_force / self.rectangle.area) / self.steel.E_a
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertAlmostEqual(
            self.m_n_by_strain.strain, self.strain, 5
        )

    def test_negative_axial_force_in_elastic(self):
        self.axial_force = -10.0
        self.strain = (self.axial_force / self.rectangle.area) / self.steel.E_a
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertAlmostEqual(
            self.m_n_by_strain.strain, self.strain, 5
        )

    def test_positive_axial_force_above_maximum_axial_force(self):
        self.axial_force = self.f_y * self.rectangle.area + 50
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertEqual(
            self.m_n_by_strain.strain, None
        )
        self.assertEqual(
            self.m_n_by_strain.not_successful_reason, same_sign
        )

    def test_negative_axial_force_below_maximum_axial_force(self):
        self.axial_force = - self.f_y * self.rectangle.area - 50
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertEqual(
            self.m_n_by_strain.strain, None
        )
        self.assertEqual(
            self.m_n_by_strain.not_successful_reason, same_sign
        )


if __name__ == "__main__":
    main()