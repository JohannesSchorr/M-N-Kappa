from dataclasses import dataclass

from .general import StrainPosition, EdgeStrains

import logging
import logging.config
import yaml
import pathlib

with open(pathlib.Path(__file__).parent.absolute() / "logging-config.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


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
                    ))
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
    """""
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


@dataclass
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
        logger.info(f'Created {self.__repr__()}')

    @property
    def positive(self) -> list[StrainPosition]:
        """maximum positive :py:class:`~m_n_kappa.StrainPosition` of all materials and positions"""
        return self.maximum_positive_section_strains

    @property
    def negative(self) -> list[StrainPosition]:
        """maximum negative :py:class:`~m_n_kappa.StrainPosition` of all materials and positions"""
        return self.maximum_negative_section_strains

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
        logger.info(f"Computed maximum curvature for {strain_position}: {curvature}")
        return curvature

    def __has_positive_curvature(self) -> bool:
        """check due to the curvature if its positive or negative"""
        if self.curvature > 0.0:
            return True
        else:
            return False

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
        decisive_edge_strain = max(edge_strains, key=lambda x: x.curvature)
        if decisive_edge_strain.top_edge_strain == strain_position:
            logger.info(f'Decisive strain-position values: {decisive_edge_strain.bottom_edge_strain}')
        else:
            logger.info(f'Decisive strain-position values: {decisive_edge_strain.top_edge_strain}')
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
        decisive_edge_strain = min(edge_strains, key=lambda x: x.curvature)
        if decisive_edge_strain.top_edge_strain == strain_position:
            logger.info(f'Decisive strain-position values: {decisive_edge_strain.bottom_edge_strain}')
        else:
            logger.info(f'Decisive strain-position values: {decisive_edge_strain.top_edge_strain}')
        return decisive_edge_strain.curvature


@dataclass
class MinimumCurvature:

    """store maximum positive and negative section strains
    for determination of minimum curvature

    Parameters
    ----------
    maximum_positive_section_strains : list
        maximum positive material strains of the sections in the cross_section
    maximum_negative_section_strains : list
        maximum negative material strains of the sections in the cross_section
    curvature_is_positive : bool
        if True than positive curvature is assumed
        if False than negative curvature is assumed
    """

    maximum_positive_section_strains: list[StrainPosition]
    maximum_negative_section_strains: list[StrainPosition]
    curvature_is_positive: bool

    @property
    def positive(self) -> list[StrainPosition]:
        return self.maximum_positive_section_strains

    @property
    def negative(self) -> list[StrainPosition]:
        return self.maximum_negative_section_strains

    def compute(self, strain_position: StrainPosition) -> float:
        """
        compute the minimum possible curvature considering the strain at a position
        as well as the possible maximum
        """
        if self.curvature_is_positive:
            return self.__compute_positive_curvature(strain_position)
        else:
            return self.__compute_negative_curvature(strain_position)

    def __compute_positive_curvature(self, strain_position: StrainPosition) -> float:
        """compute the maximum positive curvature"""
        position_strains = self.__get_positive_position_strains(strain_position)
        curvatures = compute_curvatures(strain_position, position_strains)
        if len(curvatures) == 0:
            edge_positions = self.__edge_positions()
            curvatures += compute_curvatures(strain_position, edge_positions)
        return max(curvatures)

    def __edge_positions(self) -> list[StrainPosition]:
        """
        Get edge-positions of the cross-section and apply zero strain.
        Edge-positions of the cross-section are:
        - top-edge
        - bottom-edge

        Returns
        -------
        list[StrainPosition]
            edge-positions with zero-strain
        """
        section_strains = self.maximum_negative_section_strains + self.maximum_positive_section_strains
        positions = [min(section_strains, key=lambda x: x.position),  # top-edge
                     max(section_strains, key=lambda x: x.position)]  # bottom-edge
        return [StrainPosition(strain=0.0, position=position.position, material="-") for position in positions]

    def __get_positive_position_strains(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        if strain_position.strain > 0.0:
            position_strains = get_lower_positions(
                strain_position.position, self.positive
            )
            position_strains = remove_higher_strains(
                strain_position.strain, position_strains
            )
        else:
            position_strains = get_higher_positions(
                strain_position.position, self.negative
            )
            position_strains = remove_smaller_strains(
                strain_position.strain, position_strains
            )
        return position_strains

    def __compute_negative_curvature(self, strain_position: StrainPosition) -> float:
        position_strains = self.__get_negative_position_strains(strain_position)
        curvatures = compute_curvatures(strain_position, position_strains)
        if len(curvatures) == 0:
            edge_positions = self.__edge_positions()
            curvatures += compute_curvatures(strain_position, edge_positions)
        return min(curvatures)

    def __get_negative_position_strains(
        self, strain_position: StrainPosition
    ) -> list[StrainPosition]:
        if strain_position.strain < 0.0:
            position_strains = get_higher_positions(
                strain_position.position, self.positive
            )
            position_strains = remove_higher_strains(
                strain_position.strain, position_strains
            )
        else:
            position_strains = get_lower_positions(
                strain_position.position, self.negative
            )
            position_strains = remove_smaller_strains(
                strain_position.strain, position_strains
            )
        return position_strains


@dataclass
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


@dataclass
class Boundaries:
    """store boundary conditions

    Parameters
    ----------
    positive : BoundaryValues
        container for the positive boundary condition values
    negative : BoundaryValues
        container for the negative boundary condition values
    """

    positive: BoundaryValues
    negative: BoundaryValues