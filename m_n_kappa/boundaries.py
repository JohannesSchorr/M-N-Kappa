import operator
from dataclasses import dataclass

from .general import StrainPosition, EdgeStrains, neutral_axis

from .log import LoggerMethods

log = LoggerMethods(__name__)


def compute_curvatures(
    strain_position: StrainPosition, position_strains: list[StrainPosition]
) -> list[EdgeStrains]:
    """
    compute curvatures from a position with associated strains
    and a list of strains with its associated positions

    Parameters
    ----------
    strain_position : :py:class:`~m_n_kappa.StrainPosition`
        strain-position value that serves as basis
    position_strains : list[:py:class:`~m_n_kappa.StrainPosition`]
        Strain-position values the method iterates over

    Returns
    -------
    list[:py:class:`~m_n_kappa.general.EdgeStrains`]
        edge-strains the curvature may be computed from
    """
    edge_strains = []
    if len(position_strains) > 0:
        for position_strain in position_strains:
            if strain_position.position != position_strain.position:
                edge_strains.append(
                    EdgeStrains(
                        bottom_edge_strain=strain_position,
                        top_edge_strain=position_strain,
                    )
                )
    return edge_strains


def remove_higher_strains(strain: float, position_strains: list[StrainPosition]):
    """
    Return strain-position values where ``strain``-attribute is smaller ``strain``

    Parameters
    ----------
    strain : float
        strain-value that serves as "split"-line
    position_strains : list[:py:class:`~m_n_kappa.general.StrainPosition`]
        :py:class:`~m_n_kappa.general.StrainPosition` to check for strain

    Returns
    -------
    list[:py:class:`~m_n_kappa.general.StrainPosition`]
        strain-position values with strain smaller than ``strain``
    """
    return list(filter(lambda x: x.strain < strain, position_strains))


def remove_smaller_strains(strain: float, position_strains: list[StrainPosition]):
    """
    Return strain-position values where ``strain``-attribute is greater ``strain``

    Parameters
    ----------
    strain : float
        strain-value that serves as "split"-line
    position_strains : list[:py:class:`~m_n_kappa.general.StrainPosition`]
        :py:class:`~m_n_kappa.general.StrainPosition` to check for strain

    Returns
    -------
    list[:py:class:`~m_n_kappa.general.StrainPosition`]
        strain-position values with strain smaller than ``strain``
    """ ""
    return list(filter(lambda x: strain < x.strain, position_strains))


def get_lower_positions(position: float, position_strains: list[StrainPosition]):
    """
    get all positions in 'position_strains',
    that are lower than the given position_value

    lower: greater position-value than given by position as vertical axis is vice versa
    """
    return list(filter(lambda x: x.position > position, position_strains))


def get_higher_positions(position: float, position_strains: list[StrainPosition]):
    """
    get all positions in 'position_strains',
    that are higher than the given position_value

    higher: smaller position-value than given by position as vertical axis is vice versa
    """
    return list(filter(lambda x: x.position < position, position_strains))


