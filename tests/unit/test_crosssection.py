from m_n_kappa.crosssection import (
    Crosssection,
    ComputationCrosssectionCurvature,
    ComputationCrosssectionStrain,
)
from m_n_kappa.material import Concrete, Steel
from m_n_kappa.geometry import Rectangle
from m_n_kappa.general import EffectiveWidths, StrainPosition

from unittest import TestCase, main

# Concrete section
f_cm = 30
concrete_top_edge = 0.0
concrete_bottom_edge = 20.0
concrete_width = 10.0
concrete = Concrete(f_cm=f_cm)
concrete_rectangle = Rectangle(
    top_edge=concrete_top_edge, bottom_edge=concrete_bottom_edge, width=concrete_width
)
concrete_section = concrete + concrete_rectangle

# Steel section
f_y = 355
epsilon_u = 0.2
steel_top_edge = 20.0
steel_bottom_edge = 30.0
steel_width = 10.0
steel = Steel(f_y=f_y, failure_strain=epsilon_u)
steel_rectangle = Rectangle(
    top_edge=steel_top_edge, bottom_edge=steel_bottom_edge, width=steel_width
)
steel_section = steel + steel_rectangle

sections = [concrete_section, steel_section]


class TestCrosssection(TestCase):
    def setUp(self):
        self.cs = Crosssection(sections)

    def test_sections(self):
        self.assertListEqual(self.cs.sections, sections)

    def test_top_edge(self):
        self.assertEqual(self.cs.top_edge, concrete_top_edge)

    def test_bottom_edge(self):
        self.assertEqual(self.cs.bottom_edge, steel_bottom_edge)

    def test_girder_sections(self):
        self.assertListEqual(self.cs.girder_sections, [steel_section])

    def test_slab_sections(self):
        self.assertListEqual(self.cs.slab_sections, [concrete_section])

    def test_height(self):
        self.assertEqual(self.cs.height, steel_bottom_edge - concrete_top_edge)

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

    def test_left_edge(self):
        self.assertEqual(self.cs.left_edge(), -0.5 * concrete_width)

    def test_right_edge(self):
        self.assertEqual(self.cs.right_edge(), 0.5 * concrete_width)

    def test_concrete_slab_width(self):
        self.assertEqual(self.cs.concrete_slab_width(), concrete_width)


class TestCrossSectionStrainPositions(TestCase):

    def setUp(self) -> None:
        self.cross_section = Crosssection([steel_section])

    def test_strain_positions(self):
        self.assertCountEqual(
            self.cross_section.strain_positions(),
            [
                StrainPosition(strain=-epsilon_u, position=steel_top_edge, material='Steel'),
                StrainPosition(strain=-steel.epsilon_y, position=steel_top_edge, material='Steel'),
                StrainPosition(strain=steel.epsilon_y, position=steel_top_edge, material='Steel'),
                StrainPosition(strain=epsilon_u, position=steel_top_edge, material='Steel'),
                StrainPosition(strain=-epsilon_u, position=steel_bottom_edge, material='Steel'),
                StrainPosition(strain=-steel.epsilon_y, position=steel_bottom_edge, material='Steel'),
                StrainPosition(strain=steel.epsilon_y, position=steel_bottom_edge, material='Steel'),
                StrainPosition(strain=epsilon_u, position=steel_bottom_edge, material='Steel'),
            ]
        )


