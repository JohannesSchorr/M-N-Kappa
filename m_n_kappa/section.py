from .general import (
    str_start_end,
    print_chapter,
    print_sections,
    position,
    strain,
    StrainPosition,
    EffectiveWidths,
)

from .log import LoggerMethods

log = LoggerMethods(__name__)


class Section:

    """
    Combines material and geometric entity

    .. versionadded:: 0.1.0
    """

    @log.init
    def __init__(self, geometry, material):
        """
        Parameters
        ----------
        geometry : :py:class:`~m_n_kappa.geometry.Geometry`
            geometry of the section, e.g. :py:class:`~m_n_kappa.Rectangle`, :py:class:`~m_n_kappa.Circle`
            or :py:class:`~m_n_kappa.Trapezoid`
        material: :py:class:`~m_n_kappa.material.Material`
            material of the section, e.g. :py:class:`~m_n_kappa.Steel`, :py:class:`~m_n_kappa.Reinforcement`
            or :py:class:`~m_n_kappa.Concrete`

        Examples
        --------
        A section may be created in two ways.
        In both cases a :py:class:`~m_n_kappa.Material` and a :py:class:`~m_n_kappa.Geometry` instance
        is needed.

        >>> from m_n_kappa import Steel, Rectangle
        >>> steel = Steel(f_y=355.0)
        >>> rectangle = Rectangle(top_edge=0.0, bottom_edge=10, width=10.0)

        The first way is by simply adding the ``steel`` (:py:class:`~m_n_kappa.Material` instance)
        and a ``rectangle`` (:py:class:`~m_n_kappa.Geometry` instance).

        >>> section_top = steel + rectangle
        >>> section_top
        Section(\
geometry=Rectangle(top_edge=0.00, bottom_edge=10.00, width=10.00, left_edge=-5.00, right_edge=5.00), \
material=Steel(f_y=355.0, f_u=None, failure_strain=None, E_a=210000.0))

        Alternatively a section is created by passing ``rectangle`` and ``steel`` as arguments to
        :py:class:`~m_n_kappa.Section`.

        >>> from m_n_kappa import Section
        >>> section_bottom = Section(geometry=rectangle, material=steel)
        >>> section_bottom
        Section(\
geometry=Rectangle(top_edge=0.00, bottom_edge=10.00, width=10.00, left_edge=-5.00, right_edge=5.00), \
material=Steel(f_y=355.0, f_u=None, failure_strain=None, E_a=210000.0))

        """
        self._geometry = geometry
        self._material = material

    def __repr__(self):
        return (
            f"Section("
            f"geometry={self.geometry.__repr__()}, "
            f"material={self.material.__repr__()})"
        )

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
        return self._material == other.material and self._geometry == other.geometry

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
        """:py:class:`~m_n_kappa.material.Material` of the section"""
        return self._material

    @property
    def geometry(self):
        """:py:class:`~m_n_kappa.geometry.Geometry` of the section"""
        return self._geometry

    @property
    def top_edge_maximum_strain(self) -> StrainPosition:
        """:py:class:`~m_n_kappa.general.StrainPosition` with maximum strain on top edge of section"""
        return StrainPosition(
            strain=self.material.maximum_strain,
            position=self.geometry.top_edge,
            material=self.material.__class__.__name__,
        )

    @property
    def top_edge_minimum_strain(self) -> StrainPosition:
        """:py:class:`~m_n_kappa.general.StrainPosition` with minimum strain on top edge of section"""
        return StrainPosition(
            strain=self.material.minimum_strain,
            position=self.geometry.top_edge,
            material=self.material.__class__.__name__,
        )

    @property
    def bottom_edge_maximum_strain(self) -> StrainPosition:
        """:py:class:`~m_n_kappa.general.StrainPosition` with maximum strain on bottom edge of section"""
        return StrainPosition(
            strain=self.material.maximum_strain,
            position=self.geometry.bottom_edge,
            material=self.material.__class__.__name__,
        )

    @property
    def bottom_edge_minimum_strain(self) -> StrainPosition:
        """:py:class:`~m_n_kappa.general.StrainPosition` with minimum strain on bottom edge of section"""
        return StrainPosition(
            position=self.geometry.bottom_edge,
            strain=self.material.minimum_strain,
            material=self.material.__class__.__name__,
        )

    def maximum_positive_strain_position(self) -> StrainPosition:
        """
        maximum positive strain from associated material-model

        .. versionadded:: 0.2.0
        """
        return StrainPosition(
            self.material.maximum_strain,
            self.geometry.edges[0],
            self.material.__class__.__name__,
        )

    def maximum_negative_strain_position(self) -> StrainPosition:
        """
        maximum negative strain from associated material-model

        .. versionadded:: 0.2.0
        """
        return StrainPosition(
            self.material.minimum_strain,
            self.geometry.edges[0],
            self.material.__class__.__name__,
        )

    def maximum_positive_strain(self) -> float:
        """maximum positive strain from associated material-model"""
        return self.material.maximum_strain

    def maximum_negative_strain(self) -> float:
        """maximum negative strain from associated material-model"""
        return self.material.minimum_strain

    def material_strains(self) -> list[float]:
        """strains of the associated material-model"""
        return self.material.strains

    def section_strains(self) -> list[dict]:
        """strains of the associated material-model"""
        print("Section.section_strains is needed")
        return [
            {"section-section_type": self.section_type, "strain_value": strain_value}
            for strain_value in self.material_strains()
        ]

    def strain_positions(
        self, strain_1: float = None, strain_2: float = None, include_strains: bool = False
    ) -> list[StrainPosition]:
        """
        collect all strain-positions between ``strain_1`` and ``strain_2`` (if given)

        .. versionadded:: 0.2.0

        Parameters
        ----------
        strain_1 : float
            first strain border  (Default: None)
        strain_2 : float
            second strain border  (Default: None)
        include_strains : bool
            includes the boundary strain values (Default: False)

        Returns
        -------
        list[StrainPosition]
            collected :py:class:`~m_n_kappa.StrainPosition
        """
        if strain_1 is not None:
            if strain_2 is None:
                strain_2 = 0.0
            strains = self.material.get_intermediate_strains(strain_1, strain_2, include_strains)
        else:
            strains = [stress_strain.strain for stress_strain in self.material.stress_strain if stress_strain.strain != 0.0]
        strain_positions = []
        for edge in self.geometry.edges:
            strain_positions += [
                StrainPosition(strain_value, edge, self.material.__class__.__name__)
                for strain_value in strains
            ]
        return strain_positions


