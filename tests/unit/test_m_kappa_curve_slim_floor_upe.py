from unittest import TestCase, main

from m_n_kappa import (
    MKappaCurve,
    StrainPosition,
    EffectiveWidths,
    Crosssection,
    Rectangle,
    Steel,
    UPEProfile,
    Concrete,
    RebarLayer,
    Reinforcement,
)
from m_n_kappa.general import NotSuccessfulReason

same_sign = NotSuccessfulReason(variable="curvature").reason
max_iterations = NotSuccessfulReason("iteration").reason

plate_geometry = Rectangle(top_edge=220.0, bottom_edge=220.0 + 10.0, width=400.0)
bottom_flange_material = Steel(f_y=313, f_u=460, failure_strain=0.15)
bottom_flange = plate_geometry + bottom_flange_material
upe200_geometry = UPEProfile(top_edge=144, t_f=5.2, b_f=76, t_w=9.0, h=200)
upe200_material = Steel(f_y=293, f_u=443, failure_strain=0.15)
upe200 = upe200_geometry + upe200_material
concrete_left = Rectangle(
    top_edge=0.00,
    bottom_edge=220.00,
    width=1650.00,
    left_edge=-1750.00,
    right_edge=-100.00,
)
concrete_middle = Rectangle(
    top_edge=0.00,
    bottom_edge=144.00,
    width=200.00,
    left_edge=-100.00,
    right_edge=100.00,
)
concrete_right = Rectangle(
    top_edge=0.00,
    bottom_edge=220.00,
    width=1650.00,
    left_edge=100.00,
    right_edge=1750.00,
)
concrete_geometry = concrete_left + concrete_middle + concrete_right
concrete_material = Concrete(
    f_cm=29.5,
    f_ctm=2.8,
    compression_stress_strain_type="Nonlinear",
    tension_stress_strain_type="consider opening behaviour",
)
concrete_slab = concrete_geometry + concrete_material
rebar_top_layer_geometry = RebarLayer(
    rebar_diameter=12.0, centroid_z=10.0, width=3500, rebar_horizontal_distance=100.0
)
rebar_bottom_layer_left_geometry = RebarLayer(
    rebar_diameter=10.0,
    centroid_z=220 - 10,
    width=1650.0,
    rebar_horizontal_distance=100.0,
    left_edge=-1740.0,
)
rebar_bottom_layer_right_geometry = RebarLayer(
    rebar_diameter=10.0,
    centroid_z=220 - 10,
    width=1650.0,
    rebar_horizontal_distance=100.0,
    right_edge=1740.0,
)
rebar10_material = Reinforcement(f_s=594, f_su=685, failure_strain=0.25, E_s=200000)
rebar12_material = Reinforcement(f_s=558, f_su=643, failure_strain=0.25, E_s=200000)
rebar_top_layer = rebar_top_layer_geometry + rebar12_material
rebar_bottom_layer_left = rebar_bottom_layer_left_geometry + rebar10_material
rebar_bottom_layer_right = rebar_bottom_layer_right_geometry + rebar10_material
rebar_layer = rebar_top_layer + rebar_bottom_layer_left + rebar_bottom_layer_right
cross_section = bottom_flange + upe200 + concrete_slab + rebar_layer


class TestSlimFloorUPEPositive(TestCase):
    def setUp(self) -> None:
        self.m_kappa_curve = MKappaCurve(cross_section)

    def test_not_successful(self):
        self.maxDiff = None
        self.assertCountEqual(
            self.m_kappa_curve.not_successful_reason,
            [
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.00279, position=10.0, material="Reinforcement"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0013952380952380952, position=144, material="Steel"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.0014904761904761905, position=220.0, material="Steel"
                    ),
                ),
                NotSuccessfulReason(
                    variable="curvature",
                    strain_position=StrainPosition(
                        strain=-0.00297, position=210, material="Reinforcement"
                    ),
                ),
                NotSuccessfulReason(
                    keyword="iteration",
                    strain_position=StrainPosition(
                        strain=-0.0035, position=0.0, material="Concrete"
                    ),
                ),
            ],
        )


class TestSlimFloorUPEPositiveWithEffectiveWidth(TestCase):
    def setUp(self) -> None:
        self.cross_section = Crosssection(
            cross_section.sections, EffectiveWidths(membran=473.7, bending=1364.8)
        )
        self.m_kappa_curve = MKappaCurve(
            self.cross_section,
        )

    def test_not_successful(self):
        self.maxDiff = None
        self.assertCountEqual(
            self.m_kappa_curve.not_successful_reason,
            [
                NotSuccessfulReason(
                    keyword="converge",
                    strain_position=StrainPosition(
                        strain=-0.0007875097747723546, position=0.0, material="Concrete"
                    ),
                )
            ]
            * 3,
        )


class TestSlimFloorUPENegative(TestCase):

    pass


if __name__ == "__main__":
    main()
