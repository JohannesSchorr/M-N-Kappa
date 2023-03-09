from m_n_kappa import (
    Steel,
    Rectangle,
    Crosssection,
)
from m_n_kappa.general import NotSuccessfulReason
from m_n_kappa.points import MNByStrain, MomentAxialForce

from unittest import TestCase, main

same_sign = NotSuccessfulReason(variable="strain")


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
        self.assertAlmostEqual(self.m_n_by_strain.strain, self.strain, 5)

    def test_negative_axial_force(self):
        self.axial_force = -10.0
        self.strain = (self.axial_force / self.rectangle.area) / self.steel.E_a
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertAlmostEqual(self.m_n_by_strain.strain, self.strain, 5)


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
        self.assertAlmostEqual(self.m_n_by_strain.strain, self.strain, 5)

    def test_negative_axial_force_in_elastic(self):
        self.axial_force = -10.0
        self.strain = (self.axial_force / self.rectangle.area) / self.steel.E_a
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertAlmostEqual(self.m_n_by_strain.strain, self.strain, 5)

    def test_positive_axial_force_above_maximum_axial_force(self):
        self.axial_force = self.f_y * self.rectangle.area + 50
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertEqual(self.m_n_by_strain.strain, None)
        self.assertEqual(self.m_n_by_strain.not_successful_reason, same_sign)

    def test_negative_axial_force_below_maximum_axial_force(self):
        self.axial_force = -self.f_y * self.rectangle.area - 50
        self.m_n_by_strain = MNByStrain(self.cross_section, self.axial_force)
        self.assertEqual(self.m_n_by_strain.strain, None)
        self.assertEqual(self.m_n_by_strain.not_successful_reason, same_sign)


class TestMomentAxialForceElastic(TestCase):
    def setUp(self):
        self.steel = Steel()
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.strain = 0.0001
        self.axial_force = self.rectangle_top.area * self.strain * self.steel.E_a
        self.moment = (
            -self.axial_force
            * 0.5
            * (self.rectangle_top.height + self.rectangle_bottom.height)
        )
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.cross_sections_switched = [
            self.cross_section_bottom,
            self.cross_section_top,
        ]

    def test_positive_strain_axial_force(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=self.strain
        )
        self.assertEqual(m_n.axial_force, self.axial_force)

    def test_negative_strain_axial_force(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=-self.strain
        )
        self.assertEqual(m_n.axial_force, -self.axial_force)

    def test_positive_strain_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=self.strain
        )
        self.assertAlmostEqual(m_n.moment(), self.moment)

    def test_negative_strain_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=-self.strain
        )
        self.assertAlmostEqual(m_n.moment(), -self.moment)

    def test_positive_strain_axial_force_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=self.strain
        )
        self.assertEqual(m_n.axial_force, self.axial_force)

    def test_negative_strain_axial_force_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=-self.strain
        )
        self.assertEqual(m_n.axial_force, -self.axial_force)

    def test_positive_strain_moment_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=self.strain
        )
        self.assertAlmostEqual(m_n.moment(), -self.moment)

    def test_negative_strain_moment_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=-self.strain
        )
        self.assertAlmostEqual(m_n.moment(), self.moment)

    def test_positive_axial_force_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, axial_force=self.axial_force
        )
        self.assertAlmostEqual(m_n.moment(), self.moment)

    def test_negative_axial_force_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, axial_force=-self.axial_force
        )
        self.assertAlmostEqual(m_n.moment(), -self.moment)


class TestMomentAxialForceYield(TestCase):
    def setUp(self):
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.strain = self.steel.epsilon_y
        self.axial_force = self.rectangle_top.area * self.strain * self.steel.E_a
        self.moment = (
            -self.axial_force
            * 0.5
            * (self.rectangle_top.height + self.rectangle_bottom.height)
        )
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.cross_sections_switched = [
            self.cross_section_bottom,
            self.cross_section_top,
        ]

    def test_positive_strain_axial_force(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=self.strain
        )
        self.assertAlmostEqual(m_n.axial_force, self.axial_force, 0)

    def test_negative_strain_axial_force(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=-self.strain
        )
        self.assertAlmostEqual(m_n.axial_force, -self.axial_force, 0)

    def test_positive_strain_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=self.strain
        )
        self.assertAlmostEqual(m_n.moment(), self.moment, -2)

    def test_negative_strain_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, strain=-self.strain
        )
        self.assertAlmostEqual(m_n.moment(), -self.moment, -2)

    def test_positive_strain_axial_force_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=self.strain
        )
        self.assertAlmostEqual(m_n.axial_force, self.axial_force, 0)

    def test_negative_strain_axial_force_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=-self.strain
        )
        self.assertAlmostEqual(m_n.axial_force, -self.axial_force, 0)

    def test_positive_strain_moment_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=self.strain
        )
        self.assertAlmostEqual(m_n.moment(), -self.moment, -2)

    def test_negative_strain_moment_switched_cross_sections(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections_switched, strain=-self.strain
        )
        self.assertAlmostEqual(m_n.moment(), self.moment, -2)

    def test_positive_axial_force_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, axial_force=self.axial_force
        )
        self.assertAlmostEqual(m_n.moment(), self.moment, -2)

    def test_negative_axial_force_moment(self):
        m_n = MomentAxialForce(
            sub_cross_sections=self.cross_sections, axial_force=-self.axial_force
        )
        self.assertAlmostEqual(m_n.moment(), -self.moment, -2)


if __name__ == "__main__":
    main()
