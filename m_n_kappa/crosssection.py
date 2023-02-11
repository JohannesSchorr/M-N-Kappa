from .general import (
    str_start_end,
    print_chapter,
    print_sections,
    neutral_axis,
    remove_duplicates,
    StrainPosition,
    EffectiveWidths,
    EdgeStrains,
)
from .section import (
    Section,
    ComputationSection,
    ComputationSectionStrain,
    ComputationSectionCurvature,
)

from .boundaries import (
    MaximumCurvature,
    MinimumCurvature,
    Boundaries,
    BoundaryValues,
    DecisiveNeutralAxis,
)

from .log import LoggerMethods

log = LoggerMethods(__name__)


def axial_force(sections: list[ComputationSection]) -> float:
    """
    compute the sum of axial-force from a list of computed sections

    .. versionadded:: 0.1.0

    Parameters
    ----------
    sections : list[:py:class:`~m_n_kappa.section.ComputationSection`]
        individual computed sections where the axial-forces are taken from

    Returns
    -------
    float
        sum of axial-forces from the computed sections

    See Also
    --------
    moment : computes the sum of moments

    Notes
    -----
    In mathematical notation the computation of the sum of axial forces :math:`N`
    looks like this.

    .. math::
       N = \\sum_i N_i
    """
    axial_forces = [section.axial_force for section in sections]
    return sum(axial_forces)


def moment(sections: list[ComputationSection]):
    """
    compute the sum of moments from a list of computed sections

    .. versionadded:: 0.1.0

    Parameters
    ----------
    sections : list[:py:class:`~m_n_kappa.section.ComputationSection`]
        individual computed sections where the moments are taken from

    Returns
    -------
    float
        sum of moments from the computed sections

    See Also
    --------
    axial_force : computes the sum of axial-forces

    Notes
    -----
    In mathematical notation the computation of the sum of axial forces :math:`N`
    looks like this.

    .. math::
       M = \\sum_i M_i
    """
    moments = [section.moment() for section in sections]
    return sum(moments)


