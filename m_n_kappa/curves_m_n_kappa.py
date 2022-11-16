from .general import (
    print_sections,
    print_chapter,
    str_start_end,
    remove_duplicates,
)
from .crosssection import Crosssection, ComputationCrosssectionStrain
from .solver import Solver, Newton


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
        cross_section: Crosssection,
        input_section_type: str,
        input_strain: float,
        counter_lower_strain: float,
        counter_upper_strain: float,
        axial_force_tolerance: float = 5.0,
        maximum_iterations: int = 10,
        solver: Solver = Newton,
    ):
        """
        Initialization

        Paramters
        ---------
        cross_section : Crosssection
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
            self._print_initalization(),
            self._print_input_sections_result(),
            self._print_other_sections_result(),
            self._print_other_sections_iterations(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initalization(self) -> str:
        return print_sections(
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
        return print_sections(text)

    def _print_other_sections_result(self) -> str:
        text = [
            "Other Section",
            "-------------",
            f"strain: {self.other_strain}",
            f"axial-force: {self.other_axial_force}",
            f"moment: {self.other_sections_moment()}",
        ]
        return print_sections(text)

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
        return print_sections(text)

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
    def cross_section(self) -> Crosssection:
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
    def input_strain(self) -> float:
        return self._input_strain

    @property
    def input_cross_section(self) -> Crosssection:
        return self._input_cross_section

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def maximum_iterations(self) -> int:
        return self._maximum_iterations

    @property
    def other_strain(self) -> float:
        return self._other_strain

    @property
    def other_axial_force(self) -> float:
        return self._other_axial_force

    @property
    def other_cross_section(self) -> Crosssection:
        return self._other_cross_section

    @property
    def successful(self) -> bool:
        return self._successful

    @property
    def solver(self) -> Solver:
        return self._solver

    def moment(self) -> float:
        return self.other_sections_moment() + self.input_sections_moment()

    def input_sections(self) -> list:
        return self.cross_section.sections_of_type(self.input_section_type)

    def other_sections(self) -> list:
        return self.cross_section.sections_not_of_type(self.input_section_type)

    def _compute_input_section(self) -> None:
        self._input_cross_section = self._create_crosssection(
            self.input_sections(), self.input_strain
        )
        self._axial_force = self.input_cross_section.total_axial_force()

    def _compute_other_section(self) -> None:
        self._other_cross_section = self._create_crosssection(
            self.other_sections(), self.other_strain
        )
        self._other_axial_force = self.other_cross_section.total_axial_force()
        self._save()

    def input_sections_moment(self) -> float:
        return self.input_cross_section.total_moment()

    def other_sections_moment(self) -> float:
        return self.other_cross_section.total_moment()

    def other_sections_initialize(self) -> None:
        self._compute_other_section()
        self._iteration = 1
        self._other_strain = self.counter_upper_strain
        self._compute_other_section()
        if self._axial_force_within_tolerance():
            self._successful = True
        else:
            self.other_sections_iterate()

    def other_sections_iterate(self) -> None:
        for iteration in range(2, self.maximum_iterations):
            self._iteration = iteration
            self._other_strain = self._guess_new_strain()
            self._compute_other_section()
            if self._axial_force_within_tolerance():
                self._successful = True
                break

    def other_maximum_strain(self) -> float:
        cross_section = Crosssection(self.other_sections())
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

    def _create_crosssection(self, sections, strain) -> ComputationCrosssectionStrain:
        return ComputationCrosssectionStrain(sections, strain)

    def _guess_new_strain(self) -> float:
        return self.solver(
            data=self.computations, variable="strain", target="axial-force"
        ).compute()

    def _save(self) -> None:
        self._computations.append(
            {
                "iteration": self.iteration,
                "strain": self.other_strain,
                "axial-force": self._axial_force_equilibrium(),
                "cross-section": self.other_cross_section,
            }
        )

    def resulting_crosssection(self) -> Crosssection:
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

    def __init__(self, cross_section: Crosssection):
        """
        Initialization

        Parameters
        ----------
        cross_section : Crosssection
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

    @str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_section_results_table(),
            self._print_axial_force_table(),
            self._print_m_n_points_table(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(
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
        return print_sections(text)

    def _print_section_results_table(self) -> str:
        return self._print_results_table(
            "Section Results", self._print_section_results()
        )

    def _print_section_results(self) -> str:
        return print_sections(
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
        return print_sections(
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
        return print_sections(text)

    def _print_m_n_points_table_content(self) -> str:
        return print_sections(
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
        return remove_duplicates(section_strains)

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
        return ComputationCrosssectionStrain(sections, strain)

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

    def __init__(self, cross_section: Crosssection, axial_force: float):
        self._cross_section = cross_section
        self._axial_force: float

    @property
    def cross_section(self) -> Crosssection:
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

    def __init__(self, cross_section: Crosssection, m_n_points: list):
        """
        Initialization

        Parameters
        ----------
        cross_section : Crosssection
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

    @str_start_end
    def __str__(self):
        text = []
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(["Initialization", "--------------", self.__repr__()])

    @property
    def cross_section(self) -> Crosssection:
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


class MKappaAtAxialForce:

    """
    compute M-Kappa-Curve at given axial force

    procedure:
            1. get maximum curvature
            2.
    """

    def __init__(self, cross_section: Crosssection, axial_force: float):
        self._cross_section = cross_section
        self._axial_force = axial_force