import unittest
import os
import sys
sys.path.append(os.path.realpath('..'))
from m_n_kappa import internalforces


class TestSingleSpanUniformLoad(unittest.TestCase): 
	
	beam_length = 10.
	load = 20.
	forces = internalforces.SingleSpan(length=beam_length, uniform_load=load)
	
	def test_moment(self): 
		self.assertEqual(self.forces.moment(0.5*self.beam_length), self.load*self.beam_length**(2.)/8.)
		
	def test_maximum_moment(self): 
		self.assertEqual(self.forces.maximum_moment, self.load*self.beam_length**(2.)/8.)
			
	def test_transversal_shear_1(self): 
		self.assertEqual(self.forces.transversal_shear(0.5*self.beam_length), 0.)
		
	def test_transversal_shear_2(self): 
		self.assertEqual(self.forces.transversal_shear(0.), 0.5*self.load*self.beam_length)
		
	def test_transversal_shear_3(self): 
		self.assertEqual(self.forces.transversal_shear(self.beam_length), -0.5*self.load*self.beam_length)	
		
	def test_transversal_shear_support_left(self): 
		self.assertEqual(self.forces.transversal_shear_support_left, 0.5*self.load*self.beam_length)
	
	def test_transversal_shear_support_right(self): 
		self.assertEqual(self.forces.transversal_shear_support_right, -0.5*self.load*self.beam_length)
	
	def test_length(self): 
		self.assertEqual(self.forces.length, self.beam_length)
		
	def test_load(self): 
		self.assertEqual(self.forces.loading, self.load*self.beam_length)



class TestSingleSpanSingleLoad(unittest.TestCase): 
	
	beam_length = 10.
	load = 10.
	forces = internalforces.SingleSpan(length=beam_length, loads=[[0.5*beam_length, load]])
	
	def test_transversal_shear_support_left(self): 
		self.assertEqual(self.forces.transversal_shear_support_left, 0.5*self.load)
	
	def test_transversal_shear_support_right(self): 
		self.assertEqual(self.forces.transversal_shear_support_right, -0.5*self.load)
	
	def test_length(self): 
		self.assertEqual(self.forces.length, self.beam_length)
		
	def test_load(self): 
		self.assertEqual(self.forces.loading, self.load)
		
	def test_maximum_moment(self): 
		self.assertEqual(self.forces.maximum_moment, 0.5*self.load*0.5*self.beam_length)
		
	def test_moment(self): 
		self.assertEqual(self.forces.moment(0.5*self.beam_length), 0.5*self.load*0.5*self.beam_length)


if __name__ == '__main__': 
	unittest.main()
