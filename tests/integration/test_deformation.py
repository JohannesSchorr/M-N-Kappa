import unittest

from m_n_kappa import material, geometry, deformation, points

# Concrete section
concrete = material.Concrete(f_cm=30)
concrete_rectangle = geometry.Rectangle(top_edge=0.0, bottom_edge=20, width=10)
concrete_section = concrete + concrete_rectangle

# Steel section
steel = material.Steel(f_y=355, epsilon_u=0.2)
steel_rectangle = geometry.Rectangle(top_edge=20, bottom_edge=30, width=10)
steel_section = steel + steel_rectangle

# Crosssection
cs = concrete_section + steel_section

beam_length = 10000
element_number = 10
load = 15

# compute M-Kappa curves along the beam
m_kappa_curves = deformation.MKappaCurvesAlongBeam(
    crosssection=cs, beam_length=beam_length
)

# compute Beam-Curvatures
beam_curvatures = deformation.BeamCurvatures(m_kappa_curves.m_kappa_curves, beam_length)


class TestMKappaCurvesAlongBeam(unittest.TestCase):
    def test_crosssection(self):
        self.assertEqual(m_kappa_curves.crosssection, cs)

    def test_beam_length(self):
        self.assertEqual(m_kappa_curves.beam_length, beam_length)

    def test_loading_type(self):
        self.assertEqual(m_kappa_curves.loading_type, "uniform")

    def test_m_kappa_curves(self):
        self.assertEqual(type(m_kappa_curves.m_kappa_curves), list)

    def test_m_kappa_curves_2(self):
        for index in range(len(m_kappa_curves.m_kappa_curves)):
            self.assertEqual(
                type(m_kappa_curves.m_kappa_curves[index]["position"]), float
            )

    def test_m_kappa_curves_3(self):
        for index in range(len(m_kappa_curves.m_kappa_curves)):
            self.assertEqual(
                type(m_kappa_curves.m_kappa_curves[index]["curve"]),
                points.MKappaCurvePoints,
            )

    def test_elements(self):
        self.assertEqual(m_kappa_curves.elements, element_number)

    def test_element_length(self):
        self.assertEqual(m_kappa_curves.element_length, beam_length / element_number)

    def test_positions(self):
        self.assertEqual(
            m_kappa_curves.positions(),
            [
                number * beam_length / element_number
                for number in range(1, element_number)
            ],
        )


class TestBeamCurvatures(unittest.TestCase):
    def test_beam_length(self):
        self.assertEqual(beam_curvatures.beam_length, beam_length)

    def test_moment(self):
        self.assertEqual(
            beam_curvatures._moment(0.5 * beam_length, load),
            load * beam_length ** (2.0) * 0.125,
        )

    def test_m_kappa_curve(self):
        self.assertEqual(
            type(beam_curvatures._m_kappa_curve(0.5 * beam_length)),
            points.MKappaCurvePoints,
        )

    def test_compute(self):
        self.assertEqual(list(beam_curvatures.compute(10)), list)


if __name__ == "__main__":
    unittest.main()
