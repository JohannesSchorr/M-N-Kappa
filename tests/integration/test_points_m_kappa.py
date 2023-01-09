from m_n_kappa.material import Concrete, Steel
from m_n_kappa.geometry import Rectangle
from m_n_kappa.points import MKappaByStrainPosition
from m_n_kappa.crosssection import Crosssection
from m_n_kappa.general import StrainPosition

from unittest import TestCase, main

# Concrete section
f_cm = 30
concrete_top_edge = 0.0
concrete_bottom_edge = 10.0
concrete_width = 10.0
concrete = Concrete(f_cm=f_cm)
concrete_rectangle = Rectangle(top_edge=concrete_top_edge, bottom_edge=concrete_bottom_edge, width=concrete_width)
concrete_section = concrete + concrete_rectangle

# Steel section
f_y = 355.0
f_u = 360.0
epsilon_u = 0.2
steel_top_edge = 0.0
steel_bottom_edge = 10.0
steel_width = 10.0
steel = Steel(f_y=f_y, f_u=f_u, failure_strain=epsilon_u)
steel_rectangle = Rectangle(top_edge=steel_top_edge, bottom_edge=steel_bottom_edge, width=steel_width)
steel_section = steel + steel_rectangle

# Crosssection
cs = concrete_section + steel_section

# Values
strain_position = StrainPosition(strain=-0.00039, position=concrete_top_edge, material='Concrete')

# Boundary Conditions
bc = cs.get_boundary_conditions()
max_curvature = bc.positive.maximum_curvature.compute(strain_position)
min_curvature = bc.positive.minimum_curvature.compute(strain_position)


class TestMKappaByStrainPosition(TestCase):
    def setUp(self):
        self.cs = Crosssection([steel_section])
        self.bc = self.cs.get_boundary_conditions()
        self.strain = -f_y / steel.E_a
        self.strain_position = StrainPosition(strain=self.strain, position=steel_top_edge, material='Steel')
        self.m_kappa = MKappaByStrainPosition(
            cross_section=self.cs,
            strain_position=self.strain_position,
            maximum_curvature=self.bc.positive.maximum_curvature.compute(strain_position),
            minimum_curvature=self.bc.positive.minimum_curvature.compute(strain_position),
        )

    def test_steel_section(self):
        self.assertEqual(self.cs.sections[0], steel_section)

    def test_cs_top_edge(self):
        self.assertEqual(self.cs.top_edge, steel_top_edge)

    def test_cs_bottom_edge(self):
        self.assertEqual(self.cs.bottom_edge, steel_bottom_edge)

    def test_maximum_curvature(self):
        curvature = (self.strain - steel.failure_strain) / (steel_top_edge - steel_bottom_edge)
        self.assertAlmostEqual(self.m_kappa.maximum_curvature, curvature, places=3)

    def test_minimum_curvature(self):
        self.assertAlmostEqual(self.m_kappa.minimum_curvature, 0.0, places=4)

    def test_strain_position(self):
        self.assertEqual(self.m_kappa.strain_position, self.strain_position)

    def test_neutral_axis(self):
        self.assertAlmostEqual(
            self.m_kappa.neutral_axis,
            0.5 * (steel_top_edge + steel_bottom_edge), places=3
        )

    def test_curvature(self):
        curvature = (self.strain - steel.epsilon_y) / (steel_top_edge - steel_bottom_edge)
        self.assertAlmostEqual(self.m_kappa.curvature, curvature, places=5)

    def test_axial_force(self):
        self.assertAlmostEqual(self.m_kappa.axial_force, 0.0, places=0)

    def test_successful(self):
        self.assertEqual(self.m_kappa.successful, True)

    def test_iterations(self):
        self.assertLessEqual(self.m_kappa.iteration, 10)


if __name__ == "__main__":
    main()