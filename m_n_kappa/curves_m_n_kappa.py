"""
curves_m_n_kappa.py

Aim
===
Computation of a curve considering moment, internal axial force and curvature

Procedure
=========
1. moment-axial-force-points (M-N)
   1.1 determine maximum positive and negative strain of the sub-cross-sections, that do not lead to failure in
       case of a uniform distribution of strain
   1.2 determine all strain-points that lie in between the above given positive and negative strains
   1.3 compute the moment-axial-force-point under each of these points
2. moment-axial-force-curvature-points (M-N-Kappa)
   2.1 the following procedure must be applied to each of the above given M-N-points
   2.2 determine the strain- and position-values leading to failure under the axial-force of the M-N-point
   2.3 compute the moment-axial-force-curvature-point at failure
   2.4 determine strain- and position-values that are between the failure curvature and no curvature
   2.5 compute moment-curvature-point for each of the strain- and position-values given above

Each of the above given points requires a split of the cross-sections
"""
import operator

from .general import (
    print_sections,
    print_chapter,
    str_start_end,
    StrainPosition,
    NotSuccessfulReason,
)

from .crosssection import (
    Crosssection,
    ComputationCrosssectionCurvature,
    ComputationCrosssectionStrain,
)
from .points import (
    MNByStrain,
    MomentAxialForce,
    MomentAxialForceCurvature,
)

from dataclasses import dataclass
import itertools

from .log import LoggerMethods

log = LoggerMethods(__name__)


def remove_duplicates(list_with_duplicates: list, sorting_function) -> list:
    """
    Remove the duplicates from a list considering ``sorting_function``.

    Make removal of duplicates also possible if elements of list are for example instances of a class with
    specific attributes.

    Parameters
    ----------
    list_with_duplicates : list
        list with the duplicates
    sorting_function : function
        function to identify the duplicates

    Returns
    -------
    list
        duplicate-free list

    Examples
    --------
    The ``duplicate_list`` consists of a number of :py:class:`~m_n_kappa.StrainPosition` instances.

    >>> from m_n_kappa import StrainPosition
    >>> duplicate_list = [
    ...     StrainPosition(strain=0.1, position=10, material="Steel"),
    ...     StrainPosition(strain=0.1, position=10, material="Steel"),
    ...     StrainPosition(strain=0.1, position=10, material="Steel"),
    ...     StrainPosition(strain=0.1, position=10, material="Steel"),
    ... ]

    To remove all duplicates from the list we used the Attribute-getter method by the :py:mod:`operator`-module.

    >>> from m_n_kappa.curves_m_n_kappa import remove_duplicates
    >>> import operator
    >>> remove_duplicates(list_with_duplicates=duplicate_list, sorting_function=operator.attrgetter('strain'))
    [StrainPosition(strain=0.1, position=10, material="Steel")]
    """
    list_with_duplicates.sort(key=sorting_function)
    new_list = [
        list(point)[0]
        for _, point in itertools.groupby(list_with_duplicates, key=sorting_function)
    ]
    return new_list


