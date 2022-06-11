import abc
import math

from . import general


class Material:

    """Defines a custom material-type"""

    def __init__(self, section_type: str, stress_strain: list = None):
        """
        Initialization

        Parameters
        ----------
        stress_strain : list
                list with stress-strain-relationship
        section_type : str
                type of section this material is ordered to
                possible values are:
                        - slab
                        - girder
        """
        self._stress_strain = stress_strain
        self._section_type = section_type

    def __repr__(self) -> str:
        return f"Material(stress_strain={self.stress_strain}, section_type={self.section_type})"

    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_stress_strains(),
        ]
        return general.print_chapter(text)

    def _print_title(self) -> str:
        class_name = self.__class__.__name__
        return general.print_sections(
            [class_name, len(class_name) * "=", "section-type: " + self.section_type]
        )

    def _print_initialization(self) -> str:
        return general.print_sections(
            ["Initialization", "--------------", self.__repr__()]
        )

    def _print_stress_strains(self) -> str:
        text = [
            "Stress-strain-relationship",
            "--------------------------",
            "type: {}".format(self.stress_strain_type.lower()),
            "   stress  |   strain  ",
            "-----------------------",
            self._print_stress_strain_points(),
            "-----------------------",
        ]
        return general.print_sections(text)

    def _print_stress_strain_points(self) -> str:
        return general.print_sections(
            [
                " {:9.2f} | {:9.5f}".format(point[0], point[1])
                for point in self.stress_strain
            ]
        )

    def __eq__(self, other):
        return (
            self.stress_strain == other.stress_strain
            and self.section_type == other.section_type
        )

    @property
    def maximum_strain(self) -> float:
        """maximum strain in the stress-strain-relationsship"""
        self.sort_strains_descending()
        return self.stress_strain[0][1]

    @property
    def minimum_strain(self) -> float:
        """minimum strain in the stress-strain-relationsship"""
        self.sort_strains_ascending()
        return self.stress_strain[0][1]

    @property
    def stress_strain(self) -> list:
        """list of stress-strain points"""
        return self._stress_strain

    @property
    def section_type(self) -> str:
        """section type"""
        return self._section_type

    @property
    def strains(self) -> list:
        """strains from the stress-strain-relationsship"""
        return [stress_strain[1] for stress_strain in self.stress_strain]

    @property
    def stresses(self) -> list:
        """stresses from the stress-strain-relationsship"""
        return [stress_strain[0] for stress_strain in self.stress_strain]

    def get_intermediate_strains(self, strain_1: float, strain_2: float = 0.0) -> list:
        """determine material points with strains between zero and given strain"""
        material_index_1 = self._get_material_index(strain_1)
        material_index_2 = self._get_material_index(strain_2)
        min_index, max_index = self._order_material_indizes(
            material_index_2, material_index_1
        )
        return self._remove_zero_strain(self.strains[min_index:max_index])

    def get_material_stress(self, strain: float) -> float:
        """
        gives stress from the stress-strain-relationship corresponding with the given strain

        Parameters
        ----------
        strain : float
                strain a corresponding stress value should be given

        Returns
        -------
        float
                stress corresponding to the given strain
        """
        material_index = self._get_material_index(strain)
        return self._interpolate_stress(strain, material_index)

    def sort_strains(self, reverse: bool = False) -> None:
        """sorts stress-strain-relationship depending on strains

        Parameters
        ----------
        reverse : bool
                True: sorts strains descending
                False: sorts strains ascending (Default)
        """
        self._stress_strain.sort(key=lambda x: x[1], reverse=reverse)

    def sort_strains_ascending(self) -> None:
        """sorts stress-strain-relationsship so strains are ascending"""
        self.sort_strains(reverse=False)

    def sort_strains_descending(self) -> None:
        """sorts stress-strain-relationsship so strains are descending"""
        self.sort_strains(reverse=True)

    def _get_material_index(self, strain: float):
        self.sort_strains_ascending()
        strain = self.__round_strain(strain)
        if strain == self.stress_strain[-1][1]:
            return len(self.stress_strain) - 2
        for material_index in range(len(self.stress_strain) - 1):
            if (
                self.stress_strain[material_index][1]
                <= strain
                < self.stress_strain[material_index + 1][1]
            ):
                return material_index
        print(f"No stress-strain-pair found in {self.__class__.__name__}")
        print(f"strain: {strain}")
        print(f"stress-strains: {self.stress_strain}")

    def _get_material_stress_by_index(self, index: int) -> float:
        return self.stress_strain[index][0]

    def _order_material_indizes(self, zero_index: int, strain_index: int) -> tuple:
        if strain_index < zero_index:
            if strain_index == 0:
                return (strain_index + 1, zero_index + 1)
            else:
                return (strain_index, zero_index + 1)
        else:
            return (zero_index, strain_index + 1)

    def _remove_zero_strain(self, strains):
        return list(filter(lambda x: x != 0.0, strains))

    def __is_max_index(self, index: int) -> bool:
        if index == len(self.stress_strain) - 1:
            return True
        else:
            return False

    def __round_strain(self, strain: float):
        """prevent rounding errors by rounding strain"""
        return round(strain, 7)

    def _interpolate_stress(self, strain: float, material_index: int) -> float:
        return general.interpolation(
            position=strain,
            first_pair=self.stress_strain[material_index],
            second_pair=self.stress_strain[material_index + 1],
        )


