from m_n_kappa.material import Concrete, Steel
from m_n_kappa.geometry import Rectangle
from m_n_kappa.points import MKappaByStrainPosition

from unittest import TestCase, main

# Concrete section
concrete = Concrete(f_cm=30)
concrete_rectangle = Rectangle(top_edge=0.0, bottom_edge=20, width=10)
concrete_section = concrete + concrete_rectangle

# Steel section
steel = Steel(f_y=355, epsilon_u=0.2)
steel_rectangle = Rectangle(top_edge=20, bottom_edge=30, width=10)
steel_section = steel + steel_rectangle

# Crosssection
cs = concrete_section + steel_section

# Values
position = 20.0
strain = -0.00169

# Boundary Conditions
bc = cs.get_boundary_conditions()
max_curvature = bc.negative.maximum_curvature.curvature
min_curvature = bc.negative.minimum_curvature.compute(strain, position)


class TestMKappaByStrainPosition(TestCase):
    def setUp(self):
        self.m_kappa = MKappaByStrainPosition(
            cross_section=cs,
            strain_position=position,
            strain_at_position=strain,
            maximum_curvature=max_curvature,
            minimum_curvature=min_curvature,
        )

    def test_crosssection(self):
        self.assertEqual(self.m_kappa.cross_section, cs)


if __name__ == "__main__":
    main()