@dataclass
class MNKappaCurvePoint:
    """
    Container for single point on Moment-Axial-Force-Curvature-Curve

    .. versionadded:: 0.2.0

    Parameters
    ----------
    moment: float
        the computed moment of the curve-point
    curvature: float
        the computed curvature of the curve-point
    axial_force : float
        Computed axial force.
        Applied to one sub-cross-section with positive sign and
        to other sub-cross-section with negative sign.
    axial_force_cross_section_number: int
        number of the sub-cross-sections (tuple) the axial-force is applied to
    strain_difference: float
        Difference in strain between the two sub-cross-sections
    cross_section: :py:class:`~m_n_kappa.Crosssection`
        computed cross-section
    strain_position: :py:class:`~m_n_kappa.StrainPosition`
        :py:class:`~m_n_kappa.StrainPosition` leading to the
        resulting moment, curvature and neutral-axis
    neutral_axis_1: float
        the computed 1st neutral-axis of the computed curve-point
    neutral_axis_2: float
        the computed 2nd neutral-axis of the computed curve-point

    See Also
    --------
    :py:class:`~m_n_kappa.curves_m_kappa.MKappaCurvePoint` : container for a Moment-Curvature-Point
    MNKappaCurvePoints : container for Moment-Axial-Force-Curvature-Points
    """

    moment: float
    curvature: float
    axial_force: float
    axial_force_cross_section_number: int
    strain_difference: float
    cross_section: Crosssection
    strain_position: StrainPosition
    neutral_axis_1: float = None
    neutral_axis_2: float = None

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")

    def __eq__(self, other) -> bool:
        if not isinstance(other, MNKappaCurvePoint):
            return False
        elif (
            self.moment == other.moment
            and self.curvature == other.curvature
            and self.neutral_axis_1 == other.neutral_axis_1
            and self.neutral_axis_2 == other.neutral_axis_2
            and self.axial_force == other.axial_force
            and self.strain_difference == other.strain_difference
        ):
            return True
        else:
            return False

    def moment_curvature(self) -> list[float]:
        """pair of moment and curvature"""
        return [self.moment, self.curvature]

    def curvature_moment(self) -> list[float]:
        """pair of curvature and moment"""
        return [self.curvature, self.moment]

    def m_n_kappa(self) -> list[float]:
        """moment, axial-force, curvature"""
        return [self.moment, self.axial_force, self.curvature]

    def n_m_kappa(self) -> list[float]:
        """axial-force,moment, curvature"""
        return [self.axial_force, self.moment, self.curvature]


