import operator
from dataclasses import dataclass

from .general import (
    print_sections,
    print_chapter,
    str_start_end,
    curvature,
    neutral_axis,
    StrainPosition,
)
from .crosssection import Crosssection, ComputationCrosssectionCurvature
from .solver import Solver, Newton

from .log import LoggerMethods

log = LoggerMethods(__name__)


@dataclass
class Computation:
    """
    stores the results of an iteration-step during a computation

    .. versionadded:: 0.1.0

    Parameters
    ----------
    iteration: int
        iteration-number
    computed_cross_section: :py:class:`~m_n_kappa.Crosssection`
        computed cross-section that inherits from `~m_n_kappa.Crosssection`
    curvature: float
        computed curvature
    neutral_axis_value: float
        computed neutral axis
    axial_force: float
        computed axial-force
    """

    iteration: int
    computed_cross_section: Crosssection
    curvature: float
    neutral_axis_value: float
    axial_force: float
    axial_force_equilibrium: float

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")


class MKappa:

    """
    computation of one Moment-Curvature-Point by fixation of
    one point and varying the neutral axis

    .. versionadded:: 0.1.0

    works as base-class for :py:class:`MKappaByStrainPosition` and
    :py:class:`MKappaByConstantCurvature`
    """

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        applied_axial_force: float = 0.0,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: Solver = Newton,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crossection`
            cross-section to compute
        applied_axial_force : float
            applied axial force (Default: 0.0)
        maximum_iterations : int
            maximum allowed iterations (Default: 10).
            In case the given number of iterations before axial force within desired tolerance,
            the computation is classified as not successful and will be stopped
        axial_force_tolerance : float
            if axial force within this tolerance the computation is terminated and
            classified as successful (Default: 5.0)
        solver : :py:class:`~m_n_kappa.solver.Solver`
            used solver (Default: :py:class:`~m_n_kappa.solver.Newton`)
        """
        self._cross_section = cross_section
        self._applied_axial_force = applied_axial_force
        self._axial_force_tolerance = axial_force_tolerance
        self._maximum_iterations = maximum_iterations
        self._computations: list[Computation] = []
        self._solver = solver
        self._successful = False
        self._not_successful_reason = "-"
        self._iteration = 0
        self._curvature = None
        self._neutral_axis = None
        self._computed_cross_section = None
        self._axial_force = None
        self._is_called_by_user = True

    def __repr__(self):
        return (
            f"MKappa(cross_section=CrossSection, "
            f"applied_axial_force={self.applied_axial_force}, "
            f"maximum_iterations={self.maximum_iterations})"
        )

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_iterations(),
            self._print_results(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        class_name = self.__class__.__name__
        return print_sections([class_name, len(class_name) * "="])

    def _print_initialization(self):
        return print_sections(["Initialization", "--------------", self.__repr__()])

    def _print_iterations(self):
        text = [
            "Iterations",
            "----------",
            f"number: {len(self.computations)}",
            "",
            "------------------------------------------------------------",
            "iter | curvature | neutral-axis | axial-force | equilibrium ",
            "------------------------------------------------------------",
        ]
        self.__sort_computations_by("iteration")
        for computation in self.computations:
            text.append(
                f"{computation.iteration:4} | "
                f"{computation.curvature:9.6f} | "
                f"{computation.neutral_axis_value:12.2f} | "
                f"{computation.axial_force:10.2f} | "
                f"{computation.axial_force - self.applied_axial_force:11.4f}"
            )
        text.append("------------------------------------------------------------")
        return print_sections(text)

    def _print_results(self) -> str:
        if self.successful:
            text = [
                "Results",
                "-------",
                "\t" + f"N = {self.axial_force:.2f}",
                "\t" + f"M = {self.moment:.2f}",
                "\t" + f"Kappa = {self.curvature:.5f}",
                "\t" + f"z_m = {self.neutral_axis:.2f}",
            ]
            return print_sections(text)
        else:
            return ""

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
    def computations(self) -> list[Computation]:
        """saved computations"""
        return self._computations

    @property
    def computed_cross_section(self):
        """computed cross_section of the current iteration"""
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
        """computed moment of the cross_section"""
        return self._computed_cross_section.total_moment()

    @property
    def neutral_axis(self) -> float:
        """point where strain_value is zero"""
        return self._neutral_axis

    @property
    def solver(self):
        """used solver to computed equilibrium"""
        return self._solver

    @property
    def not_successful_reason(self) -> str:
        """In case computation was not successful gives a reason"""
        return self._not_successful_reason

    @property
    def successful(self) -> bool:
        """
        ``True``:  equilibrium has been found,
        ``False``: equilibrium has not (yet) been found
        """
        return self._successful

    @property
    def variable(self):
        """
        name variable that is changed to reach equilibrium of axial force

        .. versionadded:: 0.2.0
        """
        return ""

    def compute(self) -> None:
        """
        compute the cross-section with given initial values (curvature and neutral axis)
        and save it
        """
        self._computed_cross_section = self._get_compute_cross_section()
        self._axial_force = self.computed_cross_section.total_axial_force()
        self.__save()
        if self.__is_axial_force_within_tolerance():
            self._successful = True

    def initialize(self) -> None:
        """initialize computation"""
        self.initialize_boundary_curvatures()
        if not self._successful:
            if self._initial_axial_forces_have_different_sign():
                self.iterate()
            else:
                self._not_successful_reason = (
                    f"difference of axial forces at minimum and maximum "
                    f"{self.variable} have same sign"
                )
                self._message()
                self.__set_values_none()

    def _message(self) -> None:
        message = (
            f"Difference of axial-force and applied axial-force at minimum and maximum {self.variable} "
            f"have same sign. "
            f"No equilibrium of axial-forces possible. "
        )
        if self._is_called_by_user:
            message += "Computation will be aborted."
            log.warning(message)
        else:
            message += "Computation will be skipped."
            log.info(message)

    def _initial_axial_forces_have_different_sign(self) -> bool:
        if (
            self.computations[0].axial_force_equilibrium
            * self.computations[1].axial_force_equilibrium
            < 0.0
        ):
            return True
        else:
            return False

    def initialize_boundary_curvatures(self):
        pass

    def iterate(self) -> None:
        """
        iterate as long as one of the following criteria are reached:
        - number of maximum iterations
        - absolute axial force smaller than desired one
        """
        for iter_index in range(self.iteration + 1, self.maximum_iterations + 1, 1):
            self._iteration = iter_index
            self._neutral_axis = self._guess_neutral_axis()
            if self.neutral_axis is None:
                self._not_successful_reason = "Iteration not converging"
                log.info(self.not_successful_reason)
                return
            self._curvature = self._compute_new_curvature()
            self.compute()
            if self._successful:
                return
        self._not_successful_reason = "maximum iterations reached"  # maybe using enum?
        log.info(
            f"Maximum number of iterations ({self.maximum_iterations}) reached, "
            f"without finding equilibrium of axial forces"
        )

    def axial_force_equilibrium(self) -> float:
        """compute the equilibrium of computed and applied axial-force"""
        return self.axial_force - self.applied_axial_force

    def _compute_new_curvature(self) -> float:
        pass

    def _get_compute_cross_section(self) -> ComputationCrosssectionCurvature:
        return ComputationCrosssectionCurvature(
            cross_section=self.cross_section,
            curvature=self.curvature,
            neutral_axis_value=self.neutral_axis,
        )

    @log.result
    def _guess_neutral_axis(self) -> float:
        """
        Guess a new value for the neutral axis

        Uses the defined Solver and checks if the preceding computations
        lead to an improvement of the target value (here: axial-forces)

        Returns
        -------
        float
            new value of the neutral axis
        """
        self.__sort_computations_by("axial_force")
        temp_computations = [
            {
                # "axial_force": computation.axial_force,
                "axial_force_equilibrium": computation.axial_force_equilibrium,
                "neutral_axis_value": computation.neutral_axis_value,
            }
            for computation in self._computations
        ]
        solver = self.solver(
            data=temp_computations,
            target="axial_force_equilibrium",
            variable="neutral_axis_value",
        )
        if self._target_value_is_improved():
            use_fallback = False
        else:
            use_fallback = True
            log.info("Axial force equilibrium not improved: use fallback")
        return solver.compute(use_fallback)

    def __is_axial_force_within_tolerance(self) -> bool:
        """
        check if equilibrium of axial-forces is within the given tolerance
        (see attribute :py:attr:`~m_n_kappa.points.MKappa.axial_force_tolerance`)
        """
        if abs(self.axial_force_equilibrium()) < self.axial_force_tolerance:
            return True
        else:
            return False

    def __save(self) -> None:
        self._computations.append(
            Computation(
                iteration=self.iteration,
                computed_cross_section=self.computed_cross_section,
                curvature=self.curvature,
                neutral_axis_value=self.neutral_axis,
                axial_force=self.axial_force,
                axial_force_equilibrium=self.axial_force_equilibrium(),
            )
        )

    def _target_value_is_improved(self) -> bool:
        self.__sort_computations_by("iteration")
        if operator.truth(self._computations):
            if (
                abs(
                    self._computations[-1].axial_force
                    - self._computations[-2].axial_force
                )
                < 1.0
            ):
                return False
        return True

    def __set_values_none(self) -> None:
        self._axial_force = None
        self._curvature = None
        self._moment = None
        self._neutral_axis = None

    def __sort_computations_by(self, attribute: str) -> None:
        """sorts attribute ``computations`` by given attribute-key"""
        self._computations.sort(key=operator.attrgetter(attribute))


class MKappaByStrainPosition(MKappa):

    """
    computation of one Moment-Curvature-Point by fixed stress-strain_value-point and
    varying the neutral axis

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_cross_section",
        "_strain_position",
        "_applied_axial_force",
        "_axial_force_tolerance",
        "_maximum_iterations",
        "_maximum_curvature",
        "_minimum_curvature",
        "_computations",
        "_solver",
        "_successful",
        "_not_successful_reason",
        "_computed_cross_section",
        "_iteration",
        "_is_called_by_user",
    )

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        strain_position: StrainPosition,
        maximum_curvature: float = None,
        minimum_curvature: float = None,
        positive_curvature: bool = None,
        applied_axial_force: float = 0.0,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: Solver = Newton,
        is_called_by_user: bool = True,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crossection`
            cross-section to compute
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            position_value of the given strain_value (Default: None)
        maximum_curvature : float
            maximum positive or negative allowed curvature (Default: None)
        minimum_curvature : float
            minimum positive or negative allowed curvature
            (needs same sign as edge_strains, Default: None)
        applied_axial_force : float
            applied axial force (Default: 0.0)
        maximum_iterations : int
            maximum allowed iterations (Default: 10)
            In case the given number of iterations before axial force within desired tolerance,
            the computation is classified as not successful and will be stopped
        axial_force_tolerance : float
            if axial force within this tolerance the computation is terminated and
            classified as successful (Default: 5.0)
        solver : :py:class:`~m_n_kappa.solver.Solver`
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
        if maximum_curvature is None and minimum_curvature is None:
            if isinstance(positive_curvature, bool):
                maximum_curvature = self._determine_maximum_curvature(
                    positive_curvature
                )
                minimum_curvature = self._determine_minimum_curvature(
                    positive_curvature
                )
            else:
                raise ValueError(
                    f"If 'maximum_curvature=None' and 'minimum_curvature=None', "
                    f"then 'positive_curvature' must be set to 'True' or 'False'"
                )
        self._maximum_curvature = maximum_curvature
        self._minimum_curvature = minimum_curvature
        self._is_called_by_user = is_called_by_user
        self.initialize()

    def __repr__(self):
        return (
            f"MKappaByStrainPosition("
            f"cross_section=CrossSection, "
            f"strain_position={self.strain_position}, "
            f"applied_axial_force={self.applied_axial_force}, "
            f"maximum_iterations={self.maximum_iterations}, "
            f"axial_force_tolerance={self.axial_force_tolerance}, "
            f"solver={self.solver})"
        )

    @property
    def variable(self):
        """
        name variable that is changed to reach equilibrium of axial force

        .. versionadded:: 0.2.0
        """
        return "curvature"

    @property
    def maximum_curvature(self) -> float:
        """maximum positive or negative allowed curvature"""
        return self._maximum_curvature

    @property
    def minimum_curvature(self) -> float:
        """minimum positive or negative allowed curvature"""
        return self._minimum_curvature

    @property
    def strain_position(self) -> StrainPosition:
        """position_value of the given strain_value"""
        return self._strain_position

    def initialize_boundary_curvatures(self):
        log.debug("Start computing boundary values")
        for index, curvature_value in enumerate(
            [self.minimum_curvature, self.maximum_curvature]
        ):
            self._iteration = index
            self._curvature = curvature_value
            self._neutral_axis = self._compute_neutral_axis()
            log.debug(
                f"Compute {curvature_value=}, "
                f"neutral-axis: {self._neutral_axis},\n"
                f"\t{self.strain_position}"
            )
            self.compute()
        log.debug("Finished computing boundary values")

    def _compute_new_curvature(self):
        if self.neutral_axis is None:
            log.warning(
                f"neutral-axis: {self.neutral_axis}\n"
                f"position: {self.strain_position.position}, "
                f"curvature: {self.curvature}, "
                f"strain: {self.strain_position.strain}"
                f"{self._print_iterations()}"
            )
        return curvature(
            neutral_axis_value=self.neutral_axis,
            position_value=self.strain_position.position,
            strain_at_position=self.strain_position.strain,
        )

    def _compute_neutral_axis(self):
        return neutral_axis(
            strain_at_position=self.strain_position.strain,
            curvature_value=self.curvature,
            position_value=self.strain_position.position,
        )

    def _determine_maximum_curvature(self, for_positive_curvature: bool) -> float:
        """
        gets the theoretically maximum curvature of the ``cross_section``
        considering the input ``strain_position``

        Parameters
        ----------
        for_positive_curvature : bool
            decide if curvature is to be computed for positive (``True``) or negative (``False``)
            curvatue

        Returns
        -------
        float
            theoretically maximum curvature of the ``cross_section``
            considering the input ``strain_position``
        """
        boundary = self.cross_section.get_boundary_conditions()
        if for_positive_curvature:
            return boundary.positive.maximum_curvature.compute(self.strain_position)
        else:
            return boundary.negative.maximum_curvature.compute(self.strain_position)

    def _determine_minimum_curvature(self, for_positive_curvature: bool) -> float:
        """
        gets the theoretically minimum curvature of the ``cross_section``
        considering the input ``strain_position``

        Parameters
        ----------
        for_positive_curvature : bool
            decide if curvature is to be computed for positive (``True``) or negative (``False``)
            curvatue

        Returns
        -------
        float
            theoretically maximum curvature of the ``cross_section``
            considering the input ``strain_position``
        """
        boundary = self.cross_section.get_boundary_conditions()
        if for_positive_curvature:
            return boundary.positive.minimum_curvature.compute(self.strain_position)
        else:
            return boundary.negative.minimum_curvature.compute(self.strain_position)


