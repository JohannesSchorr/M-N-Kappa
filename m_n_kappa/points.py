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

import logging
import logging.config
import yaml
import pathlib

with open(pathlib.Path(__file__).parent.absolute() / "logging-config.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


@dataclass
class Computation:
    """
    stores the results of an iteration-step during a computation

    Parameters
    ----------
    iteration: int
        iteration-number
    computed_cross_section: :py:class:`~m_n_kappa.crosssection.Crosssection`
        computed cross-section that inherits from `~m_n_kappa.crosssection.Crosssection`
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

    def __post_init__(self):
        logger.info(f"Created {self.__repr__()}")


class MKappa:

    """
    computation of one Moment-Curvature-Point by fixation of
    one point and varying the neutral axis

    works as base-class for :py:class:`MKappaByStrainPosition` and
    :py:class:`MKappaByConstantCurvature`
    """

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
        cross_section : cross_section.Crossection
            cross-section to compute
        applied_axial_force : float
                applied axial force (Default: 0.0)
        maximum_iterations : int
                maximum allowed iterations (Default: 10).
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
        self._computations: list[Computation] = []
        self._solver = solver
        self._successful = False
        self._iteration = 0
        self._curvature = None
        self._neutral_axis = None
        self._computed_cross_section = None
        self._axial_force = None
        if not issubclass(type(self), MKappa):
            if logger.level == logging.DEBUG:
                logger.debug(f'{self.__str__()}')
            else:
                logger.info(f'Created {self.__repr__()}')

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
            "---------------------------------------------",
            "iter | curvature | neutral-axis | axial-force",
            "---------------------------------------------",
        ]
        self.__sort_computations_by_iteration()
        for computation in self.computations:
            text.append(
                "{:4} | {:9.6f} | {:12.2f} | {:10.2f}".format(
                    computation.iteration,
                    computation.curvature,
                    computation.neutral_axis_value,
                    computation.axial_force,
                )
            )
        text.append("---------------------------------------------")
        return print_sections(text)

    def _print_results(self) -> str:
        text = [
            "Results",
            "-------",
            "\t" + "N = {:.2f}".format(self.axial_force),
            "\t" + "M = {:.2f}".format(self.moment),
            "\t" + "Kappa = {:.5f}".format(self.curvature),
        ]
        return print_sections(text)

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
    def successful(self) -> bool:
        """
        True:  equilibrium has been found,
        False: equilibrium has not (yet) been found
        """
        return self._successful

    def compute(self):
        """
        compute the cross-section with given initial values (curvature and neutral axis)
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
        elif self._initial_axial_forces_have_different_sign():
            self.iterate()
        else:
            print("Axial-forces computed with minimum and maximum curvature have same sign.\n"
                  "Therefore, no equilibrium of Axial-forces possible. --> break")
            self.__set_values_none()

    def _initial_axial_forces_have_different_sign(self):
        if self.computations[0].axial_force * self.computations[1].axial_force < 0.0:
            return True
        else:
            return False

    def initialize_boundary_curvatures(self):
        pass

    def iterate(self):
        """
        iterate as long as one of the following criteria are reached:
        - number of maximum iterations
        - absolute axial force smaller than desired one
        """
        for iter_index in range(self.iteration + 1, self.maximum_iterations+1, 1):
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
        return ComputationCrosssectionCurvature(
            cross_section=self.cross_section,
            curvature=self.curvature,
            neutral_axis_value=self.neutral_axis,
        )

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
        self.__sort_computations_by_axial_forces()
        temp_computations = [
            {
                "axial_force": computation.axial_force,
                "neutral_axis_value": computation.neutral_axis_value,
            }
            for computation in self._computations
        ]
        solver = self.solver(
            data=temp_computations, target="axial_force", variable="neutral_axis_value"
        )
        if self._target_value_is_improved():
            use_fallback = False
        else:
            use_fallback = True
            # print('Axial force not improved: use fallback') # TODO: Logging
        return solver.compute(use_fallback)

    def __is_axial_force_within_tolerance(self):
        if abs(self._axial_force_equilibrium()) < self.axial_force_tolerance:
            return True
        else:
            return False

    def __save(self):
        self._computations.append(
            Computation(
                iteration=self.iteration,
                computed_cross_section=self.computed_cross_section,
                curvature=self.curvature,
                neutral_axis_value=self.neutral_axis,
                axial_force=self.axial_force,
            )
        )
        # print(self._computations[-1])
        # print(self.print_iterations())
        # print(self.computed_cross_section._print_results())

    def _target_value_is_improved(self) -> bool:
        self.__sort_computations_by_iteration()
        if len(self._computations) > 1:
            if abs(self._computations[-1].axial_force - self._computations[-2].axial_force) < 1.0:
                return False
        return True

    def __set_values_none(self):
        self._axial_force = None
        self._curvature = None
        self._moment = None
        self._neutral_axis = None

    def __sort_computations_by(self, key: str):
        self._computations.sort(key=lambda x: x[key])

    def __sort_computations_by_curvature(self):
        self._computations.sort(key=lambda x: x.curvature)

    def __sort_computations_by_neutral_axis(self):
        self._computations.sort(key=lambda x: x.neutral_axis_value)

    def __sort_computations_by_axial_forces(self):
        self._computations.sort(key=lambda x: x.axial_force)

    def __sort_computations_by_iteration(self):
        self._computations.sort(key=lambda x: x.iteration)


class MKappaByStrainPosition(MKappa):

    """
    computation of one Moment-Curvature-Point by fixed stress-strain_value-point and
    varying the neutral axis
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
        "_computed_cross_section",
        "_iteration",
    )

    def __init__(
        self,
        cross_section: Crosssection,
        maximum_curvature: float,
        minimum_curvature: float,
        strain_position: StrainPosition,
        applied_axial_force: float = 0.0,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: Solver = Newton,
    ):
        """
        Parameters
        ----------
        cross_section : cross_section.Crossection
            cross-section to compute
        maximum_curvature : float
            maximum positive or negative allowed curvature
        minimum_curvature : float
            minimum positive or negative allowed curvature
            (needs same sign as edge_strains)
        strain_position : StrainPosition
            position_value of the given strain_value (Default: None)
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
        self._maximum_curvature = maximum_curvature
        self._minimum_curvature = minimum_curvature
        self.initialize()
        if logger.level == logging.DEBUG:
            logger.debug(f'{self.__str__()}')
        else:
            logger.info(f'Created {self.__repr__()}')

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
        for index, curvature_value in enumerate(
            [self.minimum_curvature, self.maximum_curvature]
        ):
            self._iteration = index
            self._curvature = curvature_value
            self._neutral_axis = self._compute_neutral_axis()
            self.compute()

    def _compute_new_curvature(self):
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


class MKappaByConstantCurvature(MKappa):

    """
    computation of one Moment-Curvature-Point by fixed curvature and
    varying the neutral axis
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
        "_computed_cross_section",
        "_iteration",
    )

    def __init__(
        self,
        cross_section: Crosssection,
        applied_curvature: float,
        maximum_neutral_axis: float,
        minimum_neutral_axis: float,
        applied_axial_force,
        maximum_iterations=10,
        axial_force_tolerance=5,
        solver=Newton,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.crosssection.Crossection`
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
        if logger.level == logging.DEBUG:
            logger.debug(f'{self.__str__()}')
        else:
            logger.info(f'Created {self.__repr__()}')

    def __repr__(self):
        return (
            f"MKappaByConstantCurvature("
            f"cross_section=cross_section, "
            f"applied_curvature={self.applied_curvature}, "
            f"maximum_neutral_axis={self.maximum_neutral_axis}, "
            f"minimum_neutral_axis={self.minimum_neutral_axis}, "
            f"applied_axial_force={self.applied_axial_force}, "
            f"maximum_iterations={self.maximum_iterations}, "
            f"axial_force_tolerance={self.axial_force_tolerance}, "
            f"solver={self.solver})"
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

    def initialize_boundary_curvatures(self):
        for index, neutral_axis_value in enumerate(
            [self.minimum_neutral_axis, self.maximum_neutral_axis]
        ):
            self._iteration = index
            self._curvature = self.applied_curvature
            self._neutral_axis = neutral_axis_value
            self.compute()

    def _compute_new_curvature(self):
        return self.applied_curvature