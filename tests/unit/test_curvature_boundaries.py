from unittest import TestCase, main

from m_n_kappa.boundaries import (
    compute_curvatures,
    remove_higher_strains,
    remove_smaller_strains,
    get_lower_positions,
    get_higher_positions,
    MaximumCurvature,
    MinimumCurvature,
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


from m_n_kappa import IProfile, Steel, Rectangle, Concrete, RebarLayer, Reinforcement

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
    top_edge=100.0, b_fo=200, t_fo=15, h_w=200 - 2 * 15, t_w=15, centroid_y=0.0
)
steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
steel_section = i_profile + steel
cross_section = concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section


class TestComputeCurvatures(TestCase):
    pass


class TestRemoveStrains(TestCase):
    def setUp(self) -> None:
        self.position_strain_positive = StrainPosition(10, 0.0, "Concrete")
        self.position_strain_zero = StrainPosition(0.0, 10.0, "Concrete")
        self.position_strain_negative = StrainPosition(-10, 20.0, "Concrete")
        self.position_strains = [
            self.position_strain_positive,
            self.position_strain_zero,
            self.position_strain_negative,
        ]

    def test_remove_higher_strains_1(self):
        self.assertListEqual(
            remove_higher_strains(-5.0, self.position_strains),
            [self.position_strain_negative],
        )
        self.assertListEqual(
            remove_higher_strains(0.0, self.position_strains),
            [self.position_strain_negative],
        )
        self.assertListEqual(
            remove_higher_strains(5.0, self.position_strains),
            [self.position_strain_zero, self.position_strain_negative],
        )

    def test_remove_higher_strains_2(self):
        self.assertListEqual(
            remove_higher_strains(15.0, self.position_strains), self.position_strains
        )

    def test_remove_smaller_strains_1(self):
        self.assertListEqual(
            remove_smaller_strains(-5.0, self.position_strains),
            [self.position_strain_positive, self.position_strain_zero],
        )
        self.assertListEqual(
            remove_smaller_strains(0.0, self.position_strains),
            [self.position_strain_positive],
        )
        self.assertListEqual(
            remove_smaller_strains(5.0, self.position_strains),
            [self.position_strain_positive],
        )

    def test_remove_smaller_strains_2(self):
        self.assertListEqual(
            remove_smaller_strains(-15.0, self.position_strains), self.position_strains
        )


class TestGetPositions(TestCase):
    def setUp(self) -> None:
        self.position_strain_positive = StrainPosition(10, 0.0, "Concrete")
        self.position_strain_zero = StrainPosition(0.0, 10.0, "Concrete")
        self.position_strain_negative = StrainPosition(-10, 20.0, "Concrete")
        self.position_strains = [
            self.position_strain_positive,
            self.position_strain_zero,
            self.position_strain_negative,
        ]

    def test_get_lower_position_1(self):
        self.assertListEqual(
            get_lower_positions(-1, self.position_strains), self.position_strains
        )

    def test_get_lower_position_2(self):
        self.assertListEqual(
            get_lower_positions(15, self.position_strains),
            [self.position_strain_negative],
        )

    def test_get_lower_position_3(self):
        self.assertListEqual(get_lower_positions(20, self.position_strains), [])

    def test_get_higher_position_1(self):
        self.assertListEqual(
            get_higher_positions(21, self.position_strains), self.position_strains
        )

    def test_get_higher_position_2(self):
        self.assertListEqual(
            get_higher_positions(5, self.position_strains),
            [self.position_strain_positive],
        )

    def test_get_higher_position_3(self):
        self.assertListEqual(get_higher_positions(-1, self.position_strains), [])


