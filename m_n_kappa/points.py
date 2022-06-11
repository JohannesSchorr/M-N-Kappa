import general
import section
import solver

"""

Todo
----
  - Implement effective width
"""


class MKappa:

    """computation of one Moment-Curvature-Point by fixation of one point and varying the neutral axis"""

    def __init__(
        self,
        cross_section: section.Crosssection,
        applied_axial_force: float = 0.0,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: solver.Solver = solver.Newton,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crossection
                cross-section to compute
        maximum_curvature : float
                maximum positive or negative allowed curvature
        minimum_curvature : float
                minimum positive or negative allowed curvature
                (needs same sign as maximum_curvature)
        strain_position : float
                position of the given strain (Default: None)
        strain_at_postion : float
                strain at the given position (Default: None)
        applied_axial_force : float
                applied axial force (Default: 0.0)
        maximum_iterations : int
                maximum allowed iterations (Default: 10)
                In case the given number of iterations before axial force within desired tolerance,
                the computation is classified as unsuccessful and will be stopped
        axial_force_tolerance : float
                if axial force within this tolerance the computation is terminated and
                classified as successful (Default: 5.0)
        solver : solver.Solver
                used solver (Default: solver.Newton)
        """
        self._cross_section = cross_section
        self._applied_axial_force = applied_axial_force
        self._axial_force_tolerance = axial_force_tolerance
        self._maximum_iterations = maximum_iterations
        self._computations = (
            []
        )  # [iteration, computed_cross_section, curvature, neutral_axis, horizontal_forces]
        self._solver = solver
        self._successful = False

    def __repr__(self):
        return f"MKappa(cross_section=CrossSection, applied_axial_force={self.applied_axial_force}, maximum_iterations={self.maximum_iterations})"

    @general.str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_iterations(),
            self._print_results(),
        ]
        return general.print_chapter(text)

    def _print_title(self) -> str:
        return general.print_sections(["MKappa", len("MKappa") * "="])

    def _print_initialization(self):
        return general.print_sections(
            ["Initialization", "--------------", self.__repr__()]
        )

    def _print_iterations(self):
        text = [
            "Iterations",
            "----------",
            f"number: {len(self.computations)}",
            "",
            "---------------------------------------------",
            "iter | curvature | neutral-axis | axial-force",
            "---------------------------------------------",
        ]
        self.__sort_computations_by_iteration()
        for iteration in self.computations:
            text.append(
                "{:4} | {:9.6f} | {:12.2f} | {:10.2f}".format(
                    iteration["iteration"],
                    iteration["curvature"],
                    iteration["neutral_axis"],
                    iteration["axial_force"],
                )
            )
        text.append("---------------------------------------------")
        return general.print_sections(text)

    def _print_results(self) -> str:
        text = [
            "Results",
            "-------",
            "\t" + "N = {:.2f}".format(self.axial_force),
            "\t" + "M = {:.2f}".format(self.moment),
            "\t" + "Kappa = {:.5f}".format(self.curvature),
        ]
        return general.print_sections(text)

    @property
    def applied_axial_force(self):
        """applied axial force"""
        return self._applied_axial_force

    @property
    def axial_force(self) -> float:
        """computed axial force"""
        return self._axial_force

    @property
    def axial_force_tolerance(self) -> float:
        """
        if axial force within this tolerance the computation is terminated and
        classified as successful
        """
        return self._axial_force_tolerance

    @property
    def computations(self) -> list:
        """
        list of computations with dictionaries including the following values
                'iteration' : number of the iteration
                'computed_cross_section' : computed crosssection
                'curvature' : computed curvature
                'neutral_axis' : computed neutral axis
                'axial_force' : computed axial force within this iteration
        """
        return self._computations

    @property
    def computed_cross_section(self):
        """computed crosssection of the current iteration"""
        return self._computed_cross_section

    @property
    def cross_section(self):
        """cross-section to compute"""
        return self._cross_section

    @property
    def curvature(self) -> float:
        """applied curvature"""
        return self._curvature

    @property
    def iteration(self) -> int:
        """number of current iteration"""
        return self._iteration

    @property
    def maximum_iterations(self) -> int:
        """maximum allowed iterations"""
        return self._maximum_iterations

    @property
    def moment(self) -> float:
        """computed moment of the crosssection"""
        return self._computed_cross_section.total_moment()

    @property
    def neutral_axis(self) -> float:
        """point where strain is zero"""
        return self._neutral_axis

    @property
    def solver(self):
        """used solver to computed equilibrium"""
        return self._solver

    @property
    def successful(self) -> bool:
        """
        True:  equilibrium has been found,
        False: equilibrium has not (yet) been found
        """
        return self._successful

    def compute(self):
        """
        compute the crosssection with given inital values (curvature and neutral axis)
        and save it
        """
        self._computed_cross_section = self._get_compute_cross_section()
        self._axial_force = self.computed_cross_section.total_axial_force()
        self.__save()

    def initialize(self):
        """initialize computation"""
        self.initialize_boundary_curvatures()
        if self.__is_axial_force_within_tolerance():
            self._successful = True
        elif self.initial_axial_forces_have_different_sign():
            self.iterate()
        else:
            # print('has different sign --> break')
            self.__set_values_none()

    def initial_axial_forces_have_different_sign(self):
        if (
            self.computations[0]["axial_force"] * self.computations[1]["axial_force"]
            < 0.0
        ):
            return True
        else:
            return False

    def initialize_boundary_curvatures(self):
        pass

    def iterate(self):
        for iter_index in range(self.iteration + 1, self.maximum_iterations, 1):
            self._iteration = iter_index
            self._neutral_axis = self._guess_neutral_axis()
            self._curvature = self._compute_new_curvature()
            self.compute()
            if self.__is_axial_force_within_tolerance():
                self._successful = True
                break

    def _axial_force_equilibrium(self):
        return self.axial_force - self.applied_axial_force

    def _compute_new_curvature(self):
        pass

    def _get_compute_cross_section(self):
        return section.ComputationCrosssectionCurvature(
            sections=self.cross_section.sections,
            curvature=self.curvature,
            neutral_axis=self.neutral_axis,
        )

    def _guess_neutral_axis(self):
        self.__sort_computations_by_axial_forces()
        return self.solver(
            data=self._computations, target="axial_force", variable="neutral_axis"
        ).compute()

    def __is_axial_force_within_tolerance(self):
        if abs(self._axial_force_equilibrium()) < self.axial_force_tolerance:
            return True
        else:
            return False

    def __save(self):
        self._computations.append(
            {
                "iteration": self.iteration,
                "computed_cross_section": self.computed_cross_section,
                "curvature": self.curvature,
                "neutral_axis": self.neutral_axis,
                "axial_force": self.axial_force,
            }
        )
        # print(self._computations[-1])
        # print(self.print_iterations())
        # print(self.computed_cross_section._print_results())

    def __set_values_none(self):
        self._axial_force = None
        self._curvature = None
        self._moment = None
        self._neutral_axis = None

    def __sort_computations_by(self, key: str):
        self._computations.sort(key=lambda x: x[key])

    def __sort_computations_by_curvature(self):
        self.__sort_computations_by("curvature")

    def __sort_computations_by_neutral_axis(self):
        self.__sort_computations_by("neutral_axis")

    def __sort_computations_by_axial_forces(self):
        self.__sort_computations_by("axial_force")

    def __sort_computations_by_iteration(self):
        self.__sort_computations_by("iteration")


class MKappaByStrainPosition(MKappa):

    """computation of one Moment-Curvature-Point by fixed stress-strain-point and varying the neutral axis"""

    __slots__ = (
        "_cross_section",
        "_strain_position",
        "_strain_at_position",
        "_applied_axial_force",
        "_axial_force_tolerance",
        "_maximum_iterations",
        "_maximum_curvature",
        "_minimum_curvature",
        "_computations",
        "_solver",
        "_successful",
        "_computed_cross_section",
        "_iteration",
    )

    def __init__(
        self,
        cross_section: section.Crosssection,
        maximum_curvature: float,
        minimum_curvature: float,
        strain_position: float,
        strain_at_position: float,
        applied_axial_force: float = 0.0,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: solver.Solver = solver.Newton,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crossection
                cross-section to compute
        maximum_curvature : float
                maximum positive or negative allowed curvature
        minimum_curvature : float
                minimum positive or negative allowed curvature
                (needs same sign as maximum_curvature)
        strain_position : float
                position of the given strain (Default: None)
        strain_at_postion : float
                strain at the given position (Default: None)
        applied_axial_force : float
                applied axial force (Default: 0.0)
        maximum_iterations : int
                maximum allowed iterations (Default: 10)
                In case the given number of iterations before axial force within desired tolerance,
                the computation is classified as unsuccessful and will be stopped
        axial_force_tolerance : float
                if axial force within this tolerance the computation is terminated and
                classified as successful (Default: 5.0)
        solver : solver.Solver
                used solver (Default: solver.Newton)
        """
        super().__init__(
            cross_section,
            applied_axial_force,
            maximum_iterations,
            axial_force_tolerance,
            solver,
        )
        self._strain_position = strain_position
        self._strain_at_position = strain_at_position
        self._maximum_curvature = maximum_curvature
        self._minimum_curvature = minimum_curvature
        self.initialize()

    def __repr__(self):
        return f"MKappaByStrainPosition(cross_section=CrossSection, strain_position={self.strain_position}, strain_at_position={self.strain_at_position}, applied_axial_force={self.applied_axial_force}, maximum_iterations={self.maximum_iterations}, axial_force_tolerance={self.axial_force_tolerance}, solver={self.solver})"

    @property
    def maximum_curvature(self) -> float:
        """maximum positive or negative allowed curvature"""
        return self._maximum_curvature

    @property
    def minimum_curvature(self) -> float:
        """minimum positive or negative allowed curvature"""
        return self._minimum_curvature

    @property
    def strain_position(self) -> float:
        """position of the given strain"""
        return self._strain_position

    @property
    def strain_at_position(self) -> float:
        """strain at the given position"""
        return self._strain_at_position

    def initialize_boundary_curvatures(self):
        for index, curvature in enumerate(
            [self.minimum_curvature, self.maximum_curvature]
        ):
            self._iteration = index
            self._curvature = curvature
            self._neutral_axis = self._compute_neutral_axis()
            self.compute()

    def _compute_new_curvature(self):
        return general.curvature(
            neutral_axis=self.neutral_axis,
            position=self.strain_position,
            strain_at_position=self.strain_at_position,
        )

    def _compute_neutral_axis(self):
        return general.neutral_axis(
            strain_at_position=self.strain_at_position,
            curvature=self.curvature,
            position=self.strain_position,
        )


class MKappaByConstantCurvature(MKappa):

    """computation of one Momente-Curvature-Point by fixed curvature and varying the neutral axis"""

    __slots__ = (
        "_cross_section",
        "_applied_curvature",
        "_maximum_neutral_axis",
        "_minimum_neutral_axis",
        "_applied_axial_force",
        "_axial_force_tolerance",
        "_maximum_iterations",
        "_computations",
        "_solver",
        "_successful",
        "_computed_cross_section",
        "_iteration",
    )

    def __init__(
        self,
        cross_section,
        applied_curvature: float,
        maximum_neutral_axis: float,
        minimum_neutral_axis: float,
        applied_axial_force,
        maximum_iterations=10,
        axial_force_tolerance=5,
        solver=solver.Newton,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crossection
                cross-section to compute
        maximum_neutral_axis : float
                maximum allowed neutral-axis
        minimum_neutral_axis : float
                minimum allowed neutral-axis
        applied_axial_force : float
                applied axial force (Default: 0.0)
        maximum_iterations : int
                maximum allowed iterations (Default: 10)
                In case the given number of iterations before axial force within desired tolerance,
                the computation is classified as unsuccessful and will be stopped
        axial_force_tolerance : float
                if axial force within this tolerance the computation is terminated and
                classified as successful (Default: 5.0)
        solver : solver.Solver
                used solver (Default: solver.Newton)
        """
        super().__init__(
            cross_section,
            applied_axial_force,
            maximum_iterations,
            axial_force_tolerance,
            solver,
        )
        self._applied_curvature = applied_curvature
        self._maximum_neutral_axis = maximum_neutral_axis
        self._minimum_neutral_axis = minimum_neutral_axis
        self.initialize()

    def __repr__(self):
        return f"MKappaByConstantCurvature(cross_section=cross_section, applied_curvature={self.applied_curvature}, maximum_neutral_axis={self.maximum_neutral_axis}, minimum_neutral_axis={self.minimum_neutral_axis}, applied_axial_force={self.applied_axial_force}, maximum_iterations={self.maximum_iterations}, axial_force_tolerance={self.axial_force_tolerance}, solver={self.solver})"

    @property
    def applied_curvature(self) -> float:
        """applied curvature (no variation)"""
        return self._applied_curvature

    @property
    def maximum_neutral_axis(self) -> float:
        """boundary condition of the neutral axis"""
        return self._maximum_neutral_axis

    @property
    def minimum_neutral_axis(self) -> float:
        """boundary_condition of the neutral axis"""
        return self._minimum_neutral_axis

    def initialize_boundary_curvatures(self):
        for index, neutral_axis in enumerate(
            [self.minimum_neutral_axis, self.maximum_neutral_axis]
        ):
            self._iteration = index
            self._curvature = self.applied_curvature
            self._neutral_axis = neutral_axis
            self.compute()

    def _compute_new_curvature(self):
        return self.applied_curvature


class MKappaCurvePoints:

    """Container for the M-Kappa-Points"""

    def __init__(self):
        self._points = []

    @property
    def points(self) -> list:
        return self._points

    def add(
        self,
        moment: float,
        curvature: float,
        neutral_axis: float,
        crosssection,
        strain: float,
        position: float,
        material: str,
    ):
        self._points.append(
            {
                "moment": moment,
                "curvature": curvature,
                "neutral-axis": neutral_axis,
                "cross_section": crosssection,
                "strain": strain,
                "position": position,
                "material": material,
            }
        )
        self.sort_points_by_curvature()

    def curvature(self, by_moment: float):
        """get curvature at given moment"""
        point_index = self.determine_index(by_moment)
        return general.interpolate(
            by_moment,
            self.moment_curvature(point_index),
            self.moment_curvature(point_index + 1),
        )

    def moment_curvature(self, by_index) -> list:
        return [self.points[by_index]["curvature"], self.points[by_index]["moment"]]

    def determine_index(self, moment):
        for index in range(len(self.points) - 1):
            if (
                self.points[index]["moment"]
                <= moment
                <= self.points[index + 1]["moment"]
            ):
                return index

    def sort_points_by_curvature(self):
        self.points.sort(key=lambda x: x["curvature"])


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
        cross_section: section.Crosssection,
        include_positive_curvature: bool = True,
        include_negative_curvature: bool = False,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crosssection
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
        self._m_kappa_points = (
            MKappaCurvePoints()
        )  # [moment, curvature, computed_cross_section]
        self._compute_positive_curvature_values()
        self._compute_negative_curvature_values()
        self._insert_zero()

    def __repr__(self):
        return f"MKappaCurve(cross_section=cross_section)"

    @general.str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_m_kappa_points(),
            self._print_legend(),
        ]
        return general.print_chapter(text)

    def _print_title(self) -> str:
        return general.print_sections(["MKappaCurve", len("MKappaCurve") * "="])

    def _print_initialization(self) -> str:
        return general.print_chapter(
            ["Initialization", "--------------", self.__repr__()]
        )

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
        for point in self.m_kappa_points:
            text.append(
                "{:13.1f} | {:9.6f} | {:12.2f} | {:8.5f} | {:8.2f} | {}".format(
                    point["moment"],
                    point["curvature"],
                    point["neutral-axis"],
                    point["strain"],
                    point["position"],
                    point["material"],
                )
            )
        text.append(
            "--------------------------------------------------------------------------"
        )
        return general.print_sections(text)

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
        return general.print_sections(text)

    @property
    def boundaries(self):
        return self._boundaries

    @property
    def cross_section(self):
        return self._cross_section

    @property
    def include_positive_curvature(self):
        return self._include_positive_curvature

    @property
    def include_negative_curvature(self):
        return self._include_negative_curvature

    @property
    def positive(self):
        return self._positive

    @property
    def negative(self):
        return self._negative

    @property
    def m_kappa_points(self) -> list:
        """
        list of dictionaries with following values:
                'moment': Resulting resistance moment at the given curvature and neutral axis
                'curvature': curvature resulting from the "neutral-axis" and the "strain" at "position"
                'neutral-axis': computed neutral axis
                'strain': starting strain at "position"
                'position': starting position for the "strain"
                'material': material where "strain" and "position" are taken from'
        """
        return self._m_kappa_points

    def _get_m_kappa_curve_curvature(self, boundary):
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

    def _get_positive_m_kappa_curve_curvature(self):
        if self.include_positive_curvature:
            return self._get_m_kappa_curve_curvature(self.boundaries.positive)
        else:
            return None

    def _get_negative_m_kappa_curve_curvature(self):
        if self.include_negative_curvature:
            return self._get_m_kappa_curve_curvature(self.boundaries.negative)
        else:
            return None

    def _compute_negative_curvature_failure(self):
        m_kappa = self.negative.m_kappa_failure
        self._compute_values(m_kappa)

    def _compute_negative_curvature_intermediate(self):
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

    def _compute_negative_curvature_values(self):
        if self.negative is not None:
            self._compute_negative_curvature_failure()
            self._compute_negative_curvature_intermediate()

    def _compute_positive_curvature_failure(self):
        m_kappa = self.positive.m_kappa_failure
        self._compute_values(m_kappa, "Concrete")

    def _compute_positive_curvature_intermediate(self):
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

    def _maximum_positive_curvature(self, strain: float, position: float):
        return self.boundaries.positive.maximum_curvature.compute(strain, position)

    def _minimum_positive_curvature(self, strain: float, position: float):
        return self.boundaries.positive.minimum_curvature.compute(strain, position)

    def _maximum_negative_curvature(self, strain: float, position: float):
        return self.boundaries.negative.maximum_curvature.compute(strain, position)

    def _minimum_negative_curvature(self, strain: float, position: float):
        return self.boundaries.negative.minimum_curvature.compute(strain, position)

    def _compute_positive_curvature_values(self):
        if self.positive is not None:
            self._compute_positive_curvature_failure()
            self._compute_positive_curvature_intermediate()

    def _compute_values(self, m_kappa: MKappa, material: str = None):
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

    def _insert_zero(self):
        self._save_values(0.0, 0.0, 0.0, None, 0.0, 0.0, "-")

    def _m_kappa(
        self,
        position_strain: float,
        strain_at_position: float,
        maximum_curvature: float,
        minimum_curvature: float,
    ):
        return MKappaByStrainPosition(
            self.cross_section,
            strain_position=position_strain,
            strain_at_position=strain_at_position,
            maximum_curvature=maximum_curvature,
            minimum_curvature=minimum_curvature,
        )

    def _save_values(
        self,
        moment,
        curvature,
        neutral_axis,
        computed_cross_section,
        strain: float = None,
        position: float = None,
        material: str = None,
    ):
        self._m_kappa_points.add(
            moment,
            curvature,
            neutral_axis,
            computed_cross_section,
            strain,
            position,
            material,
        )

    def __sort_m_kappa_by_curvature(self):
        self._m_kappa_points.sort(key=lambda x: x["curvature"])


class MKappaCurveCurvature:

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
        cross_section,
        maximum_curvature: float,
        minimum_curvature,
        start_strain: float,
        start_position: float,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crosssection

        maximum_curvature : float

        minimum : float

        start_strain : float

        start_position : float
        """
        self._cross_section = cross_section
        self._maximum_curvature = maximum_curvature
        self._minimum_curvature = minimum_curvature
        self._start_strain = start_strain
        self._start_position = start_position
        self._m_kappa_failure = self._get_m_kappa_failure()

    @property
    def cross_section(self):
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
        return self._m_kappa_failure

    def get_material_points_inside_curvature(self) -> list:
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
    ):
        return MKappaByStrainPosition(
            self.cross_section,
            strain_position=strain_position,
            strain_at_position=strain_at_position,
            maximum_curvature=maximum_curvature,
            minimum_curvature=minimum_curvature,
        )


class MKappaAtAxialForce:

    """
    compute M-Kappa-Curve at given axial force

    procedure:
            1. get maximum curvature
            2.
    """

    def __init__(self, cross_section: section.Crosssection, axial_force: float):
        self._cross_section = cross_section
        self._axial_force = axial_force


class MNZeroCurvature:
    """
    compute moment and axial force at zero curvature
    """

    __slots__ = (
        "_cross_section",
        "_input_section_type",
        "_input_strain",
        "_counter_lower_strain",
        "_counter_upper_strain",
        "_axial_force_tolerance",
        "_maximum_iterations",
        "_solver",
        "_computations",
        "_iteration",
        "_other_strain",
        "_other_axial_force",
        "_other_cross_section",
        "_successful",
        "_input_cross_section",
        "_other_cross_section",
        "_axial_force",
    )

    def __init__(
        self,
        cross_section: section.Crosssection,
        input_section_type: str,
        input_strain: float,
        counter_lower_strain: float,
        counter_upper_strain: float,
        axial_force_tolerance: float = 5.0,
        maximum_iterations: int = 10,
        solver: solver.Solver = solver.Newton,
    ):
        """
        Initialization

        Paramters
        ---------
        cross_section : section.Crosssection
                given cross-section
        input_section_type : str
                section where strain is applied to
                possible values are (steel-)'girder' or (concrete-)'slab'
        input_strain : str
                strain where axial force and moment were calculated
        axial_force_tolerance : float
                tolerance of axial force to be met
        maximum_iterations : int
                maximum number of iterations
        solver : solver.Solver
                solver to compute the axial force
        """
        self._cross_section = cross_section
        self._input_section_type = input_section_type
        self._input_strain = input_strain
        self._counter_lower_strain = counter_lower_strain
        self._counter_upper_strain = counter_upper_strain
        self._axial_force_tolerance = axial_force_tolerance
        self._maximum_iterations = maximum_iterations
        self._solver = solver
        self._compute_input_section()
        self._computations = []
        self._iteration = 0
        self._other_strain = self.counter_lower_strain
        self._other_axial_force = 0.0
        self._other_cross_section = None
        self._successful = False
        self.other_sections_initialize()

    def __repr__(self):
        return f"MNZeroCurvature(cross_section=cross_section, input_section_type={self.input_section_type}, input_strain={self.input_strain})"

    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_input_sections_result(),
            self._print_other_sections_result(),
            self._print_other_sections_iterations(),
        ]
        return general.print_chapter(text)

    def _print_title(self) -> str:
        return general.print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initalization(self) -> str:
        return general.print_sections(
            ["Initialization", len("Initialization") * "-"], self.__repr__()
        )

    def _print_input_sections_result(self) -> str:
        text = [
            "Input Section",
            "-------------",
            f"section-type: {self.input_section_type}",
            f"strain: {self.input_strain}",
            f"axial-force: {self.axial_force}",
            f"moment: {self.input_sections_moment()}",
        ]
        return general.print_sections(text)

    def _print_other_sections_result(self) -> str:
        text = [
            "Other Section",
            "-------------",
            f"strain: {self.other_strain}",
            f"axial-force: {self.other_axial_force}",
            f"moment: {self.other_sections_moment()}",
        ]
        return general.print_sections(text)

    def _print_other_sections_iterations(self) -> str:
        text = [
            "Iterations",
            "----------",
            "",
            "----------------------------",
            "iter |  strain  | ax. force ",
            "----------------------------",
        ]
        for computation in self.computations:
            text.append(
                "{:4} | {:8.5f} | {:9.2f}".format(
                    computation["iteration"],
                    computation["strain"],
                    computation["axial-force"],
                )
            )
        text.append("----------------------------")
        return general.print_sections(text)

    @property
    def axial_force(self) -> float:
        return self._axial_force

    @property
    def axial_force_tolerance(self) -> float:
        return self._axial_force_tolerance

    @property
    def computations(self) -> list:
        return self._computations

    @property
    def cross_section(self) -> section.Crosssection:
        return self._cross_section

    @property
    def counter_lower_strain(self) -> float:
        return self._counter_lower_strain

    @property
    def counter_upper_strain(self) -> float:
        return self._counter_upper_strain

    @property
    def input_section_type(self) -> str:
        return self._input_section_type

    @property
    def input_strain(self):
        return self._input_strain

    @property
    def input_cross_section(self):
        return self._input_cross_section

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def maximum_iterations(self) -> int:
        return self._maximum_iterations

    @property
    def other_strain(self):
        return self._other_strain

    @property
    def other_axial_force(self) -> float:
        return self._other_axial_force

    @property
    def other_cross_section(self) -> section.Crosssection:
        return self._other_cross_section

    @property
    def successful(self) -> bool:
        return self._successful

    @property
    def solver(self):
        return self._solver

    def moment(self) -> float:
        return self.other_sections_moment() + self.input_sections_moment()

    def input_sections(self) -> list:
        return self.cross_section.sections_of_type(self.input_section_type)

    def other_sections(self) -> list:
        return self.cross_section.sections_not_of_type(self.input_section_type)

    def _compute_input_section(self):
        self._input_cross_section = self._create_crosssection(
            self.input_sections(), self.input_strain
        )
        self._axial_force = self.input_cross_section.total_axial_force()

    def _compute_other_section(self):
        self._other_cross_section = self._create_crosssection(
            self.other_sections(), self.other_strain
        )
        self._other_axial_force = self.other_cross_section.total_axial_force()
        self._save()

    def input_sections_moment(self):
        return self.input_cross_section.total_moment()

    def other_sections_moment(self):
        return self.other_cross_section.total_moment()

    def other_sections_initialize(self):
        self._compute_other_section()
        self._iteration = 1
        self._other_strain = self.counter_upper_strain
        self._compute_other_section()
        if self._axial_force_within_tolerance():
            self._successful = True
        else:
            self.other_sections_iterate()

    def other_sections_iterate(self):
        for iteration in range(2, self.maximum_iterations):
            self._iteration = iteration
            self._other_strain = self._guess_new_strain()
            self._compute_other_section()
            if self._axial_force_within_tolerance():
                self._successful = True
                break

    def other_maximum_strain(self) -> float:
        cross_section = section.Crosssection(self.other_sections())
        if self.input_strain < 0.0:
            return cross_section.maximum_positive_strain()
        else:
            return cross_section.maximum_negative_strain()

    def _axial_force_equilibrium(self) -> float:
        return self.axial_force + self.other_axial_force

    def _axial_force_within_tolerance(self) -> bool:
        if abs(self._axial_force_equilibrium()) < self.axial_force_tolerance:
            return True
        else:
            return False

    def _create_crosssection(self, sections, strain):
        return section.ComputationCrosssectionStrain(sections, strain)

    def _guess_new_strain(self):
        return self.solver(
            data=self.computations, variable="strain", target="axial-force"
        ).compute()

    def _save(self):
        self._computations.append(
            {
                "iteration": self.iteration,
                "strain": self.other_strain,
                "axial-force": self._axial_force_equilibrium(),
                "cross-section": self.other_cross_section,
            }
        )

    def resulting_crosssection(self):
        return self.input_cross_section + self.other_cross_section


