"""

Procedure
---------
  1. part girder in elements (X)
  2. compute m-kappa-line between elements (considering effective width) (X)
  3. deformation at position where maximum moment is expected (for each moment point)

"""
# import general
import section
import points
import internalforces


class MKappaCurvesAlongBeam:

    """computes M-Kappa Curves along the beam"""

    __slots__ = (
        "_crossection",
        "_beam_length",
        "_elements",
        "_m_kappa_curves",
        "_loading",
    )

    def __init__(
        self,
        crosssection: section.Crosssection,
        beam_length: float,
        elements: int = 10,
        loading_type: str = "uniform",
    ):
        self._crosssection = crosssection
        self._beam_length = beam_length
        self._elements = elements
        self._loading_type = loading_type
        self._m_kappa_curves = self._compute_m_kappa_curves()

    @property
    def beam_length(self) -> float:
        """length of the investigated beam"""
        return self._beam_length

    @property
    def crosssection(self) -> section.Crosssection:
        """crosssection of the beam"""
        return self._crosssection

    @property
    def elements(self) -> int:
        """number of elements"""
        return self._elements

    @property
    def element_length(self) -> float:
        """length of an individual element"""
        return self.beam_length / self.elements

    @property
    def m_kappa_curves(self) -> list:
        """list of m_kappa_curves"""
        return self._m_kappa_curves

    @property
    def loading(self) -> str:
        """loading-type"""
        return self._loading

    def _compute_m_kappa_curves(self) -> list:
        """compute all M-Kappa-Curves"""
        return [
            {"position": position, "curve": self._m_kappa(position)}
            for position in self.positions()
        ]

    def _compute_m_kappa_curve(self, position: float) -> list:
        """m_kappa_curve at given position"""
        return dict(filter(lambda x: x["position"] == position))["curve"]

    def positions(self) -> list:
        """position between elements"""
        return [number * self.element_length for number in range(1, self.elements)]

    def _m_kappa(self, position: float):
        """compute M-Kappa-Curve at specific position"""
        return points.MKappaCurve(
            self.crosssection, position
        ).m_kappa_points  # Todo: position


class BeamCurvatures:
    def __init__(self, m_kappa_curves: list):
        self._m_kappa_curves = m_kappa_curves
        self._beam_length = max(self.m_kappa_curves, key=lambda x: x["position"])[
            "position"
        ]

    @property
    def beam_length(self) -> float:
        return self.beam_length

    @property
    def m_kappa_curves(self) -> list:
        return self._m_kappa_curves

    def beam_curvatures(self, load: float) -> list:
        """give the curvatures of the beam at a given load"""
        return self._curvatures_at_supports() + self._curvatures_within_supports(load)

    def _curvatures_at_supports(self) -> list:
        """curvatures at the supports (are always zero in case of single span beams)"""
        return [
            {"position": 0.0, "curvature": 0.0},
            {"position": self.beam_length, "curvature": 0.0},
        ]

    def _curvatures_within_supports(self, load: float) -> list:
        """curvatures inside beam"""
        return [
            {
                "position": m_kappa["position"],
                "curvature": self._curvature(m_kappa["position"], load),
            }
            for m_kappa in self.m_kappa_curves
        ]

    def _moment(self, position, load):
        """compute moment at given position under given load"""
        return internalforces.SingleSpanUniformLoad(self.beam_length, load).moment(
            position
        )

    def _curvature(self, position: float, load: float) -> float:
        """curvature at given position and load"""
        moment = self._moment(position, load)
        return m_kappa_curve(position).curvature(moment)


class DeformationByCurvatures:

    """computes deformation by given curvatures"""

    __slots__ = "_beam_curvatures", "_positions", "_curvatures"

    def __init__(self, beam_curvatures: list):
        self._beam_curvatures = beam_curvatures
        self.__sort_by_position()
        self._positions = self.__positions()
        self._curvatures = self.__curvatures()

    @property
    def beam_curvatures(self) -> list:
        """curvatures at beam positions: [{'position':XX, 'curvature':XX}]"""
        return self._beam_curvatures

    @property
    def beam_length(self) -> float:
        return self.beam_curvatures[-1]["position"]

    @property
    def positions(self) -> list:
        """positions of the beam-curvatures"""
        return self._positions

    @property
    def curvatures(self) -> list:
        """curvatures of the beam_curvatures"""
        return self._curvatures

    @property
    def element_number(self) -> int:
        return len(self.beam_curvatures)

    def deformations(self):
        """compute the deformations at each postion with the given curvatures"""
        return [
            {"position": position, "deformation": self.deformation(position)}
            for position in self.positions
        ]

    def deformation(self, position):
        """compute the deformation at given position"""
        return sum(self.incremental_deformations(position))

    def _element_length(self, index) -> list:
        """compute element-length of element indicated by index"""
        return self.positions[index + 1] - self.positions[index]

    def _incremental_deformations(self, position: float):
        """compute the incremental deformations of each element"""
        moment_curvature = self._moments_times_curvatures(position)
        return [
            self._incremental_deformation(index, moment_curvature)
            for index in range(self.element_number - 1)
        ]

    def _incremental_deformation(self, index: int, moment_curvature: list) -> float:
        """compute a incremental deformation"""
        return self._mean(index, moment_curvature) * self._element_length(index)

    def _mean(self, index: int, lst: list) -> float:
        """
        mean value of two values in the given list

        first value is given by index
        second value is given by index+1
        """
        return 0.5 * (lst[index] + lst[index + 1])

    def _moments_times_curvatures(self, position: float):
        """multiply moments with curvatures"""
        moments = self._single_load_moments(position)
        return [
            m_curvature[0] * m_curvature[1]
            for m_curvature in zip(moments, self.curvatures)
        ]

    def _single_load(self, position: float) -> internaforces.SingleSpanSingleLoads:
        """internal forces with load at given position"""
        return internalforces.SingleSpanSingleLoads(self.beam_length, [position, 1.0])

    def _single_load_moments(self, single_load_position: float) -> list:
        """moments by single load at existing positions"""
        single_load = self._single_load(single_load_position)
        return [single_load.moment(position) for position in self.positions]

    def __curvatures(self):
        return [beam_curvature["curvature"] for beam_curvature in self.beam_curvatures]

    def __positions(self):
        return [beam_curvature["position"] for beam_curvature in self.beam_curvatures]

    def __sort_by_position(self):
        """sorts the beam-curvatures by position"""
        sort(self._beam_curvatures, key=lambda x: x["position"])


class AllDeformation:
    def deformations(self, load: float):
        """
        compute deformation by given curvatures along the beam

        Returns
        -------
        list[dict]
                list with deformations at positions in case of given beam-curvatures
        """
        beam_curvatures = self.beam_curvatures(load)
        return DeformationByCurvatures(beam_curvatures).deformations()


if __name__ == "__main__":

    pass
