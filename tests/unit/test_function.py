import unittest
import os
import sys
sys.path.append(os.path.realpath('..'))
from m_n_kappa import function

data = [
	[0, 2], 
	[-5, -3],
	[4, 1]]
	

class TestLinear(unittest.TestCase): 
	
	func = function.Linear(data, variable=0, target=1)
	print(func)
	
	def test_intersection(self): 
		self.assertEqual(self.func.intersection, 2.0)
		
	def test_slope(self): 
		self.assertEqual(self.func.slope, 1.0)
		
	def test_derivate(self): 
		self.assertEqual(self.func.derivate(None), 1.0)


class TestPolynominal(unittest.TestCase): 
	
	func = function.Polynominal(data, variable=0, target=1)
	
	def test_a(self): 
		self.assertAlmostEqual(self.func.a, -0.13888, places=5)
	
if __name__ == '__main__': 
	unittest.main()
