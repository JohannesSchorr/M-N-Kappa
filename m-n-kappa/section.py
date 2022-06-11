
import abc
import time 

from . import general
from . import geometry
from . import material


class Section: 

	"""
	Combines material and geometric entity
	"""
	def __init__(self, geometry, material):
		"""
		Initialize
		
		Parameters
		----------
		geometry 
			geometry of the section
		material
			material of the section 
		"""
		self._geometry = geometry
		self._material = material 
		
	def __repr__(self): 
		return f'Section(geometry={self.geometry.__repr__()}, material={self.material.__repr__()})'
	
	def __add__(self, other): 
		return self._build_crosssection(other)
	
	def __radd__(self, other): 
		return self._build_crosssection(other)
			
	def _build_crosssection(self, other): 
		if isinstance(other, Section): 
			sections = [self, other]
			return Crosssection(sections)
		elif isinstance(other, Crosssection): 
			sections = other.sections + [self]
			return Crosssection(sections)
		else: 
			raise TypeError(f'unsupported operand type(s) for +: "{type(self)}" and "{type(other)}"')
	
	def __eq__(self, other): 
		return self._material == other._material and self._geometry == other._geometry
					
	@general.str_start_end	
	def __str__(self): 
		text = [
			self._print_title(),  
			self._print_initialization(), 
			self._print_geometry(),  
			self._print_material()]
		return general.print_chapter(text)
	
	def _print_title(self) -> str: 
		return general.print_sections([self.__class__.__name__, len(self.__class__.__name__)*'='])
	
	def _print_initialization(self) -> str: 
		return general.print_sections(['Initialization', len('Initialization')*'-', self.__repr__()])
	
	def _print_geometry(self) -> str: 
		return general.print_sections(['Geometry', '--------', self.geometry.__repr__()])
	
	def _print_material(self) -> str:  
		return general.print_sections(['Material', '--------', self.material.__repr__()])
		
	@property
	def section_type(self) -> str: 
		return self.material.section_type
	
	@property 
	def material(self): 
		return self._material
		
	@property 
	def geometry(self): 
		return self._geometry
	
	@property
	def top_edge_maximum_strain(self) -> list: 
		return [self.geometry.top_edge, self.material.maximum_strain]
		
	@property
	def top_edge_minimum_strain(self) -> list: 
		return [self.geometry.top_edge, self.material.minimum_strain]

	@property
	def bottom_edge_maximum_strain(self) -> list: 
		return [self.geometry.bottom_edge, self.material.maximum_strain]
		
	@property
	def bottom_edge_minimum_strain(self) -> list: 
		return [self.geometry.bottom_edge, self.material.minimum_strain]
	
	def maximum_positive_strain(self) -> float: 
		return self.material.maximum_strain
		
	def maximum_negative_strain(self) -> float: 
		return self.material.minimum_strain

	def material_strains(self) -> list: 
		return self.material.strains
	
	def section_strains(self) -> list: 
		return [{'section-type': self.section_type, 'strain':strain} for strain in self.material_strains()]

		
class ComputationSection(Section): 
	
	__slots__ = '_geometry', '_material'
	
	@property
	def geometry(self): 
		return self.section.geometry
	
	@property
	def material(self): 
		return self.section.material
		
	@property
	def edges_strain(self) -> list:  
		return self._edges_strain
		
	@property
	def edges_stress(self) -> list: 
		return self._edges_stress
	
	@property
	def material(self): 
		return self._section.material
		
	@property
	def geometry(self): 
		return self._section.geometry
	
	@property
	def axial_force(self) -> float: 
		return self._axial_force	
		
	@property 
	def section(self): 
		return self._section
		
	@property
	def stress_slope(self) -> float: 
		return self._stress_slope
		
	@property
	def stress_interception(self) -> float: 
		return self._stress_interception
	
	def lever_arm(self) -> float: 
		if self.axial_force == 0.0: 
			return 0.0
		else:
			return self._lever_arm_numerator() / self.axial_force
	
	def moment(self) -> float: 
		return self.axial_force * self.lever_arm()
		
	def _axial_force_integrated(self): 
		force = self._axial_force_integrated_at_position(position=self.geometry.edges[1])
		force -= self._axial_force_integrated_at_position(position=self.geometry.edges[0])
		return force
		
	def _compute_stress_slope(self) -> float: 
		pass
	
	def _compute_stress_interception(self) -> float: 
		return self.edges_stress[0] - self.geometry.top_edge * self.stress_slope
	
	def _compute_axial_force(self) -> float: 
		if len(self.geometry.edges) > 1: 
			return self._axial_force_integrated()
		else: 
			return self.geometry.area * self.edges_stress[0]
	
	def _get_edges_strain(self) -> list: 
		pass 
		
	def _get_edges_stress(self) -> list: 
		return [self._material_stress(strain) for strain in self.edges_strain]
		
	def _axial_force_integrated_at_position(self, position) -> float: 
		return (
			(1. / 3.) * self.geometry.width_slope * self.stress_slope * position ** (3.) + 
			(1. / 2.) * (self.stress_interception * self.geometry.width_slope + self.geometry.width_interception * self.stress_slope) * position ** (2.) + 
			self.geometry.width_interception * self.stress_interception * position)
	
	def _lever_arm_integrated_at_position(self, position : float): 
		return (
			(1. / 4.) * self.geometry.width_slope * self.stress_slope * position ** (4.) + 
			(1. / 3.) * (self.stress_interception * self.geometry.width_slope + self.geometry.width_interception * self.stress_slope) * position ** (3.) + 
			(1. / 2.) * self.geometry.width_interception * self.stress_interception * position ** (2.))
	
	def _lever_arm_numerator(self): 
		if len(self.geometry.edges) > 1: 
			return self._lever_arm_numerator_rectangle()
		else: 
			return self.geometry.centroid
		
	def _lever_arm_numerator_rectangle(self): 
		lever_arm = self._lever_arm_integrated_at_position(position=self.geometry.edges[1])
		lever_arm -= self._lever_arm_integrated_at_position(position=self.geometry.edges[0])
		return lever_arm
		
	def _material_stress(self, strain) -> float: 
		return self.material.get_material_stress(round(strain, 7))	
		
	def _print_results(self) -> str: 
		text = [
			'Results', '-------',
			'axial force: ' + 'N = {:10.1f} N'.format(self.axial_force), 
			'lever arm:   ' + 'z = {:10.1f} mm'.format(self.lever_arm()), 
			'moment:      ' + 'M = {:10.1f} Nmm'.format(self.moment())]
		return general.print_sections(text)
		
	