class ConcreteCompression(abc.ABC):
    def __init__(self, f_cm: float, yield_strain: float, E_cm: float):
        self._f_cm = f_cm
        self._yield_strain = yield_strain
        self._E_cm = E_cm

    @property
    def E_cm(self) -> float:
        return self._E_cm

    @property
    def yield_strain(self) -> float:
        return self._yield_strain

    @property
    def f_cm(self) -> float:
        return self._f_cm

    @property
    def f_ck(self) -> float:
        return self.f_cm - 8.0

    @abc.abstractproperty
    def c(self) -> float:
        """strain at maximum stress"""
        ...

    @abc.abstractproperty
    def cu(self) -> float:
        """strain at failure"""
        ...

    @abc.abstractproperty
    def strains(self) -> list:
        ...

    @abc.abstractmethod
    def stress(self, strain) -> float:
        ...

    def stress_strain(self) -> list:
        stress_strain = [[0.0, 0.0]]
        for epsilon in self.strains:
            stress_strain.append([self.stress(epsilon), epsilon])
        return general.negative_sign(stress_strain)


class ConcreteCompressionNonlinear(ConcreteCompression):

    """non-linear concrete behaviour according to EN 1992-1-1"""

    @property
    def c(self) -> float:
        return min(0.7 * (self.f_cm) ** (0.31), 2.8) * 0.001

    @property
    def cu(self) -> float:
        return 0.001 * min(
            (2.8 + 27.0 * ((98.0 - float(self.f_cm)) / 100.0) ** (4.0)), 3.5
        )

    @property
    def strains(self) -> list:
        return [
            self.yield_strain,
            0.33 * (self.yield_strain + self.c),
            0.66 * (self.yield_strain + self.c),
            self.c,
            0.5 * (self.c + self.cu),
            self.cu,
        ]

    def eta(self, strain):
        return strain / self.c

    def k(self):
        return 1.05 * self.E_cm * abs(self.c) / self.f_cm

    def stress(self, strain: float) -> float:
        if self.yield_strain <= strain <= self.cu:
            eta = self.eta(strain)
            k = self.k()
            return self.f_cm * ((k * eta - eta ** (2.0)) / (1.0 + (k - 2) * eta))
        else:
            return 0.0