class MNKappaCurvePoints:

    """
    Container for points on computed :math:`M`-:math:`N`-:math:`\\kappa`-Curve

    .. versionadded:: 0.2.0

    """

    def __init__(self) -> None:
        self._points = []
        log.info(f"Created MNKappaCurvePoints")

    def __repr__(self) -> str:
        return """MNKappaCurvePoints()"""

    def __str__(self) -> str:
        text = [
            self._print_initialization(),
            self.print_points(),
        ]
        return print_chapter(text)

    def _print_initialization(self) -> str:
        text = ["Initialization", "------------", self.__repr__()]
        return print_sections(text)

    def print_points(self) -> str:
        points = sorted(self._points, key=lambda x: x.axial_force)
        line = 105 * "-"
        text = [
            line,
            "    Moment    | Curvature  | Neutral A.1 | Neutral A.2 | Axial-force | strain-diff. |   Strain   "
            "|  Position  | Material    ",
            line,
        ]
        for point in points:
            neutral_axis_1 = point.neutral_axis_1
            if neutral_axis_1 is None:
                neutral_axis_1 = "  Infinity "
            else:
                neutral_axis_1 = f"{neutral_axis_1:10.4f} "
            neutral_axis_2 = point.neutral_axis_2
            if neutral_axis_2 is None:
                neutral_axis_2 = "  Infinity "
            else:
                neutral_axis_2 = f"{neutral_axis_2:10.4f} "
            text.append(
                f"{point.moment:13.1f} | {point.curvature:10.6f} | {neutral_axis_1} | {neutral_axis_2} |"
                f"{point.axial_force:12.2f} | {point.strain_difference:12.6f} | {point.strain_position.strain:10.6f} |"
                f"{point.strain_position.position:11.1f} | {point.strain_position.material}"
            )
        text.append(line)
        return print_sections(text)

    @property
    def moments(self) -> list[float]:
        """computed moments of the Moment-Axial Force-Curvature-Curve"""
        return [point.moment for point in self.points]

    @property
    def curvatures(self) -> list[float]:
        """computed curvatures of the Moment-Axial Force-Curvature-Curve"""
        return [point.curvature for point in self.points]

    @property
    def axial_forces(self) -> list[float]:
        """axial forces of the Moment-Axial Force-Curvature-Curve"""
        return [point.axial_force for point in self.points]

    @property
    def strain_differences(self) -> list[float]:
        """strain differences of the Moment-Axial Force-Curvature-Curve"""
        return [point.strain_difference for point in self.points]

    @property
    def strains(self) -> list[float]:
        """strains that lead to moment-curvature pair"""
        return [point.strain_position.strain for point in self.points]

    @property
    def positions(self) -> list[float]:
        """positions that lead to moment-curvature pair"""
        return [point.strain_position.position for point in self.points]

    @property
    def materials(self) -> list[str]:
        """materials the strain-position-points is obtained from that lead to moment-curvature pair"""
        return [point.strain_position.material for point in self.points]

    def results_as_dict(self, moment_factor: float = 1.0) -> dict:
        """
        The moment-curvature points as descriptive Dictionary.

        Following keys are given with the corresponding lists:

        - ``'Moment'``: computed moments of the Moment-Axial-Force-Curvature curve
        - ``'Curvature'``: computed curvatures of the Moment-Axial-Force-Curvature curve
        - ``'Axial-Force'``: computed axial-forces of the Moment-Axial-Force-Curvature curve
        - ``'Strain-Difference'``: Differences between sub-cross-section of the
          Moment-Axial-Force-Curvature curve
        - ``'Strain'``: strains that lead to the above given moment-curvature-pair
        - ``'Position'``: position that corresponds to the above given strain
        - ``'Material'``: material ``strain`` and ``position`` are obtained from

        Parameters
        ----------
        moment_factor : float
            factor to compute the moment (default: 1.0)

        Returns
        -------
        dict
            moment-curvature points
        """
        return {
            "Moment": [moment * moment_factor for moment in self.moments],
            "Curvature": self.curvatures,
            "Axial-Force": self.axial_forces,
            "Strain-Difference": self.strain_differences,
            "Strain": self.strains,
            "Position": self.positions,
            "Material": self.materials,
        }

    @property
    def points(self) -> list[MNKappaCurvePoint]:
        """
        :math:`M`-:math:`\\kappa`-curve points
        """
        return self._points

    def add(
        self,
        moment: float,
        curvature: float,
        axial_force: float,
        axial_force_cross_section_number: int,
        strain_difference: float,
        cross_section,  # TODO: type-hint
        strain_position: StrainPosition,
        neutral_axis_1: float = None,
        neutral_axis_2: float = None,
    ) -> None:
        """add moment-curvature point to list

        Parameters
        ----------
        moment : float
            computed moment of the point
        curvature : float
            computed curvature of the point
        axial_force : float
            axial_force between sub-cross-sections
        axial_force_cross_section_number: int

        strain_difference : float
            difference in strain between sub-cross-sections
        cross_section : :py:class:`~m_n_kappa.points.MKappaByStrainPosition`
            computed cross-section
        strain_position : :py:class:`~m_n_kappa.general.StrainPosition`
            strain and its position
        neutral_axis_1 : float
            computed neutral-axis leading to equilibrium (after variation)
        neutral_axis_2 : float
            computed neutral-axis leading to equilibrium (after variation)
        """
        if neutral_axis_1 is not None and neutral_axis_2 is not None:
            max_neutral_axis = max(neutral_axis_1, neutral_axis_2)
            min_neutral_axis = min(neutral_axis_1, neutral_axis_2)
        else:
            max_neutral_axis = neutral_axis_1
            min_neutral_axis = neutral_axis_2
        point = MNKappaCurvePoint(
            moment,
            curvature,
            axial_force,
            axial_force_cross_section_number,
            strain_difference,
            cross_section,
            strain_position,
            min_neutral_axis,
            max_neutral_axis,
        )
        if point not in self.points:
            self._points.append(point)
            self._sort_points_by_curvature()
            log.info(f"Added {point} to MNKappaCurvePoint\n----")

    def curvature(self, by_moment: float, axial_force: float) -> float:
        """
        get curvature at given ``moment`` and ``axial_force``

        Parameters
        ----------
        by_moment : float
            moment the curvature is to be computed from
        axial_force : float

        Returns
        -------
        float
            curvature :math:`\\kappa` computed from the given ``moment``
            and ``axial_force``

        Raises
        ------
        ValueError
            in case the moment is outside the computed moment-range
        """
        pass  # TODO: compute curvature

    def _moment_curvature(self, by_index: int) -> list[float]:
        """get moment-curvature of curve-point at given index.rst"""
        return self.points[by_index].moment_curvature()

    def _curvature_moment(self, by_index: int) -> list[float]:
        """get curvature-moment of curve-point at given index.rst"""
        return self.points[by_index].curvature_moment()

    def _determine_index(self, moment: float) -> int:
        """
        get index of curve-point that has greater or equal moment as given

        Parameters
        ----------
        moment : float
            moment to find the index.rst of the moment-curvature-index.rst

        Returns
        -------
        int
            index of the moment-curvature-point that has smaller or equal moment
            than the given moment

        Raises
        ------
        ValueError
            in case no moment is found that lies between two moment-curvature-points
        """
        for index in range(len(self.points) - 1):
            if self.points[index].moment <= moment <= self.points[index + 1].moment:
                return index
        raise ValueError(f"No index found for {moment=}")

    def _sort_points_by_curvature(self):
        """sorts the moment-curvature-points ascending by its curvature"""
        self.points.sort(key=operator.attrgetter("curvature"))

    def maximum_moment(self) -> float:
        """computes the maximum moment of the curve"""
        return max(self.moments)


