from unittest import TestCase, main

from m_n_kappa import (
    Rectangle,
    Concrete,
    Reinforcement,
    RebarLayer,
    Steel,
    IProfile,
    MKappaCurve,
    StrainPosition,
)
from m_n_kappa.general import NotSuccessfulReason

same_sign = NotSuccessfulReason("same sign curvature")
max_iterations = NotSuccessfulReason("iterations")

concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
concrete = Concrete(f_cm=30 + 8)
concrete_section = concrete_slab + concrete
reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
top_layer = RebarLayer(
    centroid_z=25, width=2000, rebar_horizontal_distance=200, rebar_diameter=10
)
top_rebar_layer = reinforcement + top_layer
bottom_layer = RebarLayer(
    centroid_z=75, width=2000, rebar_horizontal_distance=100, rebar_diameter=10
)
bottom_rebar_layer = reinforcement + bottom_layer
i_profile = IProfile(
    top_edge=100.0, b_fo=200, t_fo=15, h_w=200 - 2 * 15, t_w=15, centroid_y=0.0
)
steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
steel_section = i_profile + steel


class TestCompositeBeamPositive(TestCase):
    def setUp(self) -> None:
        self.cross_section = (
            concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section
        )
        self.m_kappa_curve = MKappaCurve(cross_section=self.cross_section)

    def test_cross_section(self):
        self.assertEqual(self.m_kappa_curve.cross_section, self.cross_section)

    def test_not_successful(self):
        self.maxDiff = None
        self.assertCountEqual(
            self.m_kappa_curve.not_successful_reason,
            [
                NotSuccessfulReason(
                    keyword="iteration",
                    strain_position=StrainPosition(
                        strain=-0.0035, position=0.0, material="Concrete"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0025, position=25, material="Reinforcement"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0025, position=75, material="Reinforcement"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0016904761904761904, position=100.0, material="Steel"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0016904761904761904, position=115.0, material="Steel"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0016904761904761904, position=285.0, material="Steel"
                    ),
                ),
            ],
        )

    def test_m_kappa_points_moments(self):
        self.assertCountEqual(
            self.m_kappa_curve.m_kappa_points.moments,
            [
                0.0,
                279065090.70273054,
                438755789.00432056,
                516818301.88354325,
                538683420.997121,
                541724537.7407295,
            ],
        )


class TestCompositeBeamNegative(TestCase):
    def setUp(self) -> None:
        self.cross_section = (
            concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section
        )
        self.m_kappa_curve = MKappaCurve(
            cross_section=self.cross_section,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )

    def test_not_successful(self):
        self.assertCountEqual(
            self.m_kappa_curve.not_successful_reason,
            [
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0016904761904761904, position=115.0, material="Steel"
                    ),
                )
            ],
        )

    def test_m_kappa_points_moments(self):
        self.assertCountEqual(
            self.m_kappa_curve.m_kappa_points.moments,
            [
                -442383661.16446424,
                -409298265.3218652,
                -405044752.007268,
                -349978085.7744969,
                -319574554.1645081,
                -296103666.48247814,
                -54944467.314156845,
                -54718951.26913915,
                0.0,
            ],
        )


class TestSlimFloorTProfile(TestCase):
    def setUp(self) -> None:
        self.t_profile = IProfile(
            top_edge=50.0,
            t_w=10.0,
            h_w=200.0,
            b_fu=200.0,
            t_fu=15.0,
            has_top_flange=False,
        )
        self.steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
        self.steel_profile = self.t_profile + self.steel
        self.concrete_top_cover = Rectangle(
            top_edge=0.0, bottom_edge=self.t_profile.top_edge, width=2000
        )
        self.concrete_left = Rectangle(
            top_edge=self.concrete_top_cover.bottom_edge,
            bottom_edge=self.t_profile.top_edge + self.t_profile.h_w,
            width=0.5 * (2000 - self.t_profile.t_w),
            left_edge=-1000,
        )
        self.concrete_right = Rectangle(
            top_edge=self.concrete_top_cover.bottom_edge,
            bottom_edge=self.t_profile.top_edge + self.t_profile.h_w,
            width=0.5 * (2000 - self.t_profile.t_w),
            right_edge=1000,
        )
        self.slab = self.concrete_top_cover + self.concrete_left + self.concrete_right
        self.concrete = Concrete(
            f_cm=30 + 8,
        )
        self.concrete_slab = self.slab + self.concrete
        self.reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
        self.top_layer = RebarLayer(
            centroid_z=0.5 * 50,
            width=2000,
            rebar_horizontal_distance=200,
            rebar_diameter=10,
        )
        self.top_rebar_layer = reinforcement + top_layer
        self.bottom_layer_left = RebarLayer(
            centroid_z=self.t_profile.top_edge + self.t_profile.h_w - 25,
            width=0.5 * (2000 - self.t_profile.t_w),
            right_edge=-0.5 * self.t_profile.t_w,
            rebar_horizontal_distance=200,
            rebar_diameter=10,
        )
        self.bottom_layer_right = RebarLayer(
            centroid_z=self.t_profile.top_edge + self.t_profile.h_w - 25,
            width=0.5 * (2000 - self.t_profile.t_w),
            left_edge=0.5 * self.t_profile.t_w,
            rebar_horizontal_distance=200,
            rebar_diameter=10,
        )
        self.rebar_layer = (
            self.top_layer + self.bottom_layer_left + self.bottom_layer_right
        )
        self.rebar = self.rebar_layer + self.reinforcement
        self.cross_section = self.steel_profile + self.concrete_slab + self.rebar

    def test_positive_m_kappa_points_moments(self):
        m_kappa = MKappaCurve(self.cross_section, include_positive_curvature=True)
        self.assertCountEqual(
            m_kappa.m_kappa_points.moments,
            [
                0.0,
                71211445.03228515,
                71374571.33219278,
                205968550.09273192,
                285400028.1651079,
                299068407.68595254,
                316019720.53199005,
                344682943.7980188,
                344715262.62252504,
                347915715.8045602,
                353497818.111975,
                356951836.7731828,
                356669646.6707282,
            ],
        )

    def test_negative_m_kappa_points_moments(self):
        m_kappa = MKappaCurve(
            self.cross_section,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )
        self.assertCountEqual(
            m_kappa.m_kappa_points.moments,
            [
                -266658328.88693628,
                -264608705.54766303,
                -261745840.47151956,
                -259654595.5370506,
                -259444537.56853175,
                -257605598.7625466,
                -210575974.4809118,
                -196199248.54844183,
                -151260748.11754704,
                -145421046.21804398,
                -115656324.44475287,
                -45136432.612406135,
                -45546900.487594225,
                -65836509.07521711,
                -65807365.76743883,
                0.0,
            ],
        )


if __name__ == "__main__":
    main()
