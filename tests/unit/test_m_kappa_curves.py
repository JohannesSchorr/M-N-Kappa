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
                        strain=-0.0016905, position=100.0, material="Steel"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0016905, position=115.0, material="Steel"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0016905, position=285.0, material="Steel"
                    ),
                ),
            ],
        )

    def test_m_kappa_points_moments(self):
        self.assertCountEqual(
            self.m_kappa_curve.m_kappa_points.moments,
            [
                0.0,
                279064106.6935997,
                438757586.99726015,
                516819111.03838825,
                538682845.0830967,
                541724583.2808295,
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
                        strain=-0.0016905, position=115.0, material="Steel"
                    ),
                )
            ],
        )

    def test_m_kappa_points_moments(self):
        self.maxDiff = None
        self.assertCountEqual(
            self.m_kappa_curve.m_kappa_points.moments,
            [
                -442383659.8050097,
                -409298629.82524645,
                -405044578.8388414,
                -349978336.3245533,
                -319575350.2268986,
                -296104456.0631782,
                -54941561.964923926,
                -54716034.825507574,
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
        self.maxDiff = None
        m_kappa = MKappaCurve(self.cross_section, include_positive_curvature=True)
        self.assertCountEqual(
            m_kappa.m_kappa_points.moments,
            [
                0.0,
                71208518.13882212,
                71371648.46965477,
                205967692.23350403,
                285399850.8339556,
                299068176.37613595,
                316020154.4669411,
                344682554.3843546,
                344714873.888593,
                347915919.3132613,
                353497685.24627197,
                356951572.7599163,
                356669438.3570308,
            ],
        )

    def test_negative_m_kappa_points_moments(self):
        self.maxDiff = None
        m_kappa = MKappaCurve(
            self.cross_section,
            include_positive_curvature=False,
            include_negative_curvature=True,
        )
        self.assertCountEqual(
            m_kappa.m_kappa_points.moments,
            [
                -266658230.39614558,
                -264608480.209751,
                -261745867.3986844,
                -259654749.07364026,
                -259444570.4178928,
                -257606797.99770764,
                -210578142.29300994,
                -196199553.2497602,
                -151260403.34364986,
                -145420317.98855132,
                -115657247.50515783,
                -45134906.50600005,
                -45545393.81453258,
                -65834585.267866716,
                -65805433.37520586,
                0.0,
            ],
        )


if __name__ == "__main__":
    main()
