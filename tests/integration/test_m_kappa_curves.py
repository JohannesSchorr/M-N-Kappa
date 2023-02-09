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

same_sign = "difference of axial forces at minimum and maximum curvature have same sign"
max_iterations = "maximum iterations reached"

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
        self.assertListEqual(
            self.m_kappa_curve.not_successful,
            [
                [
                    StrainPosition(strain=-0.0035, position=0.0, material="Concrete"),
                    max_iterations,
                ],
                [
                    StrainPosition(
                        strain=-0.0025, position=25, material="Reinforcement"
                    ),
                    same_sign,
                ],
                [
                    StrainPosition(
                        strain=-0.0025, position=75, material="Reinforcement"
                    ),
                    same_sign,
                ],
                [
                    StrainPosition(
                        strain=-0.0016904761904761904, position=100.0, material="Steel"
                    ),
                    same_sign,
                ],
            ],
        )

    def test_m_kappa_points_moments(self):
        self.assertListEqual(
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
        self.assertListEqual(
            self.m_kappa_curve.not_successful,
            [
                [
                    StrainPosition(
                        strain=-0.0016904761904761904, position=115.0, material="Steel"
                    ),
                    same_sign,
                ]
            ],
        )

    def test_m_kappa_points_moments(self):
        self.assertListEqual(
            self.m_kappa_curve.m_kappa_points.moments,
            [
                -442383661.16446424,
                -409298265.3218652,
                -405044752.007268,
                -349978085.7744969,
                -54944467.314156845,
                -54718951.26913915,
                0.0,
            ],
        )


if __name__ == "__main__":
    main()
