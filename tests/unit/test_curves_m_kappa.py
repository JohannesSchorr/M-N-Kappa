from unittest import TestCase, main

from m_n_kappa.curves_m_n_kappa import MCurvatureCurve
from m_n_kappa import (
    Steel,
    Rectangle,
    Crosssection,
)


class TestMKappaCurve(TestCase): 
    
    def setUp(self) -> None:
        self.steel_top = Steel(f_y=355, f_u=400, failure_strain=0.15)
        self.rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        self.section_top = self.steel_top + self.rectangle_top
        self.cross_section_top = Crosssection([self.section_top])
        self.steel_bottom = Steel(f_y=235, f_u=300, failure_strain=0.1)
        self.rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        self.section_bottom = self.steel_bottom + self.rectangle_bottom
        self.cross_section_bottom = Crosssection([self.section_bottom])
        self.cross_sections = [self.cross_section_top, self.cross_section_bottom]
        self.positive_moments = [78372.81572891976, 109389.16919138256, 163189.90797100778]
        self.negative_moments = [-163189.90797098214, -109389.1691913825, -78304.57731215179, -78372.81572891944]
        self.positive_curvatures = [0, 0.0003381331618285197, 0.02, 0.00022382166415797533]
        self.negative_curvatures = [0, -0.0002238216641579755, -0.0002238216641579754, -0.02, -0.0003381331618285197]
        
    def test_points_positive_curvature(self):
        m_kappa_curve = MCurvatureCurve(self.cross_sections, positive_curvature=True)
        self.assertCountEqual(m_kappa_curve.points.moments, self.positive_moments)

    def test_points_negative_curvature(self):
        m_kappa_curve = MCurvatureCurve(self.cross_sections, positive_curvature=False)
        self.assertCountEqual(m_kappa_curve.points.moments, self.negative_moments)
   
    def test_positive_curvatures(self):
        m_kappa_curve = MCurvatureCurve(self.cross_sections, positive_curvature=True)
        self.assertCountEqual(m_kappa_curve.curvatures, self.positive_curvatures)
        
    def test_negative_curvatures(self):
        m_kappa_curve = MCurvatureCurve(self.cross_sections, positive_curvature=False)
        self.assertCountEqual(m_kappa_curve.curvatures, self.negative_curvatures)


if __name__ == "__main__":
    main()