class MKappaByConstantCurvature(MKappa):

    """
    computation of one Moment-Curvature-Point by fixed curvature and
    varying the neutral axis

    .. versionadded:: 0.1.0
    """

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
        "_not_successful_reason",
        "_computed_cross_section",
        "_iteration",
        "_is_called_by_user",
    )

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        applied_curvature: float,
        applied_axial_force: float,
        maximum_neutral_axis: float = None,
        minimum_neutral_axis: float = None,
        maximum_iterations=10,
        axial_force_tolerance=5,
        solver=Newton,
        is_called_by_user: bool = True,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            cross-section to compute
        applied_axial_force : float
            applied axial force (Default: 0.0)
        maximum_neutral_axis : float
            maximum possible vertical position of the neutral-axis (Default: None)
        minimum_neutral_axis : float
            minimum possible vertical position of the neutral-axis (Default: None)
        maximum_iterations : int
            maximum allowed iterations (Default: 10)
            In case the given number of iterations before axial force within desired tolerance,
            the computation is classified as not successful and will be stopped
        axial_force_tolerance : float
            if axial force within this tolerance the computation is terminated and
            classified as successful (Default: 5.0)
        solver : :py:class:`~m_n_kappa.solver.Solver`
            used solver (Default: :py:class:`~m_n_kappa.solver.Newton`)

        See Also
        --------
        MKappaByStrainPosition : compute curvature and neutral axis by a given :py:class:`~m_n_kappa.StrainPosition`

        Examples
        --------
        The ``cross_section`` of type :py:class:`~m_n_kappa.Crosssection` that is defined in the following
        will be used to demonstrate the functionality of :py:class:`~m_n_kappa.MKappaByConstantCurvature`.
        For reproducibility ``cross_section`` consist of one rectangular steel section.

        >>> from m_n_kappa import Rectangle, Steel, Crosssection
        >>> geometry = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        >>> steel = Steel(f_y=355, failure_strain=0.15)
        >>> section = geometry + steel
        >>> cross_section = Crosssection(sections=[section])

        :py:class:`~m_n_kappa.MKappaByConstantCurvature` only by passing ``cross_section``
        an ``applied_curvature`` and an ``applied_axial_force``.
        Initializing :py:class:`~m_n_kappa.MKappaByConstantCurvature` starts an iterative process to
        compute equilibrium of ``applied_axial_force`` and the ``axial_force``.
         ``axial_force`` results from the strain-distribution applied by ``applied_curvature`` and
         a neutral-axis value.

        >>> from m_n_kappa import MKappaByConstantCurvature
        >>> computation = MKappaByConstantCurvature(
        ...     cross_section=cross_section,
        ...     applied_curvature=0.001,
        ...     applied_axial_force=100.)

        In case the computation was successful the attribute
        :py:attr:`~m_n_kappa.MKappaByConstantCurvature.successful` will return ``True``.

        >>> computation.successful
        True

        :py:attr:`~m_n_kappa.MKappaByConstantCurvature.neutral_axis` is the computed neutral-axis.

        >>> computation.neutral_axis

        In case the ``applied_axial_force`` is higher than maximum positive or negative
        axial force of the ``cross_section`` the computation will be marked by
        :py:attr:`~m_n_kappa.MKappaByConstantCurvature.successful` = ``False``.

        >>> computation = MKappaByConstantCurvature(
        ...     cross_section=cross_section,
        ...     applied_curvature=0.001,
        ...     applied_axial_force=36000.)
        >>> computation.successful
        False

        The :py:attr:`~m_n_kappa.MKappaByConstantCurvature.not_successful_reason` will than give you
        a reason why it was not working.

        >>> computation.not_successful_reason
        difference of axial forces at minimum and maximum neutral-axis have same sign

        In this case you should choose a smaller value for the ``applied_axial_force``.
        """
        super().__init__(
            cross_section,
            applied_axial_force,
            maximum_iterations,
            axial_force_tolerance,
            solver,
        )
        self._applied_curvature = applied_curvature
        if maximum_neutral_axis is None or minimum_neutral_axis is None:
            (
                self._maximum_neutral_axis,
                self._minimum_neutral_axis,
            ) = self._get_neutral_axes_boundary_values()
        else:
            self._maximum_neutral_axis = maximum_neutral_axis
            self._minimum_neutral_axis = minimum_neutral_axis
        self._is_called_by_user = is_called_by_user
        self.initialize()

    def __repr__(self):
        return (
            f"MKappaByConstantCurvature("
            f"\n\tcross_section=cross_section, "
            f"\n\tapplied_curvature={self.applied_curvature}, "
            f"\n\tmaximum_neutral_axis={self.maximum_neutral_axis}, "
            f"\n\tminimum_neutral_axis={self.minimum_neutral_axis}, "
            f"\n\tapplied_axial_force={self.applied_axial_force}, "
            f"\n\tmaximum_iterations={self.maximum_iterations}, "
            f"\n\taxial_force_tolerance={self.axial_force_tolerance}, "
            f"\n\tsolver={self.solver})"
        )

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

    @property
    def variable(self):
        """
        name variable that is changed to reach equilibrium of axial force

        .. versionadded:: 0.2.0
        """
        return "neutral-axis"

    def initialize_boundary_curvatures(self) -> None:
        """
        initialize iteration process by computing the cross-section
        with boundary values of the neutral-axis (see attributes
        'minimum_neutral_axis' and 'maximum_neutral_axis')
        """
        for index, neutral_axis_value in enumerate(
            [self.minimum_neutral_axis, self.maximum_neutral_axis]
        ):
            self._iteration = index
            self._curvature = self.applied_curvature
            self._neutral_axis = neutral_axis_value
            self.compute()

    def _get_neutral_axes_boundary_values(self) -> tuple[float, float]:
        """
        Compute the boundary values of the neutral axis

        .. versionadded:: 0.2.0

        Returns
        -------
        tuple[float, float]
            maximum and minimum possible neutral axis for the given ``cross_section`` under the given
            curvature
        """
        boundaries = self.cross_section.get_boundary_conditions()
        neutral_axes = boundaries.neutral_axes.compute(self.applied_curvature)
        return max(neutral_axes), min(neutral_axes)

    def _compute_new_curvature(self) -> float:
        """
        Curvature is kept the same (=``applied_curvature``) during iteration.
        Equilibrium is found by changing the value of the neutral-axis.
        """
        return self.applied_curvature
