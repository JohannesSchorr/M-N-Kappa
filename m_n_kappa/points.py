"""
points.py

Aim
===
provide classes to compute the equilibrium of axial forces

Overview
========
Point: base-class for computing equilibrium of axial-forces
MKappa: base class for computation of one Moment-Curvature-Point by varying the neutral axis
   (inherits from Point)
MKappaByStrainPosition: computation of one Moment-Curvature-Point by fixed stress-strain_value-point and
    varying the neutral axis (inherits from MKappa)
MKappaByConstantCurvature: computation of one Moment-Curvature-Point by fixed curvature and
   varying the neutral axis (inherits from MKappa)
MNByStrain : computation of uniform strain leading to given axial-force
   (inherits from Point)
"""

import operator
from dataclasses import dataclass

from .general import (
    print_sections,
    print_chapter,
    str_start_end,
    curvature,
    neutral_axis,
    StrainPosition,
    NotSuccessfulReason,
    strain,
)
from .crosssection import (
    Crosssection,
    ComputationCrosssectionCurvature,
    ComputationCrosssectionStrain,
)
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
    axial_force_equilibrium : float
        equilibrium of axial-forces
    curvature: float
        computed curvature (Default: ``None``)
    neutral_axis_value: float
        computed neutral axis (Default: ``None``)
    axial_force: float
        computed axial-force (Default: ``None``)
    strain : float
        computed strain (Default: ``None``)
    """

    iteration: int
    computed_cross_section: Crosssection
    axial_force_equilibrium: float
    curvature: float = None
    neutral_axis_value: float = None
    axial_force: float = None
    strain: float = None

    def __post_init__(self):
        log.info(f"Created {self.__repr__()}")


class Point:
    """
    base-class for computing equilibrium of axial-forces

    .. versionadded:: 0.2.0
    """

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        applied_axial_force: float,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: Solver = Newton,
        is_called_by_user: bool = True,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
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
        is_called_by_user : bool
            indicates if the class is initialized by a user (``True``, Default) or by another class (``False``)
        """
        self._cross_section = cross_section
        self._applied_axial_force = applied_axial_force
        self._maximum_iterations = maximum_iterations
        self._axial_force_tolerance = axial_force_tolerance
        self._solver = solver
        self._is_called_by_user = is_called_by_user
        self._computations: list[Computation] = []
        self._iteration = 0
        self._axial_force = None
        self._successful = False
        self._not_successful_reason = None
        self._computed_cross_section = None

    @property
    def applied_axial_force(self) -> float:
        """axial-force the strain is to be computed"""
        return self._applied_axial_force

    @property
    def axial_force(self) -> float:
        """latest computed axial-force-value"""
        return self._computed_cross_section.total_axial_force()

    @property
    def axial_force_tolerance(self) -> float:
        """
        tolerance the :py:meth:`~m_n_kappa.points.MNByStrain.axial_force_equilibrium`
        must be within for a successful computation
        """
        return self._axial_force_tolerance

    @property
    def computations(self) -> list[Computation]:
        """conducted computations"""
        return self._computations

    @property
    def computed_cross_section(self) -> ComputationCrosssectionStrain | ComputationCrosssectionCurvature:
        """computed cross_section of the current iteration"""
        return self._computed_cross_section

    @property
    def cross_section(self) -> Crosssection:
        """cross-section to be computed"""
        return self._cross_section

    @property
    def iteration(self) -> int:
        """number of iteration"""
        return self._iteration

    @property
    def maximum_iterations(self) -> int:
        """maximum iterations"""
        return self._maximum_iterations

    @property
    def moment(self) -> float:
        """computed moment of the cross_section"""
        return self._computed_cross_section.total_moment()

    @property
    def not_successful_reason(self) -> NotSuccessfulReason:
        """In case computation was not successful gives a reason"""
        return self._not_successful_reason

    @property
    def solver(self) -> Solver:
        """used solver to computed equilibrium"""
        return self._solver

    @property
    def successful(self) -> bool:
        """indicates if strain has been computed successfully"""
        return self._successful

    @property
    def variable(self):
        """
        name variable that is changed to reach equilibrium of axial force
        """
        return ""

    def axial_force_equilibrium(self) -> float:
        """latest computed axial-force-value"""
        return self._axial_force - self.applied_axial_force

    def _is_axial_force_equilibrium_within_tolerance(self) -> bool:
        """check if equilibrium of axial forces is within tolerance"""
        if abs(self.axial_force_equilibrium()) < self.axial_force_tolerance:
            return True
        else:
            return False

    def _initial_axial_forces_have_different_sign(self) -> bool:
        """
        check if the axial forces of the initial axial-forces
        have different signs
        """
        if (
            self.computations[0].axial_force_equilibrium
            * self.computations[1].axial_force_equilibrium
            < 0.0
        ):
            return True
        else:
            return False

    def _iterate(self) -> None:
        """iteration process"""
        pass

    def _iteration_range(self) -> range:
        """range the iteration shall take place into"""
        return range(self.iteration + 1, self.maximum_iterations + 1, 1)

    def _message(self) -> None:
        """logging message depending on if the class is called by user or by another class"""
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

    def _set_values_none(self) -> None:
        """set all important value to ``None``"""
        pass

    def _sort_computations_by(self, attribute: str) -> None:
        """sorts attribute ``computations`` by given attribute-key"""
        self._computations.sort(key=operator.attrgetter(attribute))

    def _start_computation(self) -> None:
        """
        start the iteration-process in case the equilibrium of
        axial-forces has not been reached already
        """
        if not self._successful:
            if self._initial_axial_forces_have_different_sign():
                self._iterate()
            else:
                self._not_successful_reason = NotSuccessfulReason(
                    variable=self.variable
                )
                self._message()
                self._set_values_none()

    def _target_value_is_improved(self) -> bool:
        """check if latest computation decreased the difference of axial-forces"""
        self._sort_computations_by("iteration")
        if operator.truth(self._computations):
            if (
                abs(
                    self._computations[-1].axial_force_equilibrium
                    - self._computations[-2].axial_force_equilibrium
                )
                < 1.0
            ):
                return False
        return True

    def _use_fallback(self) -> bool:
        """use fallback in case the target-value has not been improved"""
        if self._target_value_is_improved():
            return False
        else:
            log.info("Axial force equilibrium not improved: use fallback")
            return True

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
        """print the title (see __str__())"""
        class_name = self.__class__.__name__
        return print_sections([class_name, len(class_name) * "="])

    def _print_initialization(self):
        """print the initialization (see __str__()), i.e. the __repr__()"""
        return print_sections(["Initialization", "--------------", self.__repr__()])

    def _print_iterations(self) -> str:
        """print the iterations in tabular form"""
        pass

    def _print_results(self) -> str:
        """print the result of the computation"""
        pass