class TestComputationCrosssectionStrainPositive(TestCase):
    def setUp(self):
        self.strain = 0.1
        self.concrete_stress = concrete.get_material_stress(self.strain)
        self.concrete_force = concrete_rectangle.area * self.concrete_stress
        self.concrete_lever_arm = concrete_rectangle.centroid
        self.concrete_moment = self.concrete_force * self.concrete_lever_arm

        self.steel_stress = steel.get_material_stress(self.strain)
        self.steel_force = steel_rectangle.area * self.steel_stress
        self.steel_lever_arm = steel_rectangle.centroid
        self.steel_moment = self.steel_force * self.steel_lever_arm

        self.cs = ComputationCrosssectionStrain(sections, self.strain)

    def test_strain(self):
        self.assertEqual(self.cs.strain, self.strain)

    def test_total_axial_force(self):
        self.assertEqual(
            self.cs.total_axial_force(), self.concrete_force + self.steel_force
        )

    def test_slab_axial_force(self):
        self.assertEqual(self.cs.slab_sections_axial_force(), self.concrete_force)

    def test_girder_axial_force(self):
        self.assertEqual(self.cs.girder_sections_axial_force(), self.steel_force)

    def test_total_moment(self):
        self.assertEqual(
            self.cs.total_moment(), self.steel_moment + self.concrete_moment
        )

    def test_girder_moment(self):
        self.assertEqual(self.cs.girder_sections_moment(), self.steel_moment)

    def test_slab_moment(self):
        self.assertEqual(self.cs.slab_sections_moment(), self.concrete_moment)

    def test_slab_section(self):
        self.assertEqual(self.cs.slab_sections, [concrete_section])

    def test_girder_section(self):
        self.assertEqual(self.cs.girder_sections, [steel_section])


class TestComputationCrosssectionStrainNegative(TestCase):
    def setUp(self):
        self.strain = -0.001
        self.concrete_stress = concrete.get_material_stress(self.strain)
        self.concrete_force = concrete_rectangle.area * self.concrete_stress
        self.concrete_lever_arm = concrete_rectangle.centroid
        self.concrete_moment = self.concrete_force * self.concrete_lever_arm

        self.steel_stress = steel.get_material_stress(self.strain)
        self.steel_force = steel_rectangle.area * self.steel_stress
        self.steel_lever_arm = steel_rectangle.centroid
        self.steel_moment = self.steel_force * self.steel_lever_arm

        self.cs = ComputationCrosssectionStrain(sections, self.strain)

    def test_strain(self):
        self.assertEqual(self.cs.strain, self.strain)

    def test_total_axial_force(self):
        self.assertAlmostEqual(
            self.cs.total_axial_force(), self.concrete_force + self.steel_force
        )

    def test_slab_axial_force(self):
        self.assertAlmostEqual(self.cs.slab_sections_axial_force(), self.concrete_force)

    def test_girder_axial_force(self):
        self.assertAlmostEqual(self.cs.girder_sections_axial_force(), self.steel_force)

    def test_total_moment(self):
        self.assertEqual(
            self.cs.total_moment(), self.steel_moment + self.concrete_moment
        )

    def test_girder_moment(self):
        self.assertEqual(self.cs.girder_sections_moment(), self.steel_moment)

    def test_slab_moment(self):
        self.assertAlmostEqual(self.cs.slab_sections_moment(), self.concrete_moment)


