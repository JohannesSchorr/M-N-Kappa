from dataclasses import dataclass
from .general import (
    str_start_end,
    print_chapter,
    print_sections,
    position,
    strain,
)


@dataclass
class StrainPosition:

    """Container for strains at a position within a given material"""

    strain: float
    position: float
    material: str


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
        return f"Section(geometry={self.geometry.__repr__()}, material={self.material.__repr__()})"

    def __add__(self, other):
        return self._build_crosssection(other)

    def __radd__(self, other):
        return self._build_crosssection(other)

    def _build_crosssection(self, other):
        from .crosssection import Crosssection

        if isinstance(other, Section):
            sections = [self, other]
            return Crosssection(sections)
        elif isinstance(other, Crosssection):
            sections = other.sections + [self]
            return Crosssection(sections)
        else:
            raise TypeError(
                f'unsupported operand section_type(s) for +: "{type(self)}" and "{type(other)}"'
            )

    def __eq__(self, other):
        return self._material == other._material and self._geometry == other._geometry

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_material(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(
            ["Initialization", len("Initialization") * "-", self.__repr__()]
        )

    def _print_geometry(self) -> str:
        return print_sections(["Geometry", "--------", self.geometry.__repr__()])

    def _print_material(self) -> str:
        return print_sections(["Material", "--------", self.material.__repr__()])

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
        return [
            {"section-section_type": self.section_type, "strain_value": strain_value}
            for strain_value in self.material_strains()
        ]


class ComputationSection(Section):

    __slots__ = "_geometry", "_material"

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
        force = self._axial_force_integrated_at_position(
            position=self.geometry.edges[1]
        )
        force -= self._axial_force_integrated_at_position(
            position=self.geometry.edges[0]
        )
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
            (1.0 / 3.0)
            * self.geometry.width_slope
            * self.stress_slope
            * position ** (3.0)
            + (1.0 / 2.0)
            * (
                self.stress_interception * self.geometry.width_slope
                + self.geometry.width_interception * self.stress_slope
            )
            * position ** (2.0)
            + self.geometry.width_interception * self.stress_interception * position
        )

    def _lever_arm_integrated_at_position(self, position: float):
        return (
            (1.0 / 4.0)
            * self.geometry.width_slope
            * self.stress_slope
            * position ** (4.0)
            + (1.0 / 3.0)
            * (
                self.stress_interception * self.geometry.width_slope
                + self.geometry.width_interception * self.stress_slope
            )
            * position ** (3.0)
            + (1.0 / 2.0)
            * self.geometry.width_interception
            * self.stress_interception
            * position ** (2.0)
        )

    def _lever_arm_numerator(self):
        if len(self.geometry.edges) > 1:
            return self._lever_arm_numerator_rectangle()
        else:
            return self.geometry.centroid

    def _lever_arm_numerator_rectangle(self):
        lever_arm = self._lever_arm_integrated_at_position(
            position=self.geometry.edges[1]
        )
        lever_arm -= self._lever_arm_integrated_at_position(
            position=self.geometry.edges[0]
        )
        return lever_arm

    def _material_stress(self, strain) -> float:
        return self.material.get_material_stress(round(strain, 7))

    def _print_results(self) -> str:
        text = [
            "Results",
            "-------",
            "axial force: " + "N = {:10.1f} N".format(self.axial_force),
            "lever arm:   " + "z = {:10.1f} mm".format(self.lever_arm()),
            "moment:      " + "M = {:10.1f} Nmm".format(self.moment()),
        ]
        return print_sections(text)


class ComputationSectionStrain(ComputationSection):

    """compute section  under a constant strain_value"""

    __slots__ = (
        "_section",
        "_strain",
        "_edges_strain",
        "_edges_stress",
        "_stress_slope",
        "_stress_interception",
        "_axial_force",
    )

    def __init__(self, section: Section, strain: float):
        """
        Initialize

        Parameters
        ----------
        section : Section
                section to compute
        strain : float
                given strain_value to compute
        """
        self._section = section
        self._strain = strain
        self._edges_strain = self._get_edges_strain()
        self._edges_stress = self._get_edges_stress()
        self._stress_slope = 0.0
        self._stress_interception = self._compute_stress_interception()
        self._axial_force = self._compute_axial_force()

    def __repr__(self):
        return f"ComputationSectionStrain(section={self.section.__repr__()}, strain_value={self.strain})"

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_results(),
        ]
        return print_chapter(text)

    @property
    def strain(self) -> float:
        return self._strain

    def _get_edges_strain(self) -> list:
        return [self.strain for _ in self.section.geometry.edges]

    def _print_result(self) -> str:
        return " {:8.2f} | {:8.2f} | {:10.6f} | {:8.2f} | {:10.2f} | {:7} | {}".format(
            self.geometry.top_edge,
            self.geometry.bottom_edge,
            self.strain,
            self.edges_stress[0],
            self.axial_force,
            self.section_type,
            self.material.__class__.__name__,
        )