class ConcreteCompressionParabolaRectangle(ConcreteCompression):

    """parabola-rectangle behaviour of concrete under compression according to EN 1992-1-1"""

    @property
    def c(self) -> float:
        if self.f_ck <= 50:
            return 0.001 * 2.0
        else:
            return 0.001 * (2.0 + (0.085 * (float(self.f_ck) - 50.0) ** (0.53)))

    @property
    def cu(self) -> float:
        return 0.001 * min(
            (2.6 + 35.0 * ((90.0 - float(self.f_ck)) / 100.0) ** (4.0)), 3.5
        )

    @property
    def n(self) -> float:
        return min(1.4 + 23.4 * ((90.0 - self.f_ck) / 100.0) ** (4.0), 2.0)

    @property
    def strains(self) -> list:
        return [0.33 * self.c, 0.66 * self.c, self.c, self.cu]

    def stress(self, strain) -> float:
        if 0.0 <= strain <= self.c:
            return self.f_ck * (1 - (1 - strain / self.c) ** (self.n))
        elif self.c < strain < self.cu:
            return self.f_ck
        else:
            return 0.0


class ConcreteCompressionBilinear(ConcreteCompression):
    @property
    def c(self) -> float:
        return 0.001 * max((1.75 + 0.55 * ((self.f_ck - 50.0) / 40.0)), 1.75)

    @property
    def cu(self) -> float:
        return 0.001 * min((2.6 + 35.0 * ((90.0 - self.f_ck) / 100) ** (4.0)), 3.5)

    @property
    def strains(self) -> list:
        return [self.c, self.cu]

    def stress(self, strain: float) -> float:
        if 0.0 <= strain < self.c:
            return self.f_ck * (self.c - strain) / self.c
        elif self.c <= strain <= self.cu:
            return self.f_ck
        else:
            return 0.0


class ConcreteTension:
    def __init__(
        self, f_cm: float, E_cm: float, f_ctm: float = None, use_tension: bool = True
    ):
        self._f_cm = f_cm
        self._E_cm = E_cm
        self._f_ctm = f_ctm
        self._use_tension = use_tension

    @property
    def f_cm(self):
        return self._f_cm

    @property
    def f_ck(self):
        return self._f_cm - 8.0

    @property
    def E_cm(self):
        return self._E_cm

    @property
    def yield_strain(self):
        return self.f_ctm / self.E_cm

    @property
    def f_ctm(self) -> float:
        if self._f_ctm is None:
            if self.f_ck <= 50.0:
                return 0.3 * self.f_cm
            else:
                return 2.12 * math.log(1.0 + 0.1 * self.f_cm)
        else:
            return self._f_ctm

    def stress_strain(self) -> list:
        stress_strain = [[0.0, 0.0]]
        if self.use_tension:
            stress_strain.append([self.f_ctm, self.yield_strain])
            stress_strain.append([0.0, self.yield_strain + 0.000001])
        stress_strain.append([0.0, 10.0])
        return general.positive_sign(stress_strain)

    @property
    def use_tension(self) -> bool:
        return self._use_tension


