"""

Procedure
---------
  1. part girder in elements (X)
  2. compute m-kappa-line between elements (considering effective width) (X)
  3. deformation at position where maximum moment is expected (for each moment point)

"""
from dataclasses import dataclass
from .crosssection import Crosssection
from .curves_m_kappa import MKappaCurve, MKappaCurvePoints
from .internalforces import (
    ABCSingleSpan,
    SingleSpanSingleLoads,
    SingleSpanUniformLoad,
    SingleLoad,
)


@dataclass
class MKappaCurveInBeam:
    """
    container for M-Kappa-Curve at specific beam-position

    Parameters
    ----------
    position_in_beam : float
        position where M-Kappa-Curve is computed for
    m_kappa_curve: MKappaCurvePoints
        points of the M-Kappa-Curve
    """
    position_in_beam: float
    m_kappa_curve: MKappaCurvePoints

    def max_resistance_moment(self):
        return self.m_kappa_curve.maximum_moment()


@dataclass
class MKappaCurvesAlongBeam:

    """computes M-Kappa Curves along the beam"""

    crosssection: Crosssection
    beam_length: float
    position_of_maximum_moment: float
    elements: int = 10

    def __post_init__(self):
        self.m_kappa_curves = self._compute_m_kappa_curves()

    @property
    def element_length(self) -> float:
        """length of an individual element"""
        return self.beam_length / self.elements

    def positions(self) -> list:
        """position between elements"""
        positions = [number * self.element_length for number in range(1, self.elements)]
        positions.append(self.position_of_maximum_moment)
        positions = list(set(positions))
        positions = sorted(positions)
        return positions

    def _compute_m_kappa_curves(self) -> list[MKappaCurveInBeam]:
        """compute all M-Kappa-Curves between elements"""
        return [
            MKappaCurveInBeam(position, self._m_kappa(position))
            for position in self.positions()
        ]

    def _m_kappa(self, position: float) -> MKappaCurvePoints:
        """compute M-Kappa-Curve at specific position"""
        return MKappaCurve(
            self.crosssection, include_positive_curvature=True
        ).m_kappa_points  # Todo: position


@dataclass
class Loading:

    """compute the load-steps by analysis of decisive m-kappa-curve

    decisive M-Kappa-curve is determined by the position of the maximum moment
    """

    beam_length: float
    m_kappa_curves: list[MKappaCurveInBeam]
    load: ABCSingleSpan = None

    def __post_init__(self):
        if self.load is None:
            self.load = SingleSpanUniformLoad(self.beam_length, 1.0)

    def maximum_resistance_moments(self) -> list[float]:
        return [m_kappa.max_resistance_moment() for m_kappa in self.m_kappa_curves]

    def _position_maximum_moment(self) -> float:
        return self.load.position_of_maximum_moment()

    def decisive_m_kappa_curve(self) -> MKappaCurvePoints:
        position = self._position_maximum_moment()
        m_kappa_curve = self.m_kappa_curve_at(position)
        return m_kappa_curve.m_kappa_curve

    def decisive_moments(self) -> list[float]:
        m_kappa_curve = self.decisive_m_kappa_curve()
        return m_kappa_curve.moments

    def load_steps(self) -> list[ABCSingleSpan]:
        return [
            self.load.load_by(moment, self._position_maximum_moment())
            for moment in self.decisive_moments()
        ]

    def m_kappa_curve_at(self, position) -> MKappaCurveInBeam:
        return list(
            filter(lambda x: x.position_in_beam == position, self.m_kappa_curves)
        )[0]


@dataclass
class BeamCurvature:

    """container for computed curvatures"""

    position: float
    curvature: float
    load_step: ABCSingleSpan


