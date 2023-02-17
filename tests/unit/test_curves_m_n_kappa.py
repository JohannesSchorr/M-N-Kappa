from m_n_kappa.curves_m_n_kappa import MNKappaCurve
from m_n_kappa import (
    IProfile,
    Steel,
    Rectangle,
    Concrete,
    RebarLayer,
    Reinforcement,
    Crosssection,
)

from unittest import TestCase, main


class TestMNKappaCurveEquivalentCrossSections(TestCase):
    def setUp(self) -> None:
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.cross_section = Crosssection(
            sections=[self.section_top, self.section_bottom]
        )
        self.positive_moments = [
            400000.0,
            355026.8934963956,
            361270.5959888153,
            372381.58415482414,
        ]
        self.negative_moments = [
            -400000.0,
            -355026.8934963956,
            -361270.5959888153,
            -372381.58415482554,
        ]

    def test_input_cross_section_list(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_sections)
        self.assertCountEqual(
            m_n_kappa_curve.sub_cross_sections, tuple(self.cross_sections)
        )

    def test_input_cross_section_tuple(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=tuple(self.cross_sections))
        self.assertCountEqual(
            m_n_kappa_curve.sub_cross_sections, tuple(self.cross_sections)
        )

    def test_points_positive_moment(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_sections)
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.positive_moments)

    def test_points_negative_moment(self):
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_sections,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.negative_moments)

    def test_points_all(self):
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_sections,
            include_positive_curvature=True,
            include_negative_curvature=True,
        )
        self.assertCountEqual(
            m_n_kappa_curve.points.moments,
            self.negative_moments + self.positive_moments,
        )


class TestMNKappaCurveEquivalentCrossSectionsDifferentMaterial(TestCase):
    def setUp(self) -> None:
        self.steel_top = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel_top + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.steel_bottom = Steel(f_y=235, f_u=300, failure_strain=0.1)
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel_bottom + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.cross_section = Crosssection(
            sections=[self.section_top, self.section_bottom]
        )
        self.positive_moments = [
            344405.2855266683,
            235021.795018096,
            295216.89888096845,
            300000.0,
        ]
        self.negative_moments = [
            -344405.2855266683,
            -235021.79501809616,
            -295216.8988809693,
            -300000.0,
        ]

    def test_points_positive_moment(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_sections)
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.positive_moments)

    def test_points_negative_moment(self):
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_sections,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.negative_moments)

    def test_points_all(self):
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_sections,
            include_positive_curvature=True,
            include_negative_curvature=True,
        )
        self.assertCountEqual(
            m_n_kappa_curve.points.moments,
            self.negative_moments + self.positive_moments,
        )


class TestMNKappaCurveCompositeGirder(TestCase):
    def setUp(self) -> None:
        self.concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
        self.concrete = Concrete(f_cm=30 + 8, compression_stress_strain_type='Parabola')
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
        self.positive_moments = [
            440926757.53892136,
            464727043.9961377,
            468057239.82207,
            503430142.9521369,
            503493742.3022555,
            527919385.7951919,
            527919397.17408717,
        ]

        self.negative_moments = [
            -366676709.2688143,
            -351445334.90257263,
            -335153500.3201116,
            -330151819.0727011,
            -330143367.3714007,
            -259460750.0000002,
            -259460749.9999999,
            -124179458.88143954,
        ]

    def test_input_cross_section(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_section)
        self.assertCountEqual(
            m_n_kappa_curve.sub_cross_sections,
            tuple([self.girder_cross_section, self.slab_cross_section]),
        )

    def test_points_positive_moment(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_section)
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.positive_moments)

    def test_points_negative_moment(self):
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_section,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.negative_moments)

    def test_points_all(self):
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_section,
            include_positive_curvature=True,
            include_negative_curvature=True,
        )
        self.assertCountEqual(
            m_n_kappa_curve.points.moments,
            self.negative_moments + self.positive_moments,
        )


if __name__ == "__main__":
    main()