class TestMaximumCurvature(TestCase):
    def setUp(self):
        """
        Asssume steel-rectangel of S355 material
        """
        self.top_edge = 0.0
        self.bottom_edge = 10.0
        self.material = "Steel"
        self.maximum_strain = 355.0
        self.minimum_strain = -355.0
        self.maximum_positive_section_strains = [
            StrainPosition(self.maximum_strain, self.top_edge, self.material),
            StrainPosition(self.maximum_strain, self.bottom_edge, self.material),
        ]
        self.maximum_negative_section_strains = [
            StrainPosition(self.minimum_strain, self.top_edge, self.material),
            StrainPosition(self.minimum_strain, self.bottom_edge, self.material),
        ]
        self.curvature = (self.maximum_strain - self.minimum_strain) / (self.bottom_edge - self.top_edge)
        self.maximum_curvature = MaximumCurvature(
            curvature=self.curvature,
            start=self.maximum_positive_section_strains[0],
            other=self.maximum_positive_section_strains[-1],
            maximum_positive_section_strains=self.maximum_positive_section_strains,
            maximum_negative_section_strains=self.maximum_negative_section_strains,
        )

    def test_input_maximum_strain_other_position(self):
        position = 0.5 * (self.bottom_edge - self.top_edge)
        strain_position = StrainPosition(self.maximum_strain, position=position, material="Steel")
        self.assertEqual(self.maximum_curvature.compute(strain_position), 0.0)

    def test_input_maximum_strain_maximum_position(self):
        strain_position = StrainPosition(self.maximum_strain, position=self.bottom_edge, material="Steel")
        self.assertEqual(self.maximum_curvature.compute(strain_position), self.curvature)

    def test_input_minimum_strain_minimum_position(self):
        strain_position = StrainPosition(self.minimum_strain, position=self.top_edge, material="Steel")
        self.assertEqual(self.maximum_curvature.compute(strain_position), self.curvature)


class TestMinimumCurvature(TestCase):
    def setUp(self):
        """
        Asssume steel-rectangel of S355 material
        """
        self.top_edge = 0.0
        self.bottom_edge = 10.0
        self.material = "Steel"
        self.maximum_strain = 355.0
        self.minimum_strain = -355.0
        self.maximum_positive_section_strains = [
            StrainPosition(self.maximum_strain, self.top_edge, self.material),
            StrainPosition(self.maximum_strain, self.bottom_edge, self.material),
        ]
        self.maximum_negative_section_strains = [
            StrainPosition(self.minimum_strain, self.top_edge, self.material),
            StrainPosition(self.minimum_strain, self.bottom_edge, self.material),
        ]
        self.minimum_curvature = MinimumCurvature(
            self.maximum_positive_section_strains,
            self.maximum_negative_section_strains,
            curvature_is_positive=True,
        )

    def test_positive_curvature_compute(self):
        position = 0.5 * (self.bottom_edge - self.top_edge)
        strain_position = StrainPosition(0.0, position=position, material="Steel")
        self.assertEqual(
            self.minimum_curvature.compute(strain_position),
            0.0001 / 5.0,
        )

    def test_negative_curvature_compute(self):
        # TODO: TestMinimumCurvature - test_negative_curvature_compute
        pass

    def test_positive_curvature_max_value(self):
        strain_position = StrainPosition(self.maximum_strain, self.top_edge, self.material)
        self.assertEqual(
            self.minimum_curvature.compute(strain_position),
            0.0
        )

    def test_negative_curvature_max_value(self):
        strain_position = StrainPosition(self.minimum_strain, self.bottom_edge - 1.0 , self.material)
        self.assertEqual(
            self.minimum_curvature.compute(strain_position),
            0.0
        )


