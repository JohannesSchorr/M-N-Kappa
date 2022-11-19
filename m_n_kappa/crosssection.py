from dataclasses import dataclass

from .general import (
    str_start_end,
    print_chapter,
    print_sections,
    curvature_by_points,
    neutral_axis,
    remove_duplicates,
    StrainPosition,
)
from .section import (
    Section,
    ComputationSection,
    ComputationSectionStrain,
    ComputationSectionCurvature,
)

from .curvature_boundaries import MaximumCurvature, MinimumCurvature, Boundaries, BoundaryValues


def axial_force(sections: list[ComputationSection]):
    """compute the sum of axial-force from a list of computed sections"""
    axial_forces = [section.axial_force for section in sections]
    return sum(axial_forces)


def moment(sections: list[ComputationSection]):
    """compute the sum of moments from a list of computed sections"""
    moments = [section.moment() for section in sections]
    return sum(moments)


class Crosssection:

    """Combines a number of sections"""

    def __init__(self, sections: list[Section] = None):
        self._sections = sections
        self._top_edge = self.__compute_top_edge()
        self._bottom_edge = self.__compute_bottom_edge()

    def __repr__(self):
        return "Crosssection(sections=sections)"

    def __iter__(self):
        self._section_iterator = iter(self.sections)
        return self

    def __next__(self):
        return self._section_iterator.__next__()

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_sections(),
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

    @property
    def bottom_edge(self) -> float:
        return self._bottom_edge

    @property
    def girder_sections(self) -> list:
        return self.sections_of_type(section_type="girder")

    @property
    def height(self) -> float:
        return self.bottom_edge - self.top_edge

    @property
    def half_point(self) -> float:
        return 0.5 * (self.bottom_edge + self.top_edge)

    @property
    def sections(self) -> list[Section]:
        return self._sections

    @property
    def slab_sections(self) -> list[Section]:
        return self.sections_of_type(section_type="slab")

    @property
    def section_type(self) -> str:
        if len(self.girder_sections) > 0 and len(self.slab_sections) == 0:
            return "girder"
        elif len(self.girder_sections) == 0 and len(self.slab_sections) > 0:
            return "slab"

    @property
    def top_edge(self) -> float:
        return self._top_edge

    def add_section(self, section: Section):
        if self.sections is None:
            self._sections = [section]
        else:
            self._sections.append(section)

    def _print_geometry(self):
        text = [
            "Geometry",
            "--------",
            "top_edge: {:.1f} | bottom_edge: {:.1f}".format(
                self.top_edge, self.bottom_edge
            ),
        ]
        return print_sections(text)

    def _print_sections(self):
        text = [
            "Sections",
            "--------",
        ]
        for section in self.sections:
            text.append(section.__repr__())
        return print_sections(text)

    def sections_of_type(self, section_type: str) -> list[Section]:
        return [
            section for section in self.sections if section.section_type == section_type
        ]

    def sections_not_of_type(self, section_type: str) -> list[Section]:
        """
        get a list of sections that are not of the specified typ

        Possible section-types are:
        - 'slab'   -> concrete slab + reinforcement
        - 'girder' -> Steel girder
        """
        return [
            section for section in self.sections if section.section_type != section_type
        ]

    def get_boundary_conditions(self) -> Boundaries:
        """
        curvature boundary values under positive and negative curvature

        see :meth:`CrossSectionBoundaries.get_boundaries`

        Returns
        -------
        Boundaries
            curvature boundary values under positive and negative curvature
        """
        cross_section_boundaries = CrossSectionBoundaries(self.sections)
        return cross_section_boundaries.get_boundaries()

    def maximum_positive_strain(self) -> float:
        return max([section.maximum_positive_strain() for section in self.sections])

    def maximum_negative_strain(self) -> float:
        return min([section.maximum_negative_strain() for section in self.sections])

    def __compute_top_edge(self) -> float:
        """compute top-edge of cross-section"""
        top_edges = [min(section.geometry.edges) for section in self.sections]
        return min(top_edges)

    def __compute_bottom_edge(self) -> float:
        """compute bottom-edge of cross-section"""
        bottom_edges = [max(section.geometry.edges) for section in self.sections]
        return max(bottom_edges)


