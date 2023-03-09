from unittest import TestCase, main

from m_n_kappa.geometry import (
    Rectangle,
    Circle,
    Trapezoid,
    StrainPosition,
    EffectiveWidths,
    check_width,
    IProfile,
    UPEProfile,
    RebarLayer,
    ComposedGeometry,
)


class TestCheckWidth(TestCase):
    def setUp(self) -> None:
        self.left_edge = -5.0
        self.right_edge = 5.0
        self.width = self.right_edge - self.left_edge

    def test_width(self):
        self.assertEqual(
            check_width(self.width), (self.width, self.left_edge, self.right_edge)
        )

    def test_width_and_left_edge(self):
        width = 10
        left_edge = -10.0
        right_edge = left_edge + width
        self.assertEqual(
            check_width(width=width, left_edge=left_edge),
            (width, left_edge, right_edge),
        )

    def test_width_and_right_edge(self):
        width = 10
        right_edge = -10.0
        left_edge = right_edge - width
        self.assertEqual(
            check_width(width=width, right_edge=right_edge),
            (width, left_edge, right_edge),
        )

    def test_left_and_right_edge(self):
        left_edge = -10.0
        right_edge = 10.0
        width = right_edge - left_edge
        self.assertEqual(
            check_width(left_edge=left_edge, right_edge=right_edge),
            (width, left_edge, right_edge),
        )

    def test_left_and_right_edge_swapped_numbers(self):
        left_edge = 10.0
        right_edge = -10.0
        width = left_edge - right_edge
        self.assertEqual(
            check_width(left_edge=left_edge, right_edge=right_edge),
            (width, right_edge, left_edge),
        )


class TestRectangle(TestCase):
    def setUp(self):
        self.top_edge = 0.0
        self.bottom_edge = 10.0
        self.width = 10.0
        self.height = self.bottom_edge - self.top_edge
        self.rectangle = Rectangle(
            top_edge=self.top_edge, bottom_edge=self.bottom_edge, width=self.width
        )
        self.membran_width = 2.0
        self.bending_width = 4.0
        self.effective_widths = EffectiveWidths(
            membran=self.membran_width,
            bending=self.bending_width,
            reinforcement_under_tension_use_membran_width=False,
            reinforcement_under_compression_use_membran_width=True,
            concrete_under_tension_use_membran_width=False,
            concrete_under_compression_use_membran_width=True,
        )

    def test_area(self):
        self.assertEqual(self.rectangle.area, self.height * self.width)

    def test_top_edge(self):
        self.assertEqual(self.rectangle.top_edge, self.top_edge)

    def test_bottom_edge(self):
        self.assertEqual(self.rectangle.bottom_edge, self.bottom_edge)

    def test_left_edge(self):
        self.assertEqual(self.rectangle.left_edge, -0.5 * self.width)

    def test_right_edge(self):
        self.assertEqual(self.rectangle.right_edge, 0.5 * self.width)

    def test_width(self):
        self.assertEqual(self.rectangle.width, self.width)

    def test_height(self):
        self.assertEqual(self.rectangle.height, self.height)

    def test_width_interception(self):
        self.assertEqual(self.rectangle.width_interception, self.width)

    def test_width_slope(self):
        self.assertEqual(self.rectangle.width_slope, 0.0)

    def test_centroid(self):
        self.assertEqual(
            self.rectangle.centroid, 0.5 * (self.top_edge + self.bottom_edge)
        )

    def test_edges(self):
        edges = [self.top_edge, self.bottom_edge]
        self.assertEqual(self.rectangle.edges, edges)

    def test_split(self):
        split_point = self.top_edge + 0.5 * self.height
        rectangle_1 = Rectangle(self.top_edge, split_point, self.width)
        rectangle_2 = Rectangle(split_point, self.bottom_edge, self.width)
        split_list = [rectangle_1, rectangle_2]
        self.assertListEqual(
            self.rectangle.split([StrainPosition(1.0, split_point, "Concrete")]),
            split_list,
        )

    def test_split_considering_effective_widths_positive(self):
        strain = 1.0
        split_point = StrainPosition(
            strain, self.top_edge + 0.5 * self.height, "Concrete"
        )
        rectangle_1 = Rectangle(
            self.top_edge, split_point.position, 2.0 * self.bending_width
        )
        rectangle_2 = Rectangle(
            split_point.position, self.bottom_edge, 2.0 * self.bending_width
        )
        split_list = [rectangle_1, rectangle_2]
        self.assertListEqual(
            self.rectangle.split([split_point], self.effective_widths), split_list
        )

    def test_split_considering_effective_widths_negative(self):
        strain = -1.0
        split_point = StrainPosition(
            strain, self.top_edge + 0.5 * self.height, "Concrete"
        )
        rectangle_1 = Rectangle(
            self.top_edge, split_point.position, 2.0 * self.membran_width
        )
        rectangle_2 = Rectangle(
            split_point.position, self.bottom_edge, 2.0 * self.membran_width
        )
        split_list = [rectangle_1, rectangle_2]
        self.assertListEqual(
            self.rectangle.split([split_point], self.effective_widths), split_list
        )

    def test_split_considering_effective_widths_zero(self):
        split_point = StrainPosition(0.0, self.top_edge + 0.5 * self.height, "Concrete")
        strain_positions = [
            StrainPosition(-10.0, self.top_edge, "Concrete"),
            split_point,
            StrainPosition(10.0, self.bottom_edge, "Concrete"),
        ]
        top_rectangle = Rectangle(
            self.top_edge, split_point.position, 2.0 * self.membran_width
        )
        bottom_rectangle = Rectangle(
            split_point.position, self.bottom_edge, 2.0 * self.bending_width
        )
        split_list = [top_rectangle, bottom_rectangle]
        self.assertListEqual(
            self.rectangle.split(strain_positions, self.effective_widths), split_list
        )


