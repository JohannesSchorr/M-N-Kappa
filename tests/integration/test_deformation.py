import unittest
import os
import sys
sys.path.append(os.path.realpath('..'))
from m_n_kappa import material, geometry, deformation

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


class TestMKappaCurvesAlongBeam(unittest.TestCase): 
	
	pass 
	
	
if __name__ == '__main__': 
	unittest.main()