class ComputationSectionStrain(ComputationSection): 
	
	""" compute section  under a constant strain """
	
	__slots__ = '_section', '_strain', '_edges_strain', '_edges_stress', '_stress_slope', '_stress_interception', '_axial_force'
	
	def __init__(self, section:Section, strain:float): 
		"""
		Initialize 
				
		Parameters
		----------
		section : Section
			section to compute
		strain : float
			given strain to compute
		"""
		self._section = section
		self._strain = strain
		self._edges_strain = self._get_edges_strain()
		self._edges_stress = self._get_edges_stress()
		self._stress_slope = 0.0
		self._stress_interception = self._compute_stress_interception()
		self._axial_force = self._compute_axial_force()
	
	def __repr__(self): 
		return f'ComputationSectionStrain(section={self.section.__repr__()}, strain={self.strain})'
		
	@general.str_start_end
	def __str__(self): 
		text = [
			self._print_title(), 
			self._print_initialization(), 
			self._print_geometry(), 
			self._print_results()]
		return general.print_chapter(text)
		
	@property
	def strain(self) -> float: 
		return self._strain
	
	def _get_edges_strain(self) -> list: 
		return [self.strain for _ in self.section.geometry.edges]
	
	def _print_result(self) -> str: 
		return ' {:8.2f} | {:8.2f} | {:10.6f} | {:8.2f} | {:10.2f} | {:7} | {}'.format(self.geometry.top_edge, self.geometry.bottom_edge, self.strain, self.edges_stress[0], self.axial_force, self.section_type, self.material.__class__.__name__)
		
		
class ComputationSectionCurvature(ComputationSection): 
	
	""" compute section given a curvature and a neutral axis """
	
	__slots__ = '_section', '_curvature', '_neutral_axis', '_edges_strain', '_edges_stress', '_stress_slope', '_stress_interception', '_axial_force'
	
	def __init__(self, section:Section, curvature:float, neutral_axis:float): 
		"""
		Initialize
		
		Parameters
		----------
		section : Section 
			section to compute
		curvature : float 
			curvature to apply to the section 
		neutral axis : float 
			point where the strain is zero
		"""
		self._section = section
		self._curvature = curvature
		self._neutral_axis = neutral_axis
		self.__sort_material_strains_by_curvature()
		self._edges_strain = self._get_edges_strain()
		self._edges_stress = self._get_edges_stress()
		self._stress_slope = self._compute_stress_slope()
		self._stress_interception = self._compute_stress_interception()
		self._axial_force = self._compute_axial_force()
	
	def __repr__(self): 
		return f'CompuationSectionCurvature(section={self.section.__class__.__name__}, curvature={self.curvature}, neutral_axis={self.neutral_axis})'
	
	@general.str_start_end
	def __str__(self): 
		text = [
			self._print_title(), 
			self._print_initialization(), 
			self._print_geometry(), 
			self._print_material(), 
			self._print_results()]
		return general.print_chapter(text) 
	
	def _print_geometry(self) -> str: 
		text = ['Geometry', '--------', 'type: ' + self.geometry.__class__.__name__]
		if len(self.geometry.edges) > 1: 
			text += [
				'top_edge: {:.1f} | bottom_edge: {:.1f}'.format(self.geometry.edges[0], self.geometry.edges[1]), 
				'width-formula: {:.1f} * position + {:.1f}'.format(self.geometry.width_slope, self.geometry.width_interception), 
				'top_strain: {:.5f} | bottom_strain: {:.5f}'.format(self.edges_strain[0], self.edges_strain[1])]
		else: 
			text += ['area: {:.1f} | centroid: {:.1f}'.format(self.geometry.area, self.geometry.centroid)]
		return general.print_sections(text)
		
	def _print_material(self) -> str: 
		text = ['Material', '--------']
		if len(self.geometry.edges) > 1: 
			text += [
				'top_stress {:.1f} N/mm^2 | bottom_stress {:.1f} N/mm^2'.format(self.edges_stress[0], self.edges_stress[1]), 
				'stress-formula: {:.1f} * position + {:.1f}'.format(self.stress_slope, self.stress_interception)
				]
		else: 
			text += ['stress {:.1f} N/mm^2'.format(self.edges_stress[0])]
		return general.print_sections(text)
		
	@property
	def curvature(self) -> float:
		return self._curvature
		
	@property
	def neutral_axis(self) -> float:
		return self._neutral_axis
			
	@property
	def edges_stress_difference(self): 
		return self.edges_stress[1] - self.edges_stress[0]  
	
	def _print_result(self): 
		return '{:10.2f} | {:10.6f} | {:10.2f} | {:8.2f} | {:10.6f} | {:10.2f} | {:10.2f} | {:7} | {}'.format(self.geometry.top_edge, self.edges_strain[0], self.edges_stress[0], self.geometry.bottom_edge, self.edges_strain[1], self.edges_stress[1], self.axial_force, self.section_type, self.material.__class__.__name__)
		
	def split_section(self) -> list: 
		sub_geometries = self.__get_sub_geometries()
		split_sections = []
		for sub_geometry in sub_geometries: 
			split_sections.append(self.__computation_section(sub_geometry))
		return split_sections
		
	def material_points_inside_curvature(self): 
		strain_position = []
		for strain_index, strain in enumerate(self._edges_strain):
			if strain_index == self.__get_allowed_position_index(strain): 
				for intermediate_strain in self.material.get_intermediate_strains(strain):
					strain_position.append({
						'strain': intermediate_strain, 
						'position': self.geometry.edges[strain_index], 
						'material': self.material.__class__.__name__})
		return strain_position
	
	def __get_allowed_position_index(self, strain:float) -> int: 
		if self.curvature > 0.0: 
			if strain > 0.0: 
				return 1 # bottom_edge
			else: 
				return 0 # top_edge
		else: 
			if strain > 0.0: 
				return 0 # top_edge
			else: 
				return 1 # bottom_edge
		
	def __computation_section(self, geometry): 
		return ComputationSectionCurvature(
				section=self.__sub_section(geometry), 
				curvature=self.curvature, 
				neutral_axis=self.neutral_axis)
	
	def _compute_stress_slope(self) -> float:
		if self.geometry.height == 0.0: 
			return 0.0
		else: 
			return self.edges_stress_difference / self.geometry.height
	
	def _get_edges_strain(self) -> list:
		return [self.__get_strain_by_position(position) for position in self.geometry.edges]
	
	def __get_strain_by_position(self, position:float): 
		return general.strain(neutral_axis=self.neutral_axis, curvature=self.curvature, position=position)
	
	def __get_sub_geometries(self): 
		material_points = self.__material_points_position()
		return self.geometry.split(material_points)
	
	def __sort_material_strains_by_curvature(self) -> None:
		if self.curvature > 0: 
			self.material.sort_strains_ascending()
		else: 
			self.material.sort_strains_descending()
			
	def __sub_section(self, geometry): 
		return Section(geometry, self.material)
	
	def __material_points_position(self) -> list: 
		positions = []
		for stress_strain in self.material.stress_strain: 
			position = self.__compute_position(strain=stress_strain[1])
			positions.append(position)
		return positions
	
	def __compute_position(self, strain:float): 
		return general.position(
				curvature=self.curvature, 
				neutral_axis=self.neutral_axis, 
				strain_at_position=strain)


