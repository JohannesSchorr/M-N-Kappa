from m_n_kappa import (
    Concrete,
    Steel,
    Reinforcement,
    Rectangle,
    IProfile,
    RebarLayer,
    Crosssection,
    StrainPosition,
    MKappaByStrainPosition,
    MKappaByConstantCurvature,
)

from unittest import TestCase, main

# Concrete section
f_cm = 30
concrete_top_edge = 0.0
concrete_bottom_edge = 10.0
concrete_width = 10.0
concrete = Concrete(f_cm=f_cm)
concrete_rectangle = Rectangle(
    top_edge=concrete_top_edge, bottom_edge=concrete_bottom_edge, width=concrete_width
)
concrete_section = concrete + concrete_rectangle

# Steel section
f_y = 355.0
f_u = 360.0
epsilon_u = 0.2
steel_top_edge = 0.0
steel_bottom_edge = 10.0
steel_width = 10.0
steel = Steel(f_y=f_y, f_u=f_u, failure_strain=epsilon_u)
steel_rectangle = Rectangle(
    top_edge=steel_top_edge, bottom_edge=steel_bottom_edge, width=steel_width
)
steel_section = steel + steel_rectangle

# Crosssection
cs = concrete_section + steel_section

# Values
strain_position = StrainPosition(
    strain=-0.00039, position=concrete_top_edge, material="Concrete"
)

# Boundary Conditions
bc = cs.get_boundary_conditions()
max_curvature = bc.positive.maximum_curvature.compute(strain_position)
min_curvature = bc.positive.minimum_curvature.compute(strain_position)


class TestMKappaByStrainPosition(TestCase):
    def setUp(self):
        self.cs = Crosssection([steel_section])
        self.bc = self.cs.get_boundary_conditions()
        self.strain = -f_y / steel.E_a
        self.strain_position = StrainPosition(
            strain=self.strain, position=steel_top_edge, material="Steel"
        )
        self.m_kappa = MKappaByStrainPosition(
            cross_section=self.cs,
            strain_position=self.strain_position,
            maximum_curvature=self.bc.positive.maximum_curvature.compute(
                strain_position
            ),
            minimum_curvature=self.bc.positive.minimum_curvature.compute(
                strain_position
            ),
        )

    def test_steel_section(self):
        self.assertEqual(self.cs.sections[0], steel_section)

    def test_cs_top_edge(self):
        self.assertEqual(self.cs.top_edge, steel_top_edge)

    def test_cs_bottom_edge(self):
        self.assertEqual(self.cs.bottom_edge, steel_bottom_edge)

    def test_maximum_curvature(self):
        curvature = (self.strain - steel.failure_strain) / (
            steel_top_edge - steel_bottom_edge
        )
        self.assertAlmostEqual(self.m_kappa.maximum_curvature, curvature, places=3)

    def test_minimum_curvature(self):
        self.assertAlmostEqual(self.m_kappa.minimum_curvature, 0.0, places=4)

    def test_strain_position(self):
        self.assertEqual(self.m_kappa.strain_position, self.strain_position)

    def test_neutral_axis(self):
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            0.5 * (steel_top_edge + steel_bottom_edge),
            places=2,
        )

    def test_curvature(self):
        curvature = (self.strain - steel.epsilon_y) / (
            steel_top_edge - steel_bottom_edge
        )
        self.assertAlmostEqual(self.m_kappa.curvature, curvature, places=5)

    def test_axial_force(self):
        self.assertAlmostEqual(self.m_kappa.axial_force, 3.7680649693647865, places=0)

    def test_successful(self):
        self.assertEqual(self.m_kappa.successful, True)

    def test_iterations(self):
        self.assertLessEqual(self.m_kappa.iteration, 10)


class TestMKappaByStrainPositionAbortBecauseOfInputStrainPosition(TestCase):
    def setUp(self) -> None:
        self.cs = Crosssection([steel_section])

    def test_positive_curvature_not_successful(self):
        m_kappa = MKappaByStrainPosition(
            self.cs,
            strain_position=StrainPosition(
                self.cs.decisive_maximum_positive_strain_position().strain, 100, "Steel"
            ),
            positive_curvature=True,
        )
        self.assertEqual(m_kappa.successful, False)

    def test_positive_curvature_successful(self):
        m_kappa = MKappaByStrainPosition(
            self.cs,
            strain_position=StrainPosition(
                self.cs.decisive_maximum_negative_strain_position().strain, steel_top_edge, "Steel"
            ),
            positive_curvature=True,
        )
        self.assertEqual(m_kappa.successful, True)


class TestMKappabyStrainPositionCompositeBeam(TestCase):
    def setUp(self) -> None:
        concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
        concrete = Concrete(
            f_cm=30 + 8,
        )
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
            top_edge=0.0, b_fo=200, t_fo=15, h_w=200 - 2 * 15, t_w=15, centroid_y=0.0
        )
        steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
        steel_section = i_profile + steel
        self.cross_section = (
            concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section
        )


class TestMKappaByConstantCurvature(TestCase):
    def setUp(self):
        self.geometry = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.steel = Steel(f_y=355, failure_strain=0.15)
        self.section = self.geometry + self.steel
        self.cross_section = Crosssection(sections=[self.section])
        self.curvature_1 = 0.001
        self.applied_force_1 = 100
        self.applied_force_2 = 355 * 100

    def test_positive_curvature_positive_force(self):
        self.m_kappa = MKappaByConstantCurvature(
            cross_section=self.cross_section,
            applied_curvature=self.curvature_1,
            applied_axial_force=self.applied_force_1,
        )
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            5.0
            - ((self.applied_force_1 / self.geometry.area) / 210000) / self.curvature_1,
            1,
        )

    def test_negative_curvature_positive_force(self):
        self.m_kappa = MKappaByConstantCurvature(
            cross_section=self.cross_section,
            applied_curvature=-self.curvature_1,
            applied_axial_force=self.applied_force_1,
        )
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            5.0
            + ((self.applied_force_1 / self.geometry.area) / 2100000)
            / self.curvature_1,
            1,
        )

    def test_positive_curvature_negative_force(self):
        self.m_kappa = MKappaByConstantCurvature(
            cross_section=self.cross_section,
            applied_curvature=self.curvature_1,
            applied_axial_force=-self.applied_force_1,
        )
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            5.0
            + ((self.applied_force_1 / self.geometry.area) / 2100000)
            / self.curvature_1,
            1,
        )

    def test_negative_curvature_negative_force(self):
        self.m_kappa = MKappaByConstantCurvature(
            cross_section=self.cross_section,
            applied_curvature=-self.curvature_1,
            applied_axial_force=-self.applied_force_1,
        )
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            5.0
            - ((self.applied_force_1 / self.geometry.area) / 2100000)
            / self.curvature_1,
            1,
        )

    def test_negative_curvature_negative_force_plastic(self):
        self.m_kappa = MKappaByConstantCurvature(
            cross_section=self.cross_section,
            applied_curvature=-self.curvature_1,
            applied_axial_force=-self.applied_force_2,
        )
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            10.0 - (self.steel.failure_strain / self.curvature_1),
            1,
        )

    def test_negative_curvature_negative_force_neutral_axis_outside_scope(self):
        self.m_kappa = MKappaByConstantCurvature(
            cross_section=self.cross_section,
            applied_curvature=-self.curvature_1,
            applied_axial_force=-self.applied_force_2 - 10,
        )
        self.assertAlmostEqual(self.m_kappa.successful, False)


if __name__ == "__main__":
    main()
