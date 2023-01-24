from dataclasses import dataclass

from .crosssection import Crosssection
from .curvature_boundaries import BoundaryValues, Boundaries

from .general import (
    interpolation,
    print_sections,
    print_chapter,
    str_start_end,
    StrainPosition,
)
from .points import MKappaByStrainPosition
from .solver import Newton, Bisection

import logging
import logging.config
import yaml
import pathlib

with open(pathlib.Path(__file__).parent.absolute() / "logging-config.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


@dataclass
class MKappaCurvePoint:
    """
    Container for single point on Moment-Curvature-Curve

    .. versionadded:: 0.1.0

    Parameters
    ----------
    moment: float
        the computed moment of the curve-point
    curvature: float
        the computed curvature of the curve-point
    neutral_axis: float
        the computed neutral-axis of the computed curve-point
    cross_section: :py:class:`~m_n_kappa.Crosssection`
        computed cross-section
    strain_position: :py:class:`~m_n_kappa.StrainPosition`
        :py:class:`~m_n_kappa.StrainPosition` leading to the
        resulting moment, curvature and neutral-axis
    """
    moment: float
    curvature: float
    neutral_axis: float
    cross_section: Crosssection
    strain_position: StrainPosition

    def __post_init__(self):
        logger.info(f'Created {self.__repr__()}')

    def __eq__(self, other) -> bool:
        if not isinstance(other, MKappaCurvePoint):
            return False
        elif (
            self.moment == other.moment
            and self.curvature == other.curvature
            and self.neutral_axis == other.neutral_axis
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


class MKappaCurvePoints:

    """
    Container for points on computed :math:`M`-:math:`\\kappa`-Curve

    .. versionadded:: 0.1.0

    """

    def __init__(self) -> None:
        self._points = []
        logger.info(f'Created MKappaCurvePoints')

    def __repr__(self) -> str:
        return """MKappaCurvePoints()"""

    def __str__(self) -> str:
        text = [
            self._print_initialization(),
            self._print_points(),
        ]
        return print_chapter(text)

    def _print_initialization(self) -> str:
        text = ['Initialization', '------------', self.__repr__()]
        return print_sections(text)

    def _print_points(self) -> str:
        points = sorted(self._points, key=lambda x: x.curvature)
        line = 81 * '-'
        text = [
            line,
            "   Moment   | Curvature  | Neutral A. |   Strain   |  Position  |    Material    ",
            line
        ]
        for point in points:
            text.append(
                f'{point.moment:10.1f} | {point.curvature:10.6f} | {point.neutral_axis:10.2f} | '
                f'{point.strain_position.strain:10.2f} | {point.strain_position.position:10.1f} | '
                f'{point.strain_position.material}'
            )
        text.append(line)
        return print_sections(text)

    @property
    def moments(self) -> list[float]:
        """computed moments of the Moment-Curvature-Curve"""
        return [point.moment for point in self.points]

    @property
    def curvatures(self) -> list[float]:
        """computed curvatures of the Moment-Curvature-Curve"""
        return [point.curvature for point in self.points]

    @property
    def points(self) -> list[MKappaCurvePoint]:
        """
        :math:`M`-:math:`\\kappa`-curve points
        """
        return self._points

    def add(
        self,
        moment: float,
        curvature: float,
        neutral_axis: float,
        cross_section: MKappaByStrainPosition,
        strain_position: StrainPosition,
    ) -> None:
        """add moment-curvature point to list

        Parameters
        ----------
        moment : float
            computed moment of the point
        curvature : float
            computed curvature of the point
        neutral_axis : float
            computed neutral-axis leading to equilibrium (after variation)
        cross_section : :py:class:`~m_n_kappa.points.MKappaByStrainPosition`
            computed cross-section
        strain_position : :py:class:`~m_n_kappa.general.StrainPosition`
            strain and its position
        """
        point = MKappaCurvePoint(
            moment,
            curvature,
            neutral_axis,
            cross_section,
            strain_position,
        )
        if point not in self.points:
            self._points.append(point)
            self._sort_points_by_curvature()
            logger.info(f'Added {point} to MKappaCurvePoints')

    def curvature(self, by_moment: float) -> float:
        """
        get curvature at given moment

        Parameters
        ----------
        by_moment : float
            moment the curvature is to be computed from

        Returns
        -------
        float
            curvature :math:`\\kappa` computed from the given moment

        Raises
        ------
        ValueError
            in case the moment is outside the computed moment-range
        """
        if -.00001 <= by_moment <= 0.00001:
            return 0.0
        if self.maximum_moment() < by_moment:
            if self.maximum_moment() < by_moment * 0.999:
                raise ValueError(
                    f"{by_moment=:.2f} > {self.maximum_moment():.2f} = maximum moment in the curve .\n"
                    f"Therefore, no matching moment value could be found."
                )
            else:
                by_moment = self.maximum_moment()
        point_index = self._determine_index(by_moment)
        return interpolation(
            by_moment,
            self._curvature_moment(point_index),
            self._curvature_moment(point_index + 1),
        )

    def _moment_curvature(self, by_index: int) -> list[float]:
        """get moment-curvature of curve-point at given index.rst"""
        return self.points[by_index].moment_curvature()

    def _curvature_moment(self, by_index: int) -> list[float]:
        """get curvature-moment of curve-point at given index.rst"""
        return self.points[by_index].curvature_moment()

    def _determine_index(self, moment: float) -> int:
        """
        get index.rst of curve-point that has greater or equal moment as given

        Parameters
        ----------
        moment : float
            moment to find the index.rst of the moment-curvature-index.rst

        Returns
        -------
        int
            index.rst of the moment-curvature-point that has smaller or equal moment than the given moment

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
        self.points.sort(key=lambda x: x.curvature)

    def maximum_moment(self) -> float:
        """computes the maximum moment of the curve"""
        return max(self.moments)


class MKappaCurveCurvature:

    """Compute moment-curvature (M-Kappa) at failure"""

    __slots__ = (
        "_cross_section",
        "_maximum_curvature",
        "_minimum_curvature",
        "_m_kappa_failure",
        "_start_strain_position",
    )

    def __init__(
        self,
        cross_section: Crosssection,
        maximum_curvature: float,
        minimum_curvature: float,
        start_strain_position: StrainPosition,
    ):
        self._cross_section = cross_section
        self._maximum_curvature = maximum_curvature
        self._minimum_curvature = minimum_curvature
        self._start_strain_position = start_strain_position
        self._m_kappa_failure = self._get_m_kappa_failure()
        logger.info("Computed M-Kappa-Point at failure (MKappaCurveCurvature)")

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def maximum_curvature(self) -> float:
        return self._maximum_curvature

    @property
    def minimum_curvature(self) -> float:
        return self._minimum_curvature

    @property
    def start_strain_position(self) -> StrainPosition:
        return self._start_strain_position

    @property
    def m_kappa_failure(self):
        """Moment and curvature at failure of cross-section"""
        return self._m_kappa_failure

    def get_material_points_inside_curvature(self) -> list[StrainPosition]:
        """material points between zero curvature and failure of the cross-section"""
        return (
            self.m_kappa_failure.computed_cross_section.get_material_points_inside_curvature()
        )

    def _get_m_kappa_failure(self):
        return self._m_kappa(
            strain_position=self.start_strain_position,
            maximum_curvature=self.maximum_curvature,
            minimum_curvature=self.minimum_curvature,
        )

    def _m_kappa(
        self,
        strain_position: StrainPosition,
        maximum_curvature: float,
        minimum_curvature: float,
    ) -> MKappaByStrainPosition:
        return MKappaByStrainPosition(
            self.cross_section,
            strain_position=strain_position,
            maximum_curvature=maximum_curvature,
            minimum_curvature=minimum_curvature,
        )


class MKappaCurve:
    """computation of M-Kappa-Curve assuming full interaction"""

    __slots__ = (
        "_cross_section",
        "_include_positive_curvature",
        "_include_negative_curvature",
        "_boundaries",
        "_positive",
        "_negative",
        "_m_kappa_points",
    )

    def __init__(
        self,
        cross_section: Crosssection,
        include_positive_curvature: bool = True,
        include_negative_curvature: bool = False,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : Crosssection
                cross-section to compute
        include_positive_curvature : bool
                if True than positive curvature values are computed
        include_negative_curvature : bool
                if True than negative curvature values are computed
        """
        self._cross_section = cross_section
        self._include_positive_curvature = include_positive_curvature
        self._include_negative_curvature = include_negative_curvature
        self._boundaries = self.cross_section.get_boundary_conditions()
        self._positive = self._get_positive_m_kappa_curve_curvature()
        self._negative = self._get_negative_m_kappa_curve_curvature()
        self._m_kappa_points: MKappaCurvePoints = MKappaCurvePoints()
        self._compute_positive_curvature_values()
        self._compute_negative_curvature_values()
        self._insert_zero()
        if logger.level == logging.DEBUG:
            logger.debug(f'{self.__str__()}')
        else:
            logger.info(f'Created {self.__repr__()}')

    def __repr__(self):
        return f"MKappaCurve(cross_section=cross_section)"

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_m_kappa_points(),
            self._print_legend(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        class_name = self.__class__.__name__
        return print_sections([class_name, len(class_name) * "="])

    def _print_initialization(self) -> str:
        return print_chapter(["Initialization", "--------------", self.__repr__()])

    def _print_m_kappa_points(self) -> str:
        text = [
            "M-Kappa-Points",
            "--------------",
            "",
            "--------------------------------------------------------------------------",
            "    Moment    | Curvature | Neutral axis |  Strain  | Position | Material ",
            "--------------------------------------------------------------------------",
        ]
        self.__sort_m_kappa_by_curvature()
        for point in self.m_kappa_points.points:
            text.append(
                "{:13.1f} | {:9.6f} | {:12.2f} | {:8.5f} | {:8.2f} | {}".format(
                    point.moment,
                    point.curvature,
                    point.neutral_axis,
                    point.strain_position.strain,
                    point.strain_position.position,
                    point.strain_position.material,
                )
            )
        text.append(
            "--------------------------------------------------------------------------"
        )
        return print_sections(text)

    @staticmethod
    def _print_legend() -> str:
        text = [
            "Legend",
            "------",
            "\t"
            + "Moment:       Resulting resistance moment at the given curvature and neutral axis",
            "\t"
            + 'Curvature:    curvature resulting from the "Neutral axis" and the "Strain" at "Position"',
            "\t" + "Neutral axis: computed neutral axis",
            "\t" + 'Strain:       starting strain_value at "Position"',
            "\t" + 'Position:     starting position_value for the "Strain"',
            "\t"
            + 'Material:     material where "Strain" and "Position" are taken from',
        ]
        return print_sections(text)

    @property
    def boundaries(self) -> Boundaries:
        return self._boundaries

    @property
    def cross_section(self) -> Crosssection:
        return self._cross_section

    @property
    def include_positive_curvature(self) -> bool:
        return self._include_positive_curvature

    @property
    def include_negative_curvature(self) -> bool:
        return self._include_negative_curvature

    @property
    def positive(self) -> MKappaCurveCurvature:
        return self._positive

    @property
    def negative(self) -> MKappaCurveCurvature:
        return self._negative

    @property
    def m_kappa_points(self) -> MKappaCurvePoints:
        return self._m_kappa_points

    def _get_m_kappa_curve_curvature(
        self, boundary: BoundaryValues
    ) -> MKappaCurveCurvature:
        return MKappaCurveCurvature(
            cross_section=self.cross_section,
            maximum_curvature=boundary.maximum_curvature.curvature,
            minimum_curvature=boundary.minimum_curvature.compute(
                boundary.maximum_curvature.start
            ),
            start_strain_position=boundary.maximum_curvature.start,
        )

    def _get_positive_m_kappa_curve_curvature(self) -> MKappaCurveCurvature:
        if self.include_positive_curvature:
            return self._get_m_kappa_curve_curvature(self.boundaries.positive)

    def _get_negative_m_kappa_curve_curvature(self) -> MKappaCurveCurvature:
        if self.include_negative_curvature:
            return self._get_m_kappa_curve_curvature(self.boundaries.negative)

    def _compute_negative_curvature_failure(self) -> None:
        m_kappa = self.negative.m_kappa_failure
        self._compute_values(m_kappa)

    def _compute_negative_curvature_intermediate(self) -> None:
        for strain_position in self.negative.get_material_points_inside_curvature():
            m_kappa = self._m_kappa(
                position_strain=strain_position,
                maximum_curvature=self._maximum_negative_curvature(strain_position),
                minimum_curvature=self._minimum_negative_curvature(strain_position),
            )
            self._compute_values(m_kappa)

    def _compute_negative_curvature_values(self) -> None:
        if self.negative is not None:
            self._compute_negative_curvature_failure()
            self._compute_negative_curvature_intermediate()

    def _compute_positive_curvature_failure(self) -> None:
        m_kappa = self.positive.m_kappa_failure
        self._compute_values(m_kappa)

    def _compute_positive_curvature_intermediate(self) -> None:
        for strain_position in self.positive.get_material_points_inside_curvature():
            m_kappa = self._m_kappa(
                position_strain=strain_position,
                maximum_curvature=self._maximum_positive_curvature(strain_position),
                minimum_curvature=self._minimum_positive_curvature(strain_position),
            )
            if not m_kappa.successful:
                # print(m_kappa._print_iterations()) # TODO: Logging?
                m_kappa = MKappaByStrainPosition(
                    self.cross_section,
                    strain_position=strain_position,
                    maximum_curvature=self._maximum_positive_curvature(strain_position),
                    minimum_curvature=self._minimum_positive_curvature(strain_position),
                    maximum_iterations=100,
                    solver=Bisection,
                )
            self._compute_values(m_kappa)

    def _maximum_positive_curvature(self, strain_position: StrainPosition) -> float:
        """compute the maximum possible positive curvature given the strain_value
        and its position_value for the cross-section"""
        return self.boundaries.positive.maximum_curvature.compute(strain_position)

    def _minimum_positive_curvature(self, strain_position: StrainPosition) -> float:
        """compute the minimum possible positive curvature given the strain_value
        and its position_value for the cross-section"""
        return self.boundaries.positive.minimum_curvature.compute(strain_position)

    def _maximum_negative_curvature(self, strain_position: StrainPosition) -> float:
        """compute the maximum possible negative curvature given the strain_value
        and its position_value for the cross-section"""
        return self.boundaries.negative.maximum_curvature.compute(strain_position)

    def _minimum_negative_curvature(self, strain_position: StrainPosition) -> float:
        """compute the minimum possible negative curvature given the strain_value
        and its position_value for the cross-section"""
        return self.boundaries.negative.minimum_curvature.compute(strain_position)

    def _compute_positive_curvature_values(self) -> None:
        if self.positive is not None:
            self._compute_positive_curvature_failure()
            self._compute_positive_curvature_intermediate()

    def _compute_values(self, m_kappa: MKappaByStrainPosition) -> None:
        if m_kappa.successful:
            self._save_values(
                m_kappa.moment,
                m_kappa.curvature,
                m_kappa.neutral_axis,
                m_kappa.computed_cross_section,
                m_kappa.strain_position,
            )
        else:
            print(
                f"============\n"
                f"not successful:\n"
                f"position_value={m_kappa.strain_position},\n"
                f"iterations={m_kappa.iteration} ({m_kappa.maximum_iterations})\n"
                f"{m_kappa._print_iterations()}",
            )
            #print(m_kappa._print_initialization())
            #print(m_kappa._print_iterations())

    def _insert_zero(self) -> None:
        self._save_values(0.0, 0.0, 0.0, None, None)

    def _m_kappa(
        self,
        position_strain: StrainPosition,
        maximum_curvature: float,
        minimum_curvature: float,
    ) -> MKappaByStrainPosition:
        return MKappaByStrainPosition(
            self.cross_section,
            strain_position=position_strain,
            maximum_curvature=maximum_curvature,
            minimum_curvature=minimum_curvature,
        )

    def _save_values(
        self,
        moment: float,
        curvature: float,
        neutral_axis: float,
        computed_cross_section,
        strain_position: StrainPosition = None,
    ) -> None:
        self._m_kappa_points.add(
            moment, curvature, neutral_axis, computed_cross_section, strain_position
        )

    def __sort_m_kappa_by_curvature(self) -> None:
        self._m_kappa_points._sort_points_by_curvature()