class Crosssection:

	""" Combines a number of sections """
	
	def __init__(self, sections : list = None): 
		self._sections = sections
		self._top_edge = self.__compute_top_edge()
		self._bottom_edge = self.__compute_bottom_edge()
		
	def __repr__(self): 
		return 'Crosssection(sections=sections)'
	
	def __iter__(self): 
		self._section_iterator = iter(self.sections)
		return self
		
	def __next__(self): 
			return self._section_iterator.__next__()
			
	@general.str_start_end	
	def __str__(self): 
		text = [
			self._print_title(),
			self._print_initialization(),  
			self._print_geometry(), 
			self._print_sections()]
		return general.print_chapter(text)
		
	def _print_title(self) -> str: 
		return general.print_sections([self.__class__.__name__, len(self.__class__.__name__)*'='])
	
	def _print_initialization(self) -> str: 
		return general.print_sections(['Initialization', len('Initialization')*'-', self.__repr__()])
	
	@property
	def bottom_edge(self) -> float: 
		return self._bottom_edge
	
	@property
	def boundary_conditions(self): # -> Boundaries: 
		return self._boundary_conditions
	
	@property		
	def girder_sections(self) -> list: 
		return self.sections_of_type(type='girder')
	
	@property
	def height(self) -> float: 
		return self.bottom_edge - self.top_edge
	
	@property
	def half_point(self) -> float: 
		return 0.5 * (self.bottom_edge + self.top_edge)
		
	@property
	def sections(self) -> list:
		return self._sections

	@property
	def slab_sections(self) -> list: 
		return self.sections_of_type(type='slab')
		
	@property
	def section_type(self) -> str: 
		if len(self.girder_sections) > 0 and len(self.slab_sections) == 0: 
			return 'girder'
		elif len(self.girder_sections) == 0 and len(self.slab_sections) > 0: 
			return 'slab'
		else: 
			return None 
	
	@property
	def top_edge(self) -> float: 
		return self._top_edge
			
	def add_section(self, section : Section):
		if self.sections is None: 
			self._sections = [section]
		else: 
			self._sections.append(section)
			
	def _print_geometry(self): 
		text = [
			'Geometry', '--------', 
			'top_edge: {:.1f} | bottom_edge: {:.1f}'.format(self.top_edge, self.bottom_edge)]
		return general.print_sections(text)
		
	def _print_sections(self): 
		text = ['Sections', '--------',]
		for section in self.sections: 
			text.append(section.__repr__())
		return general.print_sections(text)
	
	def sections_of_type(self, type : str): 
		return [section for section in self.sections if section.section_type == type]
	
	def sections_not_of_type(self, type : str): 
		return [section for section in self.sections if section.section_type != type]
		
	def __compute_top_edge(self): 
		top_edge = min(self.sections[0].geometry.edges)
		for section in self.sections: 
			top_edge = min(top_edge, min(section.geometry.edges))
		return top_edge
		
	def __compute_bottom_edge(self): 
		bottom_edge = max(self.sections[0].geometry.edges)
		for section in self.sections: 
			bottom_edge = max(bottom_edge, max(section.geometry.edges))
		return bottom_edge	
		
	def get_boundary_conditions(self): 
		cross_section_boundaries = CrosssectionBoundaries(self.sections)
		return cross_section_boundaries.get_boundaries()
	
	def maximum_positive_strain(self): 
		return max([section.maximum_positive_strain() for section in self.sections])
		
	def maximum_negative_strain(self): 
		return min([section.maximum_negative_strain() for section in self.sections])
		
			