class MNCurve:

    """
    compute the moment and axial-force curve of a cross-section in case of no curvature

    .. versionadded:: 0.2.0

    procedure:
        1. determine strains in the sub-cross-sections (girder and slab)
        2. compute strain_value at the corresponding counter-sections
        3. determine moment, axial-force, strain-value-difference, etc.r
    """

    __slots__ = (
        "_sub_cross_sections",
        "_points",
        "_decisive_strains_cross_sections",
        "_strain_values",
        "_strain_positions",
        "_not_successful_reason",
    )

    @log.init
    def __init__(self, sub_cross_sections: list[Crosssection]):
        """
        Parameters
        ----------
        sub_cross_sections : list[:py:class:`~m_n_kappa.Crosssection`]
            sub-cross-sections to compute

        Examples
        --------
        To compute a moment-axial-force curve you need two sub-cross-
        sections.
        In the following two identical cross-sections are defined as
        our sub-cross-sections.

        >>> from m_n_kappa import Steel, Rectangle
        >>> steel = Steel()
        >>> rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        >>> section_top = steel + rectangle_top
        >>> cross_section_top = Crosssection([section_top])
        >>> rectangle_bottom= Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> section_bottom= steel + rectangle_bottom
        >>> cross_section_bottom = Crosssection([section_top])
        >>> cross_sections = [cross_section_top, cross_section_bottom]

        The ``cross_sections`` are passed to :py:class:`~m_n_kappa.MNCurve`.
        By initializing the moment-axial-force curve is computed.

        >>> from m_n_kappa import MNCurve
        >>> m_n = MNCurve(cross_sections)

        :py:class:`~m_n_kappa.MNCurve.points` gives us the opportunity
        access the results.
        Attribute :py:class:`~m_n_kappa.curves_m_n_kappa.MNKappaCurvePoints.moments`
        gives us the computed moments.

        >>> m_n.points.moments
        [400000.0, 355026.8934963956, -355026.8934963956, -400000.0, \
        400000.0, 355026.8934963956, -355026.8934963956, -400000.0]

        The computed curvatures are by definition zero.

        >>> m_n.points.curvatures
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        Attribute :py:class:`~m_n_kappa.curves_m_n_kappa.MNKappaCurvePoints.axial_forces`
        gives us the computed axial-forces.

        >>> m_n.points.axial_forces
        [40000.0, 35500.0, -35500.0, -40000.0, 40000.0, 35500.0, -35500.0, -40000.0]
        """
        self._sub_cross_sections = sub_cross_sections
        self._points = MNKappaCurvePoints()
        self._decisive_strains_cross_sections = self._determine_maximum_strains()
        self._strain_positions = self._determine_intermediate_strain_positions()
        self._not_successful_reason: list[NotSuccessfulReason] = []
        self._compute()

    def __repr__(self):
        return "MNCurve(cross_sections=cross_sections)"

    @str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self.points.print_points(),
        ]
        return print_chapter(text)

    @property
    def sub_cross_sections(self) -> list[Crosssection]:
        """cross-section to be computed"""
        return self._sub_cross_sections

    @property
    def points(self) -> MNKappaCurvePoints:
        """computed points"""
        return self._points

    @property
    def strain_positions(self) -> tuple:
        """strain-positions of the sub-cross-sections"""
        return self._strain_positions

    @property
    def not_successful_reason(self) -> list:
        """"""
        return self._not_successful_reason

    @log.result
    def _determine_maximum_strains(self) -> tuple[list, list]:
        """
        compute the maximum strains of each sub-cross-section by comparing corresponding axial-forces

        1. determine the maximum positive strain of the 1st sub-cross-section
        2. determine the maximum negative strain of the 2nd sub-cross-section
        3. compute the axial-forces by the strains in the corresponding sub-cross-sections
        4. compare the axial-forces (the minimum in absolute values is decisive)
        5. compute the strain-value of the not decisive cross-section from the decisive axial-force

        Returns
        -------
        tuple[list, list]
            maximum positive and negative strain of the 1st cross-section (1st list),
            maximum positive and negative strain of the 1st cross-section (2nd list)
        """
        sub_cross_section_1_strains = []
        sub_cross_section_2_strains = []

        for strain_1, strain_2 in [
            [
                self.sub_cross_sections[0].decisive_maximum_positive_strain_position(),
                self.sub_cross_sections[1].decisive_maximum_negative_strain_position(),
            ],
            [
                self.sub_cross_sections[0].decisive_maximum_negative_strain_position(),
                self.sub_cross_sections[1].decisive_maximum_positive_strain_position(),
            ],
        ]:
            axial_force_1 = ComputationCrosssectionStrain(
                self.sub_cross_sections[0], strain_1.strain
            ).total_axial_force()
            axial_force_2 = ComputationCrosssectionStrain(
                self.sub_cross_sections[1], strain_2.strain
            ).total_axial_force()
            if abs(axial_force_1) <= abs(axial_force_2):
                sub_cross_section_1_strains.append(strain_1)
                strain_2.strain = MNByStrain(
                    self.sub_cross_sections[1], (-1) * axial_force_1
                ).strain
                sub_cross_section_2_strains.append(strain_2)
            else:
                strain_1.strain = MNByStrain(
                    self.sub_cross_sections[0], (-1) * axial_force_2
                ).strain
                sub_cross_section_1_strains.append(strain_1)
                sub_cross_section_2_strains.append(strain_2)

        return sub_cross_section_1_strains, sub_cross_section_2_strains

    @log.result
    def _determine_intermediate_strain_positions(self) -> tuple:
        """
        determine the strain-values of each cross-section between the maximum-strains

        goes into the material of each sub-cross-sections' section and extracts all strain-values
        between maximum and minimum strain determined by :py:meth:`~m_n_kappa.MNCurve._determine_maximum_strains`

        Returns
        -------
        tuple[list[StrainPositions], list[StrainPositions]]
            strain
        """
        strains = []
        for cross_section_index, sub_cross_section in enumerate(
            self.sub_cross_sections
        ):
            strains.append([])
            max_strains = self._decisive_strains_cross_sections[cross_section_index]
            for section in sub_cross_section:
                strains[cross_section_index] += section.strain_positions(
                    max_strains[0].strain, max_strains[1].strain
                )
                strain_positions = remove_duplicates(
                    strain_positions, operator.attrgetter("strain", "position")
                )
                strains[cross_section_index] += strain_positions
                strains[cross_section_index] += max_strains
        return tuple(strains)

    def _compute(self) -> None:
        """compute the moment-axial-force points for each strain-position-value"""
        for cross_section_index in [0, 1]:
            strain_positions = remove_duplicates(
                self._strain_positions[cross_section_index],
                sorting_function=operator.attrgetter("strain"),
            )
            strain_positions = [
                list(strain_position)[0]
                for _, strain_position in itertools.groupby(
                    strain_positions, key=lambda x: x.strain
                )
            ]
            sub_cross_sections = self.sub_cross_sections
            if cross_section_index == 1:
                sub_cross_sections.reverse()
            for strain_position in strain_positions:
                m_n = MomentAxialForce(
                    cross_sections=sub_cross_sections,
                    strain=strain_position.strain,
                )
                if m_n.successful:
                    self._save(m_n, strain_position)
                else:
                    self._not_successful_reason += m_n.not_successful_reason

    def _save(
        self,
        m_n: MomentAxialForce,
        strain_position: StrainPosition,
        axial_force_cross_section_number: int,
    ) -> None:
        """save the computed value to :py:attr:`~m_n_kappa.MNCurve.points"""
        self.points.add(
            moment=m_n.moment(),
            curvature=0.0,
            axial_force=m_n.axial_force * (-1) ** axial_force_cross_section_number,
            axial_force_cross_section_number=axial_force_cross_section_number,
            strain_difference=m_n.strain_difference
            * (-1) ** axial_force_cross_section_number,
            cross_section=m_n.computed_sub_cross_sections,
            strain_position=strain_position,
            neutral_axis_1=None,
            neutral_axis_2=None,
        )

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(
            ["Initialization", len("Initialization") * "-", self.__repr__()]
        )