class TestComputationCrosssectionCurvature(TestCase):
    def setUp(self):
        self.curvature = 0.00001
        self.neutral_axis = concrete_bottom_edge

        self.concrete_top_strain = -self.curvature * self.neutral_axis
        self.concrete_top_stress = concrete.get_material_stress(
            self.concrete_top_strain
        )
        self.concrete_bottom_strain = 0.0
        self.concrete_bottom_stress = concrete.get_material_stress(
            self.concrete_bottom_strain
        )
        self.concrete_stress = 0.5 * (
            self.concrete_top_stress + self.concrete_bottom_stress
        )
        self.concrete_force = self.concrete_stress * concrete_rectangle.area
        self.concrete_lever_arm = (
            1.0 / 3.0 * (concrete_rectangle.bottom_edge - concrete_rectangle.top_edge)
        )
        self.concrete_moment = self.concrete_lever_arm * self.concrete_force

        self.steel_top_strain = 0.0
        self.steel_top_stress = steel.get_material_stress(self.steel_top_strain)
        self.steel_bottom_strain = self.curvature * (
            steel_rectangle.bottom_edge - steel_rectangle.top_edge
        )
        self.steel_bottom_stress = steel.get_material_stress(self.steel_bottom_strain)
        self.steel_stress = 0.5 * (self.steel_top_stress + self.steel_bottom_stress)
        self.steel_force = self.steel_stress * steel_rectangle.area
        self.steel_lever_arm = steel_rectangle.top_edge + 2.0 / 3.0 * (
            steel_rectangle.bottom_edge - steel_rectangle.top_edge
        )
        self.steel_moment = self.steel_lever_arm * self.steel_force

        self.cs = ComputationCrosssectionCurvature(
            Crosssection(sections), self.curvature, self.neutral_axis
        )

    def test_curvature(self):
        self.assertEqual(self.cs.curvature, self.curvature)

    def test_neutral_axis(self):
        self.assertEqual(self.cs.neutral_axis, self.neutral_axis)

    def test_compute_split_sections(self):
        self.assertEqual(type(self.cs.compute_sections), list)

    def test_slab_axial_forces(self):
        self.assertAlmostEqual(self.cs.slab_sections_axial_force(), self.concrete_force)

    def test_girder_axial_forces(self):
        self.assertAlmostEqual(self.cs.girder_sections_axial_force(), self.steel_force)

    def test_total_axial_forces(self):
        self.assertAlmostEqual(
            self.cs.total_axial_force(), self.steel_force + self.concrete_force
        )

    def test_slab_moment(self):
        self.assertAlmostEqual(self.cs.slab_sections_moment(), self.concrete_moment)

    def test_girder_moment(self):
        self.assertAlmostEqual(self.cs.girder_sections_moment(), self.steel_moment)

    def test_total_moment(self):
        self.assertAlmostEqual(
            self.cs.total_moment(), self.steel_moment + self.concrete_moment
        )


class TestComputationCrosssectionCurvaturePositiveWithEffectiveWidth(TestCase):
    def setUp(self):
        membran = 2.0
        bending = 4.0
        self.effective_width = EffectiveWidths(membran, bending)
        self.curvature = 0.00001
        self.neutral_axis = concrete_bottom_edge

        self.concrete_rectangle = Rectangle(
            concrete_top_edge, concrete_bottom_edge, 2.0 * membran
        )

        self.concrete_top_strain = -self.curvature * self.neutral_axis
        self.concrete_top_stress = concrete.get_material_stress(
            self.concrete_top_strain
        )
        self.concrete_bottom_strain = 0.0
        self.concrete_bottom_stress = concrete.get_material_stress(
            self.concrete_bottom_strain
        )
        self.concrete_stress = 0.5 * (
            self.concrete_top_stress + self.concrete_bottom_stress
        )
        self.concrete_force = self.concrete_stress * self.concrete_rectangle.area
        self.concrete_lever_arm = (
            1.0
            / 3.0
            * (self.concrete_rectangle.bottom_edge - self.concrete_rectangle.top_edge)
        )
        self.concrete_moment = self.concrete_lever_arm * self.concrete_force

        self.steel_top_strain = 0.0
        self.steel_top_stress = steel.get_material_stress(self.steel_top_strain)
        self.steel_bottom_strain = self.curvature * (
            steel_rectangle.bottom_edge - steel_rectangle.top_edge
        )
        self.steel_bottom_stress = steel.get_material_stress(self.steel_bottom_strain)
        self.steel_stress = 0.5 * (self.steel_top_stress + self.steel_bottom_stress)
        self.steel_force = self.steel_stress * steel_rectangle.area
        self.steel_lever_arm = steel_rectangle.top_edge + 2.0 / 3.0 * (
            steel_rectangle.bottom_edge - steel_rectangle.top_edge
        )
        self.steel_moment = self.steel_lever_arm * self.steel_force

        self.cross_section = Crosssection(
            sections, slab_effective_widths=self.effective_width
        )

        self.cs = ComputationCrosssectionCurvature(
            self.cross_section, self.curvature, self.neutral_axis
        )

    def test_curvature(self):
        self.assertEqual(self.cs.curvature, self.curvature)

    def test_neutral_axis(self):
        self.assertEqual(self.cs.neutral_axis, self.neutral_axis)

    def test_compute_split_sections(self):
        self.assertEqual(type(self.cs.compute_sections), list)

    def test_slab_axial_forces(self):
        self.assertAlmostEqual(self.cs.slab_sections_axial_force(), self.concrete_force)

    def test_girder_axial_forces(self):
        self.assertAlmostEqual(self.cs.girder_sections_axial_force(), self.steel_force)

    def test_total_axial_forces(self):
        self.assertAlmostEqual(
            self.cs.total_axial_force(), self.steel_force + self.concrete_force
        )

    def test_slab_moment(self):
        self.assertAlmostEqual(self.cs.slab_sections_moment(), self.concrete_moment)

    def test_girder_moment(self):
        self.assertAlmostEqual(self.cs.girder_sections_moment(), self.steel_moment)

    def test_total_moment(self):
        self.assertAlmostEqual(
            self.cs.total_moment(), self.steel_moment + self.concrete_moment
        )