class ComputationCrosssection(Crosssection): 
	
	@general.str_start_end
	def __str__(self): 
		text = [
			self._print_title(), 
			self._print_initialization(),  
			self._print_geometry(), 
			self._print_sections(), 
			self._print_sections_results(),
			self._print_results()]
		return general.print_chapter(text)
	
	@property
	def compute_sections(self): 
		return self._compute_sections
	
	@compute_sections.setter
	def compute_sections(self, compute_sections): 
		self._compute_sections = compute_sections
		
	@property
	def compute_split_sections(self): 
		return self.compute_sections
	
	@property
	def computed_slab_sections(self) -> list: 
		"""sections of the slab (computed)"""
		return self._compute_sections_of_type(type='slab')
	
	@property
	def computed_girder_sections(self) -> list: 
		"""sections of the girder (computed)"""
		return self._compute_sections_of_type(type='girder')
		
	def girder_sections_axial_force(self) -> float: 
		"""summarized axial force of the girder sections"""
		return self._axial_force(self.computed_girder_sections)
	
	def girder_sections_moment(self): 
		"""summarized moment of the girder sections"""
		return self._moment(self.computed_girder_sections)
	
	def slab_sections_axial_force(self): 
		"""summarized axial forces of the slab sections"""
		return self._axial_force(self.computed_slab_sections)
	
	def slab_sections_moment(self): 
		"""summarized moments of the slab sections"""
		return self._moment(self.computed_slab_sections)
	
	def total_axial_force(self): 
		"""summarized axial forces of the crosssection"""
		return self._axial_force(self.compute_split_sections)
	
	def total_moment(self): 
		"""summarized moments of the crosssection"""
		return self._moment(self.compute_split_sections)
	
	def _compute_sections_of_type(self, type : str): 
		return [section for section in self.compute_split_sections if section.section_type == type]
	
	def _axial_force(self, sections): 
		axial_forces = self._sections_axial_force(sections)		
		return sum(axial_forces)
	
	def _sections_axial_force(self, sections) -> list: 
		return [section.axial_force for section in sections] 
	
	def _moment(self, sections): 
		moments = self._sections_moment(sections)
		return sum(moments)
		
	def _sections_moment(self, sections) -> list: 
		return [section.moment() for section in sections]
	
	def _create_computation_sections(self): 
		return [self._create_section(section) for section in self.sections]
		
	def _print_sections(self) -> str: 
		text = ['Sections', '--------']
		section_index = 1
		for section in self.sections: 
			text += [
				f'Section {section_index}:', 
				'\t' + f'Geometry: {section.geometry.__repr__()}', 
				'\t' + f'Material: {section.material.__repr__()}']
			section_index += 1
		return general.print_sections(text)
		
	def _print_all_sections_results(self): 
		text = [
			f'All sections (n = {len(self.sections)}/{len(self.compute_sections)}):', 
			'\t' + 'N = {:.1f} N'.format(self.total_axial_force()), 
			'\t' + 'M = {:.1f} Nmm'.format(self.total_moment())]
		return general.print_sections(text)
	
	def _print_girder_sections_results(self): 
		text = [
			f'Girder sections (n = {len(self.girder_sections)}/{len(self.computed_girder_sections)}):', 
			'\t' + 'N_a = {:.1f} N'.format(self.girder_sections_axial_force()), 
			'\t' + 'M_a = {:.1f} Nmm'.format(self.girder_sections_moment())]
		return general.print_sections(text)
	
	def _print_slab_sections_results(self): 
		text = [
			f'Slab sections (n = {len(self.slab_sections)}/{len(self.computed_slab_sections)}):', 
			'\t' + 'N_c = {:.1f} N'.format(self.slab_sections_axial_force()), 
			'\t' + 'M_c = {:.1f} Nmm'.format(self.slab_sections_moment())]
		return general.print_sections(text)
		
	def _print_sections_results(self): 
		text = ['Axial Forces, Moment', '--------------------']
		if len(self.girder_sections) > 0: 
			text += [self._print_girder_sections_results(), '']
		if len(self.slab_sections) > 0: 
			text += [self._print_slab_sections_results(), '']
		text.append(self._print_all_sections_results())
		return general.print_sections(text)
	
	def _print_results(self) -> str: 
		pass 
		
class ComputationCrosssectionStrain(ComputationCrosssection): 
	
	"""computes a crosssection under a constant strain"""
	
	__slots__ = '_strain', '_compute_sections', '_bottom_edge', '_top_edge'
	 
	def __init__(self, sections:list, strain:float): 
		"""
		Initialize 
		
		Parameters
		----------
		sections : list[Section]
			sections the crosssection consists of
		strain : float
			applied constant strain
		"""
		super().__init__(sections)
		self._strain = strain
		self._compute_sections = self._create_computation_sections()
		
	def __repr__(self): 
		return f'ComputationCrosssectionStrain(sections=sections, strain={self.strain})'
	
	def __add__(self, other): 
		return ComputationCrosssectionStrainAdd(self, other)
	
	@property
	def strain(self):
		"""applied strain to the crosssection""" 
		return self._strain
		
	@property
	def compute_split_sections(self) -> list: 
		return self.compute_sections
	
	def _create_section(self, section): 
		return ComputationSectionStrain(section, self.strain)
		
	def _print_results(self): 
		text = [
			'Stress distribution', '--------------------------', '',
			' top edge | bot edge |   strain   |  stress  | axi. force | section | material ', 
			'-------------------------------------------------------------------------------']
		for section in self.compute_split_sections: 
			text.append(section._print_result())
		text.append('-------------------------------------------------------------------------------')
		return general.print_sections(text)


class ComputationCrosssectionStrainAdd(ComputationCrosssectionStrain): 
	
	def __init__(self, computed_crosssection_1, computed_crosssection_2): 
		self._computed_crosssection_1 = computed_crosssection_1
		self._computed_crosssection_2 = computed_crosssection_2
	
	def __repr__(self) -> str: 
		return f'ComputationCrosssectionStrainAdd(computed_crosssection_1={self.computed_crosssection_1.__repr__()}, computed_crosssection_2={self.computed_crosssection_2.__repr__()})'	
		
	@property
	def computed_crosssection_1(self) -> ComputationCrosssectionStrain: 
		return self._computed_crosssection_1
		
	@property
	def computed_crosssection_2(self) -> ComputationCrosssectionStrain: 
		return self._computed_crosssection_2
	
	@property
	def compute_sections(self): 
		return self.computed_crosssection_1.compute_sections + self.computed_crosssection_2.compute_sections
		
	@property
	def top_edge(self): 
		return min(self.computed_crosssection_1.top_edge, self.computed_crosssection_2.top_edge)
		
	@property
	def bottom_edge(self): 
		return max(self.computed_crosssection_1.bottom_edge, self.computed_crosssection_2.bottom_edge)
			
	@property
	def sections(self): 
		return self.computed_crosssection_1.sections + self.computed_crosssection_2.sections
	
	@property
	def axial_force(self) -> float: 	
		if self.total_moment() > 0.0:
			return abs(self.computed_crosssection_1.total_axial_force())
		else: 
			return abs(self.computed_crosssection_1.total_axial_force()) * (-1.)
			
	@property
	def strain_difference(self) -> float: 
		strain_difference = abs(self.computed_crosssection_1.strain) + abs(self.computed_crosssection_2.strain)
		if self.total_moment() > 0.0: 
			return strain_difference
		else: 
			return strain_difference * (-1.)
	
