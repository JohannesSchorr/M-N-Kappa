from dataclasses import dataclass
from .crosssection import (
    BoundaryValues,
    Crosssection,
    Boundaries,
)
from .general import (
    interpolation,
    print_sections,
    print_chapter,
    str_start_end,
)
from .points import MKappaByStrainPosition


@dataclass
class MKappaCurvePoint:
    """Container for single point on M-Kappa-Curve"""

    moment: float
    curvature: float
    neutral_axis: float
    crosssection: Crosssection
    strain: float
    position: float
    material: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, MKappaCurvePoint):
            return False
        elif (
                self.moment == other.moment and
                self.curvature == other.curvature and
                self.neutral_axis == other.neutral_axis
        ):
            return True
        else:
            return False

    def moment_curvature(self) -> list:
        """list of moment and curvature"""
        return [self.moment, self.curvature]


class MKappaCurvePoints:

    """Container for points on computed M-Kappa-Curve"""

    def __init__(self) -> None:
        self._points = []

    @property
    def points(self) -> list[MKappaCurvePoint]:
        return self._points

    def add(
        self,
        moment: float,
        curvature: float,
        neutral_axis: float,
        crosssection: MKappaByStrainPosition,
        strain: float,
        position: float,
        material: str,
    ) -> None:
        """add moment-curvature point to list

        Parameters
        ----------
        moment : float
            moment of the point
        curvature : float
            curvature of the point
        neutral_axis : float
            neutral-axis leading to equilibrium (after variation)
        crosssection : MKappaByStrainPosition
            computed cross-section
        strain : float
            strain-value
        position : float
            position where strain-value is given
        material : str
            material the strain-value is given in
        """
        point = MKappaCurvePoint(
                moment,
                curvature,
                neutral_axis,
                crosssection,
                strain,
                position,
                material,
            )
        if point not in self.points:
            self._points.append(point)
            self._sort_points_by_curvature()

    def curvature(self, by_moment: float) -> float:
        """get curvature at given moment"""
        point_index = self._determine_index(by_moment)
        return interpolation(
            by_moment,
            self._moment_curvature(point_index),
            self._moment_curvature(point_index + 1),
        )

    def _moment_curvature(self, by_index) -> list[float]:
        return self.points[by_index].moment_curvature()

    def _determine_index(self, moment):
        for index in range(len(self.points) - 1):
            if self.points[index].moment <= moment <= self.points[index + 1].moment:
                return index

    def _sort_points_by_curvature(self):
        self.points.sort(key=lambda x: x.curvature)

    @property
    def moments(self) -> list[float]:
        return [point.moment for point in self.points]

    def maximum_moment(self) -> float:
        return max(self.moments)


class MKappaCurveCurvature:

    """Compute moment-curvature (M-Kappa) at failure"""

    __slots__ = (
        "_cross_section",
        "_maximum_curvature",
        "_minimum_curvature",
        "_start_strain",
        "_start_position",
        "_m_kappa_failure",
    )

    def __init__(
        self,
        cross_section: Crosssection,
        maximum_curvature: float,
        minimum_curvature: float,
        start_strain: float,
        start_position: float,
    ):
        self._cross_section = cross_section
        self._maximum_curvature = maximum_curvature
        self._minimum_curvature = minimum_curvature
        self._start_strain = start_strain
        self._start_position = start_position
        self._m_kappa_failure = self._get_m_kappa_failure()

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
    def start_strain(self) -> float:
        return self._start_strain

    @property
    def start_position(self) -> float:
        return self._start_position

    @property
    def m_kappa_failure(self):
        """Moment and curvature at failure of cross-section"""
        return self._m_kappa_failure

    def get_material_points_inside_curvature(self) -> list:
        """material points between zero curvature and failure of the cross-section"""
        return (
            self.m_kappa_failure.computed_cross_section.get_material_points_inside_curvature()
        )

    def _get_m_kappa_failure(self):
        return self._m_kappa(
            strain_position=self.start_position,
            strain_at_position=self.start_strain,
            maximum_curvature=self.maximum_curvature,
            minimum_curvature=self.minimum_curvature,
        )

    def _m_kappa(
        self,
        strain_position: float,
        strain_at_position: float,
        maximum_curvature: float,
        minimum_curvature: float,
    ) -> MKappaByStrainPosition:
        return MKappaByStrainPosition(
            self.cross_section,
            strain_position=strain_position,
            strain_at_position=strain_at_position,
            maximum_curvature=maximum_curvature,
            minimum_curvature=minimum_curvature,
        )