class ComputationSectionCurvature(ComputationSection):

    """compute section given a curvature and a neutral axis"""

    __slots__ = (
        "_section",
        "_curvature",
        "_neutral_axis",
        "_edges_strain",
        "_edges_stress",
        "_stress_slope",
        "_stress_interception",
        "_axial_force",
    )

    def __init__(self, section: Section, curvature: float, neutral_axis: float):
        """
        Initialize

        Parameters
        ----------
        section : Section
                section to compute
        curvature : float
                curvature to apply to the section
        neutral axis : float
                point where the strain_value is zero
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
        return f"CompuationSectionCurvature(section={self.section.__class__.__name__}, curvature={self.curvature}, neutral_axis_value={self.neutral_axis})"

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_material(),
            self._print_results(),
        ]
        return print_chapter(text)

    def _print_geometry(self) -> str:
        text = ["Geometry", "--------", "section_type: " + self.geometry.__class__.__name__]
        if len(self.geometry.edges) > 1:
            text += [
                "top_edge: {:.1f} | bottom_edge: {:.1f}".format(
                    self.geometry.edges[0], self.geometry.edges[1]
                ),
                "width-formula: {:.1f} * position_value + {:.1f}".format(
                    self.geometry.width_slope, self.geometry.width_interception
                ),
                "top_strain: {:.5f} | bottom_strain: {:.5f}".format(
                    self.edges_strain[0], self.edges_strain[1]
                ),
            ]
        else:
            text += [
                "area: {:.1f} | centroid: {:.1f}".format(
                    self.geometry.area, self.geometry.centroid
                )
            ]
        return print_sections(text)

    def _print_material(self) -> str:
        text = ["Material", "--------"]
        if len(self.geometry.edges) > 1:
            text += [
                "top_stress {:.1f} N/mm^2 | bottom_stress {:.1f} N/mm^2".format(
                    self.edges_stress[0], self.edges_stress[1]
                ),
                "stress-formula: {:.1f} * position_value + {:.1f}".format(
                    self.stress_slope, self.stress_interception
                ),
            ]
        else:
            text += ["stress {:.1f} N/mm^2".format(self.edges_stress[0])]
        return print_sections(text)

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
        return "{:10.2f} | {:10.6f} | {:10.2f} | {:8.2f} | {:10.6f} | {:10.2f} | {:10.2f} | {:7} | {}".format(
            self.geometry.top_edge,
            self.edges_strain[0],
            self.edges_stress[0],
            self.geometry.bottom_edge,
            self.edges_strain[1],
            self.edges_stress[1],
            self.axial_force,
            self.section_type,
            self.material.__class__.__name__,
        )

    def split_section(self) -> list:
        sub_geometries = self.__get_sub_geometries()
        split_sections = []
        for sub_geometry in sub_geometries:
            split_sections.append(self.__computation_section(sub_geometry))
        return split_sections

    def material_points_inside_curvature(self):
        strain_position = []
        for strain_index, strain_value in enumerate(self._edges_strain):
            if strain_index == self.__get_allowed_position_index(strain_value):
                for intermediate_strain in self.material.get_intermediate_strains(
                    strain_value
                ):
                    strain_position.append(
                        StrainPosition(
                            intermediate_strain,
                            self.geometry.edges[strain_index],
                            self.material.__class__.__name__
                        )
                    )
        return strain_position

    def __get_allowed_position_index(self, strain_value: float) -> int:
        if self.curvature > 0.0:
            if strain_value > 0.0:
                return 1  # bottom_edge
            else:
                return 0  # top_edge
        else:
            if strain_value > 0.0:
                return 0  # top_edge
            else:
                return 1  # bottom_edge

    def __computation_section(self, geometry):
        return ComputationSectionCurvature(
            section=self.__sub_section(geometry),
            curvature=self.curvature,
            neutral_axis=self.neutral_axis,
        )

    def _compute_stress_slope(self) -> float:
        if self.geometry.height == 0.0:
            return 0.0
        else:
            return self.edges_stress_difference / self.geometry.height

    def _get_edges_strain(self) -> list:
        return [
            self.__get_strain_by_position(position_value) for position_value in self.geometry.edges
        ]

    def __get_strain_by_position(self, position_value: float):
        return strain(
            neutral_axis_value=self.neutral_axis,
            curvature_value=self.curvature,
            position_value=position_value
        )

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
            position_value = self.__compute_position(strain_value=stress_strain[1])
            positions.append(position_value)
        return positions

    def __compute_position(self, strain_value: float):
        return position(
            curvature_value=self.curvature,
            neutral_axis_value=self.neutral_axis,
            strain_at_position=strain_value,
        )