class Concrete(Material):

    """Concrete material"""

    def __init__(
        self,
        f_cm: float,
        f_ctm: float = None,
        use_tension: bool = True,
        compression_stress_strain_type: str = "Nonlinear",
        tension_stress_strain_type="Default",
    ):
        self._f_cm = f_cm
        self._f_ctm = f_ctm
        self._use_tension = use_tension
        self._compression_stress_strain_type = compression_stress_strain_type
        self._tension_stress_strain_type = tension_stress_strain_type
        self._compression = self.__set_compression()
        self._tension = self.__set_tension()
        self._stress_strain = self.__build_stress_strain()

    def __repr__(self):
        return f"Concrete(f_cm={self.f_cm}, f_ctm={self._f_ctm}, use_tension={self.use_tension}, stress_strain_type={self.stress_strain_type})"

    @general.str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_elastic_values(),
            self._print_compressive_values(),
            self._print_tensile_values(),
            self._print_stress_strains(),
        ]
        return general.print_chapter(text)

    def _print_elastic_values(self) -> str:
        return general.print_sections(
            [
                "Elastic",
                "-------",
                "E_cm = {:.1f} N/mm^2, | epsilon_y={:.4f}".format(
                    self.E_cm, self.epsilon_y
                ),
            ]
        )

    def _print_compressive_values(self) -> str:
        text = [
            "Compressive strength",
            "--------------------",
            "f_ck = {:.1f} N/mm^2 | f_cm = {:.1f} N/mm^2".format(self.f_ck, self.f_cm),
            "epsilon_c = {:.4f} | epsilon_cu = {:.4f}".format(
                self.epsilon_c, self.epsilon_cu
            ),
        ]
        return general.print_sections(text)

    def _print_tensile_values(self) -> str:
        text = [
            "Tensile strength",
            "----------------",
            "f_ctm = {:.1f} N/mm^2".format(self.f_ctm),
        ]
        return general.print_sections(text)

    @property
    def compression(self):
        return self._compression

    @property
    def compression_stress_strain_type(self):
        return self._compression_stress_strain_type

    @compression_stress_strain_type.setter
    def compression_stress_strain_type(self, type: str):
        self._compression_stress_strain_type = type
        self.__set_compression()

    @property
    def E_cm(self):
        return 22000 * (self.f_cm / 10) ** (0.3)

    @property
    def epsilon_y(self):
        return 0.4 * self.f_cm / self.E_cm

    @property
    def f_cm(self) -> float:
        return self._f_cm

    @property
    def section_type(self):
        return "slab"

    @property
    def tension(self):
        return self._tension

    @property
    def tension_stress_strain_type(self):
        return self._tension_stress_strain_type

    @tension_stress_strain_type.setter
    def tension_stress_strain_type(self, type: str):
        self._tension_stress_strain_type = type
        self.__set_tension()

    @property
    def use_tension(self) -> bool:
        return self._use_tension

    def __set_compression(self):
        type = self.compression_stress_strain_type.replace("-", "").replace(" ", "")
        if type.upper() == "NONLINEAR":
            return ConcreteCompressionNonlinear(self.f_cm, self.epsilon_y, self.E_cm)
        elif type.upper() == "PARABOLA":
            return ConcreteCompressionParabolaRectangle(
                self.f_cm, self.epsilon_y, self.E_cm
            )
        elif type.upper() == "BILINEAR":
            return ConcreteCompressionBilinear(self.f_cm, self.epsilon_y, self.Ecm)
        else:
            raise ValueError(
                str(type)
                + ' not a valid value. Valid values are "Nonlinear", "Parabola" or "Bilinear"'
            )

    def __set_tension(self) -> ConcreteTension:
        type = self.tension_stress_strain_type.replace("-", "").replace(" ", "")
        if type.upper() == "DEFAULT":
            return ConcreteTension(self.f_cm, self.E_cm, self._f_ctm, self.use_tension)
        else:
            raise ValueError(
                str(type) + ' is not a valid value. Valid value is "Default"'
            )

    def __build_stress_strain(self):
        stress_strains = self.compression.stress_strain() + self.tension.stress_strain()
        stress_strains = general.remove_duplicates(stress_strains)
        stress_strains.sort(key=lambda x: x[1], reverse=False)
        return stress_strains