class ComputationCrosssection(Crosssection):
    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_sections(),
            self._print_sections_results(),
            self._print_results(),
        ]
        return print_chapter(text)

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
        return self._compute_sections_of_type(section_type="slab")

    @property
    def computed_girder_sections(self) -> list:
        """sections of the girder (computed)"""
        return self._compute_sections_of_type(section_type="girder")

    def girder_sections_axial_force(self) -> float:
        """summarized axial force of the girder sections"""
        return axial_force(self.computed_girder_sections)

    def girder_sections_moment(self):
        """summarized moment of the girder sections"""
        return moment(self.computed_girder_sections)

    def slab_sections_axial_force(self):
        """summarized axial forces of the slab sections"""
        return axial_force(self.computed_slab_sections)

    def slab_sections_moment(self):
        """summarized moments of the slab sections"""
        return moment(self.computed_slab_sections)

    def total_axial_force(self):
        """summarized axial forces of the cross_section"""
        return axial_force(self.compute_split_sections)

    def total_moment(self):
        """summarized moments of the cross_section"""
        return moment(self.compute_split_sections)

    def _compute_sections_of_type(self, section_type: str):
        return [
            section
            for section in self.compute_split_sections
            if section.section_type == section_type
        ]

    def _print_sections(self) -> str:
        text = ["Sections", "--------"]
        section_index = 1
        for section in self.sections:
            text += [
                f"Section {section_index}:",
                "\t" + f"Geometry: {section.geometry.__repr__()}",
                "\t" + f"Material: {section.material.__repr__()}",
            ]
            section_index += 1
        return print_sections(text)

    def _print_all_sections_results(self):
        text = [
            f"All sections (n = {len(self.sections)}/{len(self.compute_sections)}):",
            "\t" + "N = {:.1f} N".format(self.total_axial_force()),
            "\t" + "M = {:.1f} Nmm".format(self.total_moment()),
        ]
        return print_sections(text)

    def _print_girder_sections_results(self):
        text = [
            f"Girder sections (n = {len(self.girder_sections)}/{len(self.computed_girder_sections)}):",
            "\t" + "N_a = {:.1f} N".format(self.girder_sections_axial_force()),
            "\t" + "M_a = {:.1f} Nmm".format(self.girder_sections_moment()),
        ]
        return print_sections(text)

    def _print_slab_sections_results(self):
        text = [
            f"Slab sections (n = {len(self.slab_sections)}/{len(self.computed_slab_sections)}):",
            "\t" + "N_c = {:.1f} N".format(self.slab_sections_axial_force()),
            "\t" + "M_c = {:.1f} Nmm".format(self.slab_sections_moment()),
        ]
        return print_sections(text)

    def _print_sections_results(self):
        text = ["Axial Forces, Moment", "--------------------"]
        if len(self.girder_sections) > 0:
            text += [self._print_girder_sections_results(), ""]
        if len(self.slab_sections) > 0:
            text += [self._print_slab_sections_results(), ""]
        text.append(self._print_all_sections_results())
        return print_sections(text)

    def _print_results(self) -> str:
        pass


class ComputationCrosssectionStrain(ComputationCrosssection):

    """computes a cross_section under a constant strain_value"""

    __slots__ = "_strain", "_compute_sections", "_bottom_edge", "_top_edge"

    def __init__(self, sections: list, strain: float):
        """
        Initialize

        Parameters
        ----------
        sections : list[Section]
                sections the cross_section consists of
        strain : float
                applied constant strain_value
        """
        super().__init__(sections)
        self._strain = strain
        self._compute_sections = self._create_computation_sections()

    def __repr__(self):
        return f"ComputationCrosssectionStrain(sections=sections, strain_value={self.strain})"

    def __add__(self, other):
        return ComputationCrossSectionStrainAdd(self, other)

    @property
    def strain(self):
        """applied strain_value to the cross_section"""
        return self._strain

    @property
    def compute_split_sections(self) -> list:
        return self.compute_sections

    def _create_computation_sections(self) -> list[ComputationSectionStrain]:
        return [self._create_section(section) for section in self.sections]

    def _create_section(self, basic_section) -> ComputationSectionStrain:
        return ComputationSectionStrain(basic_section, self.strain)

    def _print_results(self):
        text = [
            "Stress distribution",
            "--------------------------",
            "",
            " top edge | bot edge |   strain_value   |  stress  | axi. force | section | material ",
            "-------------------------------------------------------------------------------",
        ]
        for section in self.compute_split_sections:
            text.append(section._print_result())
        text.append(
            "-------------------------------------------------------------------------------"
        )
        return print_sections(text)


