from m_n_kappa.curves_m_n_kappa import MNKappaCurvePoint, MNKappaCurvePoints
from m_n_kappa.general import StrainPosition
from m_n_kappa import Crosssection, Steel, Rectangle

from unittest import TestCase, main


class TestMNKappaCurvePoint(TestCase):
    def setUp(self) -> None:
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section = self.steel + self.rectangle
        self.cross_section = Crosssection([self.section])
        self.strain_position = StrainPosition(
            strain=0.001, position=10.0, material="Steel"
        )
        self.point_1 = MNKappaCurvePoint(
            moment=100.0,
            curvature=100.0,
            axial_force=100.0,
            axial_force_cross_section_number=0,
            strain_difference=100.0,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=100.0,
            neutral_axis_2=100.0,
        )
        self.point_2 = MNKappaCurvePoint(
            moment=200.0,
            curvature=100.0,
            axial_force=100.0,
            axial_force_cross_section_number=0,
            strain_difference=100.0,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=100.0,
            neutral_axis_2=100.0,
        )
        self.point_3 = MNKappaCurvePoint(
            moment=200.0,
            curvature=100.0,
            axial_force=100.0,
            axial_force_cross_section_number=0,
            strain_difference=100.0,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=100.0,
            neutral_axis_2=100.0,
        )

    def test_equal_points(self):
        self.assertEqual(self.point_2, self.point_3)

    def test_unequal_points(self):
        self.assertNotEqual(self.point_1, self.point_3)


class TestMNKappaCurvePoints(TestCase):
    def setUp(self) -> None:
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section = self.steel + self.rectangle
        self.cross_section = Crosssection([self.section])
        self.test_value_1 = 100.0
        self.test_value_2 = 200.0
        self.test_value_3 = 300.0
        self.test_values = [self.test_value_1, self.test_value_2]
        self.strain_position = StrainPosition(
            strain=0.001, position=10.0, material="Steel"
        )
        self.point_1 = MNKappaCurvePoint(
            moment=self.test_value_1,
            curvature=self.test_value_1,
            axial_force=self.test_value_1,
            axial_force_cross_section_number=0,
            strain_difference=self.test_value_1,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=self.test_value_1,
            neutral_axis_2=self.test_value_1,
        )
        self.point_2 = MNKappaCurvePoint(
            moment=self.test_value_2,
            curvature=self.test_value_2,
            axial_force=self.test_value_2,
            axial_force_cross_section_number=0,
            strain_difference=self.test_value_2,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=self.test_value_2,
            neutral_axis_2=self.test_value_2,
        )
        self.point_3 = MNKappaCurvePoint(
            moment=self.test_value_2,
            curvature=self.test_value_2,
            axial_force=self.test_value_2,
            axial_force_cross_section_number=0,
            strain_difference=self.test_value_2,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=self.test_value_2,
            neutral_axis_2=self.test_value_2,
        )
        self.point_4 = MNKappaCurvePoint(
            moment=self.test_value_3,
            curvature=self.test_value_3,
            axial_force=self.test_value_3,
            axial_force_cross_section_number=0,
            strain_difference=self.test_value_3,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=self.test_value_3,
            neutral_axis_2=self.test_value_3,
        )
        self.points = MNKappaCurvePoints([self.point_1, self.point_2])
        self.points_2 = MNKappaCurvePoints([self.point_3, self.point_4])
        self.points_3 = MNKappaCurvePoints([self.point_4])

    def test_add_already_existing_point(self):
        self.points.add(
            moment=self.test_value_1,
            curvature=self.test_value_1,
            axial_force=self.test_value_1,
            axial_force_cross_section_number=0,
            strain_difference=self.test_value_1,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=self.test_value_1,
            neutral_axis_2=self.test_value_1,
        )
        self.assertCountEqual(self.points.points, [self.point_1, self.point_2])

    def test_add_new_point(self):
        self.points.add(
            moment=self.test_value_3,
            curvature=self.test_value_3,
            axial_force=self.test_value_3,
            axial_force_cross_section_number=0,
            strain_difference=self.test_value_3,
            cross_section=self.cross_section,
            strain_position=self.strain_position,
            neutral_axis_1=self.test_value_3,
            neutral_axis_2=self.test_value_3,
        )
        self.assertCountEqual(
            self.points.points, [self.point_1, self.point_2, self.point_4]
        )

    def test_add_two_similar_MNKappaCurvePoints(self):
        self.new_points = self.points + self.points
        self.assertCountEqual(self.new_points.points, self.points.points)

    def test_add_two_almost_similar_MNKappaCurvePoints(self):
        self.new_points = self.points + self.points_2
        self.assertCountEqual(self.new_points.points, MNKappaCurvePoints(points=[
            self.point_1, self.point_2, self.point_4
        ]))

    def test_add_two_different_MNKappaCurvePoints(self):
        self.new_points = self.points + self.points_3
        self.assertCountEqual(self.new_points.points, MNKappaCurvePoints(points=[
            self.point_1, self.point_2, self.point_4
        ]))

    def test_moments(self):
        self.assertCountEqual(self.points.moments, self.test_values)

    def test_axial_forces(self):
        self.assertCountEqual(self.points.axial_forces, self.test_values)

    def test_curvatures(self):
        self.assertCountEqual(self.points.curvatures, self.test_values)

    def test_strain_differences(self):
        self.assertCountEqual(self.points.strain_differences, self.test_values)

    def test_maximum_moment(self):
        self.assertEqual(self.points.maximum_moment(), self.test_value_2)

    def test_curvature(self):
        pass  # TODO


if __name__ == "__main__":
    main()
