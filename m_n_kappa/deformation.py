from dataclasses import dataclass

from .general import interpolation, EffectiveWidths
from .crosssection import Crosssection
from .curves_m_kappa import MKappaCurve, MKappaCurvePoints, MKappaCurvePoint
from .internalforces import (
    ABCSingleSpan,
    SingleSpanSingleLoads,
    SingleLoad,
    SingleSpanUniformLoad,
)
from .width import OneWeb


class Node:

    """Beam-Node

    stores the cross-section, the position_value in the beam and the computed M-Kappa-Curve
    """

    __slots__ = "_cross_section", "_m_kappa_curve", "_position", "_number"

    node_number: int = 0

    def __init__(self, cross_section: Crosssection, position: float):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.crosssection.Crosssection`
            Cross-section at this node
        position : float
            position of the node along the beam
        """
        self._cross_section = cross_section
        self._position = position
        self._m_kappa_curve = MKappaCurve(
            self.cross_section, include_positive_curvature=True
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

    def incremental_deformation(
        self, load: ABCSingleSpan, single_load: SingleSpanSingleLoads
    ) -> float:
        """
        determine curvature and single-load-moment at the node under given loading

        Parameters
        ----------
        load : ABCSingleSpan
           load applied to the beam
        single_load : SingleSpanSingleLoads
            single-load applied at the point, where deformation is computed

        Returns
        -------
        float
            product from curvature and moment of the single-load at this node
        """
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

    def decisive_position(self):
        decisive_loading = self.load.load_by(self.nodes[1].m_kappa_curve.maximum_moment(), self.nodes[1].position).loading
        decisive_node = None
        for node in self.nodes:
            if 0.0 < node.position < self.beam_length:
                load = self.load.load_by(node.m_kappa_curve.maximum_moment(), node.position)
                if decisive_loading > load.loading:
                    decisive_loading = load.loading
                    decisive_node = node
        return decisive_node.position

    def _position_maximum_moment(self) -> list[float]:
        return self.load.positions_of_maximum_moment()

    def _position_maximum_deformation(self) -> float:
        return self.load.position_of_maximum_deformation()

    def decisive_m_kappa_curve(self) -> MKappaCurvePoints:
        position = self.decisive_position()
        return self.m_kappa_curve_at(position)

    def load_steps(self) -> list[LoadStep]:
        return [
            LoadStep(
                self.load.load_by(point.moment, self._position_maximum_deformation()), point
            )
            for point in self.decisive_m_kappa_curve().points
        ]

    def m_kappa_curve_at(self, position) -> MKappaCurvePoints:
        return list(filter(lambda x: x.position == position, self.nodes))[
            0
        ].m_kappa_curve


@dataclass
class Deformation:
    """
    computed deformations

    Parameters
    ----------
    position : float
        position the deformation is computed
    load : float
        load leading to the computed deformation at the given position
    deformation : float
        computed deformation
    m_kappa_point : MKappaCurvePoint
        point in the M-Kappa-curve
    """

    position: float
    load: float
    deformation: float
    m_kappa_point: MKappaCurvePoint = None


class Beam:

    """Beam consisting of nodes"""

    __slots__ = (
        "_cross_section",
        "_length",
        "_element_number",
        "_load",
        "_element_standard_length",
        "_positions",
        "_nodes",
        "_load_steps",
        "_consider_widths",
    )

    def __init__(
        self,
        cross_section: Crosssection,
        length: float,
        element_number: int,
        load: ABCSingleSpan,
        consider_widths: bool = True,
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
        consider_widths : bool
            consider effective widths (Default: True)
        """
        self._cross_section = cross_section
        self._length = length
        self._element_number = element_number
        self._load = load
        self._consider_widths = consider_widths
        self._element_standard_length = self.length / self.element_number
        self._positions = self._create_positions()
        self._nodes = self._create_nodes()
        self._load_steps = Loading(self.length, self.nodes, self.load).load_steps()

    @property
    def consider_widths(self) -> bool:
        return self._consider_widths

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

    def nodes_at(self, beam_positions: list[float]) -> list[Node]:
        """
        nodes at the given positions along the beam

        considers only nodes where the position meets the given arguments

        Parameters
        ----------
        beam_positions : list[float]
            positions along the beam

        Returns
        -------
        list[Node]
            nodes at the given positions along the beam
        """
        if isinstance(beam_positions, float):
            beam_positions = [beam_positions]
        return [node for node in self.nodes if node.position in beam_positions]

    def nodes_at_decisive_position(self) -> list[Node]:
        """
        nodes at decisive positions

        decisive positions are:
          - position of maximum moment
          - position of maximum deformation
        In few cases these two positions differ from each other

        Returns
        -------
        list[Node]
            nodes at decisive positions
        """
        return self.nodes_at(self._decisive_positions())

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
        if load.loading == 0.0:
            return 0.0
        if self._position_in_beam(at_position):
            if at_position in self.positions:
                return self._deformation_at_node(at_position, load)
            else:
                return self._deformation_between_nodes(at_position, load)

    def deformations(self, at_position: float) -> list[Deformation]:
        """computes deformations at given position_value for relevant load-steps"""
        deformations = []
        for load_step in self.load_steps:
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
        position_of_maximum_moment = self.load.positions_of_maximum_moment()
        deformations = self.deformations(position_of_maximum_moment[0])
        return sorted(deformations, key=lambda x: x.load)

    def deformations_at_maximum_deformation_position(self) -> list[Deformation]:
        """computes deformations at the decisive beam-position for relevant load-steps"""
        position_of_maximum_deformation = self.load.position_of_maximum_deformation()
        deformations = self.deformations(position_of_maximum_deformation)
        return sorted(deformations, key=lambda x: x.load)

    def deformation_over_beam_length(self, load_step: ABCSingleSpan) -> list[Deformation]:
        """
        deformation over the length of the beam

        Parameters
        ----------
        load_step : ABCSingleSpan
            load-step the deformation is computed at

        Returns
        -------
        list[Deformation]
            deformations over the length of the beam at the given load-step
        """
        return [Deformation(
            position=position,
            deformation=self.deformation(at_position=position, load=load_step),
            load=load_step.loading,
        )
                for position in self.positions]

    def _deformation_at_node(self, at_position: float, load: ABCSingleSpan) -> float:
        return sum(self._incremental_deformations(at_position, load))

    def _decisive_positions(self) -> list[float]:
        positions = self.load.positions_of_maximum_moment()
        positions.append(self.load.position_of_maximum_deformation())
        positions += self.load.positions
        positions += [0.0, self.length]
        positions = list(set(positions))
        return positions

    def _deformation_between_nodes(
        self, at_position: float, load: ABCSingleSpan
    ) -> float:
        smaller_position = max(list(filter(lambda x: x < at_position, self.positions)))
        deformation_at_smaller_position = self._deformation_at_node(
            smaller_position, load
        )
        higher_position = min(list(filter(lambda x: x > at_position, self.positions)))
        deformation_at_higher_position = self._deformation_at_node(
            higher_position, load
        )
        return interpolation(
            position_value=at_position,
            first_pair=[smaller_position, deformation_at_smaller_position],
            second_pair=[higher_position, deformation_at_higher_position],
        )

    def _incremental_deformations(
        self, for_position: float, load: ABCSingleSpan
    ) -> list[float]:
        single_load = SingleLoad(for_position, 1.0)
        single_span_single_load = SingleSpanSingleLoads(self.length, [single_load])
        return [
            self._incremental_deformation(node_index, load, single_span_single_load)
            for node_index in range(len(self.nodes) - 1)
        ]

    def _incremental_deformation(
        self, node_index: int, load: ABCSingleSpan, single_load: SingleSpanSingleLoads
    ):
        node_1_result = self.nodes[node_index].incremental_deformation(
            load, single_load
        )
        node_2_result = self.nodes[node_index + 1].incremental_deformation(
            load, single_load
        )
        return 0.5 * (node_1_result + node_2_result) * self._element_length(node_index)

    def _create_positions(self) -> list[float]:
        positions = [
            number * self.element_standard_length
            for number in range(0, self.element_number + 1)
        ]
        positions += self._decisive_positions()
        positions = list(set(positions))
        positions = sorted(positions)
        return positions

    def _position_in_beam(self, position: float) -> bool:
        if min(self.positions) <= position <= max(self.positions):
            return True
        else:
            raise ValueError(f"{position=} is outside the beam")

    def _create_nodes(self) -> list[Node]:
        nodes = []
        for position in self.positions:
            if self.consider_widths:
                cross_section = self._cross_section_with_effective_width(position)
            else:
                cross_section = self._cross_section
            nodes.append(Node(cross_section, position))
        return nodes

    def _cross_section_with_effective_width(self, position: float) -> Crosssection:
        slab_width = 0.5 * self.cross_section.concrete_slab_width()
        width_position = abs(0.5 * self.length - position)
        widths = OneWeb(slab_width, self.length)
        if self.load.load_distribution_factor() <= 0.6:
            width_load = widths.single
        else:
            width_load = widths.line
        membran = width_load.membran.ratio_beff_to_b(width_position) * slab_width
        bending = width_load.bending.ratio_beff_to_b(width_position) * slab_width
        print(f"load-distribution-factor={self.load.load_distribution_factor()}, "
              f"{position=:5.1f}, {width_position=:5.1f}, "
              f"{membran=:.1f} ({membran / slab_width:.2f}), "
              f"{bending=:.1f} ({bending / slab_width:.2f})")
        effective_widths = EffectiveWidths(bending=bending, membran=membran)
        return Crosssection(
            sections=self.cross_section.sections, slab_effective_widths=effective_widths
        )

    def _element_length(self, node_index) -> float:
        return self.nodes[node_index + 1].position - self.nodes[node_index].position