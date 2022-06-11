import unittest

from m_n_kappa import geometry


class TestRectangle(unittest.TestCase):

    top_edge = 0.0
    bottom_edge = 10.0
    width = 10.0
    height = bottom_edge - top_edge
    rectangle = geometry.Rectangle(
        top_edge=top_edge, bottom_edge=bottom_edge, width=width
    )

    def test_area(self):
        self.assertEqual(self.rectangle.area, self.height * self.width)

    def test_top_edge(self):
        self.assertEqual(self.rectangle.top_edge, self.top_edge)

    def test_bottom_edge(self):
        self.assertEqual(self.rectangle.bottom_edge, self.bottom_edge)

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
        rectangle_1 = geometry.Rectangle(self.top_edge, split_point, self.width)
        rectangle_2 = geometry.Rectangle(split_point, self.bottom_edge, self.width)
        split_list = [rectangle_1, rectangle_2]
        self.assertListEqual(self.rectangle.split([split_point]), split_list)


class TestCircle(unittest.TestCase):
    diameter = 10.0
    centroid = 25.0

    circle = geometry.Circle(centroid=centroid, diameter=diameter)

    def test_area(self):
        self.assertEqual(self.circle.area, self.diameter ** (2.0) * 0.25 * 3.145)

    def test_centroid(self):
        self.assertEqual(self.circle.centroid, self.centroid)

    def test_edges(self):
        edges = [self.centroid]
        self.assertEqual(self.circle.edges, edges)


class TestTrapazoidRectangle(unittest.TestCase):
    top_edge = 0.0
    bottom_edge = 10.0
    top_width = 10.0
    bottom_width = 10.0

    trapazoid = geometry.Trapazoid(
        top_edge=top_edge,
        bottom_edge=bottom_edge,
        top_width=top_width,
        bottom_width=bottom_width,
    )
    rectangle = geometry.Rectangle(top_edge, bottom_edge, top_width)

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


class TestTrapazoidTriangle(unittest.TestCase):
    top_edge = 0.0
    bottom_edge = 10.0
    top_width = 10.0
    bottom_width = 0.0
    height = bottom_edge - top_edge

    trapazoid = geometry.Trapazoid(
        top_edge=top_edge,
        bottom_edge=bottom_edge,
        top_width=top_width,
        bottom_width=bottom_width,
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
        point = 5.0
        width_at_point = 0.5 * (self.top_width + self.bottom_width)
        trapazoids = [
            geometry.Trapazoid(self.top_edge, point, self.top_width, width_at_point),
            geometry.Trapazoid(
                point, self.bottom_edge, width_at_point, self.bottom_width
            ),
        ]
        self.assertListEqual(self.trapazoid.split([point]), trapazoids)


if __name__ == "__main__":
    unittest.main()
