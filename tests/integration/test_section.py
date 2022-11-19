from m_n_kappa.section import (
    Section,
    ComputationSectionStrain,
    ComputationSectionCurvature,
    StrainPosition,
)
from m_n_kappa.geometry import Rectangle
from m_n_kappa.material import Steel

from unittest import TestCase, main

rectangle = Rectangle(0.0, 10.0, 10.0)
steel = Steel(355.0)
my_section = rectangle + steel


class TestCombineMaterialGeometry(TestCase):
    def setUp(self):
        self.my_section_1 = rectangle + steel
        self.my_section_2 = Section(geometry=rectangle, material=steel)

    def test_combine_material_and_geometry_type(self):
        self.assertEqual(type(self.my_section_1), Section)

    def test_combine_material_and_geometry(self):
        self.assertEqual(self.my_section_1, self.my_section_2)

    def test_section_type(self):
        self.assertEqual(self.my_section_1.section_type, "girder")

    def test_material(self):
        self.assertEqual(self.my_section_1.material, steel)

    def test_geometry(self):
        self.assertEqual(self.my_section_1.geometry, rectangle)


class TestComputationSectionStrain(TestCase):
    def setUp(self):
        self.strain = 0.001
        self.computation_section = ComputationSectionStrain(my_section, self.strain)
        self.stress = self.strain * steel.E_a

    def test_strain(self):
        self.assertEqual(self.computation_section.strain, self.strain)

    def test_edge_strains(self):
        self.assertEqual(
            self.computation_section.edges_strain, [self.strain, self.strain]
        )

    def test_edges_stresses(self):
        self.assertEqual(
            self.computation_section.edges_stress, [self.stress, self.stress]
        )

    def test_axial_force(self):
        self.assertEqual(
            self.computation_section.axial_force, self.stress * rectangle.area
        )

    def test_centroid(self):
        self.assertEqual(
            self.computation_section.lever_arm(),
            0.5 * (rectangle.top_edge + rectangle.bottom_edge),
        )

    def test_moment(self):
        self.assertEqual(
            self.computation_section.moment(),
            0.5
            * (rectangle.top_edge + rectangle.bottom_edge)
            * self.stress
            * rectangle.area,
        )

    def test_material(self):
        self.assertEqual(self.computation_section.material, steel)

    def test_geometry(self):
        self.assertEqual(self.computation_section.geometry, rectangle)


class TestComputationSectionCurvature(TestCase):
    def setUp(self): 
        self.curvature = 0.00001
        self.neutral_axis = my_section.geometry.bottom_edge
        self.computation_section = ComputationSectionCurvature(
            my_section, curvature=self.curvature, neutral_axis=self.neutral_axis
        )
        self.lever_arm = my_section.geometry.top_edge + 1.0 / 3.0 * (
            my_section.geometry.bottom_edge - my_section.geometry.top_edge
        )
        self.axial_force = (
            (-1)
            * rectangle.area
            * self.curvature
            * (rectangle.bottom_edge - rectangle.top_edge)
            * steel.E_a
            * 0.5
        )

    def test_material(self):
        self.assertEqual(self.computation_section.material, steel)

    def test_geometry(self):
        self.assertEqual(self.computation_section.geometry, rectangle)

    def test_curvature(self):
        self.assertEqual(self.computation_section.curvature, self.curvature)

    def test_neutral_axis(self):
        self.assertEqual(self.computation_section.neutral_axis, self.neutral_axis)

    def test_edges_strain(self):
        top_strain = self.curvature * (
            my_section.geometry.top_edge - my_section.geometry.bottom_edge
        )
        self.assertEqual(self.computation_section.edges_strain, [top_strain, 0.0])

    def test_edges_stress(self):
        stresses = [
            strain * steel.E_a for strain in self.computation_section.edges_strain
        ]
        self.assertListEqual(self.computation_section.edges_stress, stresses)

    def test_lever_arm(self):
        self.assertAlmostEqual(self.computation_section.lever_arm(), self.lever_arm)

    def test_axial_force(self):
        self.assertEqual(self.computation_section.axial_force, self.axial_force)

    def test_moment(self):
        self.assertAlmostEqual(
            self.computation_section.moment(), self.axial_force * self.lever_arm
        )


class TestMaterialPointsInsideCurvature(TestCase):

    def setUp(self):
        self.geometry = Rectangle(0, 10, 10)
        self.material = Steel(355, 400, 0.15)
        self.section = self.geometry + self.material
        self.computed_section = ComputationSectionCurvature(self.section, 0.001, 10)
    def test_material_points_inside_curvature(self):
        self.assertListEqual(
            self.computed_section.material_points_inside_curvature(),
            [StrainPosition(strain=-0.0016904761904761904, position=0, material='Steel')]
        )


if __name__ == "__main__":
    main()