class ComputationCrossSectionStrainAdd(ComputationCrosssectionStrain):
    def __init__(self, computed_cross_section_1, computed_cross_section_2):
        self._computed_cross_section_1 = computed_cross_section_1
        self._computed_cross_section_2 = computed_cross_section_2

    def __repr__(self) -> str:
        return (
            f"ComputationCrossSectionStrainAdd("
            f"computed_cross_section_1={self.computed_cross_section_1.__repr__()}, "
            f"computed_cross_section_2={self.computed_cross_section_2.__repr__()})"
        )

    @property
    def computed_cross_section_1(self) -> ComputationCrosssectionStrain:
        return self._computed_cross_section_1

    @property
    def computed_cross_section_2(self) -> ComputationCrosssectionStrain:
        return self._computed_cross_section_2

    @property
    def compute_sections(self) -> list[ComputationSectionStrain]:
        return (
            self.computed_cross_section_1.compute_sections
            + self.computed_cross_section_2.compute_sections
        )

    @property
    def top_edge(self) -> float:
        return min(
            self.computed_cross_section_1.top_edge, self.computed_cross_section_2.top_edge
        )

    @property
    def bottom_edge(self) -> float:
        return max(
            self.computed_cross_section_1.bottom_edge,
            self.computed_cross_section_2.bottom_edge,
        )

    @property
    def sections(self) -> list[Section]:
        return (
            self.computed_cross_section_1.sections
            + self.computed_cross_section_2.sections
        )

    @property
    def axial_force(self) -> float:
        if self.total_moment() > 0.0:
            return abs(self.computed_cross_section_1.total_axial_force())
        else:
            return abs(self.computed_cross_section_1.total_axial_force()) * (-1.0)

    @property
    def strain_difference(self) -> float:
        strain_difference = abs(self.computed_cross_section_1.strain) + abs(
            self.computed_cross_section_2.strain
        )
        if self.total_moment() > 0.0:
            return strain_difference
        else:
            return strain_difference * (-1.0)


class ComputationCrosssectionCurvature(ComputationCrosssection):

    """computes a cross_section under a curvature and a neutral axis"""

    __slots__ = "_sections", "_curvature", "_neutral_axis", "_bottom_edge", "_top_edge"

    def __init__(self, sections: list, curvature: float, neutral_axis_value: float):
        """
        Parameters
        ----------
        sections : list[Section]
                sections the cross_section consists of
        curvature : float
                curvature to compute values
        neutral_axis_value : float
                position_value where strain_value is zero
        """
        super().__init__(sections)
        self._curvature = curvature
        self._neutral_axis = neutral_axis_value
        self._compute_sections = self._create_computation_sections()
        self._compute_split_sections = self._create_computation_split_sections()

    def __repr__(self):
        return (
            f"ComputationCrosssection("
            f"sections=sections, "
            f"curvature={self.curvature}, "
            f"neutral_axis_value={self.neutral_axis})"
        )

    @property
    def compute_split_sections(self) -> list:
        """sections split at material points"""
        return self._compute_split_sections

    @property
    def curvature(self) -> float:
        """applied curvature to the cross_section"""
        return self._curvature

    @property
    def neutral_axis(self) -> float:
        """position_value where strain_value is zero"""
        return self._neutral_axis

    def get_material_points_inside_curvature(self) -> list[StrainPosition]:
        """gives the points included between the curvature and zero strain_value"""
        strain_positions = []
        for basic_section in self.compute_sections:
            strain_positions += basic_section.material_points_inside_curvature()
        strain_positions = remove_duplicates(strain_positions)
        return strain_positions

    def _create_computation_sections(self) -> list[ComputationSectionCurvature]:
        return [self._create_section(section) for section in self.sections]

    def _create_section(self, basic_section) -> ComputationSectionCurvature:
        return ComputationSectionCurvature(
            basic_section, self.curvature, self.neutral_axis
        )

    def _create_computation_split_sections(self):
        split_sections = []
        for compute_section in self.compute_sections:
            split_sections += compute_section.split_section()
        return split_sections

    def _print_results(self):
        text = [
            "Stress-strain_value distribution",
            "--------------------------",
            "",
            "  top edge | top strain_value | top stress | bot edge | bot strain_value | bot stress | axi. force | section | material ",
            "------------------------------------------------------------------------------------------------------------",
        ]
        for section in self.compute_split_sections:
            text.append(section._print_result())
        text.append(
            "------------------------------------------------------------------------------------------------------------"
        )
        return print_sections(text)