class MKappa(Point):

    """
    base class for computation of one Moment-Curvature-Point by varying the neutral axis

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
        is_called_by_user: bool = True,
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
        super().__init__(
            cross_section=cross_section,
            applied_axial_force=applied_axial_force,
            axial_force_tolerance=axial_force_tolerance,
            maximum_iterations=maximum_iterations,
            solver=solver,
            is_called_by_user=is_called_by_user,
        )
        self._curvature = None
        self._neutral_axis = None
        self._computed_cross_section = None
        self._axial_force = None

    def __repr__(self):
        return (
            f"MKappa(cross_section=CrossSection, "
            f"applied_axial_force={self.applied_axial_force}, "
            f"maximum_iterations={self.maximum_iterations})"
        )

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
        self._sort_computations_by("iteration")
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
    def curvature(self) -> float:
        """curvature"""
        return self._curvature

    @property
    def neutral_axis(self) -> float:
        """point where strain_value is zero"""
        return self._neutral_axis

    def compute(self) -> None:
        """
        compute the cross-section with given initial values (curvature and neutral axis)
        and save it
        """
        self._computed_cross_section = self._get_compute_cross_section()
        self._axial_force = self.computed_cross_section.total_axial_force()
        self.__save()
        if self._is_axial_force_equilibrium_within_tolerance():
            self._successful = True

    def initialize_boundary_curvatures(self):
        pass

    def _iterate(self) -> None:
        """
        iterate as long as one of the following criteria are reached:
        - number of maximum iterations
        - absolute axial force smaller than desired one
        """
        for iter_index in self._iteration_range():
            self._iteration = iter_index
            self._neutral_axis = self._guess_neutral_axis()
            if self.neutral_axis is None:
                self._not_successful_reason = NotSuccessfulReason("converge")
                log.info(self.not_successful_reason)
                return
            self._curvature = self._compute_new_curvature()
            self.compute()
            if self._successful:
                return
        self._not_successful_reason = NotSuccessfulReason("iteration")
        log.info(self.not_successful_reason.reason)

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
        self._sort_computations_by("axial_force")
        temp_computations = [
            {
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
        return solver.compute(self._use_fallback())

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

    def _set_values_none(self) -> None:
        self._axial_force = None
        self._curvature = None
        self._moment = None
        self._neutral_axis = None


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
        "_positive_curvature",
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
        self._positive_curvature = positive_curvature
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
        if self._is_strain_not_outside_boundary():
            self.initialize_boundary_curvatures()
            self._start_computation()

    def _is_strain_not_outside_boundary(self) -> bool:
        """
        checks if the given ``strain`` in ``strain_position`` is outside boundary
        and would lead in combination with curvature to exceed of the maximum
        positive or negative strain within the decisive material model
        """
        if self.maximum_curvature == 0.0:
            self._not_successful_reason = NotSuccessfulReason(
                reason="strain is outside boundary and allows therefore no curvature",
                strain_position=self.strain_position,
            )
            log.info(self._not_successful_reason.reason)
            return False
        else:
            return True

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
    def positive_curvature(self) -> bool:
        """``True`` indicates a positive curvature"""
        return self._positive_curvature

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
        maximum_iterations=20,
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
        self.initialize_boundary_curvatures()
        self._start_computation()

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
            if not self._successful:
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


class MNByStrain(Point):

    """
    computation of uniform strain leading to given axial-force

    .. versionadded:: 0.2.0
    """

    __slots__ = (
        "_cross_section",
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
        applied_axial_force: float,
        maximum_iterations: int = 20,
        axial_force_tolerance: float = 5.0,
        solver: Solver = Newton,
        is_called_by_user: bool = True,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
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
        is_called_by_user : bool
            indicates if the class is initialized by a user (``True``, Default) or by another class (``False``)

        See Also
        --------
        MKappaByStrainPosition :  computation of one Moment-Curvature-Point by fixed stress-strain_value-point and
           varying the neutral axis
        MKappaByConstantCurvature : computation of one Moment-Curvature-Point by fixed curvature and
           varying the neutral axis

        Examples
        --------
        :py:class:`~m_n_kappa.MNByStrain` takes a :py:class:`~m_n_kappa.Crosssection` and an
        ``applied_axial_force`` as argument.
        The :py:class:`~m_n_kappa.Crosssection` may be a rectangular steel profile for example.

        >>> from m_n_kappa import Steel, Rectangle, Crosssection
        >>> steel = Steel(f_y=100, failure_strain=0.15)
        >>> rectangle = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        >>> section = steel + rectangle
        >>> cross_section = Crosssection([section])

        As indicated :py:class:`~m_n_kappa.MNByStrain` is then easily envoked by passing ``cross_section``
        and an axial force as argument.

        >>> from m_n_kappa.points import MNByStrain
        >>> m_n = MNByStrain(cross_section=cross_section, applied_axial_force=100)

        :py:attr:`~m_n_kappa.MNByStrain.strain` returns then the strain corresponding to the ``applied_axial_force``.

        >>> round(m_n.strain, 5)
        0.04762

        In case the applied axial force exceeds the maximum axial-force of the section a ``None``-value is
        returned.

        >>> m_n_none = MNByStrain(cross_section=cross_section, applied_axial_force=rectangle.area * 100 + 10)
        >>> m_n_none.strain
        None

        """
        super().__init__(
            cross_section=cross_section,
            applied_axial_force=applied_axial_force,
            axial_force_tolerance=axial_force_tolerance,
            maximum_iterations=maximum_iterations,
            solver=solver,
            is_called_by_user=is_called_by_user,
        )
        self._initialize_boundary_strains()
        self._start_computation()

    @property
    def strain(self) -> float:
        """currently computed strain-value"""
        return self._strain

    @property
    def variable(self) -> str:
        """name variable that is changed to reach equilibrium of axial force"""
        return "strain"

    def _compute(self) -> None:
        """compute the cross-section under :py:attr:`~m_n_kappa.points.MNByStrain.strain`"""
        self._computed_cross_section = ComputationCrosssectionStrain(
            sections=self.cross_section, strain=self.strain
        )
        self._axial_force = self._computed_cross_section.total_axial_force()
        self._save()
        if self._is_axial_force_equilibrium_within_tolerance():
            self._successful = True

    def _initialize_boundary_strains(self) -> None:
        """initialize computation of the maximum positive and negative strains"""
        for iteration, strain in enumerate(
            [
                self.cross_section.decisive_maximum_negative_strain_position(),
                self.cross_section.decisive_maximum_positive_strain_position(),
            ]
        ):
            if not self.successful:
                self._iteration = iteration
                self._strain = strain.strain
                self._compute()

    def _iterate(self) -> None:
        """
        iterate as long as one of the following criteria are reached:
        - number of maximum iterations
        - absolute axial force smaller than desired one
        """
        for iter_index in self._iteration_range():
            self._iteration = iter_index
            self._strain = self._guess_strain()
            if self._strain is None:
                self._not_successful_reason = NotSuccessfulReason("converge")
                log.info(self.not_successful_reason.reason)
                return
            self._compute()
            if self._successful:
                return
        self._not_successful_reason = NotSuccessfulReason("iteration")
        log.info(
            f"Maximum number of iterations ({self.maximum_iterations}) reached, "
            f"without finding equilibrium of axial forces"
        )

    def _guess_strain(self) -> float:
        """use ``solver`` to guess a new strain value"""
        self._sort_computations_by("axial_force")
        temp_computations = [
            {
                "axial_force_equilibrium": computation.axial_force_equilibrium,
                "strain": computation.strain,
            }
            for computation in self._computations
        ]
        solver = self.solver(
            data=temp_computations,
            target="axial_force_equilibrium",
            variable="strain",
        )
        return solver.compute(self._use_fallback())

    def _save(self) -> None:
        """saves the latest computation"""
        self._computations.append(
            Computation(
                iteration=self.iteration,
                computed_cross_section=self._computed_cross_section,
                axial_force_equilibrium=self.axial_force_equilibrium(),
                axial_force=self.axial_force,
                strain=self.strain,
            )
        )

    def _set_values_none(self) -> None:
        """set the computed values to ``None``"""
        self._strain = None
        self._axial_force = None

    def _print_results(self) -> str:
        """print the results"""
        if self.successful:
            text = [
                "Results",
                "-------",
                "\t" + f"N = {self.axial_force:.2f}",
                "\t" + f"M = {self.moment:.2f}",
                "\t" + f"strain = {self.strain:.5f}",
            ]
            return print_sections(text)
        else:
            return ""

    def _print_iterations(self) -> str:
        """print the iterations and its results in tabular form"""
        text = [
            "Iterations",
            "----------",
            f"number: {len(self.computations)}",
            "",
            "-------------------------------------------------------------",
            "iter |  strain  | neutral-axis |  axial-force  | equilibrium ",
            "-------------------------------------------------------------",
        ]
        self._sort_computations_by("iteration")
        for computation in self.computations:
            if computation.neutral_axis_value is None:
                neutral_axis_value = "  Infinite  "
            else:
                neutral_axis_value = f"{computation.neutral_axis_value:8.4f}"
            text.append(
                f"{computation.iteration:4} | "
                f"{computation.strain:8.4f} | "
                f"{neutral_axis_value} | "
                f"{computation.axial_force:13.2f} | "
                f"{computation.axial_force_equilibrium:11.2f}"
            )
        text.append("-------------------------------------------------------------")
        return print_sections(text)