class TestCircle(TestCase):
    def setUp(self):
        self.diameter = 10.0
        self.centroid_y = 25.0
        self.centroid_z = 0.0
        self.circle = Circle(
            centroid_y=self.centroid_y,
            diameter=self.diameter,
            centroid_z=self.centroid_z,
        )
        self.membran_width = 2.0
        self.bending_width = 4.0
        self.effective_widths = EffectiveWidths(
            membran=self.membran_width,
            bending=self.bending_width,
            reinforcement_under_tension_use_membran_width=False,
            reinforcement_under_compression_use_membran_width=True,
            concrete_under_tension_use_membran_width=False,
            concrete_under_compression_use_membran_width=True,
        )

    def test_area(self):
        self.assertEqual(self.circle.area, self.diameter**2.0 * 0.25 * 3.145)

    def test_centroid_y(self):
        self.assertEqual(self.circle.centroid_y, self.centroid_y)

    def test_centroid_z(self):
        self.assertEqual(self.circle.centroid_z, self.centroid_z)

    def test_edges(self):
        edges = [self.centroid_z]
        self.assertCountEqual(self.circle.edges, edges)

    def test_split_inside_effective_width(self):
        """in case reinforcement bar is inside effective width it is consiered"""
        circle = Circle(centroid_y=5.0, diameter=self.diameter, centroid_z=0.0)
        split_point = StrainPosition(1.0, 5.0, "Reinforcement")
        strain_positions = [
            StrainPosition(-10.0, 0.0, "Reinforcement"),
            split_point,
            StrainPosition(10.0, 10.0, "Reinforcement"),
        ]
        self.assertEqual(
            circle.split(strain_positions, self.effective_widths), [circle]
        )

    def test_split_outside_effective_width(self):
        """in case reinforcement bar is outside effective width it stays unconsidered"""
        circle = Circle(centroid_y=5.0, diameter=self.diameter, centroid_z=10.0)
        split_point = StrainPosition(1.0, 5.0, "Reinforcement")
        strain_positions = [
            StrainPosition(-10.0, 0.0, "Reinforcement"),
            split_point,
            StrainPosition(10.0, 10.0, "Reinforcement"),
        ]
        self.assertEqual(circle.split(strain_positions, self.effective_widths), [])


class TestTrapazoidRectangle(TestCase):
    def setUp(self):
        self.top_edge = 0.0
        self.bottom_edge = 10.0
        self.top_width = 10.0
        self.bottom_width = 10.0

        self.trapazoid = Trapezoid(
            top_edge=self.top_edge,
            bottom_edge=self.bottom_edge,
            top_width=self.top_width,
            bottom_width=self.bottom_width,
        )
        self.rectangle = Rectangle(self.top_edge, self.bottom_edge, self.top_width)

    def test_area(self):
        self.assertEqual(self.trapazoid.area, self.rectangle.area)

    def test_centroid(self):
        self.assertEqual(self.trapazoid.centroid, self.trapazoid.centroid)

    def test_edges(self):
        self.assertEqual(self.trapazoid.edges, self.rectangle.edges)

    def test_width_interception(self):
        self.assertEqual(
            self.trapazoid.width_interception, self.rectangle.width_interception
        )

    def test_width_slope(self):
        self.assertEqual(self.trapazoid.width_slope, self.rectangle.width_slope)


class TestTrapazoidTriangle(TestCase):
    def setUp(self):
        self.top_edge = 0.0
        self.bottom_edge = 10.0
        self.top_width = 10.0
        self.bottom_width = 0.0
        self.height = self.bottom_edge - self.top_edge

        self.trapazoid = Trapezoid(
            top_edge=self.top_edge,
            bottom_edge=self.bottom_edge,
            top_width=self.top_width,
            bottom_width=self.bottom_width,
        )

    def test_area(self):
        area = 0.5 * self.height * self.top_width
        self.assertEqual(self.trapazoid.area, area)

    def test_centroid(self):
        self.assertAlmostEqual(self.trapazoid.centroid, 1.0 / 3.0 * self.height)

    def test_edges(self):
        edges = [self.top_edge, self.bottom_edge]
        self.assertEqual(self.trapazoid.edges, edges)

    def test_width_interception(self):
        self.assertEqual(self.trapazoid.width_interception, self.bottom_edge)

    def test_width_slope(self):
        slope = (self.top_width - self.bottom_width) / (
            self.top_edge - self.bottom_edge
        )
        self.assertEqual(self.trapazoid.width_slope, slope)

    def test_split(self):
        width_at_point = 0.5 * (self.top_width + self.bottom_width)
        point = StrainPosition(1.0, 5.0, "Concrete")
        trapazoids = [
            Trapezoid(
                self.top_edge,
                point.position,
                self.top_width,
                bottom_width=width_at_point,
            ),
            Trapezoid(
                point.position,
                self.bottom_edge,
                width_at_point,
                bottom_width=self.bottom_width,
            ),
        ]
        self.assertListEqual(self.trapazoid.split([point]), trapazoids)