class Crosssection:

    """
    Combines a number of sections

    .. versionadded:: 0.1.0
    """

    @log.init
    def __init__(
        self,
        sections: list[Section] = None,
        slab_effective_widths: EffectiveWidths = None,
    ):
        """
        Parameters
        ----------
        sections : list[:py:class:`~m_n_kappa.Section`]
            sections the cross-section consists of
        slab_effective_widths : :py:class:`~m_n_kappa.EffectiveWidths`
            effective widths' for the slab (concrete and reinforcement)

        Examples
        --------
        There are several ways you can create a cross-section.
        Basis are either a number of :py:class:`~m_n_kappa.Section`.

        >>> from m_n_kappa import Concrete, Steel, Rectangle
        >>> concrete = Concrete(f_cm=35.0)
        >>> concrete_geometry_1 = Rectangle(
        ...     top_edge=0.0, bottom_edge=10.0, width=10.0, left_edge=-10.0)
        >>> concrete_section_1 = concrete + concrete_geometry_1
        >>> steel = Steel(f_y=355.0)
        >>> steel_geometry = Rectangle(
        ...     top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> steel_section = steel + steel_geometry

        The above create :py:class:`~m_n_kappa.Section` may be combined to a cross-section like:

        >>> cross_section_top = steel_section + concrete_section_1
        >>> cross_section_top
        Crosssection(sections=sections)

        Or alternatively like:

        >>> from m_n_kappa import Crosssection
        >>> sections_list = [steel_section, concrete_section_1]
        >>> cross_section_bottom = Crosssection(sections=sections_list)
        >>> cross_section_bottom
        Crosssection(sections=sections)

        This is also the only way nn case an :py:class:`~m_n_kappa.EffectiveWidths` is to be applied.

        >>> from m_n_kappa import EffectiveWidths
        >>> widths = EffectiveWidths(membran=2.0, bending=3.0)
        >>> cross_section_3 = Crosssection(
        ...     sections=sections_list, slab_effective_widths=widths)
        >>> cross_section_3.slab_effective_width.bending
        3.0

        By using a predifined :py:class:`~m_n_kappa.ComposedGeometry` a :py:class:`~m_n_kappa.Crosssection` may
        also be created easily:

        >>> from m_n_kappa import IProfile
        >>> i_geometry = IProfile(
        ...     top_edge=0.0, t_w=9.5, h_w=200-15*2 , t_fo=15.0, b_fo=200)
        >>> cross_section_4 = i_geometry + steel
        >>> cross_section_4
        Crosssection(sections=sections)

        Another :py:class:`~m_n_kappa.Section` may be added also on different ways:

        >>> concrete_geometry_2 = Rectangle(
        ...     top_edge=0.0, bottom_edge=10.0, width=10.0, left_edge=0.0)
        >>> concrete_section_2 = concrete + concrete_geometry_2
        >>> cross_section_top = cross_section_top + concrete_section_2
        >>> len(cross_section_top.sections)
        3

        >>> cross_section_bottom.add_section(concrete_section_2)
        >>> len(cross_section_bottom.sections)
        3

        Subsequently, the :py:class:`~m_n_kappa.Crosssection` is needed for all computations.
        """
        self._sections = sections
        self._slab_effective_widths = slab_effective_widths
        self._top_edge = self.__compute_top_edge()
        self._bottom_edge = self.__compute_bottom_edge()

    # TODO: check if rebars are within the concrete slab

    @property
    def slab_effective_width(self) -> EffectiveWidths:
        """effective widths of the (concrete) slab"""
        return self._slab_effective_widths

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(sections=sections)"

    def __iter__(self):
        self._section_iterator = iter(self.sections)
        return self

    def __next__(self):
        return self._section_iterator.__next__()

    def __add__(self, other):
        return self._build_cross_section(other)

    def __radd__(self, other):
        return self._build_cross_section(other)

    def __eq__(self, other) -> bool:
        """two cross-sections are the same if they have the same sections"""
        if self.slab_effective_width == other.slab_effective_width:
            for section in self.sections:
                if section not in other.sections:
                    return False
        return True

    def _build_cross_section(self, other):
        if isinstance(other, Crosssection):
            sections = self.sections + other.sections
            log.info("Merged two Crosssection")
            return Crosssection(sections)
        elif isinstance(other, Section):
            self.add_section(other)
            log.info(f"Add {other.__repr__()} to Crosssection")
            return self
        else:
            raise TypeError(
                f'unsupported operand section_type(s) for +: "{type(self)}" and "{type(other)}"'
            )

    @str_start_end
    def __str__(self) -> str:
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

    def _print_geometry(self) -> str:
        text = [
            "Geometry",
            "--------",
            "top_edge: {:.1f} | bottom_edge: {:.1f}".format(
                self.top_edge, self.bottom_edge
            ),
        ]
        return print_sections(text)

    def _print_sections(self) -> str:
        text = [
            "Sections",
            "--------",
        ]
        for section in self.sections:
            text.append(section.__repr__())
        return print_sections(text)

    @property
    def bottom_edge(self) -> float:
        """overall vertical position of the bottom edge of the cross-section :math:`z_\\mathrm{bottom}`"""
        return self._bottom_edge

    @property
    def girder_sections(self) -> list:
        """:py:class:`~m_n_kappa.Section` belonging to te girder"""
        return self.sections_of_type(section_type="girder")

    @property
    def height(self) -> float:
        """height of the cross-section"""
        return self.bottom_edge - self.top_edge

    @property
    def half_point(self) -> float:
        """vertical middle between and bottom"""
        return 0.5 * (self.bottom_edge + self.top_edge)

    @property
    def sections(self) -> list[Section]:
        """all sections associated with this cross-section"""
        return self._sections

    @property
    def slab_sections(self) -> list[Section]:
        """all slab-sections of this cross-section"""
        return self.sections_of_type(section_type="slab")

    @property
    def section_type(self) -> str:
        """
        section-type this cross-section is associated with,
        if it is only one
        """
        if len(self.girder_sections) > 0 and len(self.slab_sections) == 0:
            return "girder"
        elif len(self.girder_sections) == 0 and len(self.slab_sections) > 0:
            return "slab"

    @property
    def top_edge(self) -> float:
        """top-edge of the cross-section :math:`z_\\mathrm{top}`"""
        return self._top_edge

    def add_section(self, section: Section) -> None:
        """
        add a :py:class:`~m_n_kappa.Section` to this cross-section

        Parameters
        ----------
        section : :py:class:`~m_n_kappa.Section`
            section to add to this cross-section

        Returns
        -------
        None

        Raises
        ------
        ValueError
            if ``section`` is not of type :py:class:`~m_n_kappa.Section`
        """
        if not isinstance(section, Section):
            raise ValueError(
                f"section is type '{type(Section)}', " f"must be of type 'Section'"
            )
        if self.sections is None:
            self._sections = [section]
        else:
            self._sections.append(section)

    def sections_of_type(self, section_type: str) -> list[Section]:
        """
        get a list of sections that are of the specified type associated with this cross-section

        Associated sections are listed in property `sections`.
        Therefore, these sections must have been added before to this cross-section.

        Parameters
        ----------
        section_type : str
            type of section to search for.
            Possible section-types are:

            - ``'slab'``   -> concrete slab + reinforcement
            - ``'girder'`` -> Steel girder

        Returns
        -------
        list[:py:class:`~m_n_kappa.Section`]
            sections of the specified type associated with this cross-section
        """
        return [
            section for section in self.sections if section.section_type == section_type
        ]

    def sections_not_of_type(self, section_type: str) -> list[Section]:
        """
        get a list of sections that are not of the specified typ

        Parameters
        ----------
        section_type : str
            type of section to search for.
            Possible section-types are:

            - ``'slab'``   -> concrete slab + reinforcement
            - ``'girder'`` -> Steel girder

        Returns
        -------
        list[:py:class:`~m_n_kappa.Section`]
            sections of the specified type associated with this cross-section
        """
        return [
            section for section in self.sections if section.section_type != section_type
        ]

    def get_boundary_conditions(self) -> Boundaries:
        """
        curvature boundary values under positive and negative curvature

        Returns
        -------
        :py:class:`~m_n_kappa.boundaries.Boundaries`
            curvature boundary values under positive and negative curvature

        See Also
        --------
        :py:meth:`~m_n_kappa.crosssection.CrossSectionBoundaries.get_boundaries`
        """
        cross_section_boundaries = CrossSectionBoundaries(self.sections)
        return cross_section_boundaries.get_boundaries()

    def decisive_maximum_positive_strain_position(self) -> StrainPosition:
        """minimum of all maximum positive strains"""
        return min(
            [section.maximum_positive_strain_position() for section in self.sections],
            key=lambda x: x.strain,
        )

    def decisive_maximum_negative_strain_position(self) -> StrainPosition:
        """minimum of all maximum negative strains"""
        return max(
            [section.maximum_negative_strain_position() for section in self.sections],
            key=lambda x: x.strain,
        )

    def maximum_positive_strain(self) -> float:
        """
        determine maximum positive strain of all sections
        associated with this cross-section
        """
        return max([section.maximum_positive_strain() for section in self.sections])

    def maximum_negative_strain(self) -> float:
        """
        determine maximum positive strain of all sections
        associated with this cross-section
        """
        return min([section.maximum_negative_strain() for section in self.sections])

    def __compute_top_edge(self) -> float:
        """compute top-edge of cross-section"""
        if len(self.sections) == 0:
            return 0.0
        top_edges = [min(section.geometry.edges) for section in self.sections]
        return min(top_edges)

    def __compute_bottom_edge(self) -> float:
        """compute bottom-edge of cross-section"""
        if len(self.sections) == 0:
            return 0.0
        bottom_edges = [max(section.geometry.edges) for section in self.sections]
        return max(bottom_edges)

    def _concrete_sections(self) -> list[Section]:
        """get all sections with material :py:class:~m_n_kappa.material.Concrete`"""
        return [
            section
            for section in self.sections
            if section.material.__class__.__name__ == "Concrete"
        ]

    def left_edge(self) -> float:
        """
        outer left-edge of the concrete-slab

        .. warning::

            will fail in case concrete is a trapezoid or a circle
        """
        concrete_sections = self._concrete_sections()
        return min(
            concrete_sections, key=lambda x: x.geometry.left_edge
        ).geometry.left_edge

    def right_edge(self) -> float:
        """
        outer right-edge of the concrete-slab

        .. warning::

            will fail in case concrete is a trapezoid or a circle
        """
        concrete_sections = self._concrete_sections()
        return max(
            concrete_sections, key=lambda x: x.geometry.right_edge
        ).geometry.right_edge

    def concrete_slab_width(self) -> float:
        """full width of the concrete slab"""
        return self.right_edge() - self.left_edge()


