from dataclasses import dataclass

from .shearconnector import ShearConnector
from .general import interpolation, EffectiveWidths
from .crosssection import Crosssection
from .curves_m_kappa import MKappaCurvePoints, MKappaCurvePoint
from .node import Node
from .loading import (
    ABCSingleSpan,
    SingleSpanSingleLoads,
    SingleLoad,
    SingleSpanUniformLoad,
)
from .width import OneWeb

from .log import LoggerMethods

log = LoggerMethods(__name__)


@dataclass(slots=True)
class LoadStep:
    """
    Load-step re-computed from a :py:class:`~m_n_kappa.curves_m_kappa.MKappaCurvePoint`

    .. versionadded:: 0.1.0

    Parameters
    ----------
    load: :py:class:`~m_n_kappa.loading.ABCSingleSpan`
        load-step-value, may be any class derived from :py:class:`~m_n_kappa.loading.ABCSingleSpan`
    point : :py:class:`~m_n_kappa.curves_m_kappa.MKappaCurvePoint`
        Moment-curvature-point the load-step is derived from
    """

    load: ABCSingleSpan
    point: MKappaCurvePoint


@dataclass(slots=True)
class Loading:

    """
    compute the load-steps by analysis of decisive m-kappa-curve

    .. versionadded:: 0.1.0

    decisive M-Kappa-curve is determined by the position_value of the maximum moment

    Parameters
    ----------
    beam_length: float
        length of the beam
    nodes: list[:py:class:`~m_n_kappa.Node`]
        beam-nodes
    load: :py:class:`~m_n_kappa.loading.ABCSingleSpan` = None
        loading of the beam
    """

    beam_length: float
    nodes: list[Node]
    load: ABCSingleSpan = None

    def __post_init__(self):
        if self.load is None:
            self.load = SingleSpanUniformLoad(self.beam_length, 1.0)
        log.info(f"Created {self.__repr__()}")

    def maximum_resistance_moments(self) -> list[float]:
        return [node.curve_points.maximum_moment() for node in self.nodes]

    def decisive_position(self):
        decisive_loading = self.load.load_by(
            self.nodes[1].curve_points.maximum_moment(), self.nodes[1].position
        ).loading
        decisive_node = None
        for node in self.nodes:
            if 0.0 < node.position < self.beam_length:
                load = self.load.load_by(
                    node.curve_points.maximum_moment(), node.position
                )
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
                self.load.load_by(point.moment, self._position_maximum_deformation()),
                point,
            )
            for point in self.decisive_m_kappa_curve().points
        ]

    def m_kappa_curve_at(self, position) -> MKappaCurvePoints:
        return list(filter(lambda x: x.position == position, self.nodes))[
            0
        ].curve_points