class TestCrossSectionBoundaries(TestCase):
    def setUp(self) -> None:
        self.concrete = Concrete(f_cm=f_cm)
        self.concrete_rectangle = Rectangle(
            top_edge=concrete_top_edge,
            bottom_edge=concrete_bottom_edge,
            width=concrete_width,
        )
        self.concrete_section = concrete + concrete_rectangle

        self.steel = Steel(f_y=f_y, failure_strain=epsilon_u)
        self.steel_rectangle = Rectangle(
            top_edge=steel_top_edge, bottom_edge=steel_bottom_edge, width=steel_width
        )
        self.steel_section = self.steel + self.steel_rectangle

        self.sections = [self.concrete_section, self.steel_section]

        self.sections_maximum_strains = [
            StrainPosition(self.concrete.maximum_strain, concrete_top_edge, "Concrete"),
            StrainPosition(
                self.concrete.maximum_strain, concrete_bottom_edge, "Concrete"
            ),
            StrainPosition(self.steel.maximum_strain, steel_top_edge, "Steel"),
            StrainPosition(self.steel.maximum_strain, steel_bottom_edge, "Steel"),
        ]
        self.sections_minimum_strains = [
            StrainPosition(self.concrete.minimum_strain, concrete_top_edge, "Concrete"),
            StrainPosition(
                self.concrete.minimum_strain, concrete_bottom_edge, "Concrete"
            ),
            StrainPosition(self.steel.minimum_strain, steel_top_edge, "Steel"),
            StrainPosition(self.steel.minimum_strain, steel_bottom_edge, "Steel"),
        ]
        self.cs = CrossSectionBoundaries(self.sections)

    def test_sections_maximum_strains(self):
        self.assertListEqual(
            self.cs._sections_maximum_strains, self.sections_maximum_strains
        )

    def test_sections_minimum_strains(self):
        self.assertListEqual(
            self.cs._sections_minimum_strains, self.sections_minimum_strains
        )

    def test_maximum_positive_curvature(self):
        curvature = (self.concrete.minimum_strain - self.steel.maximum_strain) / (
            concrete_top_edge - steel_bottom_edge
        )
        self.assertEqual(self.cs._maximum_positive_curvature.curvature, curvature)

    def test_maximum_negative_curvature(self):
        curvature = (self.steel.maximum_strain - self.steel.minimum_strain) / (
            steel_top_edge - steel_bottom_edge
        )
        self.assertEqual(self.cs._maximum_negative_curvature.curvature, curvature)


class TestGetBoundariesSteelSection(TestCase):
    def setUp(self) -> None:
        self.steel = Steel(f_y=f_y, failure_strain=epsilon_u)
        self.i_profile = IProfile(
            top_edge=100.0, b_fo=200, t_fo=15, h_w=200 - 2 * 15, t_w=9.5, centroid_y=0.0
        )
        self.cross_section = self.steel + self.i_profile
        self.boundaries = self.cross_section.get_boundary_conditions()

    def test_boundaries_type(self):
        from m_n_kappa.boundaries import Boundaries

        self.assertEqual(type(self.boundaries), Boundaries)

    def test_boundaries_positive_maximum_curvature(self):
        self.assertEqual(
            self.boundaries.positive.maximum_curvature.curvature,
            (self.steel.maximum_strain - self.steel.minimum_strain)
            / (self.i_profile.t_fo + self.i_profile.h_w + self.i_profile.t_fu),
        )

    def test_positive_maximum_curvature_start(self):
        self.assertIn(
            self.boundaries.positive.maximum_curvature.start,
            [
                StrainPosition(
                    self.steel.minimum_strain, self.i_profile.top_edge, "Steel"
                ),
                StrainPosition(
                    self.steel.maximum_strain,
                    (
                        self.i_profile.top_edge
                        + self.i_profile.t_fo
                        + self.i_profile.h_w
                        + self.i_profile.t_fu
                    ),
                    "Steel",
                ),
            ],
        )

    def test_positive_maximum_curvature_other(self):
        self.assertIn(
            self.boundaries.positive.maximum_curvature.other,
            [
                StrainPosition(
                    self.steel.minimum_strain, self.i_profile.top_edge, "Steel"
                ),
                StrainPosition(
                    self.steel.maximum_strain,
                    (
                        self.i_profile.top_edge
                        + self.i_profile.t_fo
                        + self.i_profile.h_w
                        + self.i_profile.t_fu
                    ),
                    "Steel",
                ),
            ],
        )

    def test_negative_maximum_curvature_start(self):
        self.assertIn(
            self.boundaries.positive.maximum_curvature.other,
            [
                StrainPosition(
                    self.steel.maximum_strain, self.i_profile.top_edge, "Steel"
                ),
                StrainPosition(
                    self.steel.minimum_strain,
                    (
                        self.i_profile.top_edge
                        + self.i_profile.t_fo
                        + self.i_profile.h_w
                        + self.i_profile.t_fu
                    ),
                    "Steel",
                ),
            ],
        )

    def test_negative_maximum_curvature_other(self):
        self.assertIn(
            self.boundaries.positive.maximum_curvature.start,
            [
                StrainPosition(
                    self.steel.maximum_strain, self.i_profile.top_edge, "Steel"
                ),
                StrainPosition(
                    self.steel.minimum_strain,
                    (
                        self.i_profile.top_edge
                        + self.i_profile.t_fo
                        + self.i_profile.h_w
                        + self.i_profile.t_fu
                    ),
                    "Steel",
                ),
            ],
        )

    def test_positive_minimum_curvature(self):
        self.strain_position = StrainPosition(
            0.05,
            self.i_profile.top_edge + self.i_profile.t_fo + self.i_profile.h_w,
            "Steel",
        )
        self.bottom_edge = (
            self.i_profile.top_edge
            + self.i_profile.t_fo
            + self.i_profile.h_w
            + self.i_profile.t_fu
        )
        self.assertAlmostEqual(
            self.boundaries.positive.minimum_curvature.compute(self.strain_position),
            0.0001 / (self.strain_position.position - self.i_profile.top_edge),
        )