class ComputationSection(Section):

    """
    base class for specified ComputationsSection-classes

    .. versionadded:: 0.1.0

    See Also
    --------
    ComputationSectionStrain: ComputationSection to compute values under constant strain
    ComputationSectionCurvature: ComputationSection to compute values under linear-distributed strain

    Notes
    -----
    The computation of axial-force :math:`N_i`, lever-arm :math:`r_i` and moment :math:`M_i`

    """

    def __init_(self):
        self._section = None
        self._edges_strain = None
        self._edges_stress = None
        self._axial_force = None
        self._stress_slope = None
        self._stress_interception = None

    @property
    def geometry(self):
        """geometry of the section"""
        return self.section.geometry

    @property
    def material(self):
        """material of the section"""
        return self.section.material

    @property
    def edges_strain(self) -> list:
        """
        strains at the edges (bottom and top) of the section,
        computed from the strain distribution
        """
        return self._edges_strain

    @property
    def edges_stress(self) -> list:
        """stresses at the edges (bottom and top) of the section"""
        return self._edges_stress

    @property
    def axial_force(self) -> float:
        """
        axial-force of the section in case of the given strain-distribution :math:`N_i`

        See Also
        --------
        :ref:`theory.sections.sections.axial_force`: More descriptive explanation of the computation
        """
        return self._axial_force

    @property
    def section(self) -> Section:
        """basic :py:class:`~m_n_kappa.Section`"""
        return self._section

    @property
    def stress_slope(self) -> float:
        """linear slope of the stresses over the vertical direction of the section"""
        return self._stress_slope

    @property
    def stress_interception(self) -> float:
        """interception-value of the linear stress-distribution of the section"""
        return self._stress_interception

    def lever_arm(self) -> float:
        """
        lever-arm of the section under the given strain-distribution :math:`r_i`

        Returns
        -------
        float
            lever-arm of the section under a given strain-distribution

        See Also
        --------
        :ref:`theory.sections.sections.lever_arm`: More descriptive explanation of the computation

        Notes
        -----
        In case of a :py:class:`~m_n_kappa.Rectangle` or a :py:class:`~m_n_kappa.Trapezoid` the lever-arm is computed
        as follows.

        .. math::
           :label: eq:section_lever_arm_rectangle

           r_i = \\frac{1}{N_i} \\int_{z_\\mathrm{top}}^{z_\\mathrm{bottom}} \\sigma(z) \\cdot b(z) \\cdot z~dz

        In case of a :py:class:`~m_n_kappa.Circle` the lever-arm applies as the centroid of the circle.
        It is assumed that only reinforcement-bars are modelled as circles and therefore small in comparison to
        the rest of the cross-section.
        """
        if self.axial_force == 0.0:
            return 0.0
        else:
            return self._lever_arm_numerator() / self.axial_force

    def moment(self) -> float:
        """
        moment under the given strain distribution

        See Also
        --------
        :ref:`theory.sections.sections.moment`: More descriptive explanation of the computation

        Returns
        -------
        float
            moment under the given strain distribution
        """
        return self.axial_force * self.lever_arm()

    def _axial_force_integrated(self):
        """compute axial force for a :py:class:`~m_n_kappa.Rectangle` or a :py:class:`~m_n_kappa.Trapezoid`"""
        force = self._axial_force_integrated_at_position(
            position_value=self.geometry.edges[1]
        )
        force -= self._axial_force_integrated_at_position(
            position_value=self.geometry.edges[0]
        )
        return force

    def _compute_stress_slope(self) -> float:
        pass

    def _compute_stress_interception(self) -> float:
        return self.edges_stress[0] - self.geometry.top_edge * self.stress_slope

    def _compute_axial_force(self) -> float:
        if len(self.geometry.edges) > 1:
            return self._axial_force_integrated()
        else:  # Circle
            return self.geometry.area * self.edges_stress[0]

    def _get_edges_strain(self) -> list:
        pass

    def _get_edges_stress(self) -> list:
        """
        compute the stresses at the vertical edges of the section

        These values allow to compute a stress-slope :math:`m_\\mathrm{\\sigma}` and a corresponding
        stress-interception :math:`m_\\mathrm{\\sigma}`
        """
        return [
            self._material_stress(strain_value) for strain_value in self.edges_strain
        ]

    def _axial_force_integrated_at_position(self, position_value: float) -> float:
        """
        Integrate axial-force at a given position from the given strain-distribution

        Parameters
        ----------
        position_value : float
            vertical position where the axial force is integrated

        Returns
        -------
        float
            integrated axial force
        """
        return (
            (1.0 / 3.0)
            * self.geometry.width_slope
            * self.stress_slope
            * position_value**3.0
            + (1.0 / 2.0)
            * (
                self.stress_interception * self.geometry.width_slope
                + self.geometry.width_interception * self.stress_slope
            )
            * position_value**2.0
            + self.geometry.width_interception
            * self.stress_interception
            * position_value
        )

    def _lever_arm_integrated_at_position(self, position_value: float):
        """
        Integrate lever-arm at a given position from the given strain-distribution

        See Also
        --------
        :ref:`theory.sections.sections.lever_arm`: More descriptive explanation of the computation

        Parameters
        ----------
        position_value : float
            vertical position where the lever-arm is integrated

        Returns
        -------
        float
            integrated lever-arm
        """
        return (
            (1.0 / 4.0)
            * self.geometry.width_slope
            * self.stress_slope
            * position_value**4.0
            + (1.0 / 3.0)
            * (
                self.stress_interception * self.geometry.width_slope
                + self.geometry.width_interception * self.stress_slope
            )
            * position_value**3.0
            + (1.0 / 2.0)
            * self.geometry.width_interception
            * self.stress_interception
            * position_value**2.0
        )

    def _lever_arm_numerator(self):
        if len(self.geometry.edges) > 1:
            return self._lever_arm_numerator_rectangle()
        else:
            return self.geometry.centroid

    def _lever_arm_numerator_rectangle(self):
        lever_arm = self._lever_arm_integrated_at_position(
            position_value=self.geometry.edges[1]
        )
        lever_arm -= self._lever_arm_integrated_at_position(
            position_value=self.geometry.edges[0]
        )
        return lever_arm

    def _material_stress(self, strain_value: float) -> float:
        """
        compute the stress :math:`\\sigma` at a given strain :math:`\\varepsilon`
        using the material-curve of the section's material

        Parameters
        ----------
        strain_value : float

        Returns
        -------
        float
            stress at given strain
        """
        return self.material.get_material_stress(strain_value)

    def _print_results(self) -> str:
        text = [
            "Results",
            "-------",
            f"axial force: N = {self.axial_force:10.1f} N",
            f"lever arm:   z = {self.lever_arm():10.1f} mm",
            f"moment:      M = {self.moment():10.1f} Nmm",
        ]
        return print_sections(text)


