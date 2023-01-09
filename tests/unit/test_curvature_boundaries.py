from unittest import TestCase, main

from m_n_kappa.curvature_boundaries import (
    compute_curvatures,
    remove_higher_strains,
    remove_smaller_strains,
    get_lower_positions,
    get_higher_positions,
    MaximumCurvature,
    MinimumCurvature
)
from m_n_kappa.general import StrainPosition
from m_n_kappa.crosssection import CrossSectionBoundaries
from m_n_kappa.material import Concrete, Steel
from m_n_kappa.geometry import Rectangle

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


class TestComputeCurvatures(TestCase):
    pass


class TestRemoveStrains(TestCase):
    def setUp(self) -> None:
        self.position_strain_positive = StrainPosition(10, 0.0, 'Concrete')
        self.position_strain_zero = StrainPosition(0.0, 10., 'Concrete')
        self.position_strain_negative = StrainPosition(-10, 20., 'Concrete')
        self.position_strains = [
            self.position_strain_positive,
            self.position_strain_zero,
            self.position_strain_negative,
        ]

    def test_remove_higher_strains_1(self):
        for strain in [-5, 0., 5.]:
            with self.subTest(strain):
                self.assertListEqual(remove_higher_strains(strain, self.position_strains), [])

    def test_remove_higher_strains_2(self):
        self.assertListEqual(remove_higher_strains(15., self.position_strains), [self.position_strain_positive])

    def test_remove_smaller_strains_1(self):
        for strain in [-5, 0., 5.]:
            with self.subTest(strain):
                self.assertListEqual(remove_smaller_strains(strain, self.position_strains), [])

    def test_remove_smaller_strains_2(self):
        self.assertListEqual(remove_smaller_strains(-15., self.position_strains), [self.position_strain_negative])


class TestGetPositions(TestCase):
    def setUp(self) -> None:
        self.position_strain_positive = StrainPosition(10, 0.0, 'Concrete')
        self.position_strain_zero = StrainPosition(0.0, 10., 'Concrete')
        self.position_strain_negative = StrainPosition(-10, 20., 'Concrete')
        self.position_strains = [
            self.position_strain_positive,
            self.position_strain_zero,
            self.position_strain_negative,
        ]

    def test_get_lower_position_1(self):
        self.assertListEqual(get_lower_positions(-1, self.position_strains), self.position_strains)

    def test_get_lower_position_2(self):
        self.assertListEqual(get_lower_positions(15, self.position_strains), [self.position_strain_negative])

    def test_get_lower_position_3(self):
        self.assertListEqual(get_lower_positions(20, self.position_strains), [])

    def test_get_higher_position_1(self):
        self.assertListEqual(get_higher_positions(21, self.position_strains), self.position_strains)

    def test_get_higher_position_2(self):
        self.assertListEqual(get_higher_positions(5, self.position_strains), [self.position_strain_positive])

    def test_get_higher_position_3(self):
        self.assertListEqual(get_higher_positions(-1, self.position_strains), [])


class TestMaximumCurvature(TestCase):
    # TODO: TestMaximumCurvature
    pass

class TestMinimumCurvature(TestCase):
    def setUp(self):
        """
        Asssume steel-rectangel of S355 material
        """
        self.top_edge = 0.0
        self.bottom_edge = 10.0
        self.material = 'Steel'
        self.maximum_strain = 355.0
        self.minimum_strain = -355.0
        self.maximum_positive_section_strains = [
            StrainPosition(self.maximum_strain, self.top_edge, self.material),
            StrainPosition(self.maximum_strain, self.bottom_edge, self.material)
        ]
        self.maximum_negative_section_strains = [
            StrainPosition(self.minimum_strain, self.top_edge, self.material),
            StrainPosition(self.minimum_strain, self.bottom_edge, self.material)
        ]
        self.minimum_curvature = MinimumCurvature(
            self.maximum_positive_section_strains,
            self.maximum_negative_section_strains,
            curvature_is_positive=True,
        )

    def test_positive_curvature_compute(self):
        position = 0.5 * (self.bottom_edge - self.top_edge)
        strain_position = StrainPosition(0.0, position=position, material='Steel')
        self.assertEqual(self.minimum_curvature.compute(strain_position), self.maximum_strain-self.maximum_strain)

    def test_negative_curvature_compute(self):
        #TODO: TestMinimumCurvature - test_negative_curvature_compute
        pass


class TestCrossSectionBoundaries(TestCase):

    def setUp(self) -> None:
        self.sections_maximum_strains = [
            StrainPosition(concrete.maximum_strain, concrete_top_edge, 'Concrete'),
            StrainPosition(concrete.maximum_strain, concrete_bottom_edge, 'Concrete'),
            StrainPosition(steel.maximum_strain, steel_top_edge, 'Steel'),
            StrainPosition(steel.maximum_strain, steel_bottom_edge, 'Steel'),
        ]
        self.sections_minimum_strains = [
            StrainPosition(concrete.minimum_strain, concrete_top_edge, 'Concrete'),
            StrainPosition(concrete.minimum_strain, concrete_bottom_edge, 'Concrete'),
            StrainPosition(steel.minimum_strain, steel_top_edge, 'Steel'),
            StrainPosition(steel.minimum_strain, steel_bottom_edge, 'Steel'),
        ]
        self.cs = CrossSectionBoundaries(sections)

    def test_sections_maximum_strains(self):
        self.assertListEqual(self.cs._sections_maximum_strains, self.sections_maximum_strains)

    def test_sections_minimum_strains(self):
        self.assertListEqual(self.cs._sections_minimum_strains, self.sections_minimum_strains)

    def test_maximum_positive_curvature(self):
        curvature = (concrete.minimum_strain - steel.maximum_strain) / (concrete_top_edge - steel_bottom_edge)
        self.assertEqual(self.cs._maximum_positive_curvature.curvature, curvature)

    def test_maximum_negative_curvature(self):
        curvature = (steel.maximum_strain - steel.minimum_strain) / (steel_top_edge - steel_bottom_edge)
        self.assertEqual(self.cs._maximum_negative_curvature.curvature, curvature)


if __name__ == '__main__':
    main()