class Steel(Material):
    def __init__(
        self,
        f_y: float,
        f_u: float = None,
        epsilon_u: float = None,
        E_a: float = 210000,
    ):
        self._f_y = f_y
        self._f_u = f_u
        self._epsilon_u = epsilon_u
        self._E_a = E_a
        self._stress_strain = self.__build_stress_strain()

    def __repr__(self):
        return f"Steel(f_y={self.f_y}, f_u={self.f_u}, epsilon_u={self.epsilon_u}, E_a={self.E_a})"

    @property
    def class_name(self):
        return "Steel"

    @general.str_start_end
    def __str__(self):
        text = [
            self.class_name,
            len(self.class_name) * "=",
            "section-type: " + self.section_type,
            "",
            "Initialization",
            "--------------",
            self.__repr__(),
            "",
            "Elastic",
            "-------",
            "E_a: {:.1f}".format(self.E_a),
        ]
        if not self.__is_elastic:
            text.append("")
            text.append("Plastic")
            text.append("-------")
            text.append(
                "f_y: {:.1f} N/mm^2 | epsilon_y: {:.5f}".format(
                    self.f_y, self.epsilon_y
                )
            )
        if self.__is_plastic:
            text.append(
                "f_u: {:.1f} N/mm^2 | epsilon_u: {:.5f}".format(
                    self.f_u, self.epsilon_u
                )
            )
        text += [
            "",
            "Stress-Strain-Relationship",
            "--------------------------",
            "type: " + self.stress_strain_type,
            "   stress  |   strain  ",
            "------------------------",
        ]
        for point in self.stress_strain:
            text.append(" {:9.1f} | {:9.5f}".format(point[0], point[1]))
        return "\n".join(text)

    @property
    def section_type(self) -> str:
        return "girder"

    @property
    def stress_strain(self) -> list:
        return self._stress_strain

    @property
    def __is_elastic(self):
        if self.f_y is None or self.epsilon_u is None:
            return True
        else:
            return False

    @property
    def __is_ideal_plastic(self):
        if self.f_y is not None and self.epsilon_u is not None and self.f_u is None:
            return True
        else:
            return False

    @property
    def __is_plastic(self):
        if self.f_y is not None and self.epsilon_u is not None and self.f_u is not None:
            return True
        else:
            return False

    @property
    def stress_strain_type(self) -> str:
        if self.__is_elastic:
            return "elastic"
        elif self.__is_ideal_plastic:
            return "ideal-plastic"
        else:
            return "plastic"

    @property
    def f_y(self) -> float:
        return self._f_y

    @property
    def f_u(self) -> float:
        if self._f_u is None or self._epsilon_u is None:
            return None
        else:
            return self._f_u

    @property
    def epsilon_u(self) -> float:
        return self._epsilon_u

    @property
    def E_a(self) -> float:
        return self._E_a

    @property
    def epsilon_y(self) -> float:
        if self.f_y is not None:
            return self.f_y / self.E_a
        else:
            return None

    def stress_strain_standard(self) -> list:
        stress_strain = [
            [0.0, 0.0],
        ]
        if self.__is_elastic:
            stress_strain.append([self.E_a, 1.0])
        else:
            stress_strain.append([self.f_y, self.epsilon_y])
        if self.__is_ideal_plastic:
            stress_strain.append([self.f_y, self.epsilon_u])
        if self.__is_plastic:
            stress_strain.append([self.f_u, self.epsilon_u])
        return stress_strain

    @property
    def tension_stress_strain(self):
        return general.positive_sign(self.stress_strain_standard())

    @property
    def compression_stress_strain(self):
        return general.negative_sign(self.stress_strain_standard())

    def __build_stress_strain(self):
        stress_strains = self.compression_stress_strain + self.tension_stress_strain
        stress_strains.sort()
        return general.remove_duplicates(stress_strains)


class Reinforcement(Steel):
    @property
    def section_type(self):
        return "slab"

    @property
    def class_name(self):
        return "Reinforcement"


if __name__ == "__main__":

    concrete = Concrete(f_cm=30)
    print(concrete)

    steel = Steel(f_y=300)
    print(steel)

    reinforcement = Reinforcement(f_y=500, f_u=550, epsilon_u=0.15)
    print(reinforcement)

    # print(steel.material_points_position(curvature=0.0002, neutral_axis=10))

    print(reinforcement.get_intermediate_strains(-0.15, 0.15))
