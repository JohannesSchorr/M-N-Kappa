from m_n_kappa.curves_m_n_kappa import MNKappaCurve, MNKappaCurvePoints
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


class TestMNKappaCurvePoints(TestCase):
    def setUp(self):
        self.curvature = 0.001
        self.points = MNKappaCurvePoints()
        self.points.add(
            moment=100,
            curvature="",
            axial_force=100,
            strain_difference=0.0001,
            cross_section="",
            axial_force_cross_section_number="",
            strain_position="",
        )
        self.points.add(
            moment=200,
            curvature="",
            axial_force=100,
            strain_difference=0.0002,
            cross_section="",
            axial_force_cross_section_number="",
            strain_position="",
        )
        self.points.add(
            moment=300,
            curvature="",
            axial_force=200,
            strain_difference=0.0001,
            cross_section="",
            axial_force_cross_section_number="",
            strain_position="",
        )
        self.points.add(
            moment=400,
            curvature="",
            axial_force=200,
            strain_difference=0.0002,
            cross_section="",
            axial_force_cross_section_number="",
            strain_position="",
        )
        self.points.add(
            moment=400,
            curvature="",
            axial_force=300,
            strain_difference=0.0003,
            cross_section="",
            axial_force_cross_section_number="",
            strain_position="",
        )

    def test_moment_in_between(self):
        self.assertEqual(
            self.points.moment(axial_force=150.0, strain_difference=0.00015), 250.0
        )

    def test_moment_same_axial_force(self):
        self.assertAlmostEqual(
            self.points.moment(axial_force=100.0, strain_difference=0.00015), 150.0
        )

    def test_moment_same_strain_difference(self):
        self.assertAlmostEqual(
            self.points.moment(axial_force=150, strain_difference=0.0002), 300.0
        )

    def test_moment_same_axial_force_and_same_strain_difference(self):
        self.assertEqual(
            self.points.moment(axial_force=100.0, strain_difference=0.0001), 100.0
        )

    def test_moment_with_three_points(self):
        self.assertEqual(
            self.points.moment(axial_force=150.0, strain_difference=0.00025), 300.0
        )


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
            118310.12038053536,
            118397.16128195659,
            355026.8934163825,
            361270.59229865274,
            372282.02545773983,
            372381.6934067906,
            192407.00747329212,
            400000.0,
            406270.5922986528,
        ]
        self.negative_moments = [
            0.0,
            -118310.12038053536,
            -118397.16128195582,
            -355026.8934163825,
            -361270.5922986573,
            -372282.02545773325,
            -372381.6934067898,
            -192407.0074733372,
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
            78372.81572891976,
            109389.16919138256,
            235021.79524176393,
            163189.90797100778,
            295216.6590597687,
            300000.0,
            344405.28555681015,
        ]
        self.negative_moments = [
            0.0,
            -163189.90797098214,
            -109389.1691913825,
            -235021.795241764,
            -78304.57731215179,
            -295216.65905976767,
            -300000.0,
            -78372.81572891944,
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
            31752973.329176545,
            31946950.316480417,
            202541843.68077758,
            202542405.76940852,
            220350528.10889408,
            220350472.04692814,
            440926757.5389217,
            468057239.82187307,
            220497566.30864674,
            503429585.222551,
            503493186.5866488,
            227322060.4077785,
            512744493.3587002,
            520150830.48371154,
            521989031.60150206,
            228125734.819494,
            527919385.7951919,
            527919397.17408717,
            229538989.35381523,
            230505964.4745606,
        ]

        self.negative_moments = [
            -317389109.78996813,
            -300168065.8446009,
            -402397204.3752972,
            -390004803.4567734,
            -379545377.97262585,
            -366676197.31785566,
            -351444781.5738121,
            -290788568.90372676,
            -335152995.07909435,
            -330150913.4412089,
            -330142461.3828803,
            -324538633.8511237,
            -278531953.09826255,
            -307038309.80922854,
            -297526517.9525038,
            -285145190.0725863,
            -281696649.83730423,
            -259460750.0,
            -259460749.99999994,
            -259218558.661083,
            -124178647.99999991,
            -251211193.562506,
            -276414218.2089273,
            -35201848.42556666,
            -35020735.64617353,
            -8414269.999999916,
            -241653898.19328588,
            -241653819.78843212,
            -220509136.56065917,
            -220508448.33147323,
            -30936574.859719712,
            -30743576.176289596,
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
