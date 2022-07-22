from . import general
from . import section
from . import crosssection
from . import solver

"""

Todo
----
  - Implement effective width
"""


class MKappa:

    """computation of one Moment-Curvature-Point by fixation of one point and varying the neutral axis"""

    def __init__(
        self,
        cross_section: crosssection.Crosssection,
        applied_axial_force: float = 0.0,
        maximum_iterations: int = 10,
        axial_force_tolerance: float = 5.0,
        solver: solver.Solver = solver.Newton,
    ):
        """
        Initialization

        Parameters
        ----------
        cross_section : crosssection.Crossection
            cross-section to compute
        maximum_curvature : float
           maximum positive or negative allowed curvature
        minimum_curvature : float
            minnimum positive or negative allowed curvature
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
        return crosssection.ComputationCrosssectionCurvature(
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
        cross_section: crosssection.Crosssection,
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
        cross_section : crosssection.Crossection
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
        cross_section: crosssection.Crosssection,
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
        cross_section : crosssection.Crossection
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