@dataclass(slots=True)
class Deformation:
    """
    container for computed deformations

    .. versionadded:: 0.1.0

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

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")


@dataclass(slots=True)
class Deformations:

    """
    container for number of deformations

    .. versionadded:: 0.1.0

    Parameters
    ----------
    deformations : list[:py:class:`~m_n_kappa.deformation.Deformation`]
        list of deformations
    """

    deformations: list[Deformation]

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")

    def __iter__(self):
        self._deformation_iterator = iter(self.deformations)
        return self

    def __next__(self):
        return self._deformation_iterator.__next__()

    def positions(self) -> list[float]:
        return [deform.position for deform in self.deformations]

    def values(self) -> list[float]:
        return [deform.deformation for deform in self.deformations]

    def loadings(self, factor=1.0) -> list[float]:
        return [deform.load * factor for deform in self.deformations]

    def neutral_axes(self) -> list[float]:
        return [deform.m_kappa_point.neutral_axis for deform in self.deformations]


def is_cross_section_in_nodes(cross_section: Crosssection, nodes: list[Node]) -> bool:
    """check if a node is given in ``nodes`` that has the same ``cross_section``"""
    for node in nodes:
        if cross_section == node.cross_section:
            return True
    return False


class Beam:

    """
    Beam consisting of nodes with computed moment-curvature-curves

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_cross_section",
        "_element_number",
        "_load",
        "_element_standard_length",
        "_positions",
        "_nodes",
        "_load_steps",
        "_consider_widths",
    )

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        element_number: int,
        load: ABCSingleSpan,
        consider_widths: bool = True,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            cross-section the beam consists of
        element_number : int
            number of elements the beam consists of
        load : :py:class:`~m_n_kappa.loading.ABCSingleSpan`
            load-type applied to the beam
        consider_widths : bool
            consider effective widths (Default: True)
        """
        self._cross_section = cross_section
        self._element_number = element_number
        self._load = load
        self._consider_widths = consider_widths
        self._element_standard_length = self.length / self.element_number
        self._positions = self._create_positions()
        self._nodes = self._create_nodes()
        self._load_steps = Loading(self.length, self.nodes, self.load).load_steps()

    @property
    def consider_widths(self) -> bool:
        """indicates if effective widths are considered during computation"""
        return self._consider_widths

    @property
    def cross_section(self) -> Crosssection:
        """cross-section to be computed"""
        return self._cross_section

    @property
    def length(self) -> float:
        """length of the beam"""
        return self.load.length

    @property
    def load(self) -> ABCSingleSpan:
        """loading of the beam"""
        return self._load

    @property
    def load_steps(self) -> list[LoadStep]:
        """computed load-steps of the beam"""
        return self._load_steps

    @property
    def element_number(self) -> int:
        """input-number of elements"""
        return self._element_number

    @property
    def element_standard_length(self) -> float:
        """standard-length of the elements computed using input ``element_number``"""
        return self._element_standard_length

    @property
    def positions(self) -> list[float]:
        """positions in the beam where nodes are applied"""
        return self._positions

    @property
    def nodes(self) -> list[Node]:
        """nodes in the beam"""
        return self._nodes

    def bending_widths(self) -> list[float]:
        """computed effective bending widths of the concrete slab over the length of beam"""
        if self.consider_widths:
            return [
                min(
                    node.cross_section.slab_effective_width.bending,
                    0.5 * node.cross_section.concrete_slab_width(),
                )
                for node in self.nodes
            ]
        else:
            return [node.cross_section.concrete_slab_width() for node in self.nodes]

    def membran_widths(self) -> list[float]:
        """computed effective membran widths of the concrete slab over the length of beam"""
        if self.consider_widths:
            return [
                min(
                    node.cross_section.slab_effective_width.membran,
                    0.5 * node.cross_section.concrete_slab_width(),
                )
                for node in self.nodes
            ]
        else:
            return [node.cross_section.concrete_slab_width() for node in self.nodes]

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
        list[:py:class:`~m_n_kappa.deformation.Node`]
            nodes at decisive positions
        """
        return self.nodes_at(self._decisive_positions())

    @log.result
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
                deformation = self._deformation_at_node(at_position, load)
            else:
                deformation = self._deformation_between_nodes(at_position, load)
            return deformation

    @log.result
    def deformations(self, at_position: float) -> Deformations:
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
        deformations = Deformations(deformations)
        return deformations

    @log.result
    def deformations_at_maximum_moment_position(self) -> Deformations:
        """computes deformations at the decisive position_value for relevant load-steps"""
        position_of_maximum_moment = self.load.positions_of_maximum_moment()
        deformations = self.deformations(position_of_maximum_moment[0])
        return deformations

    @log.result
    def deformations_at_maximum_deformation_position(self) -> Deformations:
        """computes deformations at the decisive beam-position for relevant load-steps"""
        position_of_maximum_deformation = self.load.position_of_maximum_deformation()
        deformations = self.deformations(position_of_maximum_deformation)
        return deformations

    @log.result
    def deformation_over_beam_length(self, load_step: ABCSingleSpan) -> Deformations:
        """
        deformation over the length of the beam

        Parameters
        ----------
        load_step : :py:class:`~m_n_kappa.loading.ABCSingleSpan`
            load-step the deformation is computed at

        Returns
        -------
        :py:class:`~m_n_kappa.beam.Deformations`
            deformations over the length of the beam at the given load-step
        """
        deformations = [
            Deformation(
                position=position,
                deformation=self.deformation(at_position=position, load=load_step),
                load=load_step.loading,
            )
            for position in self.positions
        ]
        return Deformations(deformations)

    def _deformation_at_node(self, at_position: float, load: ABCSingleSpan) -> float:
        """compute the deformation of a node at the given position under the given load"""
        return sum(self._incremental_deformations(at_position, load))

    def _decisive_positions(self) -> list[float]:
        """determine the decisive positions along the beam"""
        positions = self.load.positions_of_maximum_moment()
        positions.append(self.load.position_of_maximum_deformation())
        positions += self.load.positions
        positions += [0.0, self.length]
        positions = list(set(positions))
        return positions

    def _deformation_between_nodes(
        self, at_position: float, load: ABCSingleSpan
    ) -> float:
        """
        compute the deformation at the given position between two nodes

        Parameters
        ----------
        at_position : float
            position where the deformation is to be computed
        load : :py:class:`~m_n_kappa.loading.ABCSingleSpan`
            load under which deformation is to be computed

        Returns
        -------
        float
            deformation at the given position
        """
        smaller_position, higher_position = self._neighboring_positions(at_position)
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
            self._incremental_deformation(element_index, load, single_span_single_load)
            for element_index in range(len(self.nodes) - 1)
        ]

    def _incremental_deformation(
        self,
        element_index: int,
        load: ABCSingleSpan,
        single_load: SingleSpanSingleLoads,
    ) -> float:
        """
        compute the incremental deformation of

        Parameters
        ----------
        element_index : int
            index of the element where the incremental deformation is to be computed
        load : :py:class:`~m_n_kappa.loading.ABCSingleSpan`
            loading of the beam
        single_load : :py:class:`~m_n_kappa.SingleSpanSingleLoads`
            single load that indicates where the deformation is to be computed

        Returns
        -------
        float
            incremental deformation from the element with the given index under given loading

        See Also
        --------
        :py:meth:`~m_n_kappa.Node.incremental_deformation` : compute the incremental deformation at the node

        """
        node_1_result = self.nodes[element_index].incremental_deformation(
            load, single_load
        )
        node_2_result = self.nodes[element_index + 1].incremental_deformation(
            load, single_load
        )
        return (
            0.5 * (node_1_result + node_2_result) * self._element_length(element_index)
        )

    def _create_positions(self) -> list[float]:
        """create the positions where M-Kappa is to be computed"""
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
        """
        create the nodes along the beam and consider effective widths if needed

        In case a similar node has already been computed the computation will be skipped
        and the m_kappa_curve will be copied from the other node.
        The ``cross_section`` works as basis for the comparison.
        """
        nodes = []
        for position in self.positions:
            if self.consider_widths:
                cross_section = self._cross_section_with_effective_width(position)
            else:
                cross_section = self._cross_section

            if is_cross_section_in_nodes(cross_section, nodes):
                for node in nodes:
                    if cross_section == node.cross_section:
                        log.info(f"M-Kappa-Curve of Node {node.number} will be copied.")
                        computed_node = Node(
                            cross_section, position, m_kappa_curve=node.curve_points
                        )
                        break
            else:
                computed_node = Node(cross_section, position)
            nodes.append(computed_node)
        return nodes

    def _cross_section_with_effective_width(self, position: float) -> Crosssection:
        """
        add effective width to cross-sections depending on the position of the cross-section
        along the beam

        In case the cross-section does not consist of Concrete and/or Reinforcement than
        no adaption is done.

        Parameters
        ----------
        position : float
            position of the node of the cross-section along the beam

        Returns
        -------
        :py:class:`~m_n_kappa.Crosssection`
            Cross-section with :py:class:`~m_n_kappa.EffectiveWidths` added.
        """
        if len(self.cross_section.slab_sections) == 0:
            log.info(
                "No concrete-slab available, therefore effective widths do not apply"
            )
            return self.cross_section
        slab_width = 0.5 * self.cross_section.concrete_slab_width()
        width_position = abs(0.5 * self.length - position)
        widths = OneWeb(slab_width, self.length)
        if self.load.load_distribution_factor() <= 0.6:
            width_load = widths.single
        else:
            width_load = widths.line
        membran = width_load.membran.ratio_beff_to_b(width_position) * slab_width
        bending = width_load.bending.ratio_beff_to_b(width_position) * slab_width
        log.info(
            f"load-distribution-factor={self.load.load_distribution_factor():.2f}, "
            f"{position=:5.1f}, {width_position=:5.1f}, "
            f"{membran=:.1f} ({membran / slab_width:.2f}), "
            f"{bending=:.1f} ({bending / slab_width:.2f})"
        )
        effective_widths = EffectiveWidths(bending=bending, membran=membran)
        log.debug("added effective width to cross-section")
        return Crosssection(
            sections=self.cross_section.sections, slab_effective_widths=effective_widths
        )

    def _element_length(self, node_index) -> float:
        """compute the length of the element with nodes with ``node_index`` and ``node_index + 1``"""
        return self.nodes[node_index + 1].position - self.nodes[node_index].position