class MNKappaCurve:
    """
    computation of Moment-Axial-Force-Curvature curve (M-N-Kappa)

    .. versionadded:: 0.2.0
    """

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        include_positive_curvature: bool = True,
        include_negative_curvature: bool = False,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            cross-section to compute the M-N-Kappa-curve
        include_positive_curvature : bool
            if ``True`` then positive curvature values are computed (Default: ``True``)
        include_negative_curvature : bool
            if ``True`` then negative curvature values are computed (Default: ``False``)

        See Also
        --------
        :py:class:`~m_n_kappa.MKappaCurve` : computation of Moment-Curvature-Curve assuming full interaction
        """
        self._cross_section = cross_section
        self._include_positive_curvature = include_positive_curvature
        self._include_negative_curvature = include_negative_curvature
        self._not_successful = None
        self._m_n_curve = MNCurve(self.cross_section)
        self._m_n_kappa_points = self.m_n_curve.points
        if self.include_positive_curvature:
            self._m_n_kappa_points += MNCurvatureCurve(
                self.cross_section, self.m_n_curve.strain_positions, True
            ).points
        if self.include_negative_curvature:
            self._m_n_kappa_points += MNCurvatureCurve(
                self.cross_section, self.m_n_curve.strain_positions, False
            ).points

    @property
    def cross_section(self) -> Crosssection:
        """cross-section the :math:`M`-:math:`N`-:math:`\\kappa`-curve shall be computed"""
        return self._cross_section

    @property
    def include_positive_curvature(self) -> bool:
        """returns if :math:`M`-:math:`N`-:math:`\\kappa` under positive bending/curvature is included"""
        return self._include_positive_curvature

    @property
    def include_negative_curvature(self) -> bool:
        """returns if :math:`M`-:math:`N`-:math:`\\kappa` under negative bending/curvature is included"""
        return self._include_negative_curvature

    @property
    def m_n_kappa_points(self) -> MNKappaCurvePoints:
        """moment-axial-force-curvature points of the curve"""
        return self._m_n_kappa_points

    @property
    def m_n_curve(self) -> MNCurve:
        """M-N-curve (without curvature)"""
        return self._m_n_curve


class MCurvatureCurve:
    """

    .. versionadded:: 0.2.0

    """

    @log.init
    def __init__(self, cross_section: Crosssection, axial_force: float):
        self._cross_section = cross_section
        self._axial_force: float

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def axial_force(self) -> float:
        return self._axial_force

    def compute(self):
        pass


class MNCurvatureCurve:

    """
    compute all points of the M-N-Curvature-Curve

    .. versionadded:: 0.2.0

    procedure:
        1.
    """

    @log.init
    def __init__(self, cross_section: Crosssection, m_n_points: list):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            cross_section
        m_n_points : list
            computed moment-axial-force-points without curvature
            serves as starting points
        """
        self._cross_section = cross_section
        self._m_n_points = m_n_points
        self._m_n_curvature_points = []

    def __repr__(self):
        return (
            f"MNCurvatureCurve("
            f"cross_section={self.cross_section}, "
            f"m_n_points={self.m_n_points})"
        )

    @str_start_end
    def __str__(self):
        text = []
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(["Initialization", "--------------", self.__repr__()])

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def m_n_points(self) -> list:
        return self._m_n_points

    @property
    def m_n_curvature_points(self) -> list:
        return self._m_n_curvature_points

    def compute_m_n_curvature_points(self):
        for m_n_point in self.m_n_points:
            raise NotImplementedError()