class ComputationSectionStrain(ComputationSection):

    """
    compute section under a constant strain-value

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_section",
        "_strain",
        "_edges_strain",
        "_edges_stress",
        "_stress_slope",
        "_stress_interception",
        "_axial_force",
    )

    @log.init
    def __init__(self, section: Section, strain_value: float):
        """
        Parameters
        ----------
        section : :py:class:`~m_n_kappa.Section`
            section to compute
        strain_value : float
            given strain-value to compute

        See Also
        --------
        ComputationSectionCurvature: ComputationSection to compute values under linear-distributed strain

        Notes
        -----
        For the basic computation refer to :py:class:`~m_n_kappa.ComputationSection`.

        Examples
        --------
        A :py:class:`~m_n_kappa.Section` is defined as follows.

        >>> from m_n_kappa import Rectangle, Steel
        >>> steel = Steel(f_y=355)
        >>> rectangle = Rectangle(top_edge=0.0, bottom_edge=10, width=10)
        >>> section = steel + rectangle

        The computation for a given strain started by initializing
        :py:class:`~m_n_kappa.section.ComputationSectionStrain`

        >>> from m_n_kappa.section import ComputationSectionStrain
        >>> computed_section = ComputationSectionStrain(section, strain_value=0.001)

        The computed axial-force :math:`N_i` is given as follows:

        >>> computed_section.axial_force
        21000.0

        The lever-arm :math:`r_i` is computed as follows:

        >>> computed_section.lever_arm()
        5.0

        And the moment :math:`M_i` is given as follows

        >>> computed_section.moment()
        105000.0
        """
        self._section = section
        self._strain = strain_value
        self._edges_strain = self._get_edges_strain()
        self._edges_stress = self._get_edges_stress()
        self._stress_slope = 0.0
        self._stress_interception = self._compute_stress_interception()
        self._axial_force = self._compute_axial_force()

    def __repr__(self):
        return (
            f"ComputationSectionStrain("
            f"section={self.section.__repr__()}, "
            f"strain_value={self.strain})"
        )

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
        """applied strain"""
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

    """
    compute section given a curvature and a neutral axis

    .. versionadded:: 0.1.0
    """

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

    @log.init
    def __init__(
        self,
        section: Section,
        curvature: float,
        neutral_axis: float,
    ):
        """
        Parameters
        ----------
        section : :py:class:`~m_n_kappa.Section`
            section to compute
        curvature : float
            curvature to apply to the section :math:`\\kappa`
        neutral_axis : float
            point where the strain_value is zero :math:`z_\\mathrm{n}`

        See Also
        --------
        ComputationSectionStrain: ComputationSection to compute values under constant strain
        :ref:`theory.sections.sections`: check out for a more detailed explanation.

        Notes
        -----
        For the basic computation refer to :py:class:`~m_n_kappa.ComputationSection`.

        The overall procedure is:

        1. Determine the strains at the edges from the given strain-distribution.
           The strain-distribution is computed by the curvature and the neutral axis
        2. Compute the stresses at the edges passing the strains to the material-model
        3. Determine the stress-distribution (slope and interception)
        4. Compute the axial-force by combining the stress-distribution with the
           crosssectional area of the section

        Lever-arm and moment may be computed in succession, if needed.

        Examples
        --------
        A :py:class:`~m_n_kappa.Section` is defined as follows.

        >>> from m_n_kappa import Rectangle, Steel
        >>> steel = Steel(f_y=355)
        >>> rectangle = Rectangle(top_edge=0.0, bottom_edge=10, width=10)
        >>> section = steel + rectangle

        The computation for a given curvature and a given neutral-axis started by invoking
        :py:class:`~m_n_kappa.section.ComputationSectionCurvature`

        >>> from m_n_kappa.section import ComputationSectionCurvature
        >>> computed_section = ComputationSectionCurvature(section, curvature=0.0001, neutral_axis=10.0)

        The computed axial-force :math:`N_i` is given as follows:

        >>> computed_section.axial_force
        -10500.0

        The lever-arm :math:`r_i` is computed as follows:

        >>> computed_section.lever_arm()
        3.3333333333333335

        And the moment :math:`M_i` is given as follows

        >>> computed_section.moment()
        -35000.0
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

    def __repr__(self) -> str:
        return (
            f"ComputationSectionCurvature("
            f"section={self.section.__class__.__name__}, "
            f"curvature={self.curvature}, "
            f"neutral_axis_value={self.neutral_axis})"
        )

    @str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_geometry(),
            self._print_material(),
            self._print_results(),
        ]
        return print_chapter(text)

    def _print_geometry(self) -> str:
        text = [
            "Geometry",
            "--------",
            "section_type: " + self.geometry.__class__.__name__,
        ]
        if len(self.geometry.edges) > 1:
            text += [
                f"top_edge: {self.geometry.edges[0]:.1f} | bottom_edge: {self.geometry.edges[1]:.1f}",
                f"width-formula: {self.geometry.width_slope:.1f} * position_value + {self.geometry.width_interception:.1f}",
                f"top_strain: {self.edges_strain[0]:.5f} | bottom_strain: {self.edges_strain[1]:.5f}",
            ]
        else:
            text += [
                f"area: {self.geometry.area:.1f} | centroid: {self.geometry.centroid:.1f}",
            ]
        return print_sections(text)

    def _print_material(self) -> str:
        text = ["Material", "--------"]
        if len(self.geometry.edges) > 1:
            text += [
                f"top_stress {self.edges_stress[0]:.1f} N/mm^2 | bottom_stress {self.edges_stress[1]:.1f} N/mm^2",
                f"stress-formula: {self.stress_slope:.1f} * position_value + {self.stress_interception:.1f}",
            ]
        else:
            text += [f"stress {self.edges_stress[0]:.1f} N/mm^2"]
        return print_sections(text)

    def _print_result(self) -> str:
        if len(self.edges_strain) == 1:
            edges_strain = [f"{self.edges_strain[0]:10.6f}", "-"]
            edges_stress = [f"{self.edges_stress[0]:10.6f}", "-"]
        else:
            edges_strain = [
                f"{self.edges_strain[0]:10.6f}",
                f"{self.edges_strain[1]:10.6f}",
            ]
            edges_stress = [
                f"{self.edges_stress[0]:10.6f}",
                f"{self.edges_stress[1]:10.6f}",
            ]
        return (
            f"{self.geometry.top_edge:10.2f} | "
            f"{edges_strain[0]} | "
            f"{edges_stress[0]} | "
            f"{self.geometry.bottom_edge:8.2f} | "
            f"{edges_strain[1]} | "
            f"{edges_stress[1]} | "
            f"{self.axial_force:10.2f} | "
            f"{self.section_type:7} | "
            f"{self.material.__class__.__name__}"
        )

    @property
    def curvature(self) -> float:
        """input-curvature :math:`\\kappa`"""
        return self._curvature

    @property
    def neutral_axis(self) -> float:
        """input neutral axis :math:`z_\\mathrm{n}`"""
        return self._neutral_axis

    @property
    def edges_stress_difference(self) -> float:
        """difference of stresses between the given edges"""
        return self.edges_stress[1] - self.edges_stress[0]

    def split_section(
        self, effective_widths: EffectiveWidths = None
    ) -> list[ComputationSection]:
        """
        split sections considering the material points and the maximum effective widths

        Parameters
        ----------
        effective_widths : :py:class:`~m_n_kappa.general.EffectiveWidths`
            effective widths applied to the split section

        Returns
        -------
        list[:py:class:`~m_n_kappa.section.ComputationSection`]
            the split sections
        """
        if (
            effective_widths is not None
            and effective_widths.for_section_type != self.section_type
        ):
            effective_widths = None
        sub_geometries = self.__get_sub_geometries(effective_widths)
        split_sections = [
            self.__computation_section(sub_geometry) for sub_geometry in sub_geometries
        ]
        return split_sections

    def material_points_inside_curvature(self) -> list[StrainPosition]:
        """
        compute those material-points that are between the given strains from
        the given curvature and zero strain.

        Returns
        -------
        list[:py:class:`~m_n_kappa.general.StrainPosition`]
        """
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
                            self.material.__class__.__name__,
                        )
                    )
        return strain_position

    def __get_allowed_position_index(self, strain_value: float) -> int:
        if self.curvature > 0.0:
            if strain_value > 0.0:
                return 1  # index bottom_edge
            else:
                return 0  # index  top_edge
        else:
            if strain_value > 0.0:
                return 0  # index top_edge
            else:
                return 1  # index bottom_edge

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
        """compute strains at edges under given curvature and neutral axis"""
        return [
            self.__get_strain_by_position(position_value)
            for position_value in self.geometry.edges
        ]

    def __get_strain_by_position(self, position_value: float) -> float:
        """compute strain at position_value under given neutral axis and curvature"""
        return strain(
            neutral_axis_value=self.neutral_axis,
            curvature_value=self.curvature,
            position_value=position_value,
        )

    def __get_sub_geometries(self, effective_widths: EffectiveWidths = None) -> list:
        """
        splits geometry corresponding with the stress-strain-relationship
        under given curvature and neutral-axis
        """
        material_points = self.__material_points_position()
        return self.geometry.split(
            at_points=material_points, max_widths=effective_widths
        )

    def __sort_material_strains_by_curvature(self) -> None:
        if self.curvature > 0:
            self.material.sort_strains_ascending()
        else:
            self.material.sort_strains_descending()

    def __sub_section(self, geometry) -> Section:
        return Section(geometry, self.material)

    def __material_points_position(self) -> list[StrainPosition]:
        positions = []
        for stress_strain in self.material.stress_strain:
            positions.append(
                StrainPosition(
                    strain=stress_strain.strain,
                    position=self.__compute_position(strain_value=stress_strain.strain),
                    material=self.material.__class__.__name__,
                )
            )
        return positions

    def __compute_position(self, strain_value: float) -> float:
        """compute position_value where strain-value is given"""
        return position(
            curvature_value=self.curvature,
            neutral_axis_value=self.neutral_axis,
            strain_at_position=strain_value,
        )