@dataclass
class EdgeStrains:
    """
    store strains at edges and compute curvature from these points
    """

    bottom_edge_strain: StrainPosition
    top_edge_strain: StrainPosition

    @property
    def curvature(self) -> float:
        """curvature by comparison of the strains at the edges"""
        return curvature_by_points(
            top_edge=self.top_edge_strain.position,
            bottom_edge=self.bottom_edge_strain.position,
            top_strain=self.top_edge_strain.strain,
            bottom_strain=self.bottom_edge_strain.strain,
        )


def determine_curvatures(
    bottom_edge_strains: list[StrainPosition],
    top_edge_strains: list[StrainPosition],
) -> list[EdgeStrains]:
    curvatures = []
    for bottom_edge_strain in bottom_edge_strains:
        for top_edge_strain in top_edge_strains:
            if top_edge_strain.position < bottom_edge_strain.position:
                curvatures.append(
                    EdgeStrains(
                        bottom_edge_strain=bottom_edge_strain,
                        top_edge_strain=top_edge_strain,
                    )
                )
    return curvatures


def compute_neutral_axis(edge_strains: EdgeStrains, starts_top: bool) -> float:
    """
    compute the neutral axis with given curvature and strain a top or at bottom

    Parameters
    ----------
    edge_strains : EdgeStrains
        edge-strains to compute
    starts_top : bool
        which edge-strain is to be used for computing the neutral axis
        True: edge-strain at top
        False: edge-strain at bottom

    Returns
    -------
    float
        neutral-axis given the chosen edge-strain (top or bottom)
    """
    if starts_top:
        position_strain = edge_strains.top_edge_strain
    else:
        position_strain = edge_strains.bottom_edge_strain
    return neutral_axis(
        curvature_value=edge_strains.curvature,
        strain_at_position=position_strain.strain,
        position_value=position_strain.position,
    )