class AxialForcePoint:

    """
    base class

    .. versionadded:: 0.2.0
    """

    @log.init
    def __init__(
        self,
        sub_cross_sections: tuple[Crosssection, Crosssection] | list[Crosssection],
        axial_force: float,
    ):
        """
        Parameters
        ----------
        sub_cross_sections list[:py:class:`~m_n_kappa.Crosssection`] |
        tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            cross-sections that are computed (must be two)
        axial_force : float
            axial-force applied to the first cross-section given in ``sub_cross_sections``

        Raises
        ------
        ValueError : if not two sub-cross-sections are given in ``sub_cross_sections``
        """
        if isinstance(sub_cross_sections, list) or isinstance(
            sub_cross_sections, tuple
        ):
            if len(sub_cross_sections) == 2:
                self._sub_cross_sections = tuple(sub_cross_sections)
            else:
                ValueError(
                    f"Exactly two sub-cross-sections must be given. Given are {len(sub_cross_sections)}"
                )
        else:
            TypeError(
                f"cross_sections must be of type list[Crosssection] or tuple[Crosssection, Crosssection]"
            )
        self._axial_force = axial_force
        self._computed_sub_cross_sections = []
        self._curvature = None
        self._strain_difference = None
        self._moment = None
        self._successful = True
        self._not_successful_reason = None

    @property
    def axial_force(self) -> float:
        """axial-force applied to first cross-section"""
        return self._axial_force

    @property
    def computed_sub_cross_sections(
        self,
    ) -> tuple[
        ComputationCrosssectionCurvature, ComputationCrosssectionCurvature
    ] | tuple[ComputationCrosssectionStrain, ComputationCrosssectionStrain]:
        """computed sub-cross-sections"""
        return self._computed_sub_cross_sections

    @property
    def curvature(self) -> float:
        """curvature"""
        return 0.0

    @property
    def strain_difference(self) -> float:
        """difference between the computed sub-cross-sections"""
        return self._strain_difference

    @property
    def successful(self) -> bool:
        """computed successfully"""
        return self._successful

    @property
    def not_successful_reason(self) -> NotSuccessfulReason:
        """if computation was not successful,here the reasons are given"""
        return self._not_successful_reason

    @property
    def sub_cross_sections(self) -> tuple[Crosssection, Crosssection]:
        """cross-sections that are computed"""
        return self._sub_cross_sections

    def moment(self) -> float:
        """computed moment, ``None`` in case not ``successful``"""
        return self._moment

    def _compute_moment(self) -> float:
        """computes the sum of the moments of the sub-cross-sections"""
        if self.successful:
            return sum(
                [
                    sub_cross_section.total_moment()
                    for sub_cross_section in self._computed_sub_cross_sections
                ]
            )


