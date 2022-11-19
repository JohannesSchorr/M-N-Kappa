from dataclasses import dataclass

from .general import interpolation, StrainPosition
from .crosssection import Crosssection
from .curves_m_kappa import MKappaCurve, MKappaCurvePoints, MKappaCurvePoint
from .internalforces import (
    ABCSingleSpan,
    SingleSpanSingleLoads,
    SingleLoad,
    SingleSpanUniformLoad
)


class Node:

    """Beam-Node

    stores the cross-section, the position_value in the beam and the computed M-Kappa-Curve
    """

    __slots__ = '_cross_section', '_m_kappa_curve', '_position', '_number'

    node_number: int = 0

    def __init__(self, cross_section: Crosssection, position: float):
        self._cross_section = cross_section
        self._position = position
        self._m_kappa_curve = MKappaCurve(
            self.cross_section,
            include_positive_curvature=True
        ).m_kappa_points
        Node.node_number += 1
        self._number = Node.node_number

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def m_kappa_curve(self) -> MKappaCurvePoints:
        return self._m_kappa_curve

    @property
    def position(self) -> float:
        return self._position

    @property
    def number(self) -> int:
        return self._number

    def curvature_by(self, moment: float) -> float:
        """compute curvature given a moment using the M-Kappa-Curve"""
        return self.m_kappa_curve.curvature(moment)

    def incremental_deformation(self, load: ABCSingleSpan, single_load: SingleSpanSingleLoads) -> float:
        """determine curvature and single-load-moment at the node under given loading"""
        moment = load.moment(self.position)
        curvature = self.curvature_by(moment)
        single_load_moment = single_load.moment(self.position)
        return curvature * single_load_moment


@dataclass
class LoadStep:

    load: ABCSingleSpan
    point: MKappaCurvePoint


@dataclass
class Loading:

    """compute the load-steps by analysis of decisive m-kappa-curve

    decisive M-Kappa-curve is determined by the position_value of the maximum moment
    """

    beam_length: float
    nodes: list[Node]
    load: ABCSingleSpan = None

    def __post_init__(self):
        if self.load is None:
            self.load = SingleSpanUniformLoad(self.beam_length, 1.0)

    def maximum_resistance_moments(self) -> list[float]:
        return [node.m_kappa_curve.maximum_moment() for node in self.nodes]

    def _position_maximum_moment(self) -> float:
        return self.load.position_of_maximum_moment()

    def decisive_m_kappa_curve(self) -> MKappaCurvePoints:
        position = self._position_maximum_moment()
        return self.m_kappa_curve_at(position)

    def load_steps(self) -> list[LoadStep]:
        return [
            LoadStep(self.load.load_by(point.moment, self._position_maximum_moment()), point)
            for point in self.decisive_m_kappa_curve().points
        ]

    def m_kappa_curve_at(self, position) -> MKappaCurvePoints:
        return list(
            filter(lambda x: x.position == position, self.nodes)
        )[0].m_kappa_curve


@dataclass
class Deformation:
    """container for deformations"""
    position: float
    load: float
    deformation: float
    m_kappa_point: MKappaCurvePoint