class MKappaAtAxialForce:

    """
    compute M-Kappa-Curve at given axial force

    .. versionadded:: 0.2.0

    procedure:
        1. get maximum curvature
        2.
    """

    @log.init
    def __init__(self, cross_section: Crosssection, axial_force: float):
        self._cross_section = cross_section
        self._axial_force = axial_force


class MNZeroCurvature:
    """
    compute moment and axial force at zero curvature

    .. versionadded:: 0.2.0
    """

    __slots__ = (
        "_cross_section",
        "_input_section_type",
        "_input_strain",
        "_counter_lower_strain",
        "_counter_upper_strain",
        "_axial_force_tolerance",
        "_maximum_iterations",
        "_solver",
        "_computations",
        "_iteration",
        "_other_strain",
        "_other_axial_force",
        "_other_cross_section",
        "_successful",
        "_input_cross_section",
        "_other_cross_section",
        "_axial_force",
    )

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        input_section_type: str,
        input_strain: float,
        counter_lower_strain: float,
        counter_upper_strain: float,
        axial_force_tolerance: float = 5.0,
        maximum_iterations: int = 10,
        solver: Solver = Newton,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            given cross-section
        input_section_type : str
            section where strain_value is applied to
            possible values are (steel-)'girder' or (concrete-)'slab'
        input_strain : str
            strain_value where axial force and moment were calculated
        axial_force_tolerance : float
            tolerance of axial force to be met
        maximum_iterations : int
            maximum number of iterations
        solver : solver.Solver
            solver to compute the axial force
        """
        self._cross_section = cross_section
        self._input_section_type = input_section_type
        self._input_strain = input_strain
        self._counter_lower_strain = counter_lower_strain
        self._counter_upper_strain = counter_upper_strain
        self._axial_force_tolerance = axial_force_tolerance
        self._maximum_iterations = maximum_iterations
        self._solver = solver
        self._compute_input_section()
        self._computations = []
        self._iteration = 0
        self._other_strain = self.counter_lower_strain
        self._other_axial_force = 0.0
        self._other_cross_section = None
        self._successful = False
        self.other_sections_initialize()

    def __repr__(self):
        return (
            f"MNZeroCurvature("
            f"cross_section=cross_section, "
            f"input_section_type={self.input_section_type}, "
            f"input_strain={self.input_strain})"
        )

    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_input_sections_result(),
            self._print_other_sections_result(),
            self._print_other_sections_iterations(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(
            ["Initialization", len("Initialization") * "-"], self.__repr__()
        )

    def _print_input_sections_result(self) -> str:
        text = [
            "Input Section",
            "-------------",
            f"section-section_type: {self.input_section_type}",
            f"strain_value: {self.input_strain}",
            f"axial-force: {self.axial_force}",
            f"moment: {self.input_sections_moment()}",
        ]
        return print_sections(text)

    def _print_other_sections_result(self) -> str:
        text = [
            "Other Section",
            "-------------",
            f"strain_value: {self.other_strain}",
            f"axial-force: {self.other_axial_force}",
            f"moment: {self.other_sections_moment()}",
        ]
        return print_sections(text)

    def _print_other_sections_iterations(self) -> str:
        text = [
            "Iterations",
            "----------",
            "",
            "----------------------------",
            "iter |  strain_value  | ax. force ",
            "----------------------------",
        ]
        for computation in self.computations:
            text.append(
                "{:4} | {:8.5f} | {:9.2f}".format(
                    computation["iteration"],
                    computation["strain_value"],
                    computation["axial-force"],
                )
            )
        text.append("----------------------------")
        return print_sections(text)

    @property
    def axial_force(self) -> float:
        """"""
        return self._axial_force

    @property
    def axial_force_tolerance(self) -> float:
        return self._axial_force_tolerance

    @property
    def computations(self) -> list:
        return self._computations

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def counter_lower_strain(self) -> float:
        return self._counter_lower_strain

    @property
    def counter_upper_strain(self) -> float:
        return self._counter_upper_strain

    @property
    def input_section_type(self) -> str:
        return self._input_section_type

    @property
    def input_strain(self) -> float:
        return self._input_strain

    @property
    def input_cross_section(self) -> Crosssection:
        return self._input_cross_section

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def maximum_iterations(self) -> int:
        return self._maximum_iterations

    @property
    def other_strain(self) -> float:
        return self._other_strain

    @property
    def other_axial_force(self) -> float:
        return self._other_axial_force

    @property
    def other_cross_section(self) -> Crosssection:
        return self._other_cross_section

    @property
    def successful(self) -> bool:
        return self._successful

    @property
    def solver(self) -> Solver:
        return self._solver

    def moment(self) -> float:
        return self.other_sections_moment() + self.input_sections_moment()

    def input_sections(self) -> list:
        return self.cross_section.sections_of_type(self.input_section_type)

    def other_sections(self) -> list:
        return self.cross_section.sections_not_of_type(self.input_section_type)

    def _compute_input_section(self) -> None:
        self._input_cross_section = self._create_crosssection(
            self.input_sections(), self.input_strain
        )
        self._axial_force = self.input_cross_section.total_axial_force()

    def _compute_other_section(self) -> None:
        self._other_cross_section = self._create_crosssection(
            self.other_sections(), self.other_strain
        )
        self._other_axial_force = self.other_cross_section.total_axial_force()
        self._save()

    def input_sections_moment(self) -> float:
        return self.input_cross_section.total_moment()

    def other_sections_moment(self) -> float:
        return self.other_cross_section.total_moment()

    def other_sections_initialize(self) -> None:
        self._compute_other_section()
        self._iteration = 1
        self._other_strain = self.counter_upper_strain
        self._compute_other_section()
        if self._axial_force_within_tolerance():
            self._successful = True
        else:
            self.other_sections_iterate()

    def other_sections_iterate(self) -> None:
        for iteration in range(2, self.maximum_iterations):
            self._iteration = iteration
            self._other_strain = self._guess_new_strain()
            self._compute_other_section()
            if self._axial_force_within_tolerance():
                self._successful = True
                break

    def other_maximum_strain(self) -> float:
        cross_section = Crosssection(self.other_sections())
        if self.input_strain < 0.0:
            return cross_section.maximum_positive_strain()
        else:
            return cross_section.maximum_negative_strain()

    def _axial_force_equilibrium(self) -> float:
        return self.axial_force + self.other_axial_force

    def _axial_force_within_tolerance(self) -> bool:
        if abs(self._axial_force_equilibrium()) < self.axial_force_tolerance:
            return True
        else:
            return False

    def _create_crosssection(self, sections, strain) -> ComputationCrosssectionStrain:
        return ComputationCrosssectionStrain(sections, strain)

    def _guess_new_strain(self) -> float:
        return self.solver(
            data=self.computations, variable="strain_value", target="axial-force"
        ).compute()

    def _save(self) -> None:
        self._computations.append(
            {
                "iteration": self.iteration,
                "strain_value": self.other_strain,
                "axial-force": self._axial_force_equilibrium(),
                "cross-section": self.other_cross_section,
            }
        )

    def resulting_crosssection(self) -> Crosssection:
        return self.input_cross_section + self.other_cross_section