class MomentAxialForce(AxialForcePoint):
    """
    compute moment and axial-force at zero curvature

    .. versionadded:: 0.2.0
    """

    @log.init
    def __init__(
        self,
        sub_cross_sections: list[Crosssection] | tuple[Crosssection, Crosssection],
        strain: float = None,
        axial_force: float = None,
    ):
        """
        Parameters
        ----------
        sub_cross_sections : list[:py:class:`~m_n_kappa.Crosssection`] |
        tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            cross-sections that are computed (must be two)
        strain : float
            applied strain to the first cross-section given in ``cross_sections``
        axial_force : float
            axial-force applied to the first cross-section given in ``sub_cross_sections``

        Raises
        ------
        ValueError: If not exactly two cross-sections are given in ``cross_sections``
        ValueError: If neither ``strain`` nor ``axial_force`` are given

        See Also
        --------
        MomentAxialForceCurvature : Computes moment and curvature under given axial-force and a
           :py:class:`~m_n_kappa.StrainPosition` point for a cross-section consisting of two sub-
           cross-sections

        Examples
        --------
        To compute the moment-axial-force you need two (sub)-cross-sections.
        In the following these are two identical steel rectangles.

        >>> from m_n_kappa import Steel, Rectangle
        >>> steel = Steel()
        >>> rectangle_top = Rectangle(top_edge=0.0, bottom_edge=10.0, width=10.0)
        >>> section_top = steel + rectangle_top
        >>> cross_section_top = Crosssection([section_top])
        >>> rectangle_bottom= Rectangle(top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> section_bottom= steel + rectangle_bottom
        >>> cross_section_bottom = Crosssection([section_top])
        >>> cross_sections = [cross_section_top, cross_section_bottom]

        By initializing :py:class:`~m_n_kappa.MomentAxialForce` the moment-
        axial-force point is computed under the given strain applied uniformly
        to the first cross-section.

        >>> from m_n_kappa import MomentAxialForce
        >>> m_n = MomentAxialForce(cross_sections, 0.0001)

        The axial-force is easily accessed by :py:attr:`~m_n_kappa.MomentAxialForce.axial_force`.

        >>> m_n.axial_force
        2100

        And the computed moment by is :py:attr:`~m_n_kappa.MomentAxialForce.moment`.

        >>> m_n.moment
        21000

        The strain-difference between both cross-sections is computed by
        :py:attr:`~m_n_kappa.MomentAxialForce.strain_difference`.

        >>> m_n.strain_difference
        0.0002
        """
        super().__init__(sub_cross_sections, axial_force)
        if strain is not None:
            self._strain = strain
            self._axial_force = self._compute_axial_force()
        elif axial_force is not None:
            self._axial_force = axial_force
        else:
            raise ValueError("Either 'strain' or 'axial_force' must be passed.")
        self._computed_sub_cross_sections: tuple[
            ComputationCrosssectionStrain, ComputationCrosssectionStrain
        ] = self._compute_sub_cross_sections()
        if self.successful:
            self._moment = self._compute_moment()
            self._strain_difference = self._compute_strain_difference()

    @property
    def strain(self) -> float:
        """applied strain to the first cross-section"""
        return self._strain

    def _compute_sub_cross_sections(
        self,
    ) -> tuple[ComputationCrosssectionStrain, ComputationCrosssectionStrain] | None:
        """computes the sub-cross-sections under the given axial-forces"""
        computations = [None, None]
        for index, sub_cross_section in enumerate(self.sub_cross_sections):
            m_n = MNByStrain(
                cross_section=sub_cross_section,
                applied_axial_force=self.axial_force * (-1.0) ** (float(index)),
                is_called_by_user=False,
            )
            computations[index] = m_n.computed_cross_section
            if not m_n.successful:
                self._successful = False
                not_successful_reason = m_n.not_successful_reason
                log.info(f"Cross-section {index}: {not_successful_reason}")
                self._not_successful_reason = not_successful_reason
                return
        return tuple(computations)

    def _compute_axial_force(self) -> float:
        """computes the axial-force of the first sub-cross-section under the given strain"""
        return ComputationCrosssectionStrain(
            sections=self.sub_cross_sections[0],
            strain=self.strain,
        ).total_axial_force()

    def _compute_strain_difference(self) -> float:
        """compute the difference of strain between the computed sub-cross-sections"""
        return (
            self.computed_sub_cross_sections[0].strain
            - self.computed_sub_cross_sections[1].strain
        )