class BeamCurvatures:

    """compute the curvatures of a beam"""

    __slots__ = "_m_kappa_curves", "_beam_length"

    def __init__(self, m_kappa_curves: list[MKappaCurveInBeam], beam_length: float):
        self._m_kappa_curves = m_kappa_curves
        self._beam_length = beam_length

    @property
    def beam_length(self) -> float:
        return self._beam_length

    @property
    def m_kappa_curves(self) -> list[MKappaCurveInBeam]:
        return self._m_kappa_curves

    def compute(self, at_load: ABCSingleSpan) -> list[BeamCurvature]:
        """give the curvatures of the beam at a given load"""
        return self._curvatures_at_supports(
            at_load
        ) + self._curvatures_between_supports(at_load)

    def _curvatures_at_supports(self, at_load: ABCSingleSpan) -> list:
        """curvatures at the supports (are always zero in case of single span beams)"""
        return [
            BeamCurvature(position=0.0, curvature=0.0, load_step=at_load),
            BeamCurvature(position=self.beam_length, curvature=0.0, load_step=at_load),
        ]

    def _curvatures_between_supports(self, load: ABCSingleSpan) -> list[BeamCurvature]:
        """curvatures inside beam"""
        return [
            BeamCurvature(
                m_kappa.position_in_beam,
                self._curvature(m_kappa.position_in_beam, load),
                load,
            )
            for m_kappa in self.m_kappa_curves
        ]

    def _moment(self, position: float, load: ABCSingleSpan) -> float:
        """compute moment at given position under given load"""
        return load.moment(position)

    def _curvature(self, position: float, load: ABCSingleSpan) -> float:
        """curvature at given position and load"""
        moment = self._moment(position, load)
        return self._m_kappa_curve(position).curvature(moment)

    def _m_kappa_curve(self, position: float) -> MKappaCurvePoints:
        """points of M-Kappa-Curve at given position"""
        curve_at_position = list(
            filter(lambda x: x.position_in_beam == position, self.m_kappa_curves)
        )[0]
        return curve_at_position.m_kappa_curve


@dataclass
class ComputedDeformation:
    """container for computed deformations by a load at specific position """

    position: float
    deformation: float
    load_step: ABCSingleSpan

@dataclass
class ExternalMoment:

    position : float
    moment : float


class DeformationByCurvatures:

    """computes deformation by given curvatures at the given load-step"""

    __slots__ = (
        "_beam_curvatures",
        "_positions",
        "_curvatures",
        "_load_step",
        "_curvatures",
    )

    def __init__(self, beam_curvatures: list[BeamCurvature], load_step: ABCSingleSpan):
        """
        Parameters
        ----------
        beam_curvatures : list[BeamCurvature]
            computed beam-curvatures
        load_step : ABCSingleSpan
            load the deformation is to be computed
        """
        self._beam_curvatures = beam_curvatures
        self._load_step = load_step
        self.__sort_by_position()
        self._positions = self.__positions()
        self._curvatures = self.__curvatures()

    @property
    def beam_curvatures(self) -> list[BeamCurvature]:
        return self._beam_curvatures

    @property
    def load_step(self) -> ABCSingleSpan:
        return self._load_step

    @property
    def beam_length(self) -> float:
        return max(self.positions)

    @property
    def positions(self) -> list[float]:
        """positions of the beam-curvatures"""
        return self._positions

    @property
    def curvatures(self) -> list[float]:
        """curvatures of the beam_curvatures"""
        return self._curvatures

    @property
    def element_number(self) -> int:
        """number of elements the beam is split into"""
        return len(self.beam_curvatures)

    def deformations(self) -> list[ComputedDeformation]:
        """compute the deformations at each position with the given curvatures"""
        return [
            ComputedDeformation(
                position=position,
                deformation=self.deformation(position),
                load_step=self.load_step)
            for position in self.positions
        ]

    def deformation(self, at_position) -> float:
        """compute the deformation at given position"""
        if at_position == 0.0 or at_position == self.beam_length:
            return 0.0 # on supports not deformation is possible
        else:
            return sum(self._incremental_deformations(at_position))

    def _element_length(self, index) -> float:
        """element-length of element indicated by index"""
        return self.positions[index + 1] - self.positions[index]

    def _incremental_deformations(self, at_position: float) -> list[float]:
        """incremental deformations of each element given single load acts at given position"""
        single_load_moment_curvature = self._single_load_moments_times_curvatures(at_position)
        return [
            self._incremental_deformation(index, single_load_moment_curvature)
            for index in range(self.element_number - 1)
        ]

    def _incremental_deformation(self, index: int, moment_curvature: list) -> float:
        """incremental deformation"""
        return self._mean(index, moment_curvature) * self._element_length(index)

    def _mean(self, index: int, lst: list) -> float:
        """
        mean value of two values in the given list

        first value is given by index
        second value is given by index+1
        """
        return 0.5 * (lst[index] + lst[index + 1])

    def _single_load_moments_times_curvatures(self, at_position: float) -> list:
        """multiply moments by single load with curvatures"""
        moments = self._single_load_moments(at_position)
        return [
            moment * curvature for moment, curvature in zip(moments, self.curvatures)
        ]

    def _single_load(self, position: float) -> SingleSpanSingleLoads:
        """internal forces with single load at given position"""
        return SingleSpanSingleLoads(self.beam_length, [SingleLoad(position, 1.0)])

    def _single_load_moments(self, single_load_position: float) -> list:
        """moments by single load at existing positions"""
        single_load = self._single_load(single_load_position)
        return [single_load.moment(position) for position in self.positions]

    def __curvatures(self) -> list[float]:
        return [beam_curvature.curvature for beam_curvature in self.beam_curvatures]

    def __positions(self) -> list[float]:
        return [beam_curvature.position for beam_curvature in self.beam_curvatures]

    def __sort_by_position(self):
        """sorts the beam-curvatures by position"""
        sorted(self._beam_curvatures, key=lambda x: x.position)

    def _curvatures_at_positions(self) -> list[float]:
        """determine curvatures at given load-step"""
        return [self._curvature_at_position(at_position) for at_position in self.positions]

    def _curvature_at_position(self, at_position):
        return list(filter(lambda x: x.position == at_position and x.load_step == self.load_step, self.beam_curvatures))[0]



