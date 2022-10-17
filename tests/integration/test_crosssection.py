from m_n_kappa.crosssection import (
    Crosssection,
    ComputationCrosssectionCurvature,
    ComputationCrosssectionStrain,
)
from m_n_kappa.material import Concrete, Steel
from m_n_kappa.geometry import Rectangle

from unittest import TestCase, main

# Concrete section
concrete = Concrete(f_cm=30)
concrete_rectangle = Rectangle(top_edge=0.0, bottom_edge=20, width=10)
concrete_section = concrete + concrete_rectangle

# Steel section
steel = Steel(f_y=355, epsilon_u=0.2)
steel_rectangle = Rectangle(top_edge=20, bottom_edge=30, width=10)
steel_section = steel + steel_rectangle

sections = [concrete_section, steel_section]


class TestCrosssection(TestCase):
    def setUp(self):
        self.cs = Crosssection([concrete_section, steel_section])

    def test_sections(self):
        self.assertListEqual(self.cs.sections, [concrete_section, steel_section])

    def test_top_edge(self):
        self.assertEqual(self.cs.top_edge, 0.0)

    def test_bottom_edge(self):
        self.assertEqual(self.cs.bottom_edge, 30)

    def test_girder_sections(self):
        self.assertListEqual(self.cs.girder_sections, [steel_section])

    def test_slab_sections(self):
        self.assertListEqual(self.cs.slab_sections, [concrete_section])

    def test_height(self):
        self.assertEqual(self.cs.height, 30)

    def test_half_points(self):
        self.assertEqual(self.cs.half_point, 0.5 * 30)

    def test_section_type(self):
        self.assertEqual(self.cs.section_type, None)

    def test_sections_of_type(self):
        self.assertEqual(self.cs.sections_of_type("slab"), [concrete_section])
        self.assertEqual(self.cs.sections_of_type("girder"), [steel_section])

    def test_sections_not_of_type(self):
        self.assertEqual(self.cs.sections_not_of_type("girder"), [concrete_section])
        self.assertEqual(self.cs.sections_not_of_type("slab"), [steel_section])

    def test_maximum_positive_strain(self):
        self.assertEqual(self.cs.maximum_positive_strain(), concrete.maximum_strain)

    def test_maximum_negative_strain(self):
        self.assertEqual(self.cs.maximum_negative_strain(), steel.minimum_strain)


class TestComputationCrosssectionStrain1(TestCase):
    def setUp(self):
        self.strain = 0.1
        self.cs = ComputationCrosssectionStrain(sections, self.strain)

    def test_strain(self):
        self.assertEqual(self.cs.strain, self.strain)

    def test_total_axial_force(self):
        self.assertGreater(self.cs.total_axial_force(), 0.0)

    def test_slab_axial_force(self):
        self.assertGreater(self.cs.girder_sections_axial_force(), 0.0)
        self.assertGreaterEqual(self.cs.slab_sections_axial_force(), 0.0)

    def test_total_moment(self):
        self.assertGreater(self.cs.total_moment(), 0.0)

    def test_slab_moment(self):
        self.assertGreater(self.cs.girder_sections_moment(), 0.0)
        self.assertGreaterEqual(self.cs.slab_sections_moment(), 0.0)


class TestComputationCrosssectionStrain2(TestCase):
    def setUp(self):
        self.strain = -0.001
        self.cs = ComputationCrosssectionStrain(sections, self.strain)

    def test_strain(self):
        self.assertEqual(self.cs.strain, self.strain)

    def test_total_axial_force(self):
        self.assertLess(self.cs.total_axial_force(), 0.0)

    def test_slab_axial_force(self):
        self.assertLess(self.cs.girder_sections_axial_force(), 0.0)
        self.assertLessEqual(self.cs.slab_sections_axial_force(), 0.0)

    def test_total_moment(self):
        self.assertLess(self.cs.total_moment(), 0.0)

    def test_slab_moment(self):
        self.assertLess(self.cs.girder_sections_moment(), 0.0)
        self.assertLessEqual(self.cs.slab_sections_moment(), 0.0)


class TestComputationCrosssectionCurvature(TestCase):
    def setUp(self):
        self.curvature = 0.0001
        self.neutral_axis = 20.0
        self.cs = ComputationCrosssectionCurvature(
            sections, self.curvature, self.neutral_axis
        )

    def test_curvature(self):
        self.assertEqual(self.cs.curvature, self.curvature)

    def test_neutral_axis(self):
        self.assertEqual(self.cs.neutral_axis, self.neutral_axis)

    def test_compute_split_sections(self):
        self.assertEqual(type(self.cs.compute_sections), list)


if __name__ == "__main__":
    main()