@dataclass(slots=True)
class MaximumCurvature:

    """store values connected to maximum curvature

    Parameters
    ----------
    curvature : float
        maximum curvature
    start : dBound
        start strain_value and position_value for the given maximum curvature
    other : Bound
        other strain_value and position_value for the given maximum curvature
    maximum_positive_section_strains : list
        maximum positive material strains of the sections in the cross_section
    maximum_negative_section_strains : list
        maximum negative material strains of the sections in the cross_section

    """

    curvature: float
    start: StrainPosition
    other: StrainPosition
    maximum_positive_section_strains: list[StrainPosition]
    maximum_negative_section_strains: list[StrainPosition]

    def __post_init__(self):
        log.info(f"Finished {self.__repr__()}")

    @property
    def positive(self) -> list[StrainPosition]:
        """maximum positive :py:class:`~m_n_kappa.StrainPosition` of all materials and positions"""
        return self.maximum_positive_section_strains

    @property
    def negative(self) -> list[StrainPosition]:
        """maximum negative :py:class:`~m_n_kappa.StrainPosition` of all materials and positions"""
        return self.maximum_negative_section_strains

    @log.result
    def compute(self, strain_position: StrainPosition) -> float:
        """
        maximum curvature for given strain_value at given position_value

        Accomplished by computing all curvatures from the given ``strain_position`` with the
        :py:class:`~m_n_kappa.StrainPosition` with maximum positive or negative strains of the cross-sections'
        material models and comparing these against each other.
        The maximum positive or negative curvature will be given.

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` working as basis for the computation

        Returns
        -------
        float
            maximum possible curvature considering the material-models of the :py:class:`~m_n_kappa.Crosssection`
            and their position
        """
        if self.__has_positive_curvature():
            curvature = self.__compute_positive_curvatures(strain_position)
        else:
            curvature = self.__compute_negative_curvatures(strain_position)
        return curvature

    def __has_positive_curvature(self) -> bool:
        """check due to the curvature if its positive or negative"""
        if self.curvature > 0.0:
            return True
        else:
            return False

    @log.result
    def __get_positive_position_strains(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        determine all :py:class:`~m_n_kappa.StrainPosition` that give positive curvature
        in combination with ``strain_position``

        1. above the given position and have smaller strains than the given one
        2. below the given position and have higher strains thant the given one

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` that functions as basis comparing element

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` that give in comparison with the given ``strain_position``
            a negative curvature
        """
        position_strains = get_higher_positions(strain_position.position, self.negative)
        position_strains += get_lower_positions(strain_position.position, self.positive)
        return position_strains

    @log.result
    def __get_negative_position_strains(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        determine all :py:class:`~m_n_kappa.StrainPosition` that give negative curvature
        in combination with ``strain_position``

        1. above the given position and have higher strains than the given one
        2. below the given position and have smaller strains thant the given one

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` that functions as basis comparing element

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` that give in comparison with the given ``strain_position``
            a negative curvature
        """
        position_strains = get_higher_positions(strain_position.position, self.positive)
        position_strains += get_lower_positions(strain_position.position, self.negative)
        return position_strains

    def __compute_negative_curvatures(self, strain_position: StrainPosition) -> float:
        """
        compute negative curvatures

        This is accomplished by getting all relevant combinations of :py:class:`~m_n_kappa.StrainPosition`
        considering ``strain_position`` leading to negative curvatures.
        The maximum of these curvatures is the desired curvature.
        Smaller curvatures lead in combination with ``strain_position`` to a failure
        as the resulting strain-distribution leads to exceeding the stress-strain curve of some materials.

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            basis :py:class:`~m_n_kappa.StrainPosition`

        Returns
        -------
        float
            maximum negative curvature
        """
        position_strains = self.__get_negative_position_strains(strain_position)
        edge_strains = compute_curvatures(strain_position, position_strains)
        decisive_edge_strain = max(edge_strains, key=operator.attrgetter("curvature"))
        if decisive_edge_strain.top_edge_strain == strain_position:
            log.info(
                f"Decisive strain-position values: {decisive_edge_strain.bottom_edge_strain}"
            )
        else:
            log.info(
                f"Decisive strain-position values: {decisive_edge_strain.top_edge_strain}"
            )
        return decisive_edge_strain.curvature

    def __compute_positive_curvatures(self, strain_position: StrainPosition) -> float:
        """
        compute positive curvatures

        This is accomplished by getting all relevant combinations of :py:class:`~m_n_kappa.StrainPosition`
        considering ``strain_position`` leading to positive curvatures.
        The minimum of these curvatures is the desired curvature.
        Higher curvatures lead in combination with ``strain_position`` to a failure,
        as the resulting strain-distribution leads to exceeding the  stress-strain curve of some materials.

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            basis :py:class:`~m_n_kappa.StrainPosition`

        Returns
        -------
        float
            maximum negative curvature
        """
        position_strains = self.__get_positive_position_strains(strain_position)
        edge_strains = compute_curvatures(strain_position, position_strains)
        decisive_edge_strain = min(edge_strains, key=operator.attrgetter('curvature'))
        if decisive_edge_strain.top_edge_strain == strain_position:
            log.info(
                f"Decisive strain-position values: {decisive_edge_strain.bottom_edge_strain}"
            )
        else:
            log.info(
                f"Decisive strain-position values: {decisive_edge_strain.top_edge_strain}"
            )
        return decisive_edge_strain.curvature


@dataclass(slots=True)
class MinimumCurvature:

    """store maximum positive and negative section strains
    for determination of minimum curvature

    Parameters
    ----------
    maximum_positive_section_strains : list[:py:class:`~m_n_kappa.StrainPosition`]
        maximum positive material strains of the sections in the cross_section
    maximum_negative_section_strains : list[:py:class:`~m_n_kappa.StrainPosition`]
        maximum negative material strains of the sections in the cross_section
    curvature_is_positive : bool
        if ``True`` then positive curvature is assumed, else negative curvature is assumed
    """

    maximum_positive_section_strains: list[StrainPosition]
    maximum_negative_section_strains: list[StrainPosition]
    curvature_is_positive: bool
    top_edge: float = None
    bottom_edge: float = None

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")
        if self.top_edge is None:
            self.top_edge = min(
                self.all, key=operator.attrgetter("position")
            ).position  # top-edge
        if self.bottom_edge is None:
            self.bottom_edge = max(
                self.all, key=operator.attrgetter('position')
            ).position  # bottom-edge

    @property
    def positive(self) -> list[StrainPosition]:
        """maximum positive :py:class:`~m_n_kappa.StrainPosition` of all materials and positions"""
        return self.maximum_positive_section_strains

    @property
    def negative(self) -> list[StrainPosition]:
        """maximum negative :py:class:`~m_n_kappa.StrainPosition` of all materials and positions"""
        return self.maximum_negative_section_strains

    @property
    def all(self) -> list[StrainPosition]:
        """maximum positive and negative :py:class:`~m_n_kappa.StrainPosition`"""
        return self.positive + self.negative

    @log.result
    def compute(self, strain_position: StrainPosition) -> float:
        """
        compute the minimum possible curvature considering the strain at a position (``strain_position``)

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` the minimum curvature is to be computed.

        Returns
        -------
        float
        """
        if (
            max(self.negative, key=operator.attrgetter("strain")).strain
            <= strain_position.strain
            <= min(self.positive, key=operator.attrgetter("strain")).strain
        ):
            log.debug(f"{strain_position} within minimal positive and negative strains")
            position_strains = self.__edge_positions(strain_position)
            edge_strains = compute_curvatures(strain_position, position_strains)
            decisive_edge_strain = min(edge_strains, key=lambda x: abs(x.curvature))
        else:
            log.debug(
                f"{strain_position} outside minimal positive and negative strains"
            )
            position_strains = self.__get_position_strains(strain_position)
            edge_strains = compute_curvatures(strain_position, position_strains)
            decisive_edge_strain = max(edge_strains, key=lambda x: abs(x.curvature))
        if decisive_edge_strain.top_edge_strain == strain_position:
            log.info(
                f"Decisive strain-position value for {strain_position=}: {decisive_edge_strain.bottom_edge_strain}"
            )
        else:
            log.info(
                f"Decisive strain-position value for {strain_position=}: {decisive_edge_strain.top_edge_strain}"
            )
        return decisive_edge_strain.curvature

    @log.result
    def __edge_positions(
        self, strain_position: StrainPosition, additional_strain: float = 0.0001
    ) -> list[StrainPosition]:
        """
        Get edge-positions of the cross-section and apply strain :math:`\\pm` ``additional_strain``

        Edge-positions of the cross-section are:
        - top-edge
        - bottom-edge

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            edge-positions with strain :math:`\\pm` ``additional_strain``
        """

        if self.curvature_is_positive:
            strain_positions = [
                StrainPosition(
                    strain=strain_position.strain - additional_strain,
                    position=self.top_edge,
                    material="-",
                ),
                StrainPosition(
                    strain=strain_position.strain + additional_strain,
                    position=self.bottom_edge,
                    material="-",
                ),
            ]
        else:
            strain_positions = [
                StrainPosition(
                    strain=strain_position.strain + additional_strain,
                    position=self.top_edge,
                    material="-",
                ),
                StrainPosition(
                    strain=strain_position.strain - additional_strain,
                    position=self.bottom_edge,
                    material="-",
                ),
            ]
        log.info(f"Top-Edge: {strain_positions[0]}, Bottom-Edge: {strain_positions[1]}")
        return strain_positions

    @log.result
    def __get_position_strains(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        Determine the :py:class:`~m_n_kappa.StrainPosition`s that give minimum curvature with
        ``strain_position``.

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` the minimum curvature is computed with

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` points that give minimum curvature with the given
            ``strain_position``
        """
        if self.curvature_is_positive:
            if strain_position.strain > 0.0:
                position_strains = self.__positive_curvature_positive_strain(
                    strain_position
                )
            else:
                position_strains = self.__positive_curvature_negative_strain(
                    strain_position
                )
        else:
            if strain_position.strain > 0.0:
                position_strains = self.__negative_curvature_positive_strain(
                    strain_position
                )
            else:
                position_strains = self.__negative_curvature_negative_strain(
                    strain_position
                )
        return position_strains

    def __positive_curvature_positive_strain(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` positive curvatures

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` must have positive ``strain``

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` positive curvatures
        """
        lower_position_strains = get_lower_positions(
            strain_position.position, self.positive
        )
        position_strains = remove_smaller_strains(
            strain_position.strain, lower_position_strains
        )
        higher_position_strains = get_higher_positions(
            strain_position.position, self.positive
        )
        position_strains += remove_higher_strains(
            strain_position.strain, higher_position_strains
        )
        return position_strains

    def __positive_curvature_negative_strain(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` positive curvatures

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` must have negative ``strain``

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` positive curvatures
        """
        higher_position_strains = get_higher_positions(
            strain_position.position, self.negative
        )
        position_strains = remove_higher_strains(
            strain_position.strain, higher_position_strains
        )
        lower_position_strains = get_lower_positions(
            strain_position.position, self.negative
        )
        position_strains += remove_smaller_strains(
            strain_position.strain, lower_position_strains
        )
        return position_strains

    def __negative_curvature_positive_strain(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` negative curvatures

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` must have positive ``strain``

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` negative curvatures
        """
        lower_position_strains = get_lower_positions(
            strain_position.position, self.positive
        )
        position_strains = remove_higher_strains(
            strain_position.strain, lower_position_strains
        )
        higher_position_strains = get_higher_positions(
            strain_position.position, self.positive
        )
        position_strains += remove_smaller_strains(
            strain_position.strain, higher_position_strains
        )
        return position_strains

    def __negative_curvature_negative_strain(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        """
        :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` negative curvatures

        Parameters
        ----------
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            :py:class:`~m_n_kappa.StrainPosition` must have negative ``strain``

        Returns
        -------
        list[:py:class:`~m_n_kappa.StrainPosition`]
            :py:class:`~m_n_kappa.StrainPosition` values that give with ``strain_position`` negative curvatures
        """
        higher_position_strains = get_higher_positions(
            strain_position.position, self.negative
        )
        position_strains = remove_smaller_strains(
            strain_position.strain, higher_position_strains
        )
        lower_position_strains = get_lower_positions(
            strain_position.position, self.negative
        )
        position_strains += remove_higher_strains(
            strain_position.strain, lower_position_strains
        )
        return position_strains


@dataclass(slots=True)
class DecisiveNeutralAxis:
    """
    compute decisive neutral axis

    .. versionadded:: 0.2.0

    Parameters
    ----------
    maximum_positive_section_strains : list
        maximum positive material strains of the sections in the cross_section
    maximum_negative_section_strains : list
        maximum negative material strains of the sections in the cross_section
    """

    maximum_positive_section_strains: list[StrainPosition]
    maximum_negative_section_strains: list[StrainPosition]

    def __post_init__(self):
        log.info(f"Finished {self.__repr__()}")

    @log.result
    def compute(self, curvature: float) -> tuple[float, float]:
        """
        compute the highest and the lowest possible neutral-axis under the given curvature

        The vertical position of the neutral axis under constant ``curvature``
        indicates the maximum and the minimum axial forces.
        The computation of the neutral-axis must consider the ``curvature``
        as well as the ``maximum_positive_section_strains`` and
        ``maximum_negative_section_strains``.
        Otherwise, iterating on the axial force may fail due to exceeding
        the maximum and minimum strains of a material.

        Parameters
        ----------
        curvature : float
            curvature-value working as boundary that needs to be fulfilled

        Returns
        -------
        tuple(float, float)
            highest and the lowest possible neutral-axis under the given curvature

        See Also
        --------
        :ref:`theory.strain_based_design.boundary_values.neutral_axis` : Neutral-axis
           baundary-values in the :ref:`theory`.
        """
        if curvature > 0.0:
            # vertical position of point below neutral axis (in coordinates: position < neutral_axis)
            max_neutral_axis = max(
                [
                    neutral_axis(
                        strain_position.strain, curvature, strain_position.position
                    )
                    for strain_position in self.maximum_positive_section_strains
                ]
            )
            # vertical position of point above neutral axis (position < neutral_axis)
            min_neutral_axis = min(
                [
                    neutral_axis(
                        strain_position.strain, curvature, strain_position.position
                    )
                    for strain_position in self.maximum_negative_section_strains
                ]
            )
        else:
            # vertical position of point above neutral axis (position < neutral_axis)
            min_neutral_axis = min(
                [
                    neutral_axis(
                        strain_position.strain, curvature, strain_position.position
                    )
                    for strain_position in self.maximum_positive_section_strains
                ]
            )
            # vertical position of point below neutral axis (in coordinates: position < neutral_axis)
            max_neutral_axis = max(
                [
                    neutral_axis(
                        strain_position.strain, curvature, strain_position.position
                    )
                    for strain_position in self.maximum_negative_section_strains
                ]
            )
        return min_neutral_axis, max_neutral_axis


@dataclass(slots=True)
class BoundaryValues:
    """store boundary condition values

    Parameters
    ----------
    maximum_curvature : MaximumCurvature
        container for the maximum curvature values
    minimum_curvature : MinimumCurvature
        container for the minimum curvature values
    """

    maximum_curvature: MaximumCurvature
    minimum_curvature: MinimumCurvature


@dataclass(slots=True)
class Boundaries:
    """store boundary conditions

    .. versionadded:: 0.1.0

    .. versionadded:: 0.2.0
       ``neutral_axes`` for computation of boundary-values of neutral
       axis

    Parameters
    ----------
    positive : BoundaryValues
        container for the positive boundary condition values
    negative : BoundaryValues
        container for the negative boundary condition values
    neutral_axes : DecisiveNeutralAxis
        use to compute the decisive neutral axes (min/max) of
        the cross-section
    """

    positive: BoundaryValues
    negative: BoundaryValues
    neutral_axes: DecisiveNeutralAxis