class MomentAxialForceCurvature(AxialForcePoint):
    """
    compute a moment-axial-force-curvature point with moment-axial-force and
    strain-position-point

    .. versionadded:: 0.2.0
    """

    @log.init
    def __init__(
        self,
        sub_cross_sections: list[Crosssection] | tuple[Crosssection, Crosssection],
        axial_force: float,
        strain_position: StrainPosition,
        positive_curvature: bool = True,
    ):
        """
        Parameters
        ----------
        sub_cross_sections : list[:py:class:`~m_n_kappa.Crosssection`] |
        tuple[:py:class:`~m_n_kappa.Crosssection`, :py:class:`~m_n_kappa.Crosssection`]
            sub-cross-sections the overall cross-section consists of
        axial_force : float
            Axial-force that is applied in sign and magnitude to the first given cross-section.
            On the second cross-section it is applied with switches sign.
        strain_position : :py:class:`~m_n_kappa.StrainPosition`
            strain- and its position, that is to be considered by determining the curvature in the first
            cross-section
        positive_curvature : bool
            ``True`` indicates positive curvature and leads to considering a positive curvature

        Raises
        ------
        ValueError: If not exactly two cross-sections are given in ``cross_sections``
        ValueError: If neither ``strain`` nor ``axial_force`` are given

        See Also
        --------
        MomentAxialForce : computes moment and axial-force in case curvature is zero for a
           cross-section consisting of two sub-cross-sections.

        Examples
        --------


        """
        super().__init__(sub_cross_sections, axial_force)
        self._strain_position = strain_position
        self._positive_curvature = positive_curvature
        self._computed_sub_cross_sections: tuple[
            ComputationCrosssectionCurvature, ComputationCrosssectionCurvature
        ] = self._compute_sub_cross_sections()
        self._curvature = self._get_curvature()
        self._moment = self._compute_moment()
        self._strain_difference = self._compute_strain_difference()

    def __repr__(self) -> str:
        return f'MomentAxialForceCurvature(' \
        f'\n\tsub_cross_sections=..., ' \
        f'\n\taxial_force={self.axial_force}, ' \
        f'\n\tstrain_position={self.strain_position}, ' \
        f'\n\tpositive_curvature={self.positive_curvature})'

    @property
    def curvature(self) -> float:
        """computed curvature"""
        return self._curvature

    @property
    def positive_curvature(self) -> bool:
        """indicate the sign of the searched curvature"""
        return self._positive_curvature

    @property
    def strain_position(self) -> StrainPosition:
        """strain-position-value that must be met by the first cross-section"""
        return self._strain_position

    def _compute_sub_cross_sections(
        self,
    ) -> tuple[ComputationCrosssectionCurvature, ComputationCrosssectionCurvature]:
        """
        compute the sub-cross-sections

        In the 1st sub_cross-section ``curvature`` and ``neutral_axis`` are determined by the given
        ``strain_position`` and the given ``axial-force.
        In the 2nd sub-cross-section the ``neutral_axis`` is determined by the computed ``curvature``
        and the ``axial_force``.

        Returns
        -------
        tuple[ComputationCrosssectionCurvature, ComputationCrosssectionCurvature]

        """
        first_sub_cross_section = MKappaByStrainPosition(
            cross_section=self.sub_cross_sections[0],
            strain_position=self.strain_position,
            applied_axial_force=self.axial_force,
            positive_curvature=self.positive_curvature,
            is_called_by_user=False,
        )
        if not first_sub_cross_section.successful:
            self._not_successful_reason = first_sub_cross_section.not_successful_reason
            self._successful = False
            return None, None

        computed_curvature = first_sub_cross_section.curvature
        second_sub_cross_section = MKappaByConstantCurvature(
            cross_section=self.sub_cross_sections[1],
            applied_curvature=computed_curvature,
            applied_axial_force=self.axial_force * (-1),
        )
        if not second_sub_cross_section.successful:
            self._not_successful_reason = second_sub_cross_section.not_successful_reason
            self._successful = False
            return None, None

        self._successful = True
        return (
            first_sub_cross_section.computed_cross_section,
            second_sub_cross_section.computed_cross_section,
        )

    @log.result
    def _compute_strain_difference(self) -> float:
        """compute the strain-difference betweeen the ``sub_cross_sections``"""
        if self.successful:
            strain_sub_cross_section_1 = strain(
                neutral_axis_value=self.computed_sub_cross_sections[0].neutral_axis,
                curvature_value=self.curvature,
                position_value=0.0,
            )
            strain_sub_cross_section_2 = strain(
                neutral_axis_value=self.computed_sub_cross_sections[1].neutral_axis,
                curvature_value=self.curvature,
                position_value=0.0,
            )
            return strain_sub_cross_section_1 - strain_sub_cross_section_2

    @log.result
    def _get_curvature(self) -> float:
        """get the curvature from the computed cross-sections"""
        if self.successful:
            return self.computed_sub_cross_sections[0].curvature