class ComputeDeformations:

    """compute deformations"""

    def __init__(
        self,
        crosssection: Crosssection,
        beam_length: float,
        loading: ABCSingleSpan,
        element_number: int = 10,
    ):
        """
        Parameters
        ----------
        crosssection : Crosssection
            cross-section that needs to be computed
        beam_length : float
            length of the beam span
        loading : ABCSingleSpan
            loading of the beam
        element_number : int
            number of elements the beam is split into
        """
        self.crosssection = crosssection
        self.beam_length = beam_length
        self.loading = loading
        self.element_number = element_number
        self.m_kappa_curves = self._compute_m_kappa_curves()
        self.load_steps = self._compute_load_steps()
        self._sort_load_steps()
        self.beam_curvatures = self._compute_curvatures()
        self.deformations = self._compute_deformations()

    def curvatures_over_total_load(self):
        pass  # TODO

    def deformations_at_position_of_maximum_moment(self) -> list[float]:
        """get the deformations at the position of maximum moment for each load-step"""
        position_results: list[
            ComputedDeformation
        ] = self.results_at_position_of_maximum_moment(self.deformations)
        deformation_results = [result.deformation for result in position_results]
        return sorted(deformation_results)

    def curvatures_at_position_of_maximum_moment(self) -> list[float]:
        position_results: list[
            BeamCurvature
        ] = self.results_at_position_of_maximum_moment(self.beam_curvatures)
        curvature_results = [result.curvature for result in position_results]
        return sorted(curvature_results)

    def results_at_position_of_maximum_moment(self, results: list) -> list:
        return list(
            filter(
                lambda x: x.position == self.loading.position_of_maximum_moment(),
                results,
            )
        )

    def curvatures_at_load_step(self, load_step: ABCSingleSpan) -> list[BeamCurvature]:
        return list(filter(lambda x: x.load_step == load_step, self.beam_curvatures))

    def deformations_at_load_step(
        self, load_step: ABCSingleSpan
    ) -> list[ComputedDeformation]:
        return list(filter(lambda x: x.load_step == load_step, self.deformations))

    def _total_load(self, load_step: ABCSingleSpan):
        return load_step.loading

    def _compute_m_kappa_curves(self):
        """compute M-Kappa-Curves along the beam"""
        return MKappaCurvesAlongBeam(
            self.crosssection,
            self.beam_length,
            self.loading.position_of_maximum_moment(),
            self.element_number,
        ).m_kappa_curves

    def _compute_load_steps(self) -> list[ABCSingleSpan]:
        """compute load-steps"""
        return Loading(self.beam_length, self.m_kappa_curves, self.loading).load_steps()

    def _compute_curvatures(self) -> list[BeamCurvature]:
        """compute curvatures for give load-steps"""
        beam_curvatures = BeamCurvatures(self.m_kappa_curves, self.beam_length)
        curvatures = []
        for load_step in self.load_steps:
            curvatures += beam_curvatures.compute(load_step)
        return curvatures

    def _compute_deformations(self) -> list[ComputedDeformation]:
        """compute deformations for the given load-steps from the computed curvatures"""
        deformations = []
        for load_step in self.beam_curvatures:
            deformations += DeformationByCurvatures(
                self.beam_curvatures, load_step.load_step
            ).deformations()
        return deformations

    def _sort_load_steps(self):
        self.load_steps.sort(key=lambda x: x.maximum_moment)