class MKappaCurve:
    """computation of a M-Kappa-Curve assuming full interaction"""

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
                cross section to compute
        include_positive_curvature : bool
                if True than positive curvature values are computed
        include_negative_curvature : bool
                if True than negative curvatrue values are computed
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
        return print_sections(["MKappaCurve", len("MKappaCurve") * "="])

    def _print_initialization(self) -> str:
        return print_chapter(["Initialization", "--------------", self.__repr__()])

    def _print_m_kappa_points(self):
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
                    point.strain,
                    point.position,
                    point.material,
                )
            )
        text.append(
            "--------------------------------------------------------------------------"
        )
        return print_sections(text)

    def _print_legend(self):
        text = [
            "Legend",
            "------",
            "\t"
            + "Moment:       Resulting resistance moment at the given curvature and neutral axis",
            "\t"
            + 'Curvature:    curvature resulting from the "Neutral axis" and the "Strain" at "Position"',
            "\t" + "Neutral axis: computed neutral axis",
            "\t" + 'Strain:       starting strain at "Position"',
            "\t" + 'Position:     starting position for the "Strain"',
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
                boundary.maximum_curvature.start.strain,
                boundary.maximum_curvature.start.position,
            ),
            start_strain=boundary.maximum_curvature.start.strain,
            start_position=boundary.maximum_curvature.start.position,
        )

    def _get_positive_m_kappa_curve_curvature(self) -> MKappaCurveCurvature:
        if self.include_positive_curvature:
            return self._get_m_kappa_curve_curvature(self.boundaries.positive)
        else:
            return None

    def _get_negative_m_kappa_curve_curvature(self) -> MKappaCurveCurvature:
        if self.include_negative_curvature:
            return self._get_m_kappa_curve_curvature(self.boundaries.negative)
        else:
            return None

    def _compute_negative_curvature_failure(self) -> None:
        m_kappa = self.negative.m_kappa_failure
        self._compute_values(m_kappa)

    def _compute_negative_curvature_intermediate(self) -> None:
        for strain_position in self.negative.get_material_points_inside_curvature():
            strain = strain_position["strain"]
            position = strain_position["position"]
            m_kappa = self._m_kappa(
                position_strain=position,
                strain_at_position=strain,
                maximum_curvature=self._maximum_negative_curvature(strain, position),
                minimum_curvature=self._minimum_negative_curvature(strain, position),
            )
            self._compute_values(m_kappa, strain_position["material"])

    def _compute_negative_curvature_values(self) -> None:
        if self.negative is not None:
            self._compute_negative_curvature_failure()
            self._compute_negative_curvature_intermediate()

    def _compute_positive_curvature_failure(self) -> None:
        m_kappa = self.positive.m_kappa_failure
        self._compute_values(m_kappa, "Concrete")

    def _compute_positive_curvature_intermediate(self) -> None:
        for strain_position in self.positive.get_material_points_inside_curvature():
            strain = strain_position["strain"]
            position = strain_position["position"]
            m_kappa = self._m_kappa(
                position_strain=position,
                strain_at_position=strain,
                maximum_curvature=self._maximum_positive_curvature(strain, position),
                minimum_curvature=self._minimum_positive_curvature(strain, position),
            )
            self._compute_values(m_kappa, strain_position["material"])

    def _maximum_positive_curvature(self, strain: float, position: float) -> float:
        return self.boundaries.positive.maximum_curvature.compute(strain, position)

    def _minimum_positive_curvature(self, strain: float, position: float) -> float:
        return self.boundaries.positive.minimum_curvature.compute(strain, position)

    def _maximum_negative_curvature(self, strain: float, position: float) -> float:
        return self.boundaries.negative.maximum_curvature.compute(strain, position)

    def _minimum_negative_curvature(self, strain: float, position: float) -> float:
        return self.boundaries.negative.minimum_curvature.compute(strain, position)

    def _compute_positive_curvature_values(self) -> None:
        if self.positive is not None:
            self._compute_positive_curvature_failure()
            self._compute_positive_curvature_intermediate()

    def _compute_values(
        self, m_kappa: MKappaByStrainPosition, material: str = None
    ) -> None:
        if m_kappa.successful:
            self._save_values(
                m_kappa.moment,
                m_kappa.curvature,
                m_kappa.neutral_axis,
                m_kappa.computed_cross_section,
                m_kappa.strain_at_position,
                m_kappa.strain_position,
                material,
            )

    def _insert_zero(self) -> None:
        self._save_values(0.0, 0.0, 0.0, None, 0.0, 0.0, "-")

    def _m_kappa(
        self,
        position_strain: float,
        strain_at_position: float,
        maximum_curvature: float,
        minimum_curvature: float,
    ) -> MKappaByStrainPosition:
        return MKappaByStrainPosition(
            self.cross_section,
            strain_position=position_strain,
            strain_at_position=strain_at_position,
            maximum_curvature=maximum_curvature,
            minimum_curvature=minimum_curvature,
        )

    def _save_values(
        self,
        moment: float,
        curvature: float,
        neutral_axis: float,
        computed_cross_section,
        strain: float = None,
        position: float = None,
        material: str = None,
    ) -> None:
        self._m_kappa_points.add(
            moment,
            curvature,
            neutral_axis,
            computed_cross_section,
            strain,
            position,
            material,
        )

    def __sort_m_kappa_by_curvature(self) -> None:
        self._m_kappa_points._sort_points_by_curvature()