class ComputationCrosssectionCurvature(ComputationCrosssection): 
	
	""" computes a crosssection under a curvature and a neutral axis """
	
	__slots__ = '_sections', '_curvature', '_neutral_axis', '_bottom_edge', '_top_edge'	
		
	def __init__(self, sections:list, curvature:float, neutral_axis:float): 
		"""
		Initializiation
		
		Parameters
		----------
		sections : list[Section]
			sections the crosssection consists of
		curvature : float
			curvature to compute values
		neutral_axis : float
			position where strain is zero
		"""
		super().__init__(sections)
		self._curvature = curvature
		self._neutral_axis = neutral_axis
		self._compute_sections = self._create_computation_sections()
		self._compute_split_sections = self._create_computation_split_sections()
		
	def __repr__(self): 
		return f'ComputationCrosssection(sections=sections, curvature={self.curvature}, neutral_axis={self.neutral_axis})'
			 
	@property
	def compute_split_sections(self): 
		"""sections split at material points"""
		return self._compute_split_sections
		
	@property 
	def curvature(self) -> float: 
		"""applied curvature to the crosssection"""
		return self._curvature
	
	@property
	def neutral_axis(self) -> float: 
		"""position where strain is zero"""
		return self._neutral_axis
		
	def get_material_points_inside_curvature(self): 
		"""gives the points included between the curvature and zero strain"""
		strain_positions = []
		for section in self.compute_sections: 
			strain_positions += section.material_points_inside_curvature()
		return strain_positions
	
	def _create_section(self, section): 
		return ComputationSectionCurvature(section, self.curvature, self.neutral_axis)
	
	def _create_computation_split_sections(self): 
		split_sections = []
		for compute_section in self.compute_sections: 
			split_sections += compute_section.split_section()
		return split_sections
			
	def _print_results(self): 
		text = [
			'Stress-strain distribution', '--------------------------', '',
			'  top edge | top strain | top stress | bot edge | bot strain | bot stress | axi. force | section | material ', 
			'------------------------------------------------------------------------------------------------------------']
		for section in self.compute_split_sections: 
			text.append(section._print_result())
		text.append('------------------------------------------------------------------------------------------------------------')
		return general.print_sections(text)
		
		
class Bound(): 
	"""store position and strain of boundary condition"""
	
	__slots__ = '_position', '_strain'
	
	def __init__(self, position:float, strain:float): 
		"""Initialization
		
		Parameters
		----------
		position : float
			position of the strain
		strain : float
			maximum positive or negative strain of the crosssection
		"""
		self._position = position
		self._strain = strain
	
	def __repr__(self): 
		return f'Bound(position={self.position}, strain={self.strain})'
	
	@property
	def position(self): 
		"""position of the strain"""
		return self._position
		
	@property
	def strain(self): 
		"""maximum positive or negative strain of the crosssection"""
		return self._strain

	
class Curvature(abc.ABC): 
			
	@abc.abstractmethod
	def compute(self, strain:float, position:float): 
		...

	def _curvature_by_points(self, position_1, strain_1, position_2, strain_2): 
		return general.curvature_by_points(
			top_edge=position_1, top_strain=strain_1, 
			bottom_edge=position_2, bottom_strain=strain_2)
			
	def _get_lower_positions(self, position:float, position_strains:list): 
		return list(filter(lambda x: x[0] < position, position_strains))
		
	def _get_higher_positions(self, position:float, position_strains:list): 
		return list(filter(lambda x: x[0] > position, position_strains))		

						
class MaximumCurvature(Curvature): 
	
	"""store values connected to maximum curvature"""
	
	__slots__ = '_curvature', '_start', '_other', '_positive', '_negative'
	
	def __init__(self, curvature:float, start:Bound, other:Bound, maximum_positive_section_strains:list, maximum_negative_section_strains:list): 
		"""
		Initialization
		
		Parameters
		----------
		curvature : float
			maximum curvature	
		start : Bound
			start strain and position for the given maximum curvature
		other : Bound
			other strain and position for the given maximum curvature
		maximum_positive_section_strains : list
			maximum positive material strains of the sections in the crosssection
		maximum_negative_section_srtains : list
			maximum negative material strains of the sections in the crosssection
		"""
		self._curvature = curvature
		self._start = start
		self._other = other
		self._positive = maximum_positive_section_strains 
		self._negative = maximum_negative_section_strains
	
	def __repr__(self): 
		return f'MaximumCurvature(curvature={self.curvature}, start={self.start}, other={self.other})'
		
	@property
	def curvature(self): 
		"""maxium curvature"""
		return self._curvature
		
	@property
	def start(self): 
		"""start strain and position for the given maximum curvature"""
		return self._start
		
	@property
	def other(self): 
		"""other strain and position for the given maximum curvature"""
		return self._other

	def compute(self, strain:float, position:float) -> float: 
		"""compute maximum curvature for given strain at given position"""
		if self.__has_positive_curvature(): 
			return self.__compute_positive_curvatures(strain, position)
		else: 
			return self.__compute_negative_curvatures(strain, position)
			
	def __has_positive_curvature(self) -> bool: 
		if self.curvature > 0.0: 
			return True
		else: 
			return False
	
	def __get_positive_position_strains(self, strain:float, position:float):
		position_strains = self._get_higher_positions(position, self._positive)
		position_strains += self._get_lower_positions(position, self._negative)
		#print(f'Strain: {strain}, Position: {position}, Position-Strains: {position_strains}')
		return position_strains
	
	def __get_negative_position_strains(self, strain:float, position:float):
		position_strains = self._get_higher_positions(position, self._negative)
		position_strains += self._get_lower_positions(position, self._positive)
		#print(f'Strain: {strain}, Position: {position}, Position-Strains: {position_strains}')
		return position_strains			
	
	def __compute_negative_curvatures(self, strain:float, position:float): 
		position_strains = self.__get_negative_position_strains(strain, position)
		curvatures = []
		if len(position_strains) > 0: 
			for position_strain in position_strains: 
				curvatures.append(self._curvature_by_points(position, strain, position_strain[0], position_strain[1]))
		else: 
			print('negative curvature failure')
		#print(f'Strain: {strain}, Position: {position}, Maximum Curvatures: {curvatures}, Maximum Curvature: {max(curvatures)}')
		return max(curvatures)
		
	def __compute_positive_curvatures(self, strain:float, position:float): 
		position_strains = self.__get_positive_position_strains(strain, position)
		curvatures = []
		if len(position_strains) > 0: 
			for position_strain in position_strains: 
				curvatures.append(self._curvature_by_points(position, strain, position_strain[0], position_strain[1]))
		else: 
			print('positive curvature failure')
		#print(f'Strain: {strain}, Position: {position}, Maximum Curvatures: {curvatures}, Maximum Curvature: {min(curvatures)}')
		return min(curvatures)

	def __remove_smaller_strains(self, strain, position_strains):
		return list(filter(lambda x: strain < x[1], position_strains))
		
	def __remove_higher_strains(self, strain, position_strains): 
		return list(filter(lambda x: x[1] < strain, position_strains))
		
		