class Beam:

    """Beam consisting of nodes"""

    __slots__ = (
        '_cross_section',
        '_length',
        '_element_number',
        '_load',
        '_element_standard_length',
        '_positions',
        '_nodes',
        '_load_steps'
    )

    def __init__(
        self,
        cross_section: Crosssection,
        length: float,
        element_number: int,
        load: ABCSingleSpan
    ):
        """
        Parameters
        ----------
        cross_section : Crosssection
            cross-section the beam consists of
        length : float
            length of the beam
        element_number : int
            number of elements the beam consists of
        load : ABCSingleSpan
            load-section_type applied to the beam
        """
        self._cross_section = cross_section
        self._length = length
        self._element_number = element_number
        self._load = load
        self._element_standard_length = self.length / self.element_number
        self._positions = self._create_positions()
        self._nodes = self._create_nodes()
        self._load_steps = Loading(self.length, self.nodes, self.load).load_steps()

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def length(self) -> float:
        return self._length

    @property
    def load(self) -> ABCSingleSpan:
        return self._load

    @property
    def load_steps(self) -> list[LoadStep]:
        return self._load_steps

    @property
    def element_number(self) -> int:
        return self._element_number

    @property
    def element_standard_length(self) -> float:
        return self._element_standard_length

    @property
    def positions(self) -> list[float]:
        return self._positions

    @property
    def nodes(self) -> list[Node]:
        return self._nodes

    def deformation(self, at_position: float, load: ABCSingleSpan) -> float:
        """compute deformation at given position_value under given load

        Parameters
        ----------
        at_position : float
            position_value the deformation is to be computed
        load : float
            load where the deformation is to be computed

        Returns
        -------
        float
            deformation under given load at given position_value
        """
        if self._position_in_beam(at_position):
            if at_position in self.positions:
                return self._deformation_at_node(at_position, load)
            else:
                return self._deformation_between_nodes(at_position, load)

    def deformations(self, at_position: float) -> list[Deformation]:
        """computes deformations at given position_value for relevant load-steps"""
        deformations = []
        for load_step in self.load_steps:
            if load_step.load.loading == 0.0:
                computed_deformation = 0.0
            else:
                computed_deformation = self.deformation(at_position, load_step.load)
            deformations.append(
                Deformation(
                    position=at_position,
                    load=load_step.load.loading,
                    deformation=computed_deformation,
                    m_kappa_point=load_step.point,
                )
            )
        return deformations

    def deformations_at_maximum_moment_position(self) -> list[Deformation]:
        """computes deformations at the decisive position_value for relevant load-steps"""
        position_of_maximum_moment = self.load.position_of_maximum_moment()
        deformations = self.deformations(position_of_maximum_moment)
        return sorted(deformations, key=lambda x: x.load)

    def _deformation_at_node(self, at_position: float, load: ABCSingleSpan) -> float:
        return sum(self._incremental_deformations(at_position, load))

    def _deformation_between_nodes(self, at_position: float, load: ABCSingleSpan) -> float:
        smaller_position = max(list(filter(lambda x: x < at_position, self.positions)))
        deformation_at_smaller_position = self._deformation_at_node(smaller_position, load)
        higher_position = min(list(filter(lambda x: x > at_position, self.positions)))
        deformation_at_higher_position = self._deformation_at_node(higher_position, load)
        return interpolation(
            position_value=at_position,
            first_pair=[smaller_position, deformation_at_smaller_position],
            second_pair=[higher_position, deformation_at_higher_position],
        )

    def _incremental_deformations(
        self,
        for_position: float,
        load: ABCSingleSpan
    ) -> list[float]:
        single_load = SingleLoad(for_position, 1.0)
        single_span_single_load = SingleSpanSingleLoads(self.length, [single_load])
        return [
            self._incremental_deformation(node_index, load, single_span_single_load)
            for node_index in range(len(self.nodes) - 1)]

    def _incremental_deformation(
        self,
        node_index: int,
        load: ABCSingleSpan,
        single_load: SingleSpanSingleLoads
    ):
        node_1_result = self.nodes[node_index].incremental_deformation(load, single_load)
        node_2_result = self.nodes[node_index+1].incremental_deformation(load, single_load)
        return 0.5*(node_1_result + node_2_result) * self._element_length(node_index)

    def _create_positions(self) -> list[float]:
        positions = [number * self.element_standard_length for number in range(1, self.element_number)]
        positions.append(self.load.position_of_maximum_moment())
        positions = list(set(positions))
        positions = sorted(positions)
        return positions

    def _position_in_beam(self, position: float) -> bool:
        if min(self.positions) <= position <= max(self.positions):
            return True
        else:
            raise ValueError(f"{position=} is outside the beam")

    def _create_nodes(self) -> list[Node]:
        return [Node(self.cross_section, position) for position in self.positions]

    def _element_length(self, node_index) -> float:
        return self.nodes[node_index+1].position - self.nodes[node_index].position