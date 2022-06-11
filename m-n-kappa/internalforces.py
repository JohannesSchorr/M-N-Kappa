import abc 
from . import general

"""
Internal Forces
###############

Provides classes to compute the internal forces of a beam under a specific load

Systems available
-----------------
  - Single Beam
    
    - Single load
    - line load / Uniform load 
   
To Do
-----
  - Multi-span beams
"""

class ABCBeam(abc.ABC): 
	
	@abc.abstractproperty	
	def loading(self): 
		... 

	@abc.abstractmethod
	def moment(self, at_position): 
		... 

	@abc.abstractmethod
	def transversal_shear(self, at_position): 
		...

		
class ABCSingleSpan(abc.ABC):
	
	@abc.abstractproperty	
	def loading(self): 
		... 

	@abc.abstractmethod
	def moment(self, at_position): 
		... 

	@abc.abstractmethod
	def transversal_shear(self, at_position): 
		...
	
	@abc.abstractproperty
	def transversal_shear_support_left(self): 
		...
		
	@abc.abstractproperty	
	def transversal_shear_support_right(self): 
		...
	

class SingleSpan(ABCSingleSpan): 
	
	__slots__ = '_length', '_uniform_load', '_loads', '_beam'
	
	def __init__(self, length:list, loads:list=None, uniform_load:float=None): 
		self._length = length
		self._uniform_load = uniform_load
		self._loads = loads
		self._beam = self.__get_beam_class()	
	
	def __str__(self): 
		return self.beam.__str__()
	
	@property
	def beam(self): 
		return self._beam
		
	@property
	def length(self): 
		return self._length
		
	@property	
	def loading(self): 
		return self.beam.loading
		
	@property
	def maximum_moment(self): 
		return self.beam.maximum_moment
		
	@property
	def transversal_shear_support_left(self): 
		return self.beam.transversal_shear_support_left
			
	@property	
	def transversal_shear_support_right(self): 
		return self.beam.transversal_shear_support_right
		
	def moment(self, at_position): 
		return self.beam.moment(at_position)

	def transversal_shear(self, at_position): 
		return self.beam.transversal_shear(at_position)
		
	def _is_uniform_load(self): 
		if self._uniform_load is not None: 
			return True
		else: 
			return False
			
	def _is_single_loads(self): 
		if self._loads is not None: 
			return True
		else: 
			return False
			
	def __get_beam_class(self): 
		if self._is_uniform_load(): 
			return SingleSpanUniformLoad(self.length, self._uniform_load)
		elif self._is_single_loads(): 
			return SingleSpanSingleLoads(self.length, self._loads)
		else: 
			raise ValueError()
	
		
class SingleSpanSingleLoads(ABCSingleSpan): 
	
	__slots__ = '_length', '_loads'
	
	def __init__(self, length:float, loads:list):
		self._length = length
		self._loads = loads
	
	@general.str_start_end
	def __str__(self): 
		text = [
			'Single span with single loads', '-----------------------------', '', 
			'Properties', '----------', 
			f'length = {self.length}', 
			f'loads = {self.loads} | loading = {self.loading}',
			f'transversal shear: column left = {self.transversal_shear_support_left} | column right = {self.transversal_shear_support_right}', 
			f'Maximum Moment = {self.maximum_moment}'
			]
		return '\n'.join(text)
		
	@property
	def length(self): 
		return self._length
		
	@property
	def loads(self) -> list: 
		return self._loads
	
	@property
	def maximum_moment(self): 
		return self._maximum_moment()
	
	@property
	def transversal_shear_support_left(self): 
		return self._loading()+self._column_right()
			
	@property	
	def transversal_shear_support_right(self): 
		return self._column_right()
	
	@property 			
	def loading(self): 
		return self._loading() 
	
	def moment(self, at_position): 
		return self._moment(at_position)
		
	def transversal_shear(self, at_position): 
		return self._transversal_shear(at_position)
	
	def _column_right(self): 
		return (-1) * self._transversal_load() / self.length
		
	def _transversal_load(self): 
		return sum([load[0]*load[1] for load in self.loads])
		
	def _loading(self): 
		return sum(self._single_loads())
		
	def _moment(self, at_position:float): 
		moment = self.transversal_shear_support_left * at_position
		for load in self.loads: 
			if load[0] < at_position: 
				moment-=self.moment_by(load)
		return moment
		
	def moment_by(self, load:list, at_position:float): 
		return (at_position-load[0])*load[1]
		
	def _moments(self): 
		return [[load[0], self._moment(load[0])] for load in self.loads]
	
	def _maximum_moment(self): 
		moments = self._moments()
		moments.sort(key=lambda x: x[1], reverse=True)
		return moments[0][1]
		
	def _single_loads(self) -> list: 
		return [load[1] for load in self.loads] 
		
	def _transversal_shear(self, at_position): 
		shear = self.transversal_shear_support_left
		for load in self._single_loads(): 
			if load[0] < at_position: 
				shear -= load[1]
		return shear
	
	
class SingleSpanUniformLoad(ABCSingleSpan): 
	
	def __init__(self, length:float, load:float): 
		self._length = length
		self._load = load
	
	@general.str_start_end
	def __str__(self): 
		text = [
			'Single span with uniform load', '-----------------------------', '', 
			'Properties', '----------', 
			f'length = {self.length}', 
			f'load = {self.load} | loading = {self.loading}',
			f'transversal shear: column left = {self.transversal_shear_support_left} | column right = {self.transversal_shear_support_right}', 
			f'Maximum Moment = {self.maximum_moment}'
			]
		return '\n'.join(text)
	
	@property
	def length(self): 
		return self._length
	
	@property
	def load(self): 
		return self._load
	
	@property
	def loading(self): 
		return self._loading() 
	
	@property
	def maximum_moment(self): 
		return self._maximum_moment()
	
	@property
	def transversal_shear_support_left(self): 
		return self._support_transversal_shear()
			
	@property	
	def transversal_shear_support_right(self): 
		return (-1) * self._support_transversal_shear()
	
	def moment(self, at_position:float): 
		return self._moment(at_position)
		
	def transversal_shear(self, at_position:float): 
		return self._transversal_shear(at_position)
	
	def load_by_moment(self, maximum_moment) -> float:
		"""compute load by given maximum moment""" 
		return maximum_moment * 8. / (self.length**(2.))
	
	def position_of_maximum_moment(self) -> float:
		"""position where the moment is the maximum"""
		return 0.5 * self.length
		
	def _support_transversal_shear(self): 
		return 0.5*self.loading
	
	def _loading(self): 
		return self.length * self.load
	
	def _moment(self, at_position:float): 
		return (
			self._support_transversal_shear()*at_position -
			0.5*self.load*at_position**(2.))
			
	def _maximum_moment(self): 
		return self.load * self.length ** (2.) / 8.
	
	def _transversal_shear(self, at_position): 
		return self._support_transversal_shear()-self.load*at_position
		
		
if __name__ == '__main__': 
	
	#beam = SingleSpanUniformLoad(10.0, 3.0)
	#print(beam)
	
	#beam = SingleSpanSingleLoads(10.0, [[5.0, 10.0], [7.0, 10.0]])
	#print(beam)
	
	beam = SingleSpan(length=10.0, loads=[[5.0, 10.0], [7.0, 10.0]])
	print(beam)
	