class MinimumCurvature(Curvature): 
	
	"""store maximum positive and negative section strains for determination of minimum curvature"""
	
	__slots__ = '_positive', '_negative', '_curvature_is_positive'
	
	def __init__(self, maximum_positive_section_strains:list, maximum_negative_section_strains:list, curvature_is_positive:bool): 
		"""Initialization
		
		Parameters
		----------
		maximum_positive_section_strains : list
			maximum positive material strains of the sections in the crosssection
		maximum_negative_section_srtains : list
			maximum negative material strains of the sections in the crosssection
		curvature_is_positive : bool
			if True than positive curvature is assumed
			if False than negative curvaature is assumed
		"""
		self._positive = maximum_positive_section_strains
		self._negative = maximum_negative_section_strains
		self._curvature_is_positive = curvature_is_positive
	
	def __repr__(self): 
		return f'MinimumCurvature(maximum_positive={self._positive}, maximum_negative={self._negative}, curvature_is_positive={self._curvature_is_positive})'
		
	def compute(self, strain:float, position:float):
		"""compute minimum curvature"""
		if self._curvature_is_positive: 
			return self.__compute_positive_curvatures(strain, position)
		else: 
			return self.__compute_negative_curvatures(strain, position)
			
				
	def __compute_positive_curvatures(self, strain:float, position:float): 
		position_strains = self.__get_positive_position_strains(strain, position)
		curvatures = []
		if len(position_strains) > 0: 
			for position_strain in position_strains: 
				curvatures.append(self._curvature_by_points(position, strain, position_strain[0], position_strain[1]))
		else: 
			curvatures.append(0.00001)
		#print(f'Strain: {strain}, Position: {position}, Minimum Curvatures: {curvatures}, Minimum Curvature: {max(curvatures)}, positive_curvature: {self._curvature_is_positive}')
		return max(curvatures)
	
	def __get_positive_position_strains(self, strain, position): 
		if strain > 0.0:
			position_strains = self._get_lower_positions(position, self._positive)
			position_strains = self._remove_higher_strains(strain, position_strains)
		else: 
			position_strains = self._get_higher_positions(position, self._negative)
			position_strains = self._remove_smaller_strains(strain, position_strains)
		return position_strains
	
	def __compute_negative_curvatures(self, strain:float, position:float): 
		position_strains = self.__get_negative_position_strains(strain, position)
		curvatures = []
		if len(position_strains) > 0: 
			for position_strain in position_strains: 
				curvatures.append(self._curvature_by_points(position, strain, position_strain[0], position_strain[1]))
		else:
			curvatures.append(-0.00001)
		#print(f'Strain: {strain}, Position: {position}, Minimum Curvatures: {curvatures}, Minimum Curvature: {min(curvatures)}, positive_curvature: {self._curvature_is_positive}')
		return min(curvatures)
	
	def __get_negative_position_strains(self, strain:float, position:float): 
		if strain > 0.0:
			position_strains = self._get_higher_positions(position, self._positive)
			position_strains = self._remove_higher_strains(strain, position_strains)
		else: 
			position_strains = self._get_lower_positions(position, self._negative)
			position_strains = self._remove_smaller_strains(strain, position_strains)
		return position_strains
	
	def _remove_higher_strains(self, strain:float, position_strains:list): 
		return list(filter(lambda x: 0.0 < x[1] < strain, position_strains))

	def _remove_smaller_strains(self, strain:float, position_strains:list): 
		return list(filter(lambda x: strain < x[1] < 0.0, position_strains))
		
	
class BoundaryValues: 
	"""store boundary condition values"""
	
	__slots__ = '_maximum_curvature', '_minimum_curvature'
	
	def __init__(self, maximum_curvature:MaximumCurvature, minimum_curvature:MinimumCurvature): 
		"""
		Initialization
		
		Parameters
		----------
		maximum_curvature : MaximumCurvature
			container for the maximum curvature values
		minimum_curvature : MinimumCurvature
			container for the minimum curvature values
		"""
		self._maximum_curvature = maximum_curvature
		self._minimum_curvature = minimum_curvature
	
	def __repr__(self):
		return f'BoundaryValues(maximum_curvature={self.maximum_curvature}, minimum_curvature={self.minimum_curvature})'
		
	@property
	def maximum_curvature(self) -> MaximumCurvature: 
		"""container for the maximum curvature values"""
		return self._maximum_curvature
	
	@property
	def minimum_curvature(self) -> MinimumCurvature: 
		"""container for the minimum curvature values"""
		return self._minimum_curvature
			
		
class Boundaries: 
	"""store boundary conditions"""
	
	__slots__ = '_positive', '_negative'
	
	def __init__(self, positive:BoundaryValues, negative:BoundaryValues): 
		"""
		Initialization
		
		Parameters
		----------
		positive : BoundaryValues
			container for the positive boundary condition values
		negative : BoundaryValues
			container for the negative boundary condition values
		"""
		self._positive = positive
		self._negative = negative
		
	def __repr__(self): 
		return f'Boundaries(\n\tpositive={self.positive}, \n\tnegative={self.negative})'
		
	@property
	def positive(self): 
		"""container for the positive boundary condition values"""
		return self._positive
		
	@property
	def negative(self): 
		"""container for the negative boundary condition values"""
		return self._negative
		
		