class TestComposedGeometries(TestCase):
    def test_upe(self):
        top_edge = 0.0
        t_f = 10.0
        b_f = 20.0
        t_w = 5.0
        h_w = 100.0
        upe = UPEProfile(top_edge, t_f, b_f, t_w, h_w)
        web = Rectangle(top_edge, top_edge + t_w, width=h_w)
        left_flange = Rectangle(
            top_edge, top_edge + b_f, left_edge=-0.5 * h_w - t_f, right_edge=-0.5 * h_w
        )
        right_flange = Rectangle(
            top_edge, top_edge + b_f, left_edge=0.5 * h_w + t_f, right_edge=0.5 * h_w
        )
        self.assertListEqual(upe.geometries, [left_flange, web, right_flange])

    def test_i_profile(self):
        top_edge = 0.0
        t_f = 10.0
        b_f = 20.0
        t_w = 5.0
        h_w = 100.0
        i = IProfile(top_edge, t_w, h_w, t_fo=t_f, b_fo=b_f)
        top_flange = Rectangle(
            top_edge, top_edge + t_f, left_edge=-0.5 * b_f, right_edge=0.5 * b_f
        )
        web = Rectangle(top_edge + t_f, top_edge + t_f + h_w, width=t_w)
        bottom_flange = Rectangle(
            top_edge + t_f + h_w, top_edge + t_f + h_w + t_f, width=b_f
        )
        self.assertListEqual(i.geometries, [top_flange, web, bottom_flange])


class TestRebarLayer(TestCase):
    def setUp(self) -> None:
        self.centroid_z = 10.0
        self.rebar_diameter = 10.0
        self.rebar_number = 10
        self.width = 100
        self.layer = RebarLayer(
            self.rebar_diameter,
            self.centroid_z,
            self.rebar_number,
            self.width,
        )

    def test_centroid(self):
        self.assertEqual(self.layer.centroid_z, self.centroid_z)

    def test_rebar_number(self):
        self.assertEqual(self.layer.rebar_number, self.rebar_number)

    def test_rebar_diameter(self):
        self.assertEqual(self.layer.rebar_diameter, self.rebar_diameter)

    def test_rebar_horizontal_distance(self):
        self.assertEqual(
            self.layer.rebar_horizontal_distance, self.width / self.rebar_number
        )

    def test_left_edge(self):
        self.assertEqual(self.layer.left_edge, -0.5 * self.width)

    def test_right_edge(self):
        self.assertEqual(self.layer.right_edge, 0.5 * self.width)

    def test_geometries(self):
        rebar_horizontal_distance = self.width / self.rebar_number
        circles = []
        for rebar_number in range(self.rebar_number):
            circles.append(
                Circle(
                    self.rebar_diameter,
                    -0.5 * self.width + rebar_number * rebar_horizontal_distance,
                    self.centroid_z,
                )
            )
        self.assertListEqual(self.layer.geometries, circles)


class TestComposition(TestCase):
    def setUp(self) -> None:
        self.section_1 = Rectangle(0.0, 10.0, 10.0)
        self.section_2 = Rectangle(10.0, 20.0, 10.0)
        self.section_3 = Rectangle(20.0, 30.0, 10.0)

    def test_composition(self):
        new_geometry = self.section_1 + self.section_2
        self.assertEqual(type(new_geometry), ComposedGeometry)

    def test_add_geometry_1(self):
        composed_geometry = self.section_1 + self.section_2
        new_geometry = composed_geometry + self.section_3
        self.assertEqual(type(new_geometry), ComposedGeometry)

    def test_add_geometry_2(self):
        composed_geometry = self.section_1 + self.section_2
        new_geometry = self.section_3 + composed_geometry
        self.assertEqual(type(new_geometry), ComposedGeometry)


class TestIProfile(TestCase):
    def setUp(self):
        self.i_profile = IProfile(
            top_edge=100.0,
            t_fo=10,
            b_fo=200,
            h_w=200 - 2 * 10,
            t_w=15,
        )

    def test_height(self):
        self.assertEqual(self.i_profile.height, 200)

    def test_bottom_edge(self):
        self.assertEqual(self.i_profile.bottom_edge, 300)


if __name__ == "__main__":
    main()
