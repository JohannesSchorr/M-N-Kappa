from m_n_kappa import (
    IProfile,
    Steel,
    Rectangle,
    Concrete,
    RebarLayer,
    Reinforcement,
    Crosssection,
    StrainPosition,
)
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
            [400000.0, 355026.8934963956, -355026.8934963956, -400000.0],
        )

    def test_points_curvature(self):
        self.assertCountEqual(
            self.m_n.points.curvatures,
            [0.0] * 4,
        )

    def test_points_neutral_axis(self):
        self.assertCountEqual(
            self.m_n.points.axial_forces,
            [40000.0, 35500.0, -35500.0, -40000.0],
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


class TestMNKappaCurveCompositeGirder(TestCase):
    def setUp(self) -> None:
        self.concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
        self.concrete = Concrete(f_cm=30 + 8, compression_stress_strain_type="Parabola")
        self.concrete_section = self.concrete_slab + self.concrete
        self.reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
        self.top_layer = RebarLayer(
            centroid_z=25, width=2000, rebar_horizontal_distance=200, rebar_diameter=10
        )
        self.top_rebar_layer = self.reinforcement + self.top_layer
        self.bottom_layer = RebarLayer(
            centroid_z=75, width=2000, rebar_horizontal_distance=100, rebar_diameter=10
        )
        self.bottom_rebar_layer = self.reinforcement + self.bottom_layer
        self.i_profile = IProfile(
            top_edge=100.0, b_fo=200, t_fo=15, h_w=200 - 2 * 15, t_w=15, centroid_y=0.0
        )
        self.steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
        self.steel_section = self.i_profile + self.steel
        self.girder_cross_section = self.steel_section
        self.slab_cross_section = (
            self.concrete_section + self.top_rebar_layer + self.bottom_rebar_layer
        )
        self.cross_section = self.girder_cross_section + self.slab_cross_section
        self.m_n = MNCurve(self.cross_section)

    def test_points_moment(self):
        self.assertCountEqual(
            self.m_n.points.moments,
            [
                -259460749.9999999,
                -124179458.88143954,
                -259460750.0000002,
                527919385.7951919,
                440926757.53892136,
                468057239.82207,
                527919397.17408717,
            ],
        )

    def test_points_curvature(self):
        self.assertCountEqual(
            self.m_n.points.curvatures,
            [0.0] * 7,
        )

    def test_points_neutral_axis(self):
        self.assertCountEqual(
            self.m_n.points.axial_forces,
            [
                -3420000.256228251,
                -3035250.0,
                -2860875.0,
                -3420000.0,
                620906.044407197,
                1297312.5,
                1297312.5000000002,
            ],
        )

    def test_maximum_strain_positions(self):
        self.assertCountEqual(
            self.m_n._decisive_strains_cross_sections[0],
            [
                StrainPosition(
                    strain=-0.000632439215071535, position=0.0, material="Concrete"
                ),
                StrainPosition(strain=0.15, position=25, material="Reinforcement"),
            ],
        )
        self.assertCountEqual(
            self.m_n._decisive_strains_cross_sections[1],
            [
                StrainPosition(0.15, 10.0, "Steel"),
                StrainPosition(
                    strain=-0.000722535505430242, position=100.0, material="Steel"
                ),
            ],
        )


if __name__ == "__main__":
    main()