class ComputationCrosssection(Crosssection):

    """
    Base for computed cross-sections

    .. versionadded: 0.1.0
    """

    @log.init
    def __init__(
        self,
        sections: list[Section] | Crosssection = None,
        slab_effective_width: EffectiveWidths = None,
    ):
        """
        This class is initialized by the classes that inherit from it.

        See Also
        --------
        ComputationCrosssectionStrain: cross-section that is loaded only by axial-forces
        ComputationCrosssectionCurvature: cross-section computing curvatures
        """
        if isinstance(sections, Crosssection):
            if slab_effective_width is None:
                slab_effective_width = sections.slab_effective_width
            sections = sections.sections
        super().__init__(sections, slab_effective_width)
        self._compute_sections = None

    @str_start_end
    def __str__(self) -> str:
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
    def compute_sections(self) -> list[ComputationSection]:
        """:py:class:`~m_n_kappa.Section` in ``sections``
        transformed into :py:class:`~m_n_kappa.section.ComputationSection`"""
        return self._compute_sections

    @compute_sections.setter
    def compute_sections(self, compute_sections: list[ComputationSection]):
        self._compute_sections = compute_sections

    @property
    def compute_split_sections(self) -> list[ComputationSection]:
        """split computation sections"""
        return self.compute_sections

    @property
    def computed_slab_sections(self) -> list:
        """sections of the slab (computed)"""
        return self._computed_sections_of_type(section_type="slab")

    @property
    def computed_girder_sections(self) -> list:
        """sections of the girder (computed)"""
        return self._computed_sections_of_type(section_type="girder")

    def girder_sections_axial_force(self) -> float:
        """summarized axial force of the girder sections"""
        return axial_force(self.computed_girder_sections)

    def girder_sections_moment(self) -> float:
        """summarized moment of the girder sections"""
        return moment(self.computed_girder_sections)

    def slab_sections_axial_force(self) -> float:
        """summarized axial forces of the slab sections"""
        return axial_force(self.computed_slab_sections)

    def slab_sections_moment(self) -> float:
        """summarized moments of the slab sections"""
        return moment(self.computed_slab_sections)

    def total_axial_force(self) -> float:
        """summarized axial forces of the cross_section"""
        return axial_force(self.compute_split_sections)

    def total_moment(self) -> float:
        """summarized moments of the cross_section"""
        return moment(self.compute_split_sections)

    def _computed_sections_of_type(self, section_type: str) -> list:
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

    def _print_all_sections_results(self) -> str:
        text = [
            f"All sections (n = {len(self.sections)}/{len(self.compute_sections)}):",
            "\t" + "N = {:.1f} N".format(self.total_axial_force()),
            "\t" + "M = {:.1f} Nmm".format(self.total_moment()),
        ]
        return print_sections(text)

    def _print_girder_sections_results(self) -> str:
        text = [
            f"Girder sections (n = {len(self.girder_sections)}/{len(self.computed_girder_sections)}):",
            "\t" + "N_a = {:.1f} N".format(self.girder_sections_axial_force()),
            "\t" + "M_a = {:.1f} Nmm".format(self.girder_sections_moment()),
        ]
        return print_sections(text)

    def _print_slab_sections_results(self) -> str:
        text = [
            f"Slab sections (n = {len(self.slab_sections)}/{len(self.computed_slab_sections)}):",
            "\t" + "N_c = {:.1f} N".format(self.slab_sections_axial_force()),
            "\t" + "M_c = {:.1f} Nmm".format(self.slab_sections_moment()),
        ]
        return print_sections(text)

    def _print_sections_results(self) -> str:
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

    """
    computes a cross-section under a constant strain_value
    assuming zero curvature

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_strain",
        "_compute_sections",
        "_bottom_edge",
        "_top_edge",
        "_slab_effective_widths",
    )

    @log.init
    def __init__(
        self,
        sections: list[Section] | Crosssection,
        strain: float,
        slab_effective_widths: EffectiveWidths = None,
    ):
        """
        Parameters
        ----------
        sections : list[:py:class:`~m_n_kappa.Section`] | :py:class:`~m_n_kappa.Crosssection`
            sections the cross_section consists of
        strain : float
            applied constant strain_value :math:`\\varepsilon`
        slab_effective_widths: :py:class:`~m_n_kappa.EffectiveWidths`
            effective widths’ for the slab (concrete and reinforcement)

        See Also
        --------
        ComputationCrosssectionCurvature : computes a cross-section under a strain-distribution initialized
           by a curvature and a neutral-axis-value

        Examples
        --------
        >>> from m_n_kappa import IProfile, Steel
        >>> steel = Steel(f_y=355.0)
        >>> i_geometry = IProfile(
        ...     top_edge=0.0, t_w=9.5, h_w=200-15*2 , t_fo=15.0, b_fo=200)
        >>> cross_section = i_geometry + steel

        To apply a ``strain`` onto the cross-section :py:class:`~m_n_kappa.crosssection.ComputationCrosssectionStrain`
        has to be initialized as follows.

        >>> from m_n_kappa.crosssection import ComputationCrosssectionStrain
        >>> compute_cross_section = ComputationCrosssectionStrain(
        ...     sections=cross_section, strain=0.001)

        The total axial-force is given by calling
        :py:meth:`~m_n_kappa.crosssection.ComputationCrosssectionStrain.total_axial_force()` as follows.

        >>> compute_cross_section.total_axial_force()
        1599150.0

        The axial-force carryied by the slab (concrete + reinforcement) is computed by calling
        :py:meth:`~m_n_kappa.crosssection.ComputationCrosssectionStrain.slab_sections_axial_force()`.

        >>> compute_cross_section.slab_sections_axial_force()
        0

        Whereas the axial-force of the streel-girder is computed by
        :py:meth:`~m_n_kappa.crosssection.ComputationCrosssectionStrain.girder_sections_axial_force()`.

        >>> compute_cross_section.girder_sections_axial_force()
        1599150.0
        """
        super().__init__(sections, slab_effective_widths)
        self._strain = strain
        self._compute_sections = self._create_computation_sections()

    def __repr__(self) -> str:
        return f"ComputationCrosssectionStrain(sections=sections, strain_value={self.strain})"

    def __add__(self, other):
        return ComputationCrosssectionStrainAdd(self, other)

    @property
    def strain(self) -> float:
        """applied strain_value to the cross_section"""
        return self._strain

    @property
    def compute_split_sections(self) -> list:
        return self.compute_sections

    def _create_computation_sections(self) -> list[ComputationSectionStrain]:
        """transforms each :py:class:`~m_n_kappa.Section`
        into :py:class:`~m_n_kappa.section.ComputationSectionStrain`"""
        return [self._create_section(section) for section in self.sections]

    def _create_section(self, basic_section: Section) -> ComputationSectionStrain:
        """transform :py:class:`~m_n_kappa.Section` into
        :py:class:`~m_n_kappa.section.ComputationSection` under given ``strain``"""
        return ComputationSectionStrain(basic_section, self.strain)

    def _print_results(self) -> str:
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


class ComputationCrosssectionStrainAdd(ComputationCrosssectionStrain):
    """
    result of adding two ComputationCrosssectionStrain-classes to each other

    .. versionadded: 0.1.0

    If the relative displacement between two cross-sections is important, these have
    to be looked at independent of each other.
    This class provides the functionality to compute this relative displacement.
    """

    def __init__(
        self,
        computed_cross_section_1: ComputationCrosssectionStrain,
        computed_cross_section_2: ComputationCrosssectionStrain,
    ):
        """
        Parameters
        ----------
        computed_cross_section_1 : :py:class:`~m_n_kappa.crosssection.ComputationCrosssectionStrain`
            1st computed strain cross-section
        computed_cross_section_2 : :py:class:`~m_n_kappa.crosssection.ComputationCrosssectionStrain`
            2nd computed strain cross-section

        See Also
        --------
        ComputationCrosssectionStrain : computed cross-section under a constant strain_value

        Examples
        --------
        This example looks at a composite beam.
        Therefore, first the concrete-slab is created.

        >>> from m_n_kappa import Concrete, Rectangle, Crosssection
        >>> concrete = Concrete(f_cm=35.0)
        >>> concrete_slab = Rectangle(
        ...     top_edge=0.0, bottom_edge=100.0, width=2000.0)
        >>> concrete_section = concrete + concrete_slab
        >>> concrete_cross_section = Crosssection(sections=[concrete_section])

        Then a steel-beam is created.

        >>> from m_n_kappa import IProfile, Steel
        >>> steel = Steel(f_y=355)
        >>> i_profile = IProfile(
        ...     top_edge=100.0, t_w=9.5, h_w=200-2*15, b_fo=200.0, t_fo=15.0)
        >>> steel_cross_section = i_profile + steel

        >>> from m_n_kappa.crosssection import ComputationCrosssectionStrain

        .. todo::
           finish doc-string
        """
        self._computed_cross_section_1 = computed_cross_section_1
        self._computed_cross_section_2 = computed_cross_section_2

    # TODO: finish doc-string - this class is of importance for m-n-kappa, not for m-kappa, therefore skipped now.

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
            self.computed_cross_section_1.top_edge,
            self.computed_cross_section_2.top_edge,
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

    """
    computes a cross-section given a curvature and a neutral axis

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_sections",
        "_curvature",
        "_neutral_axis",
        "_bottom_edge",
        "_top_edge",
        "_slab_effective_widths",
        "_girder_effective_widths",
    )

    @log.init
    def __init__(
        self,
        cross_section: Crosssection | list[Section],
        curvature: float,
        neutral_axis_value: float,
        slab_effective_width: EffectiveWidths = None,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection` | list[:py:class:`~m_n_kappa.Section`]
            the cross-section
        curvature : float
            curvature to compute values
        neutral_axis_value : float
            position_value where strain_value is zero
        slab_effective_width: :py:class:`~m_n_kappa.EffectiveWidths`
            effective widths’ for the slab (concrete and reinforcement)

        See Also
        --------
        ComputationCrosssectionStrain : computes a cross-section under a constant strain_value

        Examples
        --------
        For example a HEB 200 steel girder is computed.
        First it is created as follows.

        >>> from m_n_kappa import IProfile, Steel
        >>> steel = Steel(f_y=355, failure_strain=0.15)
        >>> i_profile = IProfile(
        ...     top_edge=0.0, t_w=9.5, h_w=200-2*15, b_fo=200.0, t_fo=15.0)
        >>> steel_cross_section = i_profile + steel

        To compute the girder a ``curvature``-value as well as a ``neutral_axis_value`` needs to be passed
        to :py:class:`~m_n_kappa.crosssection.ComputationCrosssectionCurvature`.

        >>> from m_n_kappa.crosssection import ComputationCrosssectionCurvature
        >>> computed_cross_section = ComputationCrosssectionCurvature(
        ...     cross_section=steel_cross_section, curvature=0.0001, neutral_axis_value=100.0)

        As the ``neutral_axis_value`` is chosen to be in the mid-height of the cross-section, (almost) zero
        axial-forces are computed.

        >>> round(computed_cross_section.total_axial_force(), 7)
        -0.0

        The moment on the other hand is much higher and assuming Newton and Millimeter as input is here
        computed to Kilo-Newton-Meter.

        >>> computed_cross_section.total_moment() * 0.001 * 0.001
        221.07005829554043

        """
        super().__init__(cross_section, slab_effective_width)
        self._curvature = curvature
        self._neutral_axis = neutral_axis_value
        self._compute_sections: list[
            ComputationSectionCurvature
        ] = self._create_computation_sections()
        self._compute_split_sections = self._create_computation_split_sections()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"sections=sections, "
            f"curvature={self.curvature}, "
            f"neutral_axis_value={self.neutral_axis})"
        )

    @property
    def compute_split_sections(self) -> list[ComputationSectionCurvature]:
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
        for compute_section in self.compute_sections:
            strain_positions += compute_section.material_points_inside_curvature()
        strain_positions = remove_duplicates(strain_positions)
        return strain_positions

    def _create_computation_sections(self) -> list[ComputationSectionCurvature]:
        return [self._create_section(section) for section in self.sections]

    def _create_section(self, basic_section: Section) -> ComputationSectionCurvature:
        return ComputationSectionCurvature(
            basic_section, self.curvature, self.neutral_axis
        )

    def _create_computation_split_sections(self) -> list[ComputationSectionCurvature]:
        split_sections = []
        for compute_section in self.compute_sections:
            split_sections += compute_section.split_section(self.slab_effective_width)
        return split_sections

    def _print_results(self) -> str:
        text = [
            "Stress-strain_value distribution",
            "--------------------------",
            "",
            "  top edge | top strain | top stress | bot edge | bot strain | bot stress | axi. force | section | material ",
            "-" * 108,
        ]
        for section in self.compute_split_sections:
            text.append(section._print_result())
        text.append("-" * 108)
        return print_sections(text)


def determine_curvatures(
    bottom_edge_strains: list[StrainPosition],
    top_edge_strains: list[StrainPosition],
) -> list[EdgeStrains]:
    """
    determine curvatures by combining the bottom- and
    top-edge-strains

    .. versionadded:: 0.1.0

    :py:class:`~m_n_kappa.general.EdgeStrains` allow to compute the corresponding curvature

    Parameters
    ----------
    bottom_edge_strains: list[:py:class:`~m_n_kappa.StrainPosition`]
        strains and position at the bottom-edges of all sections
    top_edge_strains: list[:py:class:`~m_n_kappa.StrainPosition`]
        strains and corresponding positions at the top-edges of all sections

    Returns
    -------
    list[:py:class:`~m_n_kappa.general.EdgeStrains`]
        list of strains at top and bottom edge
    """
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

    .. versionadded:: 0.1.0

    Parameters
    ----------
    edge_strains : EdgeStrains
        edge-strains to compute
    starts_top : bool
        which edge-strain is to be used for computing the neutral axis

        - ``True``: edge-strain at top
        - ``False``: edge-strain at bottom

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

    .. versionadded:: 0.1.0

    :py:meth:`~m_n_kappa.crosssection.CrossSectionBoundaries.get_boundaries`
    gives the curvature boundary values under positive and negative curvature
    """

    __slots__ = (
        "_sections_maximum_strains",
        "_sections_minimum_strains",
        "_positive_start_bound",
        "_negative_start_bound",
        "_maximum_positive_curvature",
        "_maximum_negative_curvature",
    )

    @log.init
    def __init__(self, sections: list):
        """
        Parameters
        ----------
        sections : list[Section]
            sections of the given cross_section

        Examples
        --------
        First the sections for the cross-section are created.

        >>> from m_n_kappa import Concrete, Steel, Rectangle
        >>> concrete = Concrete(f_cm=35.0)
        >>> concrete_geometry_1 = Rectangle(
        ...     top_edge=0.0, bottom_edge=10.0, width=10.0, left_edge=-10.0)
        >>> concrete_section_1 = concrete + concrete_geometry_1
        >>> steel = Steel(f_y=355, failure_strain=0.15)
        >>> steel_geometry = Rectangle(
        ...     top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> steel_section = steel + steel_geometry


        These sections are passed to :py:class:`~m_n_kappa.crosssection.CrossSectionBoundaries` in form of a
        list.

        >>> from m_n_kappa.crosssection import CrossSectionBoundaries
        >>> cross_section_boundaries = CrossSectionBoundaries(sections=[concrete_section_1, steel_section])

        :py:class:`~m_n_kappa.crosssection.CrossSectionBoundaries.get_boundaries` gives us then a
        :py:class:`~m_n_kappa.curvature_boundaries.Boundaries` class, where a variety of values are saved regarding
        the boundaries of our cross-section.

        >>> boundaries = cross_section_boundaries.get_boundaries()

        The following values are given for positive and negative curvature.
        In case of values under negative curvature only ``boundaries.negative`` plus the desired property is to
        be called.
        Hereafter, only examples under positive curvature are given.

        The maximum positive curvature is given as follows:

        >>> boundaries.positive.maximum_curvature.curvature
        0.0076749999999999995

        The boundary-condition representing the point of failure is given as follows:

        >>> boundaries.positive.maximum_curvature.start
        StrainPosition(strain=-0.0035, position=0.0, material='Concrete')

        Whereas method ``compute`` gives as the maximum curvature assuming another :py:class:`~m_n_kappa.StrainPosition`
        points.

        >>> from m_n_kappa import StrainPosition
        >>> boundaries.positive.maximum_curvature.compute(StrainPosition(-0.0035, 0, 'Concrete'))
        0.0076749999999999995

        :py:meth:`~m_n_kappa.Crosssection.get_boundaries` implements the above given behaviour and returns the
        boundary values directly without using :py:class:`~m_n_kappa.crosssection.CrossSectionBoundaries`.
        """
        super().__init__(sections)
        self._sections_maximum_strains = self._get_sections_maximum_strain()
        self._sections_minimum_strains = self._get_sections_minimum_strain()
        self._maximum_positive_curvature = self._get_maximum_positive_curvature()
        self._maximum_negative_curvature = self._get_maximum_negative_curvature()
        log.info("-------\nPositive_start_bound")
        self._positive_start_bound = self.__get_curvature_start_values(
            self._maximum_positive_curvature
        )
        log.info("-------\nNegative_start_bound")
        self._negative_start_bound = self.__get_curvature_start_values(
            self._maximum_negative_curvature
        )

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
        """
        :py:class:`~m_n_kappa.general.EdgeStrains` reaching the maximum possible
        positive curvature
        """
        return self._maximum_positive_curvature

    @property
    def maximum_negative_curvature(self) -> EdgeStrains:
        """
        :py:class:`~m_n_kappa.general.EdgeStrains` reaching the maximum
        possible negative curvature
        """
        return self._maximum_negative_curvature

    def get_boundaries(self) -> Boundaries:
        """
        curvature boundary values under positive and negative curvature

        .. versionadded:: 0.2.0
               ``neutral_axes`` to compute the highest and lowest position of
               the neutral axis under a given curvature

        The boundary values are derived from the stress-strain-curves
        applied to the sections that are associated with the given
        cross-section

        Returns
        -------
        :py:class:`~m_n_kappa.boundaries.Boundaries`
            curvature boundary values under positive and negative curvature
            derived from the given material curves
        """
        return Boundaries(
            positive=self.__get_positive_boundaries(),
            negative=self.__get_negative_boundaries(),
            neutral_axes=DecisiveNeutralAxis(
                self._sections_maximum_strains, self._sections_minimum_strains
            ),
        )

    @log.result
    def _get_maximum_positive_curvature(self) -> EdgeStrains:
        """
        Returns
        -------
        :py:class:`~m_n_kappa.general.EdgeStrains`
           maximum possible positive curvature for the given cross-section
        """
        curvatures = determine_curvatures(
            self._sections_maximum_strains, self._sections_minimum_strains
        )
        edge_strain = min(curvatures, key=lambda x: x.curvature)
        return edge_strain

    @log.result
    def _get_maximum_negative_curvature(self) -> EdgeStrains:
        """
        Returns
        -------
        :py:class:`~m_n_kappa.general.EdgeStrains`
           maximum possible negative curvature for the given cross-section
        """
        curvatures = determine_curvatures(
            self._sections_minimum_strains, self._sections_maximum_strains
        )
        edge_strains = max(curvatures, key=lambda x: x.curvature)
        return edge_strains

    def _get_sections_maximum_strain(self) -> list[StrainPosition]:
        """
        Returns
        -------
        list[:py:class:`~m_n_kappa.general.StrainPosition`]
            maximum strains and their position from each section of the
            given cross-section
        """
        position_strain = []
        for section in self.sections:
            position_strain.append(section.top_edge_maximum_strain)
            position_strain.append(section.bottom_edge_maximum_strain)
        position_strain.sort(key=lambda x: x.position)
        return position_strain

    def _get_sections_minimum_strain(self) -> list[StrainPosition]:
        """
        Returns
        -------
        list[:py:class:`~m_n_kappa.general.StrainPosition`]
            minium strains (or maximum negative strains) and their position from each section of the
            given cross-section
        """
        position_strain = []
        for section in self.sections:
            position_strain.append(section.top_edge_minimum_strain)
            position_strain.append(section.bottom_edge_minimum_strain)
        position_strain.sort(key=lambda x: x.position)
        return position_strain

    def _create_computation_cross_section(
        self,
        maximum_curvature: EdgeStrains,
        compute_with_strain_at_top: bool,
        factor_curvature: float,
    ) -> ComputationCrosssectionCurvature:
        """
        create a Computations-cross-section
        with given curvature and strains at bottom or at top of the section
        """
        if compute_with_strain_at_top:
            position_strain = maximum_curvature.top_edge_strain
        else:
            position_strain = maximum_curvature.bottom_edge_strain
        neutral_axis_value = neutral_axis(
            curvature_value=factor_curvature * maximum_curvature.curvature,
            strain_at_position=position_strain.strain,
            position_value=position_strain.position,
        )
        log.debug(
            f"{maximum_curvature},\n\t"
            f"Use strain on top: {compute_with_strain_at_top},\n\t"
            f"{position_strain},\n\t"
            f"curvature: {maximum_curvature.curvature}, with factor {factor_curvature}: "
            f"{maximum_curvature.curvature * factor_curvature}\n\t"
            f"Neutral axis: {neutral_axis_value:.1f}"
        )
        return ComputationCrosssectionCurvature(
            cross_section=Crosssection(self.sections, self.slab_effective_width),
            curvature=factor_curvature * maximum_curvature.curvature,
            neutral_axis_value=neutral_axis_value,
        )

    def __get_curvature_start_values(
        self, maximum_curvature: EdgeStrains, curvature_change_factor: float = 0.9
    ) -> StrainPosition:
        """

        computes two scenarios:
        1. change of curvature with strain on top
        2. change of curvature with strain on bottom

        The subsequent

        """
        cross_section_initial = self._create_computation_cross_section(
            maximum_curvature, compute_with_strain_at_top=True, factor_curvature=1.0
        )
        initial_axial_force = cross_section_initial.total_axial_force()
        # --- axial force with strain on top
        cross_section_start_with_strain_on_top = self._create_computation_cross_section(
            maximum_curvature,
            compute_with_strain_at_top=True,
            factor_curvature=curvature_change_factor,
        )
        strain_on_top_axial_force = (
            cross_section_start_with_strain_on_top.total_axial_force()
        )
        # --- axial force with strain on bottom
        cross_section_start_with_strain_on_bottom = (
            self._create_computation_cross_section(
                maximum_curvature,
                compute_with_strain_at_top=False,
                factor_curvature=curvature_change_factor,
            )
        )
        strain_on_bottom_axial_force = (
            cross_section_start_with_strain_on_bottom.total_axial_force()
        )
        # --- comparing the maximum change in axial-forces with similar change of curvature
        if abs(strain_on_top_axial_force - initial_axial_force) > abs(
            strain_on_bottom_axial_force - initial_axial_force
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
