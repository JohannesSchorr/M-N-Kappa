from m_n_kappa import (
    Steel,
    Rectangle,
    Crosssection,
    StrainPosition,
)
from m_n_kappa.general import NotSuccessfulReason
from m_n_kappa.points import MomentAxialForceCurvature

from unittest import TestCase, main

same_sign_curvature = NotSuccessfulReason(variable='curvature').reason


class TestMNKappa(TestCase):
    def setUp(self) -> None:
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.axial_force = self.rectangle_top.area * self.steel.f_u

    def test_not_successful(self):
        strain_position = StrainPosition(
            strain=self.steel.epsilon_y, position=0.0, material="Material"
        )
        m_n_k = MomentAxialForceCurvature(
            self.cross_sections, axial_force=self.axial_force*1.1, strain_position=strain_position,
            positive_curvature=False
        )
        self.assertEqual(m_n_k.successful, False)
        self.assertEqual(str(m_n_k.not_successful_reason), str(same_sign_curvature))

    def test_successful(self):
        strain_position = StrainPosition(
            strain=self.steel.epsilon_y, position=0.0, material="Material"
        )
        m_n_k = MomentAxialForceCurvature(
            self.cross_sections, axial_force=self.axial_force * 0.1, strain_position=strain_position,
            positive_curvature=False
        )
        self.assertEqual(m_n_k.successful, True)


if __name__ == "__main__":
    main()