class CrosssectionBoundaries(Crosssection): 
		
	"""Compute the Boundary-Values for the crosssection"""
	
	__slots__ = '_positive_start_position', '_positive_start_position', '_positive_start_strain', '_negative_start_position', '_negative_start_position', '_negative_start_strain', '_maximum_positive_curvature', '_maximum_negative_curvature'
				
	def __init__(self, sections:list):
		"""
		Initialization
		
		Parameters
		----------
		sections : list[Section]
			sections of the given crosssection
		"""
		super().__init__(sections)
		self._set_maximum_curvatures()
		self._set_start_values()
	
	def __repr__(self): 
		return 'CrosssectionBoundaries(sections=sections)'
		
	@general.str_start_end	
	def __str__(self): 
		text = [
			self._print_title(), 
			self._print_initialization(), 
			self._print_geometry(),   
			self._print_boundary_curvatures(),
			self._print_start_values(), 
			self._print_sections()]
		return general.print_chapter(text)
		
	def _print_title(self): 
		return general.print_sections(['CrosssectionBoundaries', '----------------------'])
		
	def _print_initialization(self) -> str: 
		return general.print_sections(['Initialization', '--------------', self.__repr__()])
		
	def _print_boundary_curvatures(self): 
		text = [
			'Boundary Curvatures', '-------------------', 
			'Positive: {:.5f}'.format(self.maximum_positive_curvature['curvature']), 
			'\t' + 'top_edge: {:.1f} | strain: {:.4f}'.format(self.maximum_positive_curvature['top_edge'][0], self.maximum_positive_curvature['top_edge'][1]), 
			'\t' + 'bottom_edge: {:.1f} | strain: {:.4f}'.format(self.maximum_positive_curvature['bottom_edge'][0], self.maximum_positive_curvature['bottom_edge'][1]),
			'Negative: {:.5f}'.format(self.maximum_negative_curvature['curvature']), 
			'\t' + 'top_edge: {:.1f} | strain: {:.4f}'.format(self.maximum_negative_curvature['top_edge'][0], self.maximum_negative_curvature['top_edge'][1]), 
			'\t' + 'bottom_edge: {:.1f} | strain: {:.4f}'.format(self.maximum_negative_curvature['bottom_edge'][0], self.maximum_negative_curvature['bottom_edge'][1])]
		return general.print_sections(text)
	
	def _print_start_values(self): 
		text = [
			'Start-values', '------------',  
			f'positive curvature: strain={self._positive_start_strain} | position={self._positive_start_position}', 
			f'negative curvature: strain={self._negative_start_strain} | position={self._negative_start_position}']
		return general.print_sections(text)
	
	@property
	def maximum_positive_curvature(self): 
		return self._maximum_positive_curvature
		
	@property
	def maximum_negative_curvature(self): 
		return self._maximum_negative_curvature
	
	@property
	def positive_start_position(self): 
		return self._positive_start_position
		
	@property
	def positive_start_strain(self): 
		return self._positive_start_strain
		
	@property
	def negative_start_position(self): 
		return self._negative_start_position
		
	@property
	def negative_start_strain(self): 
		return self._negative_start_strain	
				
	@property 
	def _positive_starts_top_neutral_axis(self): 
		return self.__compute_neutral_axis(
			curvature=0.5*self.maximum_positive_curvature['curvature'],
			strain_position=self.maximum_positive_curvature['top_edge'])
			
	@property 
	def _negative_starts_top_neutral_axis(self): 
		return self.__compute_neutral_axis(
			curvature=0.5*self.maximum_negative_curvature['curvature'],
			strain_position=self.maximum_negative_curvature['top_edge'])
				
	@property 
	def _positive_starts_bottom_neutral_axis(self): 
		return self.__compute_neutral_axis(
			curvature=0.5*self.maximum_positive_curvature['curvature'],
			strain_position=self.maximum_positive_curvature['bottom_edge'])
			
	@property 
	def _negative_starts_bottom_neutral_axis(self): 
		return self.__compute_neutral_axis(
			curvature=0.5*self.maximum_negative_curvature['curvature'], 
			strain_position=self.maximum_negative_curvature['bottom_edge'])
	
	def _determine_curvatures(self, bottom_edge_strains : list, top_edge_strains : list): 
		curvatures = []
		position_index = 0 
		strain_index = 1
		for bottom_edge_strain in bottom_edge_strains: 
			for top_edge_strain in top_edge_strains:
				if top_edge_strain[position_index] < bottom_edge_strain[position_index]: 
					curvatures.append({
						'curvature': general.curvature_by_points(
							top_edge=top_edge_strain[position_index], 
							bottom_edge=bottom_edge_strain[position_index], 
							top_strain=top_edge_strain[strain_index], 
							bottom_strain=bottom_edge_strain[strain_index]), 
						'bottom_edge': bottom_edge_strain, 
						'top_edge': top_edge_strain})
		return curvatures
				
	def _determine_positive_curvatures(self): 
		return self._determine_curvatures(
			bottom_edge_strains=self._sections_maximum_strains, # self._sections_bottom_edge_maximum_strains, 
			top_edge_strains=self._sections_minimum_strains)# self._sections_top_edge_minimum_strains)
			
	def _determine_negative_curvatures(self): 
		return self._determine_curvatures(
			bottom_edge_strains=self._sections_minimum_strains, # self._sections_bottom_edge_minimum_strains, 
			top_edge_strains=self._sections_maximum_strains)#self._sections_top_edge_maximum_strains)
	
	def _get_maximum_positive_curvature(self): 
		curvatures = self._determine_positive_curvatures()
		return min(curvatures, key=lambda x: x['curvature'])
		
	def _get_maximum_negative_curvature(self): 
		curvatures = self._determine_negative_curvatures()
		return max(curvatures, key=lambda x: x['curvature'])
	
	def _set_maximum_curvatures(self): 
		self._set_sections_strain()
		self._maximum_positive_curvature = self._get_maximum_positive_curvature()
		self._maximum_negative_curvature = self._get_maximum_negative_curvature()
	
	def _set_sections_strain(self): 
		self._set_sections_maximum_strain()
		self._set_sections_minimum_strain()
		
	def _set_sections_maximum_strain(self): 
		position_strain = []
		for section in self.sections: 
			position_strain.append(section.top_edge_maximum_strain)
			position_strain.append(section.bottom_edge_maximum_strain)
		position_strain.sort(key = lambda x: x[0])
		self._sections_maximum_strains = position_strain
		
	def _set_sections_minimum_strain(self): 
		position_strain = []
		for section in self.sections: 
			position_strain.append(section.top_edge_minimum_strain)
			position_strain.append(section.bottom_edge_minimum_strain)
		position_strain.sort(key = lambda x: x[0])
		self._sections_minimum_strains = position_strain
	
	def _set_start_values(self): 
		self.__set_positive_curvature_start_values()
		self.__set_negative_curvature_start_values()
	
	def __compute_neutral_axis(self, curvature : float, strain_position : list): 
		return general.neutral_axis(
			curvature=curvature, 
			strain_at_position=strain_position[1], 
			position=strain_position[0])
	
	def __positive_start_top_computed_cross_section(self): 
		return ComputationCrosssectionCurvature(
			sections=self.sections, 
			curvature=0.5*self.maximum_positive_curvature['curvature'],
			neutral_axis=self._positive_starts_top_neutral_axis)
			
	def __positive_start_bottom_computed_cross_section(self): 
		return ComputationCrosssectionCurvature(
			sections=self.sections, 
			curvature=0.5*self.maximum_positive_curvature['curvature'], 
			neutral_axis=self._positive_starts_bottom_neutral_axis)
	
	def __negative_start_top_computed_cross_section(self): 
		return ComputationCrosssectionCurvature(
			sections=self.sections, 
			curvature=0.5*self.maximum_negative_curvature['curvature'],
			neutral_axis=self._negative_starts_top_neutral_axis)
	
	def __negative_start_bottom_computed_cross_section(self): 
		return ComputationCrosssectionCurvature(
			sections=self.sections, 
			curvature=0.5*self.maximum_negative_curvature['curvature'], 
			neutral_axis=self._negative_starts_bottom_neutral_axis)
		
	def __set_positive_curvature_start_values(self):  
		if abs(self.__positive_start_top_computed_cross_section().total_axial_force()) < abs(self.__positive_start_bottom_computed_cross_section().total_axial_force()): 
			self._positive_edge = 'top_edge'
		else:
			self._positive_edge = 'bottom_edge'
		self._positive_start_position = self.maximum_positive_curvature[self._positive_edge][0]
		self._positive_start_strain = self.maximum_positive_curvature[self._positive_edge][1]
		
	def __set_negative_curvature_start_values(self):  
		if abs(self.__negative_start_top_computed_cross_section().total_axial_force()) < abs(self.__negative_start_bottom_computed_cross_section().total_axial_force()): 
			self._negative_edge = 'top_edge'
		else:
			self._negative_edge = 'bottom_edge'	
		self._negative_start_position = self.maximum_negative_curvature[self._negative_edge][0]
		self._negative_start_strain = self.maximum_negative_curvature[self._negative_edge][1]
		
	def __positive_start_bound(self): 
		return Bound(strain=self.positive_start_strain, position=self.positive_start_position)
		
	def __positive_other_bound(self): 
		for edge in ['top_edge', 'bottom_edge']: 
			if edge is not self._positive_edge: 
				return Bound(
					strain=self.maximum_positive_curvature[edge][1], 
					position=self.maximum_positive_curvature[edge][0])
		
	def __negative_start_bound(self): 
		return Bound(strain=self.negative_start_strain, position=self.negative_start_position)
	
	def __negative_other_bound(self): 
		for edge in ['top_edge', 'bottom_edge']: 
			if edge is not self._negative_edge: 
				return Bound(
					strain=self.maximum_negative_curvature[edge][1], 
					position=self.maximum_negative_curvature[edge][0])
		
	def __get_positive_boundaries(self): 
		return BoundaryValues(
			maximum_curvature=MaximumCurvature(
				curvature=self.maximum_positive_curvature['curvature'], 
				start=self.__positive_start_bound(), 
				other=self.__positive_other_bound(), 
				maximum_positive_section_strains=self._sections_maximum_strains, 
				maximum_negative_section_strains=self._sections_minimum_strains),  
			minimum_curvature=MinimumCurvature(
				self._sections_maximum_strains, 
				self._sections_minimum_strains, 
				curvature_is_positive=True))
	
	def __get_negative_boundaries(self): 
		return BoundaryValues(
			maximum_curvature=MaximumCurvature(
				curvature=self.maximum_negative_curvature['curvature'],
				start=self.__negative_start_bound(), 
				other=self.__negative_other_bound(),
				maximum_positive_section_strains=self._sections_maximum_strains, 
				maximum_negative_section_strains=self._sections_minimum_strains),
			minimum_curvature=MinimumCurvature(
				self._sections_maximum_strains, 
				self._sections_minimum_strains, 
				curvature_is_positive=False))
		
	def get_boundaries(self): 
		return Boundaries(
			positive=self.__get_positive_boundaries(), 
			negative=self.__get_negative_boundaries())
		
		