class MNZeroCurvatureCurve:

    """
    computes the moment and axial-force curve of a cross-section in case of no curvature

    procedure:
            1. determine strains in the sub-cross-sections (girder and slab)
            2. compute strain at the corresponding counter-sections
            3. determine moment, axial-force, strain-difference, etc.r
    """

    __slots__ = (
        "_cross_section",
        "_section_results",
        "_axial_force_starting_points",
        "_m_n_points",
    )

    def __init__(self, cross_section: section.Crosssection):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crosssection
                crosssection to compute
        """
        self._cross_section = cross_section
        self._section_results = []
        self._axial_force_starting_points = []
        self._m_n_points = []
        self.compute_section_axial_forces()
        self.collect_axial_force_starting_points()
        self.compute_m_n_points()

    def __repr__(self):
        return "MNZeroCurvatureCurve(cross_section=cross_section)"

    @general.str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_section_results_table(),
            self._print_axial_force_table(),
            self._print_m_n_points_table(),
        ]
        return general.print_chapter(text)

    def _print_title(self) -> str:
        return general.print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return general.print_sections(
            ["Initialization", len("Initialization") * "-", self.__repr__()]
        )

    def _print_results_table(self, title: str, results: str) -> str:
        text = [
            title,
            len(title) * "-",
            "",
            "-------------------------------------",
            "   strain   |  ax.-force | sec.-type ",
            "-------------------------------------",
            results,
            "-------------------------------------",
        ]
        return general.print_sections(text)

    def _print_section_results_table(self) -> str:
        return self._print_results_table(
            "Section Results", self._print_section_results()
        )

    def _print_section_results(self) -> str:
        return general.print_sections(
            [
                self._print_section_result(section_result)
                for section_result in self.section_results
            ]
        )

    def _print_section_result(self, section_result: dict) -> str:
        line = []
        line.append(" {:10.6f}".format(section_result["strain"]))
        line.append("{:10.2f}".format(section_result["axial-force"]))
        line.append("{:}".format(section_result["section-type"]))
        return " | ".join(line)

    def _print_axial_force_starting_points(self) -> str:
        return general.print_sections(
            [
                self._print_section_result(starting_point)
                for starting_point in self.axial_force_starting_points
            ]
        )

    def _print_axial_force_table(self) -> str:
        return self._print_results_table(
            "Axial force starting points", self._print_axial_force_starting_points()
        )

    def _print_m_n_points_table(self) -> str:
        text = [
            "M-N-Kappa points",
            "----------------",
            "",
            "-------------------------------------------------------",
            "    Moment    | Axi.-force |  Curvature | strain-diff. ",
            "-------------------------------------------------------",
            self._print_m_n_points_table_content(),
            "-------------------------------------------------------",
        ]
        return general.print_sections(text)

    def _print_m_n_points_table_content(self) -> str:
        return general.print_sections(
            [self._print_m_n_point_row(m_n_point) for m_n_point in self.m_n_points]
        )

    def _print_m_n_point_row(self, m_n_point) -> str:
        row = [
            " {:12.2f}".format(m_n_point["moment"]),
            "{:10.2f}".format(m_n_point["axial-force"]),
            "{:10.6f}".format(m_n_point["curvature"]),
            "{:10.6f}".format(m_n_point["strain-difference"]),
        ]
        return " | ".join(row)

    @property
    def cross_section(self):
        return self._cross_section

    @property
    def m_n_points(self) -> list:
        """
        m-n-points with zero curvature

        each m-n-point has following keys:
                - moment: computed moment of the crosssection
                - axial-force: axial force between the slab- and the girder-sections
                - curvature: curvature of the crosssection (defaults to 0.0)
                - strain-difference: strain-difference between the slab- and the girder-sections
                - cross-section: computed crosssection
        """
        return self._m_n_points

    @property
    def section_results(self):
        return self._section_results

    @property
    def axial_force_starting_points(self):
        return self._axial_force_starting_points

    def _get_section_strains(self) -> list:
        section_strains = []
        for section in self.cross_section.sections:
            section_strains += section.section_strains()
        return general.remove_duplicates(section_strains)

    def compute_section_axial_forces(self):
        for section_strain in self._get_section_strains():
            self.compute_section_axial_force(
                strain=section_strain["strain"],
                section_type=section_strain["section-type"],
            )

    def compute_section_axial_force(self, strain: float, section_type: str) -> None:
        sections = self.cross_section.sections_of_type(section_type)
        crosssection_by_strain = self._create_crosssection(sections, strain)
        self.save_section_result(crosssection_by_strain)

    def save_section_result(self, crosssection) -> None:
        self._section_results.append(
            {
                "cross-section": crosssection,
                "strain": crosssection.strain,
                "axial-force": crosssection.total_axial_force(),
                "section-type": crosssection.section_type,
            }
        )

    def results_of_section_type(self, section_type: str) -> list:
        return [
            section_result
            for section_result in self.section_results
            if section_result["section-type"] == section_type
        ]

    def _maximum_axial_force(self, section_type: str):
        return max(
            self.results_of_section_type(section_type), key=lambda x: x["axial-force"]
        )["axial-force"]

    def _minimum_axial_force(self, section_type: str):
        return min(
            self.results_of_section_type(section_type), key=lambda x: x["axial-force"]
        )["axial-force"]

    def counter_sections(self, section_type):
        return self.cross_section.sections_of_type(
            self.counter_section_type(section_type)
        )

    def find_border_strains(self, axial_force: float, counter_section_type: str):
        counter_sections = self.results_of_section_type(counter_section_type)
        for index in range(len(counter_sections) - 1):
            if (
                counter_sections[index]["axial-force"]
                <= axial_force
                <= counter_sections[index + 1]["axial-force"]
            ):
                return (
                    counter_sections[index]["strain"],
                    counter_sections[index + 1]["strain"],
                )

    def counter_section_type(self, section_type: str):
        counter_section_types = {"girder": "slab", "slab": "girder"}
        return counter_section_types[section_type]

    def collect_axial_force_starting_points(self):
        for index, section_result in enumerate(self.section_results):
            counter_section_type = self.counter_section_type(
                section_result["section-type"]
            )
            if self._is_axial_starting_point(
                counter_section_type, section_result["axial-force"]
            ):
                self._axial_force_starting_points.append(section_result)

    def _is_axial_starting_point(
        self, counter_section_type: str, axial_force: float
    ) -> bool:
        if axial_force == 0.0:
            return False
        elif (
            (-1.0) * self._maximum_axial_force(counter_section_type)
            < axial_force
            < (-1.0) * self._minimum_axial_force(counter_section_type)
        ):
            return True
        else:
            return False

    def _create_crosssection(self, sections, strain):
        return section.ComputationCrosssectionStrain(sections, strain)

    def compute_m_n_points(self) -> None:
        for starting_point in self.axial_force_starting_points:
            axial_force = starting_point["axial-force"]
            counter_section_type = self.counter_section_type(
                starting_point["section-type"]
            )
            lower_strain, upper_strain = self.find_border_strains(
                axial_force * (-1.0), counter_section_type
            )
            m_n_zero_curvature = self._create_mnzerocurvature(
                section_type=starting_point["section-type"],
                strain=starting_point["strain"],
                counter_lower_strain=lower_strain,
                counter_upper_strain=upper_strain,
            )
            self._save_m_n_points(m_n_zero_curvature.resulting_crosssection())

    def _create_mnzerocurvature(
        self,
        section_type: str,
        strain: float,
        counter_lower_strain: float,
        counter_upper_strain: float,
    ):
        return MNZeroCurvature(
            cross_section=self.cross_section,
            input_section_type=section_type,
            input_strain=strain,
            counter_lower_strain=counter_lower_strain,
            counter_upper_strain=counter_upper_strain,
        )

    def _save_m_n_points(self, mnzerocurvature: MNZeroCurvature):
        self._m_n_points.append(
            {
                "moment": mnzerocurvature.total_moment(),
                "axial-force": mnzerocurvature.axial_force,
                "curvature": 0.0,
                "strain-difference": mnzerocurvature.strain_difference,
                "cross-section": mnzerocurvature,
            }
        )


class MCurvatureCurve:
    """ """

    def __init__(self, cross_section: section.Crosssection, axial_force: float):
        self._cross_section = cross_section
        self._axial_force: float

    @property
    def cross_section(self) -> section.Crosssection:
        return self._cross_section

    @property
    def axial_force(self) -> float:
        return self._axial_force

    def compute(self):
        pass


class MNCurvatureCurve:

    """
    compute the M-N-Curvature-Curve

    procedure:
            1.
    """

    def __init__(self, cross_section: section.Crosssection, m_n_points: list):
        """
        Initialization

        Parameters
        ----------
        cross_section : section.Crosssection
                cross_section
        m_n_points : list
                list of computed moment-axial-force-points without curvature
                serves as starting points
        """
        self._cross_section = cross_section
        self._m_n_points = m_n_points
        self._m_n_curvature_points = []

    def __repr__(self):
        return f"MNCurvatureCurve(cross_section={self.cross_section}, m_n_points={self.m_n_points})"

    @general.str_start_end
    def __str__(self):
        text = []
        return general.print_chapter(text)

    def _print_title(self) -> str:
        return general.print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return general.print_sections(
            ["Initialization", "--------------", self.__repr__()]
        )

    @property
    def cross_section(self) -> section.Crosssection:
        return self._cross_section

    @property
    def m_n_points(self) -> list:
        return self._m_n_points

    @property
    def m_n_curvature_points(self) -> list:
        return self._m_n_curvature_points

    def compute_m_n_curvature_points(self):
        for m_n_point in self.m_n_points:
            raise NotImplementedError()


"""
import material 
import geometry
import section		
import time
if __name__ == '__main__': 
	
	concrete = material.Concrete(f_cm=30)
	concrete_rectangle = geometry.Rectangle(top_edge=0.0, bottom_edge=20, width=10)
	#print(concrete)
	steel = material.Steel(f_y=355, epsilon_u=0.2)
	steel_rectangle = geometry.Rectangle(top_edge=20, bottom_edge=30, width=10)
	
	#print(steel)
	
	concrete_section = section.Section(geometry=concrete_rectangle, material=concrete)
	steel_section = section.Section(geometry=steel_rectangle, material=steel)
	
	cs = section.Crosssection(sections=[concrete_section, steel_section])
	cs_bound = section.CrosssectionBoundaries(sections=cs.sections)
	#print(cs_bound)
	
	m_kappa = MKappaByStrainPosition(
		cross_section=cs, 
		strain_position=20.0, 
		strain_at_position=-0.00169, 
		maximum_curvature=0.000135)
	print(m_kappa)
	
	start = time.clock()
	m_kappa_curve = MKappaCurve(
		cross_section=cs, 
		include_positive_curvature = True,
		include_negative_curvature = True, 
		)
	print(m_kappa_curve)
	
	mncurvaturecurve = MNZeroCurvatureCurve(cross_section=cs)
	print(mncurvaturecurve)
	#mncurve = MNZeroCurvature(cross_section=cs, input_section_type='slab', input_strain=-0.002)
	#print(mncurve)
	
	end = time.clock()
	#print(m_kappa_curve)
	#print('duration:', str(end - start))
	#"""
