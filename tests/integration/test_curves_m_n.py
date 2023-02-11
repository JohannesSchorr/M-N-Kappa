from m_n_kappa import Steel, Rectangle, Crosssection, StrainPosition
from m_n_kappa.curves_m_n_kappa import MNCurve

from unittest import TestCase, main


class TestMNCurveEquivalentCrossSections(TestCase):
    def setUp(self) -> None:
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.cross_sections_switched = [
            self.cross_section_bottom,
            self.cross_section_top,
        ]
        self.m_n = MNCurve(self.cross_sections)

    def test_points_moment(self):
        self.assertCountEqual(
            self.m_n.points.moments,
            [400000.0, 355026.8934963956, -355026.8934963956, -400000.0] * 2,
        )

    def test_points_curvature(self):
        self.assertCountEqual(
            self.m_n.points.curvatures,
            [0.0] * 8,
        )

    def test_points_neutral_axis(self):
        self.assertCountEqual(
            self.m_n.points.axial_forces,
            [40000.0, 35500.0, -35500.0, -40000.0] * 2,
        )

    def test_maximum_strain_positions(self):
        self.assertCountEqual(
            self.m_n._decisive_strains_cross_sections[0],
            [StrainPosition(0.15, 0.0, "Steel"), StrainPosition(-0.15, 0.0, "Steel")],
        )
        self.assertCountEqual(
            self.m_n._decisive_strains_cross_sections[1],
            [StrainPosition(0.15, 10.0, "Steel"), StrainPosition(-0.15, 10.0, "Steel")],
        )


if __name__ == "__main__":
    main()