if __name__ == '__main__': 
	
	start = time.clock()
	concrete = material.Concrete(f_cm=30)
	concrete_rectangle = geometry.Rectangle(top_edge=0, bottom_edge=20, width=10)
	
	steel = material.Steel(f_y=355, epsilon_u=0.2)
	steel_rectangle = geometry.Rectangle(top_edge=20, bottom_edge=30, width=10)
	
	concrete_section = Section(geometry=concrete_rectangle, material=concrete)
	steel_section = Section(geometry=steel_rectangle, material=steel)
	
	cs = concrete_section + steel_section
	print(cs)
	cs += steel_section
	
	for section in cs: 
		print(section)
	
	curvature=0.0001
	neutral_axis=20
	
	curvature_section = ComputationSectionCurvature(steel_section, curvature=curvature, neutral_axis=neutral_axis)
	#print(curvature_section.__dict__)
	#print(curvature_section)
	curvature_section = ComputationSectionCurvature(concrete_section, curvature=curvature, neutral_axis=neutral_axis)
	#print(curvature_section)
	strain_section = ComputationSectionStrain(steel_section, strain=0.002)
	#print(strain_section)
	strain_section = ComputationSectionStrain(concrete_section, strain=-0.002)
	#print(strain_section)
	
	#cs = CrosssectionBoundaries(sections=[concrete_section, steel_section])
	#print(cs.maximum_positive_curvature)
	cs = Crosssection(sections=[concrete_section, steel_section])
	#cs.add_section(concrete_section)
	#cs.add_section(steel_section)
	#print(cs)
	#print(cs.get_boundary_conditions())
	
	
	ccc = ComputationCrosssectionCurvature(sections=cs.sections, curvature=curvature, neutral_axis=neutral_axis)
	#print(ccc)
	#print(ccs.get_material_points_inside_curvature())
	#print(ComputationCrosssection(sections=cs.sections, curvature=curvature, neutral_axis=neutral_axis).total_axial_force())	
	
	ccs = ComputationCrosssectionStrain(sections=cs.sections, strain=-0.002)
	#print(ccs)
	
	
	end = time.clock()
	print(end - start)
	
