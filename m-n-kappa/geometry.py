import abc
from . import general
from . import material
from . import section

"""
Geometries
##########

Basic geometries providing parameters like area, centroid, etc.

Currently available
-------------------
  - Rectangle
  - Circle 
  - Trapazoidal
"""

class Geometry(abc.ABC): 
	
	""" basic geometry class """
	
	def __add__(self, other:material.Material): 
		return self._build_section(other)
		
	def __radd__(self, other:material.Material): 
		return self._build_section(other)
		
	def _build_section(self, other:material.Material): 
		if isinstance(other, material.Material): 
			return section.Section(geometry=self, material=other)
		else: 
			raise TypeError(f'unsupported operand type(s) for +: "{type(self)}" and "{type(other)}"')	
	
	@abc.abstractmethod	
	def area(self): 
		...
		
	@abc.abstractmethod		
	def centroid(self): 
		...
	
	#@abc.abstractmethod
	#def width(self): 
	#	...
		
	@abc.abstractmethod
	def split(self, at_points): 
		...
	
	@abc.abstractmethod
	def edges(self): 
		...


class Rectangle(Geometry): 
	""" 
	Represents a rectangle
	"""
	def __init__(self, top_edge : float, bottom_edge : float, width : float): 
		self._top_edge = top_edge
		self._bottom_edge = bottom_edge
		self._width = width
	
	def __eq__(self, other): 
		return self.top_edge == other.top_edge and self.bottom_edge == other.bottom_edge and self.width == other.width
		
	def __repr__(self):
	    return f'Rectangle(top_edge={self.top_edge}, bottom_edge={self.bottom_edge}, width={self.width})'
	
	@general.str_start_end
	def __str__(self):
		text = [
			'Rectangle', '=========', '',
			'Initialization', '--------------', self.__repr__(), '',
			'Properties','----------',
			'Area: {:.2f}'.format(self.area),
			'Centroid: {:.2f}'.format(self.centroid)
			]
		return '\n'.join(text)
	    
	@property
	def top_edge(self): 
		return self._top_edge
	
	@property	
	def bottom_edge(self): 
		return self._bottom_edge	
	
	@property
	def edges(self): 
		return [self.top_edge, self.bottom_edge]
		
	@property
	def height(self): 
		return abs(self.top_edge - self.bottom_edge)
		
	@property
	def width(self): 
		return self._width
		
	@property
	def area(self): 
		return self.width * self.height
		
	@property
	def centroid(self): 
		return self.top_edge + 0.5 * self.height
	
	@property
	def width_slope(self) -> float: 
		return 0.0
		
	@property 
	def width_interception(self) -> float: 
		return self.width
	
	def split(self, at_points : list) -> list: 
		top_edge = self.top_edge
		rectangles = []
		at_points.sort()
		for point in at_points:
			if self.top_edge < point < self.bottom_edge: 
				rectangles.append(Rectangle(top_edge, point, self.width))
				top_edge = point 
		rectangles.append(Rectangle(top_edge, self.bottom_edge, self.width))
		return rectangles
	
	
class Circle(Geometry): 
	""" 
	Represents a circle
	"""
	def __init__(self, diameter : float, centroid : float):
		self._diameter = diameter
		self._centroid = centroid
	
	def __eq__(self, other) -> bool: 
		return self.diameter == other.diameter and self.centroid == other.centroid
		
	def __repr__(self):
		return f'Circle(diameter={self.diameter}, centroid={self.centroid})'	
	
	@general.str_start_end
	def __str__(self):
		text = [
			'Circle', '======', '',
			'Initialization', '--------------', self.__repr__(), '',
			'Properties','----------',
			'Area: {:.2f}'.format(self.area),
			'Centroid {:.2f}'.format(self.centroid)
			]
		return '\n'.join(text)
	
	@property
	def diameter(self): 
		return self._diameter
		
	@property
	def centroid(self): 
		return self._centroid
		
	@property
	def area(self): 
		return 3.145 * (0.5 * self.diameter)**(2.0)
	
	def split(self, at_points : list) -> list:
		return [self]#[Circle(self.diameter, self.centroid)]
	
	@property 
	def edges(self) -> list: 
		return [self.centroid]
		
	@property
	def height(self) -> float: 
		return 0.0

				
class Trapazoid(Geometry):  
	""" 
	Represents a trapazoidal
	"""
	
	def __init__(self, top_edge : float, bottom_edge : float, top_width : float, bottom_width : float): 
		self._top_edge = top_edge
		self._bottom_edge = bottom_edge
		self._top_width = top_width
		self._bottom_width = bottom_width
		
	def __repr__(self):
		return f'Trapazoid(top_edge={self.top_edge}, bottom_edge={self.bottom_edge}, top_width={self.top_width}, bottom_width={self.bottom_width})'
	
	@general.str_start_end
	def __str__(self):
		text = [
			'Trapazoid', '=========', '',
			'Initialization', '--------------', self.__repr__(), '',
			'Properties','----------',
			'Area: {:.2f}'.format(self.area),
			'Centroid: {:.2f}'.format(self.centroid),
			]
		return general.print_sections(text)

	def __eq__(self, other): 
		return (
			self.top_edge == other.top_edge and 
			self.bottom_edge == other.bottom_edge and 
			self.top_width == other.top_width and 
			self.bottom_width == other.bottom_width)
	
	@property
	def top_edge(self): 
		return self._top_edge
			
	@property
	def bottom_edge(self): 
		return self._bottom_edge
	
	@property 
	def edges(self) -> list: 
		return [self.top_edge, self.bottom_edge]
		
	@property
	def top_width(self):
		return self._top_width
			
	@property
	def bottom_width(self): 
		return self._bottom_width
			
	@property
	def height(self): 
		return abs(self.top_edge - self.bottom_edge)
				
	@property
	def area(self): 
		return 0.5 * self.height * (self.top_width + self.bottom_width)
			
	@property
	def centroid(self): 
		return self.top_edge + self.height - (1. / 3. * self.height * ((self.bottom_width + 2. * self.top_width) / (self.bottom_width + self.top_width)))
		
	def width(self, vertical_position : float):
		if self.top_edge <= vertical_position <= self.bottom_edge: 
			return self.top_width + (vertical_position - self.top_edge) * (self.bottom_width - self.top_width) / (self.bottom_edge - self.top_edge)
		else: 
			return 0.0
			
	def split(self, at_points : list) -> list: 
		top_edge = self.top_edge
		trapazoids = []
		at_points.sort()
		for point in at_points:
			if self.top_edge < point < self.bottom_edge: 
				trapazoids.append(Trapazoid(top_edge, point, self.width(top_edge), self.width(point)))
				top_edge = point 
		trapazoids.append(Trapazoid(top_edge, self.bottom_edge, self.width(top_edge), self.bottom_width))
		return trapazoids

	@property 	
	def width_slope(self) -> float: 
		return (self.bottom_width - self.top_width) / self.height	
	
	@property
	def width_interception(self) -> float: 
		return self.top_width - self.top_edge * self.width_slope
