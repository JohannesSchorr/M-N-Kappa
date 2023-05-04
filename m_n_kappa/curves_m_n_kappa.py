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
3. Moment-Curvature without axial-forces (M-Kappa)
   3.1 compute the Moment-Curvature-Curve of each sub-cross-section individually
   3.2 compare the both curves from 3.1 and add-up the moments at each curvature-point

Each of the above given points requires a split of the cross-sections
"""
import operator

from .general import (
    print_sections,
    print_chapter,
    str_start_end,
    StrainPosition,
    NotSuccessfulReason,
    interpolate_in,
    strain_difference,
)

from .crosssection import (
    Crosssection,
    ComputationCrosssectionCurvature,
    ComputationCrosssectionStrain,
)
from .points import (
    MKappaByConstantCurvature,
    MNByStrain,
    MomentAxialForce,
    MomentAxialForceCurvature,
)
from .curves_m_kappa import MKappaCurve, MKappaCurvePoints

from dataclasses import dataclass, field
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


@dataclass(slots=True)
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

    moment: float = field(compare=True)
    curvature: float = field(compare=True)
    axial_force: float = field(compare=True)
    axial_force_cross_section_number: int
    strain_difference: float = field(compare=True)
    cross_section: tuple[
        ComputationCrosssectionCurvature, ComputationCrosssectionCurvature
    ] | tuple[ComputationCrosssectionStrain, ComputationCrosssectionStrain]
    strain_position: StrainPosition
    neutral_axis_1: float = field(compare=True, default=None)
    neutral_axis_2: float = field(compare=True, default=None)

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")

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

    @log.init
    def __init__(self, points: list[MNKappaCurvePoint] = None) -> None:
        """
        Parameters
        ----------
        points : list[:py:class:`~m_n_kappa.curves_m_n_kappa.MNKappaCurvePoint`]
            M-N-Kappa-Curve-Points are already available

        Raises
        ------
        TypeError
            In case the points are not of type :py:class:`~m_n_kappa.curves_m_n_kappa.MNKappaCurvePoint`
        """
        if points is None:
            self._points = []
        elif isinstance(points, MNKappaCurvePoint):
            self._points = [points]
        elif isinstance(points, list):
            for point in points:
                if not isinstance(point, MNKappaCurvePoint):
                    raise TypeError(
                        f"entry in points must be of type MNKappaCurvePoint. It is of type {type(point)}."
                    )
            self._points = points

    def __repr__(self) -> str:
        return """MNKappaCurvePoints()"""

    def __str__(self) -> str:
        text = [
            self._print_initialization(),
            self.print_points(),
        ]
        return print_chapter(text)

    def __add__(self, other):
        if isinstance(other, MNKappaCurvePoints):
            m_n_kappa_points = MNKappaCurvePoints(points=self.points + other.points)
            m_n_kappa_points._remove_duplicate_points()
            return m_n_kappa_points
        if isinstance(other, MKappaCurvePoints):
            for point in other.points:
                self.add(
                    moment=point.moment,
                    curvature=point.curvature,
                    neutral_axis_1=point.neutral_axis,
                    neutral_axis_2=point.neutral_axis,
                    cross_section=point.cross_section,
                    strain_position=point.strain_position,
                    axial_force=0.0,
                    strain_difference=0.0,
                    axial_force_cross_section_number=1,
                )
            return self
        raise TypeError(
            f'Can not add "{type(self)}" and "{type(other)}". '
            f'Must be of type "MNKappaCurvePoints" or "MKappaCurvePoints"'
        )

    def _remove_duplicate_points(self):
        sorting_function = operator.attrgetter(
            "moment", "curvature", "axial_force", "strain_difference"
        )
        self._points = remove_duplicates(self.points, sorting_function)

    def __iter__(self):
        self._point_iterator = iter(self.points)
        return self

    def __next__(self):
        return self._point_iterator.__next__()

    def _print_initialization(self) -> str:
        text = ["Initialization", "------------", self.__repr__()]
        return print_sections(text)

    def print_points(self) -> str:
        points = sorted(self._points, key=operator.attrgetter("moment"))
        line = 130 * "-"
        text = [
            line,
            "     Moment     |  Curvature   | Neutral A.1 | Neutral A.2 |  Axial-force  | strain-diff. |   Strain   "
            "| Position | Material         ",
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
                f"{point.moment:15.1f} | {point.curvature:12.8f} | {neutral_axis_1} | {neutral_axis_2} |"
                f"{point.axial_force:14.2f} | {point.strain_difference:12.6f} | {point.strain_position.strain:10.6f} |"
                f"{point.strain_position.position:9.1f} | {point.strain_position.material}"
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
        cross_section: tuple[
            ComputationCrosssectionCurvature, ComputationCrosssectionCurvature
        ]
        | tuple[ComputationCrosssectionStrain, ComputationCrosssectionStrain],
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
        get curvature considering the given ``moment`` and ``axial_force``

        Parameters
        ----------
        by_moment : float
            moment the curvature is to be computed from
        axial_force : float
            axial-force to consider the moment

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
        return interpolate_in(
            self.points, "curvature", "axial_force", axial_force, "moment", by_moment
        )

    @log.result
    def moment(
        self,
        strain_difference: float,
        axial_force: float,
        moment_is_positive: bool = True,
    ):
        """
        get the moment from the curve corresponding with the given ``axial_force`` and
        ``strain_difference``.

        Parameters
        ----------
        strain_difference : float
           strain-difference between the sub-cross-sections
        axial_force : float
           axial-force
        moment_is_positive : float
           checks only positive moments

        Returns
        -------
        float
            moment
        """
        if moment_is_positive:
            points = list(filter(lambda x: x.moment >= 0, self.points))
        else:
            points = list(filter(lambda x: x.moment <= 0, self.points))

        return interpolate_in(
            points,
            "moment",
            "absolute_axial_force",
            axial_force,
            "absolute_strain_difference",
            strain_difference,
        )

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

    @log.result
    def cross_section_axial_forces(
        self, positive_moment: bool
    ) -> tuple[list[float], list[float]]:
        """get axial-forces for 1st and 2nd cross-section considering the sign of the moment"""
        if positive_moment:
            points = list(filter(lambda x: x.moment > 0.0, self.points))
        else:
            points = list(filter(lambda x: x.moment < 0.0, self.points))
        axial_forces = [[], []]
        for index in [0, 1]:
            cross_section_points = list(
                filter(lambda x: x.axial_force_cross_section_number == index, points)
            )
            axial_forces[index] = [
                cross_section_point.axial_force * (-1) ** index
                for cross_section_point in cross_section_points
            ]
        return tuple(axial_forces)


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
    def __init__(
        self, sub_cross_sections: list[Crosssection] | tuple[Crosssection, Crosssection]
    ):
        """
        Parameters
        ----------
        sub_cross_sections : list[:py:class:`~m_n_kappa.Crosssection`] | 
        tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            sub-cross-sections to compute

        Examples
        --------
        To compute a moment-axial-force curve you need two sub-cross-
        sections.
        In the following two identical cross-sections are defined as
        our sub-cross-sections.

        >>> from m_n_kappa import Steel, Rectangle, Crosssection
        >>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
        >>> rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        >>> section_top = steel + rectangle_top
        >>> cross_section_top = Crosssection([section_top])
        >>> rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> section_bottom = steel + rectangle_bottom
        >>> cross_section_bottom = Crosssection([section_bottom])
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
        if isinstance(sub_cross_sections, Crosssection):
            self._sub_cross_sections = sub_cross_sections.get_sub_cross_sections()
        elif isinstance(sub_cross_sections, list) or isinstance(
            sub_cross_sections, tuple
        ):
            self._sub_cross_sections = tuple(sub_cross_sections)
        else:
            raise TypeError("")
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
    def sub_cross_sections(self) -> tuple[Crosssection, Crosssection]:
        """two sub-cross-sections"""
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
    def not_successful_reason(self) -> list[NotSuccessfulReason]:
        """for those computations that were not successful, here the reasons are given"""
        return self._not_successful_reason

    @log.result
    def _determine_maximum_strains(self) -> tuple[list, list]:
        """
        compute the maximum strains of each sub-cross-section by comparing corresponding axial-forces

        1. determine the maximum positive strain of the 1st sub-cross-section
        2. determine the maximum negative strain of the 2nd sub-cross-section
        3. compute the axial-forces by the strains in the corresponding sub-cross-sections
        4. compare the axial-forces -> the minimum in absolute values is decisive
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
            log.debug(f"{strain_1=}, {strain_2=}")
            log.debug(
                f"{axial_force_1=}, {axial_force_2=} -> {min(axial_force_1, axial_force_2)}"
            )
            if abs(axial_force_1) <= abs(axial_force_2):
                sub_cross_section_1_strains.append(strain_1)
                strain_2.strain = MNByStrain(
                    self.sub_cross_sections[1], axial_force_1 * (-1)
                ).strain
                sub_cross_section_2_strains.append(strain_2)
            else:
                strain_1.strain = MNByStrain(
                    self.sub_cross_sections[0], axial_force_2 * (-1)
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
        strains = [[], []]
        for cross_section_index, sub_cross_section in enumerate(
            self.sub_cross_sections
        ):
            max_strains = self._decisive_strains_cross_sections[cross_section_index]
            strain_positions = sub_cross_section.strain_positions(
                max_strains[0].strain, max_strains[1].strain
            )
            strains[cross_section_index] = remove_duplicates(
                strain_positions, operator.attrgetter("strain", "position")
            )
            strains[cross_section_index] += max_strains
        return tuple(strains)

    def _compute(self) -> None:
        """compute the moment-axial-force points for each strain-position-value"""
        for cross_section_index in [0, 1]:
            strain_positions = remove_duplicates(
                self._strain_positions[cross_section_index],
                sorting_function=operator.attrgetter("strain"),
            )
            sub_cross_sections = self.sub_cross_sections
            if cross_section_index == 1:
                sub_cross_sections = tuple(
                    [sub_cross_sections[1], sub_cross_sections[0]]
                )
            for strain_position in strain_positions:
                m_n = MomentAxialForce(
                    sub_cross_sections=sub_cross_sections,
                    strain=strain_position.strain,
                )
                if m_n.successful:
                    self._save(m_n, strain_position, cross_section_index)
                else:
                    self._not_successful_reason.append(m_n.not_successful_reason)

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


class MNCurvatureCurve:
    """
    compute moment-axial-force-curvature curve

    .. versionadded:: 0.2.0
    """

    __slots__ = (
        "_sub_cross_sections",
        "_axial_forces",
        "_strain_positions",
        "_positive_curvature",
        "_not_successful_reason",
        "_points",
    )

    @log.init
    def __init__(
        self,
        m_n_curve: MNCurve = None,
        sub_cross_sections: Crosssection
        | list[Crosssection]
        | tuple[Crosssection, Crosssection] = None,
        axial_forces: tuple[list[float], list[float]] = None,
        strain_positions: tuple[list[StrainPosition], list[StrainPosition]] = None,
        positive_curvature: bool = True,
    ):
        """
        Parameters
        ----------
        m_n_curve : MNCurve
            computed Moment-Axial-Force curve (Default: None)
        sub_cross_sections : :py:class:`~m_n_kappa.Crosssection` |
        list[:py:class:`~m_n_kappa.Crosssection`] |
        tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            Sub-cross-sections to be computed.
            In case given as single :py:class:`~m_n_kappa.Crosssection` this cross-section must consist of
            a slab (Concrete and Reinforcement) and a girder (Steel)
        axial_forces : tuple[list[float], list[float]]
        strain_positions : tuple[list[:py:class:`~m_n_kappa.StrainPosition`], list[:py:class:`~m_n_kappa.StrainPosition`]]
            Strain- and Position-values to be considered.
            Must be split due to the cross-section they belong to.
        positive_curvature : bool
            ``True`` computes positive curvature values.
            ``False`` computes negative curvature values.

        Raises
        ------
        TypeError : if neither a ``MNCurve`` nor ``sub_cross_sections``, ``axial_forces`` and ``strain_positions`` are
           given
        """
        if (
            m_n_curve is None
            and sub_cross_sections is not None
            and axial_forces is not None
            and strain_positions is not None
        ):
            if isinstance(sub_cross_sections, Crosssection):
                self._sub_cross_sections = sub_cross_sections.get_sub_cross_sections()
            elif isinstance(sub_cross_sections, list) and len(sub_cross_sections) == 2:
                self._sub_cross_sections = tuple(sub_cross_sections)
            elif isinstance(sub_cross_sections, tuple) and len(sub_cross_sections) == 2:
                self._sub_cross_sections = sub_cross_sections
            else:
                raise TypeError("")
            self._axial_forces = axial_forces
        elif m_n_curve is not None:
            self._sub_cross_sections = m_n_curve.sub_cross_sections
            self._axial_forces = m_n_curve.points.cross_section_axial_forces(
                positive_curvature
            )
        else:
            raise ValueError("")
        self._strain_positions = self._get_strain_positions()
        self._positive_curvature = positive_curvature
        self._not_successful_reason = []
        self._points = MNKappaCurvePoints()
        self._compute_all()

    def __repr__(self) -> str:
        return (
            f"MNCurvatureCurve("
            f"\n\tsub_cross_sections={self.sub_cross_sections}, "
            f"\n\taxial_forces={self.axial_forces}, "
            f"\n\tstrain_positions={self.strain_positions}, "
            f"\n\tpositive_curvature={self.positive_curvature})"
        )

    def _get_strain_positions(
        self,
    ) -> tuple[list[StrainPosition], list[StrainPosition]]:
        """
        determine all relevant :py:class:`~m_n_kappa.StrainPosition`-values
        of the sub-cross-sections
        """
        strain_positions = [[], []]
        for index, cross_section in enumerate(self.sub_cross_sections):
            strain_positions[index] = cross_section.strain_positions(
                strain_1=cross_section.decisive_maximum_negative_strain_position().strain,
                strain_2=cross_section.decisive_maximum_positive_strain_position().strain,
                include_strains=True,
            )
        return tuple(strain_positions)

    @property
    def axial_forces(self) -> tuple[list[float], list[float]]:
        """axial forces to be applied to the 1st and the 2nd sub-cross-section"""
        return self._axial_forces

    @property
    def not_successful_reason(self) -> list[NotSuccessfulReason]:
        """for those computations that were not successful, here the reasons are given"""
        return self._not_successful_reason

    @property
    def positive_curvature(self) -> bool:
        """
        ``True`` computes positive curvature values.
        ``False`` computes negative curvature values.
        """
        return self._positive_curvature

    @property
    def points(self) -> MNKappaCurvePoints:
        """computed M-N-Kappa points"""
        return self._points

    @property
    def strain_positions(self) -> tuple[list[StrainPosition], list[StrainPosition]]:
        """Strain- and Position-values to be considered"""
        return self._strain_positions

    @property
    def sub_cross_sections(self) -> tuple[Crosssection, Crosssection]:
        """Sub-cross-sections to be computed"""
        return self._sub_cross_sections

    def _compute_all(self) -> None:
        """
        computes the Moment-Axial-Force curvature points

        Considered are the :py:attr:`~m_n_kappa.curves_m_n_kappa.MNCurvatureCurve.axial_forces`
        and the :py:attr:`~m_n_kappa.curves_m_n_kappa.MNCurvatureCurve.strain_positions`.
        Both are split due to the specific 1st sub-cross-section.

        Notes
        -----
        For better performance following features are applied:
        - duplicate strain-position-values are removed
        - Similar strain-values are first tackled from the lower position.
          In case the computation is not successful the strain-values are tackled from the higher position.
          If this is also not successful then position-values in between are neglected.
        """
        for cross_section_index in [0, 1]:
            sub_cross_sections = self.sub_cross_sections
            if cross_section_index == 1:
                sub_cross_sections = tuple(
                    [sub_cross_sections[1], sub_cross_sections[0]]
                )
            strain_positions = remove_duplicates(
                self.strain_positions[cross_section_index],
                sorting_function=operator.attrgetter("strain", "position"),
            )
            strain_position_groups = [
                list(strain_position_group)
                for _, strain_position_group in itertools.groupby(
                    strain_positions, key=operator.attrgetter("strain")
                )
            ]
            for axial_force in self.axial_forces[cross_section_index]:
                for strain_position_group in strain_position_groups:
                    for forward_strain_position_index, strain_position in enumerate(
                        strain_position_group
                    ):
                        successful = self._compute(
                            sub_cross_sections,
                            cross_section_index,
                            axial_force,
                            strain_position,
                        )
                        if (
                            not successful
                            and len(strain_position_group)
                            > forward_strain_position_index + 1
                        ):
                            break
                    if len(strain_position_group) > forward_strain_position_index + 1:
                        for backward_strain_position_index, strain_position in reversed(
                            list(
                                enumerate(
                                    strain_position_group[
                                        forward_strain_position_index + 1 :
                                    ]
                                )
                            )
                        ):
                            successful = self._compute(
                                sub_cross_sections,
                                cross_section_index,
                                axial_force,
                                strain_position,
                            )
                            if not successful:
                                break

    def _compute(
        self,
        sub_cross_sections: tuple[Crosssection, Crosssection],
        cross_section_index: int,
        axial_force: float,
        strain_position: StrainPosition,
    ) -> bool:
        """
        compute a Moment-Axial-Force Curvature Point under a given ``axial_force``
        and a ``strain_position`` value

        Parameters
        ----------
        sub_cross_sections : tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            Sub-cross-sections to be computed.
            Order is important as the ``axial_force`` is applied to the 1st sub-cross-section (index: 0) and
            the ``strain_position``-value is also assumed to be within the 1st sub-cross-section.
        cross_section_index : int
            sub-cross-section-number of the sub-cross-sections as passed to the class, where the
            axial-force is applied to.
            Important for saving and tracability after the computation.
        axial_force : float
            axial-force applied "as is" to the 1st cross-section in ``sub_cross_sections`` and with
            switched sign to the 2nd ``sub_cross_sections``
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            Strain- and position-value leading working together with ``axial_force`` as one
            boundary-condition for the computation.

        Returns
        -------
        bool
            ``True`` indicates a successful computation.
            ``False`` means the computation was not successful and the corresponding reason is appended
            together with the ``strain_position``-value to
            :py:attr:`~m_n_kappa.curves_m_n_kappa.MNCurvatureCurve.not_successful_reason`.
        """
        m_n_kappa_point = MomentAxialForceCurvature(
            sub_cross_sections=sub_cross_sections,
            axial_force=axial_force,
            strain_position=strain_position,
            positive_curvature=self.positive_curvature,
        )
        log.debug(
            f"MNCurvatureCurve._compute(): "
            f"{axial_force=}, {strain_position=}, successful={m_n_kappa_point.successful}"
        )
        if m_n_kappa_point.successful:
            self._save(m_n_kappa_point, cross_section_index)
        else:
            self._not_successful_reason.append(
                NotSuccessfulReason(
                    reason=m_n_kappa_point.not_successful_reason.reason,
                    strain_position=strain_position,
                )
            )
            log.debug(self._not_successful_reason[-1].reason)
        return m_n_kappa_point.successful

    def _save(
        self,
        m_n_kappa: MomentAxialForceCurvature,
        axial_force_cross_section_number: int,
    ) -> None:
        """save the computed value to :py:attr:`~m_n_kappa.MNCurvatureCurve.points"""
        self.points.add(
            moment=m_n_kappa.moment(),
            curvature=m_n_kappa.curvature,
            axial_force=m_n_kappa.axial_force,
            axial_force_cross_section_number=axial_force_cross_section_number,
            strain_difference=m_n_kappa.strain_difference,
            cross_section=m_n_kappa.computed_sub_cross_sections,
            strain_position=m_n_kappa.strain_position,
            neutral_axis_1=m_n_kappa.neutral_axes[0],
            neutral_axis_2=m_n_kappa.neutral_axes[1],
        )


class MCurvatureCurve:

    """
    computation of the Moment-Curvature curve assuming no
    connection between the sub-cross-sections

    .. versionadded:: 0.2.0

    The sub-cross-sections deform independently form each other,
    but the overall answer of the system
    """

    __slots__ = (
        "_sub_cross_sections",
        "_positive_curvature",
        "_m_kappa_curves",
        "_curvatures",
        "_points",
        "_not_successful_reason",
    )

    def __init__(
        self,
        sub_cross_sections: Crosssection
        | list[Crosssection]
        | tuple[Crosssection, Crosssection] = None,
        positive_curvature: bool = True,
    ):
        self._sub_cross_sections = initialize_sub_cross_sections(sub_cross_sections)
        self._positive_curvature = positive_curvature
        self._m_kappa_curves = self._compute_m_kappa_points()
        self._curvatures = self._compute_curvatures()
        self._points = MNKappaCurvePoints()
        self._not_successful_reason: list[NotSuccessfulReason] = []
        self._compute_m_kappa_curve_points()

    @property
    def curvatures(self) -> list[float]:
        """all relevant curvatures"""
        return self._curvatures

    @property
    def m_kappa_curves(self) -> list[MKappaCurvePoints]:
        """Moment-Curvature-Curve of the sub-cross-sections"""
        return self._m_kappa_curves

    @property
    def negative_curvature(self) -> bool:
        """indicates if negative curvature is to be computed"""
        if self.positive_curvature:
            return False
        else:
            return True

    @property
    def not_successful_reason(self) -> list[NotSuccessfulReason]:
        """for those computations that were not successful, here the reasons are given"""
        return self._not_successful_reason

    @property
    def positive_curvature(self) -> bool:
        """indicates if positive curvature is to be computed"""
        return self._positive_curvature

    @property
    def points(self) -> MNKappaCurvePoints:
        """computed points of the M-N-Kappa-curve"""
        return self._points

    @property
    def sub_cross_sections(self) -> tuple[Crosssection, Crosssection]:
        """sub-cross-sections to be computed"""
        return self._sub_cross_sections

    def _compute_m_kappa_points(self) -> list[MKappaCurvePoints]:
        """compute the M-Kappa-Curve-Points of both sub-cross-sections"""
        m_kappa_curves = []
        for cross_section in self.sub_cross_sections:
            m_kappa_curves.append(
                MKappaCurve(
                    cross_section, self.positive_curvature, self.negative_curvature
                ).m_kappa_points
            )
        return m_kappa_curves

    def _compute_curvatures(self) -> list[float]:
        """compute all curvatures"""
        curvatures = []
        min_curvatures = []
        max_curvatures = []
        for m_kappa_curve in self.m_kappa_curves:
            m_kappa_curvatures = m_kappa_curve.curvatures
            curvatures += m_kappa_curvatures
            min_curvatures.append(min(m_kappa_curvatures))
            max_curvatures.append(max(m_kappa_curvatures))
        min_curvature = max(min_curvatures)
        max_curvature = min(max_curvatures)
        curvatures = list(set(curvatures))
        return list(filter(lambda x: min_curvature <= x <= max_curvature, curvatures))

    def _compute_m_kappa_curve_points(self) -> None:
        """compute the new M-Kappa-Curve points from the given cross-sections"""
        for curvature in self.curvatures:
            if curvature == 0.0:
                continue
            moment = 0.0
            computed_cross_sections = []
            neutral_axes = []
            strain_position = None
            for index, m_kappa_curve in enumerate(self.m_kappa_curves):
                if curvature in m_kappa_curve.curvatures:
                    curvature_index = m_kappa_curve.curvatures.index(curvature)
                    point = m_kappa_curve.points[curvature_index]
                    computed_cross_sections.append(point.cross_section)
                    neutral_axes.append(point.neutral_axis)
                    moment += point.moment
                    strain_position = point.strain_position
                else:
                    m_kappa = MKappaByConstantCurvature(
                        cross_section=self.sub_cross_sections[index],
                        applied_curvature=curvature,
                        applied_axial_force=0.0,
                    )
                    computed_cross_sections.append(m_kappa.computed_cross_section)
                    moment += m_kappa.moment
                    neutral_axes.append(m_kappa.neutral_axis)

            self._points.add(
                moment=moment,
                curvature=curvature,
                axial_force=0.0,
                axial_force_cross_section_number=0,
                strain_position=strain_position,
                strain_difference=strain_difference(
                    curvature, neutral_axes[0], neutral_axes[1]
                ),
                cross_section=tuple(computed_cross_sections),
                neutral_axis_1=neutral_axes[0],
                neutral_axis_2=neutral_axes[1],
            )


class MNKappaCurve:
    """
    computation of Moment-Axial-Force-Curvature curve (M-N-Kappa)

    .. versionadded:: 0.2.0
    """

    __slots__ = (
        "_sub_cross_sections",
        "_include_positive_curvature",
        "_include_negative_curvature",
        "_not_successful_reason",
        "_points",
        "_m_n_curve",
        "_positive_m_n_kappa_curve",
        "_negative_m_n_kappa_curve",
        "_m_kappa_curve",
    )

    @log.init
    def __init__(
        self,
        sub_cross_sections: Crosssection
        | list[Crosssection]
        | tuple[Crosssection, Crosssection],
        include_positive_curvature: bool = True,
        include_negative_curvature: bool = False,
    ):
        r"""
        Parameters
        ----------
        sub_cross_sections : :py:class:`~m_n_kappa.Crosssection` | list[:py:class:`~m_n_kappa.Crosssection`] |
        tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            Sub-cross-sections to compute the M-N-Kappa-curve.
            In case given as single :py:class:`~m_n_kappa.Crosssection` this cross-section must consist of
            a slab (Concrete and Reinforcement) and a girder (Steel)
        include_positive_curvature : bool
            if ``True`` then positive curvature values are computed (Default: ``True``)
        include_negative_curvature : bool
            if ``True`` then negative curvature values are computed (Default: ``False``)

        Raises
        ------
        TypeError : if neither a `~m_n_kappa.Crosssection`, list[`~m_n_kappa.Crosssection`]
           or tuple[`~m_n_kappa.Crosssection`, `~m_n_kappa.Crosssection`] are passed

        See Also
        --------
        :py:class:`~m_n_kappa.MKappaCurve` : computation of Moment-Curvature-Curve assuming full interaction

        Examples
        --------
        This example illustrates the usage of :py:class:`~m_n_kappa.MNKappaCurve`.
        First two individual cross-sections may be created.
        In the following both cross-sections are :py:class:`~m_n_kappa.Rectangle`
        of material :py:class:`~m_n_kappa.Steel`.

        >>> from m_n_kappa import Steel, Rectangle, Crosssection
        >>> steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        >>> rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        >>> section_top = steel + rectangle_top
        >>> cross_section_top = Crosssection([section_top])
        >>> rectangle_bottom = Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> section_bottom = steel + rectangle_bottom
        >>> cross_section_bottom = Crosssection([section_bottom])
        >>> sub_cross_sections = [cross_section_top, cross_section_bottom]

        To compute moment-axial-force-curvature points these the list of ``sub_cross_sections``
        shall be passed to :py:class:`~m_n_kappa.MNKappaCurve`.
        In case you want to compute only positive moment-curvature-values you have to
        ``include_positive_curvature=True``, what is also the default configuration.
        Negative moment-curvature-values are included by ``include_negative_curvature=True``.

        The following code computes only positive values:

        >>> from m_n_kappa import MNKappaCurve
        >>> m_n_kappa_curve = MNKappaCurve(
        ...     sub_cross_sections=sub_cross_sections,
        ...     include_positive_curvature=True)

        :py:meth:`~m_n_kappa.MNKappaCurve.points`` returns :py:meth:`~m_n_kappa.MNKappaCurvePoints`
        what is a collection of all the successfully computed Moment-Axial force-Curvature points.
        The attributes :py:attr:`~m_n_kappa.MNKappaCurvePoints.moments`,
        :py:attr:`~m_n_kappa.MNKappaCurvePoints.curvatures`,
        :py:attr:`~m_n_kappa.MNKappaCurvePoints.axial_forces`,
        :py:attr:`~m_n_kappa.MNKappaCurvePoints.strain_differences`,
        gives you a list of the corresponding values.

        >>> m_n_kappa_points = m_n_kappa_curve.points
        >>> m_n_kappa_points.moments
        [355026.8934163825, 400000.0, 0.0, 236666.87937886757, 236666.50674824225, 372381.6934067906, 372282.02545773983, 361270.59229865274, 406270.5922986528, 384814.01494666666]

        :py:meth:`~m_n_kappa.MNKappaCurvePoints.print_points` prints a full table consisting of all
        successfully computed values.

        >>> print(m_n_kappa_points.print_points())
        ----------------------------------------------------------------------------------------------------------------------------------
             Moment     |  Curvature   | Neutral A.1 | Neutral A.2 |  Axial-force  | strain-diff. |   Strain   | Position | Material
        ----------------------------------------------------------------------------------------------------------------------------------
                    0.0 |   0.00000000 |     0.0000  |     0.0000  |          0.00 |     0.000000 |   0.000000 |      0.0 | -
               236666.5 |   0.00016905 |    10.0000  |    10.0000  |          0.00 |     0.000000 |  -0.001690 |      0.0 | Steel
               236666.9 |   0.00016905 |    10.0000  |    10.0000  |          0.00 |     0.000000 |   0.001690 |     20.0 | Steel
               355026.9 |   0.00000000 |   Infinity  |   Infinity  |     -35500.00 |    -0.003558 |  -0.001690 |      0.0 | Steel
               361270.6 |   0.01483095 |    10.1140  |    10.2916  |     -35500.00 |    -0.002634 |  -0.001690 |     10.0 | Steel
               372282.0 |   0.00923123 |     9.8175  |    10.1831  |      35500.00 |     0.003375 |  -0.001690 |     10.0 | Steel
               372381.7 |   0.00923123 |     9.8169  |    10.1825  |     -35500.00 |    -0.003375 |   0.001690 |     10.0 | Steel
               384814.0 |   0.01500000 |    10.0000  |    10.0000  |          0.00 |     0.000000 |  -0.150000 |      0.0 | Steel
               400000.0 |   0.00000000 |   Infinity  |   Infinity  |     -40000.00 |    -0.300000 |  -0.150000 |      0.0 | Steel
               406270.6 |   0.01483095 |     9.7084  |     9.8860  |      35500.00 |     0.002634 |   0.001690 |     10.0 | Steel
        ----------------------------------------------------------------------------------------------------------------------------------


        """
        if (
            isinstance(sub_cross_sections, tuple)
            and len(sub_cross_sections) == 2
            and isinstance(sub_cross_sections[0], Crosssection)
            and isinstance(sub_cross_sections[1], Crosssection)
        ):
            self._sub_cross_sections = sub_cross_sections
        elif (
            isinstance(sub_cross_sections, list)
            and len(sub_cross_sections) == 2
            and isinstance(sub_cross_sections[0], Crosssection)
            and isinstance(sub_cross_sections[1], Crosssection)
        ):
            self._sub_cross_sections = tuple(sub_cross_sections)
        elif isinstance(sub_cross_sections, Crosssection):
            self._sub_cross_sections = sub_cross_sections.get_sub_cross_sections()
        else:
            raise TypeError(
                'sub_cross_section must be of type "Crosssection" or of type "tuple[Crosssection, Crosssection]"'
            )
        self._include_positive_curvature = include_positive_curvature
        self._include_negative_curvature = include_negative_curvature
        self._m_n_curve = MNCurve(self.sub_cross_sections)
        if include_positive_curvature and not include_negative_curvature:
            self._points = MNKappaCurvePoints(
                list(filter(lambda x: x.moment > 0.0, self.m_n_curve.points.points))
            )
        elif not include_positive_curvature and include_negative_curvature:
            self._points = MNKappaCurvePoints(
                list(filter(lambda x: x.moment < 0.0, self.m_n_curve.points.points))
            )
        else:
            self._points = self.m_n_curve.points
        self._not_successful_reason = self.m_n_curve.not_successful_reason
        if self.include_positive_curvature:
            self._positive_m_n_kappa_curve = MNCurvatureCurve(
                sub_cross_sections=self.sub_cross_sections,
                axial_forces=self.m_n_curve.points.cross_section_axial_forces(
                    positive_moment=True
                ),
                strain_positions=self.m_n_curve.strain_positions,
                positive_curvature=True,
            )
            self._points += self._positive_m_n_kappa_curve.points
            self._not_successful_reason += (
                self._positive_m_n_kappa_curve.not_successful_reason
            )
        if self.include_negative_curvature:
            self._negative_m_n_kappa_curve = MNCurvatureCurve(
                sub_cross_sections=self.sub_cross_sections,
                axial_forces=self.m_n_curve.points.cross_section_axial_forces(
                    positive_moment=False
                ),
                strain_positions=self.m_n_curve.strain_positions,
                positive_curvature=False,
            )
            self._points += self._negative_m_n_kappa_curve.points
            self._not_successful_reason += (
                self._negative_m_n_kappa_curve.not_successful_reason
            )
        # add moment-curvatures with zero axial-forces
        self._m_kappa_curve = MKappaCurve(
            cross_section=self.sub_cross_sections[0] + self.sub_cross_sections[1],
            include_positive_curvature=self.include_positive_curvature,
            include_negative_curvature=self.include_negative_curvature,
        )
        self._points += self._m_kappa_curve.m_kappa_points
        self._not_successful_reason += self._m_kappa_curve.not_successful_reason

    def __repr__(self) -> str:
        return "MNKappaCurve()"

    def __str__(self) -> str:
        text = [
            self.points.print_points(),
        ]
        return print_chapter(text)

    @property
    def sub_cross_sections(self) -> tuple[Crosssection, Crosssection]:
        """cross-section the :math:`M`-:math:`N`-:math:`\\kappa`-curve shall be computed"""
        return self._sub_cross_sections

    @property
    def include_positive_curvature(self) -> bool:
        """returns if :math:`M`-:math:`N`-:math:`\\kappa` under positive bending/curvature is included"""
        return self._include_positive_curvature

    @property
    def include_negative_curvature(self) -> bool:
        """returns if :math:`M`-:math:`N`-:math:`\\kappa` under negative bending/curvature is included"""
        return self._include_negative_curvature

    @property
    def points(self) -> MNKappaCurvePoints:
        """moment-axial-force-curvature points of the curve"""
        return self._points

    @property
    def m_n_curve(self) -> MNCurve:
        """M-N-curve (without curvature)"""
        return self._m_n_curve

    @property
    def not_successful_reason(self) -> list[NotSuccessfulReason]:
        """for those computations that were not successful, here the reasons are given"""
        return self._not_successful_reason
