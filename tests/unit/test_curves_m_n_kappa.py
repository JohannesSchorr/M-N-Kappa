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
            0.0,
            236666.87937886757,
            236666.50674824225, 
            355026.8934163825,
            361270.59229865274,
            372282.02545773983,
            372381.6934067906,
            384814.01494666666, 
            400000.0,
            406270.5922986528,
        ]
        self.negative_moments = [
            0.0,
            -236666.2412422644,
            -236666.8262777007,
            -355026.8934163825,
            -361270.5922986573,
            -372282.02545773325,
            -372381.6934067898,
            -384814.0149466655,
            -400000.0,
            -406270.5922986531,
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
            list(set(self.negative_moments + self.positive_moments)),
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
            0.0,
            156664.9683024992,
            220473.64281681945, 
            235021.79524176393,
            285162.6100359638, 
            295216.6590597687,
            300000.0,
            318537.868720389,
            344405.28555681015,
        ]
        self.negative_moments = [
            0.0,
            -156664.96830249924,
            -220473.6428168192, 
            -235021.795241764,
            -285162.6100359637, 
            -295216.65905976767,
            -300000.0,
            -318537.8687203883, 
            -344405.28555680957,
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
            list(set(self.negative_moments + self.positive_moments)),
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
        self.positive_moments = [
            0.0,
            276002147.55783015,
            314408413.19173497,
            318166054.2148396,
            376022894.6108031,
            393853527.41305673,
            440108705.8153522, 
            440926757.5389217,
            468057239.82187307,
            484937769.80569863, 
            503429585.222551,
            503493186.5866488,
            511886928.6233367,
            512744493.3587002,
            520150830.48371154,
            521989031.60150206,
            523029210.643234,
            527919385.7951919,
            527919397.17408717,
            535895219.7302048,
        ]

        self.negative_moments = [
            -442383631.56713593,
            -409298629.82524645, 
            -405044585.1148733, 
            -402397204.3752972,
            -390004803.4567734,
            -379545377.97262585,
            -366676197.31785566,
            -351444781.5738121,
            -349978062.41072005, 
            -335152995.07909435,
            -330150913.4412089,
            -330142461.3828803,
            -324538633.8511237,
            -319575671.5961261, 
            -307038309.80922854,
            -297526517.9525038,
            -296104456.0811664, 
            -285145190.0725863,
            -281696649.83730423,
            -259460750.0,
            -259460749.99999994,
            -259218558.661083,
            -124178647.99999991,
            -55046304.28887214, 
            -54822261.18930392, 
            -35201848.42556666,
            -35020735.64617353,
            -8414269.999999916,
            
            0.0,
        ]

    def test_input_cross_section(self):
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_section)
        self.assertCountEqual(
            m_n_kappa_curve.sub_cross_sections,
            tuple([self.girder_cross_section, self.slab_cross_section]),
        )

    def test_points_positive_moment(self):
        self.maxDiff = None
        m_n_kappa_curve = MNKappaCurve(sub_cross_sections=self.cross_section)
        print(m_n_kappa_curve.points.print_points())
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.positive_moments)

    def test_points_negative_moment(self):
        self.maxDiff = None
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_section,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )
        self.assertCountEqual(m_n_kappa_curve.points.moments, self.negative_moments)
        print(m_n_kappa_curve.points.print_points())

    def test_points_all(self):
        self.maxDiff = None
        m_n_kappa_curve = MNKappaCurve(
            sub_cross_sections=self.cross_section,
            include_positive_curvature=True,
            include_negative_curvature=True,
        )
        self.assertCountEqual(
            m_n_kappa_curve.points.moments,
            list(set(self.negative_moments + self.positive_moments)),
        )
        print(m_n_kappa_curve.points.print_points())


if __name__ == "__main__":
    main()
