from unittest import TestCase, main

from m_n_kappa.boundaries import DecisiveNeutralAxis
from m_n_kappa import Rectangle, Steel, Concrete, Crosssection, Circle, Reinforcement


class TestSingleSectionIsotropMaterial(TestCase):
    def setUp(self) -> None:
        self.top_edge = 0.0
        self.bottom_edge = 10
        self.strain = 0.15
        self.rectangle = Rectangle(
            top_edge=self.top_edge, bottom_edge=self.bottom_edge, width=10
        )
        self.steel = Steel(f_y=355, failure_strain=self.strain)
        self.section = self.rectangle + self.steel
        self.cross_section = Crosssection(sections=[self.section])
        self.boundary = self.cross_section.get_boundary_conditions()

    def test_type(self):
        self.assertEqual(type(self.boundary.neutral_axes), DecisiveNeutralAxis)

    def test_positive_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = 0.1**superscript
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.strain / curvature,
                        self.top_edge + self.strain / curvature,
                    ),
                )

    def test_negative_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = -(0.1**superscript)
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge + self.strain / curvature,
                        self.top_edge - self.strain / curvature,
                    ),
                )


class TestTwoSectionsIsotropMaterial(TestCase):
    def setUp(self) -> None:
        self.top_edge = 0.0
        self.bottom_edge = 10
        self.strain = 0.15
        self.rectangle_1 = Rectangle(
            top_edge=self.top_edge,
            bottom_edge=0.5 * (self.top_edge + self.bottom_edge),
            width=10,
        )
        self.rectangle_2 = Rectangle(
            top_edge=0.5 * (self.top_edge + self.bottom_edge),
            bottom_edge=self.bottom_edge,
            width=10,
        )
        self.rectangles = self.rectangle_1 + self.rectangle_2
        self.steel = Steel(f_y=355, failure_strain=self.strain)
        self.cross_section = self.rectangles + self.steel
        self.boundary = self.cross_section.get_boundary_conditions()

    def test_positive_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = 0.1**superscript
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.strain / curvature,
                        self.top_edge + self.strain / curvature,
                    ),
                )

    def test_negative_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = -(0.1**superscript)
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge + self.strain / curvature,
                        self.top_edge - self.strain / curvature,
                    ),
                )


class TestSingleSectionAnisotropMaterial(TestCase):
    def setUp(self) -> None:
        self.top_edge = 0.0
        self.bottom_edge = 10
        self.max_strain = 10.0
        self.min_strain = -0.0035
        self.rectangle = Rectangle(
            top_edge=self.top_edge, bottom_edge=self.bottom_edge, width=10
        )
        self.concrete = Concrete(f_cm=30.0)
        self.section = self.rectangle + self.concrete
        self.cross_section = Crosssection(sections=[self.section])
        self.boundary = self.cross_section.get_boundary_conditions()

    def test_positive_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = 0.1**superscript
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.max_strain / curvature,
                        self.top_edge - self.min_strain / curvature,
                    ),
                )

    def test_negative_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = -(0.1**superscript)
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.min_strain / curvature,
                        self.top_edge - self.max_strain / curvature,
                    ),
                )


class TestTwoSectionsAnisotropMaterial(TestCase):
    def setUp(self) -> None:
        self.top_edge = 0.0
        self.bottom_edge = 10
        self.max_strain = 10.0
        self.min_strain = -0.0035
        self.rectangle_1 = Rectangle(
            top_edge=self.top_edge,
            bottom_edge=0.5 * (self.top_edge + self.bottom_edge),
            width=10,
        )
        self.rectangle_2 = Rectangle(
            top_edge=0.5 * (self.top_edge + self.bottom_edge),
            bottom_edge=self.bottom_edge,
            width=10,
        )
        self.rectangles = self.rectangle_1 + self.rectangle_2
        self.concrete = Concrete(f_cm=30.0)
        self.cross_section = self.rectangles + self.concrete
        self.boundary = self.cross_section.get_boundary_conditions()

    def test_positive_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = 0.1**superscript
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.max_strain / curvature,
                        self.top_edge - self.min_strain / curvature,
                    ),
                )

    def test_negative_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = -(0.1**superscript)
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.min_strain / curvature,
                        self.top_edge - self.max_strain / curvature,
                    ),
                )


class TestTwoSectionsTwoMaterials(TestCase):

    """concrete-rectangle with rebar in the middle"""

    def setUp(self) -> None:

        self.top_edge = 0.0
        self.bottom_edge = 10
        self.mean = 0.5 * (self.top_edge + self.bottom_edge)
        self.max_strain = 10.0
        self.min_strain = -0.0035
        self.rebar_strain = 0.25
        self.slab = Rectangle(
            top_edge=self.top_edge, bottom_edge=self.bottom_edge, width=10
        )
        self.concrete = Concrete(f_cm=30.0)
        self.concrete_slab = self.slab + self.concrete
        self.diameter = 1.0
        self.rebar = Circle(
            diameter=self.diameter, centroid_z=self.mean, centroid_y=0.0
        )
        self.reinforcement = Reinforcement(f_s=500, failure_strain=self.rebar_strain)
        self.reinforcement_bar = self.rebar + self.reinforcement
        self.cross_section = self.concrete_slab + self.reinforcement_bar
        self.boundary = self.cross_section.get_boundary_conditions()

    def test_positive_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = 0.1**superscript
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.mean + 0.5 * self.diameter - self.rebar_strain / curvature,
                        self.top_edge - self.min_strain / curvature,
                    ),
                )

    def test_negative_curvature(self):
        for superscript in [0, 1, 2, 3, 4, 5]:
            curvature = -(0.1**superscript)
            with self.subTest(curvature):
                self.assertCountEqual(
                    self.boundary.neutral_axes.compute(curvature=curvature),
                    (
                        self.bottom_edge - self.min_strain / curvature,
                        self.mean - 0.5 * self.diameter - self.rebar_strain / curvature,
                    ),
                )


if __name__ == "__main__":
    main()
