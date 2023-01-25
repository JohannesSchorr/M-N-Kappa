from m_n_kappa.material import Concrete, Steel
from m_n_kappa.geometry import Rectangle
from m_n_kappa.deformation import Beam
from m_n_kappa.loading import SingleSpanUniformLoad

from unittest import TestCase, main

# Concrete section
concrete = Concrete(f_cm=30)
concrete_rectangle = Rectangle(top_edge=0.0, bottom_edge=20, width=10)
concrete_section = concrete + concrete_rectangle

# Steel section
steel = Steel(f_y=355, failure_strain=0.2)
steel_rectangle = Rectangle(top_edge=20, bottom_edge=30, width=10)
steel_section = steel + steel_rectangle

# cross-section
cs = concrete_section + steel_section

beam_length = 100
element_number = 10
load = 0.0001

loading = SingleSpanUniformLoad(beam_length, load)


class TestBeam(TestCase):
    def setUp(self):
        self.beam = Beam(
            cross_section=cs,
            element_number=element_number,
            load=loading)

    def test_deformation(self):
        print(self.beam.deformation(0.5 * beam_length, loading))


if __name__ == "__main__":
    main()
