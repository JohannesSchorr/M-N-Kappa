from unittest import TestCase, main

from m_n_kappa.material import Steel, Concrete
from m_n_kappa.geometry import Rectangle
from m_n_kappa.crosssection import Crosssection
from m_n_kappa.shearconnector import HeadedStud
from m_n_kappa.node import Node, CompositeNode


class TestNodeSingleSection(TestCase):
    def setUp(self):
        self.steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle = Rectangle(0.0, 10.0, 10.0)
        self.section = self.steel + self.rectangle
        self.cross_section = Crosssection([self.section])
        self.position = 10.0
        self.node = Node(self.cross_section, position=self.position)

    def test_curvature_by(self):
        self.assertEqual(self.node.curvature_by(moment=100.0), 5.712685740878339e-07)


class TestNodeCompositeSection(TestCase):
    def setUp(self) -> None:
        self.concrete = Concrete(f_cm=35.0)
        self.concrete_geometry_1 = Rectangle(top_edge=0.0, bottom_edge=10.0, width=20.0)
        self.concrete_section_1 = self.concrete + self.concrete_geometry_1
        self.steel = Steel(f_y=355.0)
        self.steel_geometry = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.steel_section = self.steel + self.steel_geometry
        self.cross_section = self.concrete_section_1 + self.steel_section
        self.position = 10.0
        self.node = Node(self.cross_section, position=self.position)

    def test_curvature_by(self):
        self.assertEqual(self.node.curvature_by(moment=100.0), 1.4443096916449083e-07)


class TestCompositeNodeWithSingleShearConnector(TestCase):
    def setUp(self) -> None:
        self.concrete = Concrete(f_cm=35.0)
        self.concrete_geometry_1 = Rectangle(top_edge=0.0, bottom_edge=10.0, width=20.0)
        self.concrete_section_1 = self.concrete + self.concrete_geometry_1
        self.steel = Steel(f_y=355.0)
        self.steel_geometry = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.steel_section = self.steel + self.steel_geometry
        self.cross_section = self.concrete_section_1 + self.steel_section
        self.position = 10.0
        self.shear_connector = HeadedStud(19, 100, 450, 30, position=10)
        self.node = CompositeNode(
            self.cross_section,
            shear_connectors=self.shear_connector,
            position=self.position,
        )

    def test_shear_connector(self):
        self.assertEqual(self.node.shear_connectors, [self.shear_connector])

    def test_shear_force(self):
        self.assertEqual(self.node.shear_force(3.0), 127726.3125)

    def test_shear_force_negative_slip(self):
        self.assertEqual(self.node.shear_force(-3.0), -127726.3125)
        
    def test_curvature_by(self):
        self.assertEqual(
            self.node.curvature_by(moment=100, axial_force=0.0), 1.4443096916449083e-07
        )


class TestCompositeNodeWithMultipleShearConnectors(TestCase):
    def setUp(self) -> None:
        self.concrete = Concrete(f_cm=35.0)
        self.concrete_geometry_1 = Rectangle(top_edge=0.0, bottom_edge=10.0, width=20.0)
        self.concrete_section_1 = self.concrete + self.concrete_geometry_1
        self.steel = Steel(f_y=355.0)
        self.steel_geometry = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.steel_section = self.steel + self.steel_geometry
        self.cross_section = self.concrete_section_1 + self.steel_section
        self.position = 10.0
        self.shear_connectors = [HeadedStud(19, 100, 450, 30, position=10)] * 2
        self.node = CompositeNode(
            self.cross_section,
            shear_connectors=self.shear_connectors,
            position=self.position,
        )

    def test_shear_connector(self):
        self.assertEqual(self.node.shear_connectors, self.shear_connectors)

    def test_shear_force(self):
        self.assertEqual(self.node.shear_force(3.0), 2 * 127726.3125)

    def test_shear_force_negative_slip(self):
        self.assertEqual(self.node.shear_force(-3.0), (-2) * 127726.3125)


class TestCompositeNodeWithoutShearConnector(TestCase):
    def setUp(self) -> None:
        self.concrete = Concrete(f_cm=35.0)
        self.concrete_geometry_1 = Rectangle(top_edge=0.0, bottom_edge=10.0, width=20.0)
        self.concrete_section_1 = self.concrete + self.concrete_geometry_1
        self.steel = Steel(f_y=355.0)
        self.steel_geometry = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.steel_section = self.steel + self.steel_geometry
        self.cross_section = self.concrete_section_1 + self.steel_section
        self.position = 10.0
        self.node = CompositeNode(
            self.cross_section,
            position=self.position,
        )

    def test_shear_connector(self):
        self.assertEqual(self.node.shear_connectors, [])

    def test_shear_force(self):
        self.assertEqual(self.node.shear_force(3.0), 0.0)

    def test_shear_force_negative_slip(self):
        self.assertEqual(self.node.shear_force(-3.0), 0.0)


if __name__ == "__main__":
    main()