class TestComputationCrosssectionCurvatureNegativeWithEffectiveWidth(TestCase):
    def setUp(self):
        membran = 2.0
        bending = 4.0
        self.effective_width = EffectiveWidths(membran, bending)
        self.curvature = -0.000001
        self.neutral_axis = concrete_bottom_edge

        self.concrete_rectangle = Rectangle(
            concrete_top_edge, concrete_bottom_edge, 2.0 * bending
        )

        self.concrete_top_strain = -self.neutral_axis * self.curvature
        self.concrete_top_stress = concrete.get_material_stress(
            self.concrete_top_strain
        )
        self.concrete_bottom_strain = 0.0
        self.concrete_bottom_stress = concrete.get_material_stress(
            self.concrete_bottom_strain
        )
        self.concrete_stress = 0.5 * (
            self.concrete_top_stress + self.concrete_bottom_stress
        )
        self.concrete_force = self.concrete_stress * self.concrete_rectangle.area
        self.concrete_lever_arm = (
            1.0
            / 3.0
            * (self.concrete_rectangle.bottom_edge - self.concrete_rectangle.top_edge)
        )
        self.concrete_moment = self.concrete_lever_arm * self.concrete_force

        self.steel_top_strain = 0.0
        self.steel_top_stress = steel.get_material_stress(self.steel_top_strain)
        self.steel_bottom_strain = self.curvature * (
            steel_rectangle.bottom_edge - steel_rectangle.top_edge
        )
        self.steel_bottom_stress = steel.get_material_stress(self.steel_bottom_strain)
        self.steel_stress = 0.5 * (self.steel_top_stress + self.steel_bottom_stress)
        self.steel_force = self.steel_stress * steel_rectangle.area
        self.steel_lever_arm = steel_rectangle.top_edge + 2.0 / 3.0 * (
            steel_rectangle.bottom_edge - steel_rectangle.top_edge
        )
        self.steel_moment = self.steel_lever_arm * self.steel_force

        self.cross_section = Crosssection(
            sections, slab_effective_widths=self.effective_width
        )

        self.cs = ComputationCrosssectionCurvature(
            self.cross_section, self.curvature, self.neutral_axis
        )

    def test_curvature(self):
        self.assertEqual(self.cs.curvature, self.curvature)

    def test_neutral_axis(self):
        self.assertEqual(self.cs.neutral_axis, self.neutral_axis)

    def test_compute_split_sections(self):
        self.assertEqual(type(self.cs.compute_sections), list)

    def test_slab_axial_forces(self):
        self.assertAlmostEqual(self.cs.slab_sections_axial_force(), self.concrete_force)

    def test_girder_axial_forces(self):
        self.assertAlmostEqual(self.cs.girder_sections_axial_force(), self.steel_force)

    def test_total_axial_forces(self):
        self.assertAlmostEqual(
            self.cs.total_axial_force(), self.steel_force + self.concrete_force
        )

    def test_slab_moment(self):
        self.assertAlmostEqual(self.cs.slab_sections_moment(), self.concrete_moment)

    def test_girder_moment(self):
        self.assertAlmostEqual(self.cs.girder_sections_moment(), self.steel_moment)

    def test_total_moment(self):
        self.assertAlmostEqual(
            self.cs.total_moment(), self.steel_moment + self.concrete_moment
        )


if __name__ == "__main__":
    main()