class CrossSectionBoundaries(Crosssection):

    """
    Compute the Boundary-Values for the cross_section

    :meth:`CrossSectionBoundaries:get_boundaries` gives the curvature boundary values
    under positive and negative curvature
    """

    __slots__ = (
        "_sections_maximum_strains",
        "_sections_minimum_strains",
        "_positive_start_bound",
        "_negative_start_bound",
        "_maximum_positive_curvature",
        "_maximum_negative_curvature",
    )

    def __init__(self, sections: list):
        """
        Parameters
        ----------
        sections : list[Section]
                sections of the given cross_section
        """
        super().__init__(sections)
        self._sections_maximum_strains = self._get_sections_maximum_strain()
        self._sections_minimum_strains = self._get_sections_minimum_strain()
        self._maximum_positive_curvature = self._get_maximum_positive_curvature()
        self._maximum_negative_curvature = self._get_maximum_negative_curvature()
        self._positive_start_bound = self.__get_curvature_start_values(self._maximum_positive_curvature)
        self._negative_start_bound = self.__get_curvature_start_values(self._maximum_negative_curvature)

    def __repr__(self):
        return "CrossSectionBoundaries(sections=sections)"

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_boundary_curvatures(),
            self._print_start_values(),
            # self._print_sections(),
        ]
        return print_chapter(text)

    def _print_title(self):
        return print_sections(["CrossSectionBoundaries", "----------------------"])

    def _print_initialization(self) -> str:
        return print_sections(["Initialization", "--------------", self.__repr__()])

    def _print_boundary_curvatures(self):
        text = [
            "Boundary Curvatures",
            "-------------------",
            "Positive: {:.5f}".format(self.maximum_positive_curvature.curvature),
            "\t"
            + "top_edge: {:.1f} | strain_value: {:.4f}".format(
                self.maximum_positive_curvature.top_edge_strain.position,
                self.maximum_positive_curvature.top_edge_strain.strain,
            ),
            "\t"
            + "bottom_edge: {:.1f} | strain_value: {:.4f}".format(
                self.maximum_positive_curvature.bottom_edge_strain.position,
                self.maximum_positive_curvature.bottom_edge_strain.strain,
            ),
            "Negative: {:.5f}".format(self.maximum_negative_curvature.curvature),
            "\t"
            + "top_edge: {:.1f} | strain_value: {:.4f}".format(
                self.maximum_negative_curvature.top_edge_strain.position,
                self.maximum_negative_curvature.top_edge_strain.strain,
            ),
            "\t"
            + "bottom_edge: {:.1f} | strain_value: {:.4f}".format(
                self.maximum_negative_curvature.bottom_edge_strain.position,
                self.maximum_negative_curvature.bottom_edge_strain.strain,
            ),
        ]
        return print_sections(text)

    def _print_start_values(self):
        text = [
            "Start-values",
            "------------",
            f"positive curvature: strain_value={self._positive_start_bound.strain} | "
            f"position_value={self._positive_start_bound.position}",
            f"negative curvature: strain_value={self._negative_start_bound.strain} | "
            f"position_value={self._negative_start_bound.position}",
        ]
        return print_sections(text)

    @property
    def maximum_positive_curvature(self) -> EdgeStrains:
        return self._maximum_positive_curvature

    @property
    def maximum_negative_curvature(self) -> EdgeStrains:
        return self._maximum_negative_curvature

    def get_boundaries(self) -> Boundaries:
        """
        curvature boundary values under positive and negative curvature

        The boundary values are derived from the stress-strain-curves
        applied to the sections that are associated with the given
        cross-section

        Returns
        -------
        Boundaries
            curvature boundary values under positive and negative curvature
            derived from the given material curves
        """
        return Boundaries(
            positive=self.__get_positive_boundaries(),
            negative=self.__get_negative_boundaries(),
        )

    def _get_maximum_positive_curvature(self) -> EdgeStrains:
        curvatures = determine_curvatures(
            self._sections_maximum_strains, self._sections_minimum_strains
        )
        edge_strain = min(curvatures, key=lambda x: x.curvature)
        return edge_strain

    def _get_maximum_negative_curvature(self) -> EdgeStrains:
        curvatures = determine_curvatures(
            self._sections_minimum_strains, self._sections_maximum_strains
        )
        edge_strains = max(curvatures, key=lambda x: x.curvature)
        return edge_strains

    def _get_sections_maximum_strain(self) -> list[StrainPosition]:
        position_strain = []
        for section in self.sections:
            position_strain.append(section.top_edge_maximum_strain)
            position_strain.append(section.bottom_edge_maximum_strain)
        position_strain.sort(key=lambda x: x.position)
        return position_strain

    def _get_sections_minimum_strain(self) -> list[StrainPosition]:
        position_strain = []
        for section in self.sections:
            position_strain.append(section.top_edge_minimum_strain)
            position_strain.append(section.bottom_edge_minimum_strain)
        position_strain.sort(key=lambda x: x.position)
        return position_strain

    def _create_computation_cross_section(
        self, maximum_curvature: EdgeStrains, compute_with_strain_at_top: bool, factor_curvature: float
    ) -> ComputationCrosssectionCurvature:
        """
        create a Computations-cross-section
        with given curvature and strains at bottom or at top of the section
        """
        neutral_axis_value = compute_neutral_axis(
            maximum_curvature, starts_top=compute_with_strain_at_top
        )
        return ComputationCrosssectionCurvature(
            sections=self.sections,
            curvature=factor_curvature * maximum_curvature.curvature,
            neutral_axis_value=neutral_axis_value,
        )

    def __get_curvature_start_values(self, maximum_curvature: EdgeStrains) -> StrainPosition:
        """

        computes two scenarios:
        1. change of curvature with strain on top
        2. change of curvature with strain on top

        The subsequent

        """
        cross_section_initial = self._create_computation_cross_section(
            maximum_curvature, compute_with_strain_at_top=True, factor_curvature=1.0
        )
        initial_axial_force = cross_section_initial.total_axial_force()
        # ---
        curvature_change_factor = 0.5
        # --- axial force with strain on top
        cross_section_start_with_strain_on_top = self._create_computation_cross_section(
            maximum_curvature, compute_with_strain_at_top=True, factor_curvature=curvature_change_factor
        )
        strain_on_top_axial_force = cross_section_start_with_strain_on_top.total_axial_force()
        # --- axial force with strain on bottom
        cross_section_start_with_strain_on_bottom = (
            self._create_computation_cross_section(
                maximum_curvature, compute_with_strain_at_top=False, factor_curvature=curvature_change_factor
            )
        )
        strain_on_bottom_axial_force = cross_section_start_with_strain_on_bottom.total_axial_force()
        # --- comparing the maximum change in axial-forces with similar change of curvature
        if abs(strain_on_top_axial_force-initial_axial_force) < abs(
                strain_on_bottom_axial_force-initial_axial_force
        ):
            return maximum_curvature.bottom_edge_strain
        else:
            return maximum_curvature.top_edge_strain

    def __positive_other_bound(self) -> StrainPosition:
        if (
            self._positive_start_bound
            == self.maximum_positive_curvature.top_edge_strain
        ):
            return self.maximum_positive_curvature.bottom_edge_strain
        else:
            return self.maximum_positive_curvature.top_edge_strain

    def __negative_other_bound(self) -> StrainPosition:
        if (
            self._negative_start_bound
            == self.maximum_negative_curvature.top_edge_strain
        ):
            return self.maximum_negative_curvature.bottom_edge_strain
        else:
            return self.maximum_negative_curvature.top_edge_strain

    def __get_positive_boundaries(self) -> BoundaryValues:
        """
        get the curvature boundary-values of the cross-section
        in case of positive curvature

        Returns
        -------
        BoundaryValues
            maximum and minimum curvature (see :class:`curvature_boundaries:BoundaryValues`)
        """
        return BoundaryValues(
            maximum_curvature=MaximumCurvature(
                curvature=self.maximum_positive_curvature.curvature,
                start=self._positive_start_bound,
                other=self.__positive_other_bound(),
                maximum_positive_section_strains=self._sections_maximum_strains,
                maximum_negative_section_strains=self._sections_minimum_strains,
            ),
            minimum_curvature=MinimumCurvature(
                self._sections_maximum_strains,
                self._sections_minimum_strains,
                curvature_is_positive=True,
            ),
        )

    def __get_negative_boundaries(self) -> BoundaryValues:
        """
        get the curvature boundary-values of the cross-section
        in case of negative curvature

        Returns
        -------
        BoundaryValues
            maximum and minimum curvature (see `class:BoundaryValues`)
        """
        return BoundaryValues(
            maximum_curvature=MaximumCurvature(
                curvature=self.maximum_negative_curvature.curvature,
                start=self._negative_start_bound,
                other=self.__negative_other_bound(),
                maximum_positive_section_strains=self._sections_maximum_strains,
                maximum_negative_section_strains=self._sections_minimum_strains,
            ),
            minimum_curvature=MinimumCurvature(
                self._sections_maximum_strains,
                self._sections_minimum_strains,
                curvature_is_positive=False,
            ),
        )