from m_n_kappa.crosssection import Crosssection


class TestGetBoundariesConcreteSection(TestCase):
    def setUp(self) -> None:
        self.cross_section = Crosssection([concrete_section])
        self.boundaries = self.cross_section.get_boundary_conditions()

    def test_positive_maximum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.maximum_curvature.curvature, (0.0035 + 10.0) / 100
        )

    def test_start(self):
        self.assertEqual(
            self.boundaries.positive.maximum_curvature.start,
            StrainPosition(-0.0035, 0.0, "Concrete"),
        )

    def test_positive_minimum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.minimum_curvature.compute(
                StrainPosition(-0.0035, 0.0, "Concrete")
            ),
            (0.0035 - 0.0034) / 100,
        )


class TestGetBoundariesCompositeSection(TestCase):
    def setUp(self) -> None:
        self.cross_section = steel_section + concrete_section
        self.boundaries = self.cross_section.get_boundary_conditions()

    def test_positive_maximum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.maximum_curvature.curvature,
            (0.0035 + 0.15) / (100 + 200),
        )

    def test_start(self):
        self.assertEqual(
            self.boundaries.positive.maximum_curvature.start,
            StrainPosition(-0.0035, 0.0, "Concrete"),
        )

    def test_other(self):
        self.assertEqual(
            self.boundaries.positive.maximum_curvature.other,
            StrainPosition(0.15, (100 + 200), "Steel"),
        )

    def test_positive_minimum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.minimum_curvature.compute(
                StrainPosition(-0.0035, 0.0, "Concrete")
            ),
            (0.0035 - 0.0034) / (100 + 200),
        )


class TestGetBoundariesReinforcement(TestCase):
    def setUp(self) -> None:
        self.cross_section = top_rebar_layer + bottom_rebar_layer
        self.boundaries = self.cross_section.get_boundary_conditions()

    def test_positive_maximum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.maximum_curvature.curvature,
            (0.15 + 0.15) / (50 + 10),
        )

    def test_start(self):
        self.assertIn(
            self.boundaries.positive.maximum_curvature.start,
            [
                StrainPosition(-0.15, 20, "Reinforcement"),
                StrainPosition(0.15, 80, "Reinforcement"),
            ],
        )

    def test_positive_minimum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.minimum_curvature.compute(
                StrainPosition(-0.15, 0.25, "Reinforcement")
            ),
            0.0001 / 45,
        )


class TestGetBoundariesCompositeSectionWithReinforcement(TestCase):
    def setUp(self) -> None:
        self.cross_section = steel_section + concrete_section + bottom_rebar_layer
        self.boundaries = self.cross_section.get_boundary_conditions()

    def test_positive_maximum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.maximum_curvature.curvature,
            (0.0035 + 0.15) / (100 + 200),
        )

    def test_start(self):
        self.assertEqual(
            self.boundaries.positive.maximum_curvature.start,
            StrainPosition(-0.0035, 0.0, "Concrete"),
        )

    def test_positive_minimum_curvature(self):
        self.assertAlmostEqual(
            self.boundaries.positive.minimum_curvature.compute(
                StrainPosition(-0.0035, 0.0, "Concrete")
            ),
            (0.0035 - 0.0034) / (100 + 200),
        )


if __name__ == "__main__":
    main()
