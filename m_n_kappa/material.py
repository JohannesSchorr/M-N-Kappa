from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import log

from .general import (
    print_chapter,
    print_sections,
    interpolation,
    negative_sign,
    positive_sign,
    str_start_end,
    remove_duplicates,
    remove_zeros,
)


def make_float(value):
    if value is None:
        return None
    else:
        return float(value)


@dataclass
class StressStrain:

    """container for a stress-strain-point"""

    stress: float
    strain: float

    def pair(self) -> list[float]:
        return [self.stress, self.strain]


class Material:

    """Defines a custom material-section_type"""

    def __init__(self, section_type: str, stress_strain: list[StressStrain] = None):
        """
        Initialization

        Parameters
        ----------
        stress_strain : list
            list with stress-strain_value-relationship
        section_type : str
            section_type of section this material is ordered to

            possible values are:
            - slab
            - girder
        """
        self._stress_strain = stress_strain
        self._section_type = section_type

    def __repr__(self) -> str:
        return f"""Material(stress_strain={self.stress_strain}, 
        section_type={self.section_type})"""

    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_stress_strains(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        class_name = self.__class__.__name__
        return print_sections(
            [
                class_name,
                len(class_name) * "=",
                "section-section_type: " + self.section_type,
            ]
        )

    def _print_initialization(self) -> str:
        return print_sections(["Initialization", "--------------", self.__repr__()])

    def _print_stress_strains(self) -> str:
        text = [
            "Stress-strain_value-relationship",
            "--------------------------",
            # f"section_type: {self.stress_strain_type.lower()}",
            "   stress  |   strain_value  ",
            "-----------------------",
            self._print_stress_strain_points(),
            "-----------------------",
        ]
        return print_sections(text)

    def _print_stress_strain_points(self) -> str:
        return print_sections(
            [
                " {:9.2f} | {:9.5f}".format(point.stress, point.strain)
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
        """maximum strain_value in the stress-strain_value-relationship"""
        self.sort_strains_descending()
        return self.stress_strain[0].strain

    @property
    def minimum_strain(self) -> float:
        """minimum strain_value in the stress-strain_value-relationship"""
        self.sort_strains_ascending()
        return self.stress_strain[0].strain

    @property
    def stress_strain(self) -> list[StressStrain]:
        """list of stress-strain_value points"""
        return self._stress_strain

    @property
    def section_type(self) -> str:
        """section section_type"""
        return self._section_type

    @property
    def strains(self) -> list:
        """strains from the stress-strain_value-relationship"""
        return [stress_strain.strain for stress_strain in self.stress_strain]

    @property
    def stresses(self) -> list:
        """stresses from the stress-strain_value-relationship"""
        return [stress_strain.stress for stress_strain in self.stress_strain]

    def get_intermediate_strains(self, strain_1: float, strain_2: float = 0.0) -> list:
        """determine material points with strains between zero and given strain_value"""
        material_index_1 = self._get_material_index(strain_1)
        material_index_2 = self._get_material_index(strain_2)
        min_index, max_index = self._order_material_indexes(
            material_index_2, material_index_1
        )
        return self._remove_zero_strain(self.strains[min_index:max_index])

    def get_material_stress(self, strain: float) -> float:
        """
        gives stress from the stress-strain_value-relationship corresponding with the given strain_value

        Parameters
        ----------
        strain : float
                strain_value a corresponding stress value should be given

        Returns
        -------
        float
                stress corresponding to the given strain_value
        """
        material_index = self._get_material_index(strain)
        return self._interpolate_stress(strain, material_index)

    def sort_strains(self, reverse: bool = False) -> None:
        """sorts stress-strain_value-relationship depending on strains

        Parameters
        ----------
        reverse : bool
                True: sorts strains descending
                False: sorts strains ascending (Default)
        """
        self._stress_strain.sort(key=lambda x: x.strain, reverse=reverse)

    def sort_strains_ascending(self) -> None:
        """sorts stress-strain_value-relationship so strains are ascending"""
        self.sort_strains(reverse=False)

    def sort_strains_descending(self) -> None:
        """sorts stress-strain_value-relationship so strains are descending"""
        self.sort_strains(reverse=True)

    def _get_material_index(self, strain_value: float):
        self.sort_strains_ascending()
        strain_value = self.__round_strain(strain_value)
        if strain_value == self.stress_strain[-1].strain:
            return len(self.stress_strain) - 2
        for material_index in range(len(self.stress_strain) - 1):
            if (
                self.stress_strain[material_index].strain
                <= strain_value
                < self.stress_strain[material_index + 1].strain
            ):
                return material_index
        print(f"No stress-strain_value-pair found in {self.__class__.__name__}")
        print(f"strain_value: {strain_value}")
        print(f"stress-strains: {self.stress_strain}")

    def _get_material_stress_by_index(self, index: int) -> float:
        return self.stress_strain[index].stress

    @staticmethod
    def _order_material_indexes(zero_index: int, strain_index: int) -> tuple:
        if strain_index < zero_index:
            if strain_index == 0:
                return strain_index + 1, zero_index + 1
            else:
                return strain_index, zero_index + 1
        else:
            return zero_index, strain_index + 1

    @staticmethod
    def _remove_zero_strain(strains: list) -> list:
        return remove_zeros(strains)

    def __is_max_index(self, index: int) -> bool:
        if index == len(self.stress_strain) - 1:
            return True
        else:
            return False

    @staticmethod
    def __round_strain(strain_value: float):
        """prevent rounding errors by rounding strain_value"""
        return round(strain_value, 7)

    def _interpolate_stress(self, strain: float, material_index: int) -> float:
        return interpolation(
            position_value=strain,
            first_pair=self.stress_strain[material_index].pair(),
            second_pair=self.stress_strain[material_index + 1].pair(),
        )


class ConcreteCompression(ABC):
    def __init__(self, f_cm: float, yield_strain: float, E_cm: float):
        self._f_cm = float(f_cm)
        self._yield_strain = float(yield_strain)
        self._E_cm = float(E_cm)

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

    @property
    @abstractmethod
    def c(self) -> float:
        """strain_value at maximum stress"""
        ...

    @property
    @abstractmethod
    def cu(self) -> float:
        """strain_value at failure"""
        ...

    @property
    @abstractmethod
    def strains(self) -> list:
        ...

    @abstractmethod
    def stress(self, strain) -> float:
        ...

    def stress_strain(self) -> list:
        stress_strain = [[0.0, 0.0]]
        for epsilon in self.strains:
            stress_strain.append([self.stress(epsilon), epsilon])
        return negative_sign(stress_strain)


class ConcreteCompressionNonlinear(ConcreteCompression):

    """non-linear concrete behaviour according to EN 1992-1-1"""

    @property
    def c(self) -> float:
        return min(0.7 * self.f_cm**0.31, 2.8) * 0.001

    @property
    def cu(self) -> float:
        return 0.001 * min(
            (2.8 + 27.0 * ((98.0 - float(self.f_cm)) / 100.0) ** 4.0), 3.5
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
            return self.f_cm * ((k * eta - eta**2.0) / (1.0 + (k - 2) * eta))
        else:
            return 0.0


class ConcreteCompressionParabolaRectangle(ConcreteCompression):

    """parabola-rectangle behaviour of concrete under compression according to EN 1992-1-1"""

    @property
    def c(self) -> float:
        if self.f_ck <= 50:
            return 0.001 * 2.0
        else:
            return 0.001 * (2.0 + (0.085 * (float(self.f_ck) - 50.0) ** 0.53))

    @property
    def cu(self) -> float:
        return 0.001 * min(
            (2.6 + 35.0 * ((90.0 - float(self.f_ck)) / 100.0) ** 4.0), 3.5
        )

    @property
    def n(self) -> float:
        return min(1.4 + 23.4 * ((90.0 - self.f_ck) / 100.0) ** 4.0, 2.0)

    @property
    def strains(self) -> list:
        return [0.33 * self.c, 0.66 * self.c, self.c, self.cu]

    def stress(self, strain) -> float:
        if 0.0 <= strain <= self.c:
            return self.f_ck * (1 - (1 - strain / self.c) ** self.n)
        elif self.c < strain < self.cu:
            return self.f_ck
        else:
            return 0.0


class ConcreteCompressionBiLinear(ConcreteCompression):
    @property
    def c(self) -> float:
        return 0.001 * max((1.75 + 0.55 * ((self.f_ck - 50.0) / 40.0)), 1.75)

    @property
    def cu(self) -> float:
        return 0.001 * min((2.6 + 35.0 * ((90.0 - self.f_ck) / 100) ** 4.0), 3.5)

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
                return 2.12 * log(1.0 + 0.1 * self.f_cm)
        else:
            return self._f_ctm

    def stress_strain(self) -> list:
        stress_strain = [[0.0, 0.0]]
        if self.use_tension:
            stress_strain.append([self.f_ctm, self.yield_strain])
            stress_strain.append([0.0, self.yield_strain + 0.000001])
        stress_strain.append([0.0, 10.0])
        return positive_sign(stress_strain)

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
        """
        Parameters
        ----------
        f_cm : float
            mean concrete cylinder compression strength
        f_ctm : float
            mean tensile strength
        use_tension : float
            if True: considers tension (Default)
            if False: does not consider tension
        compression_stress_strain_type : str
            sets section_type of stress-strain_value curve under compression.
            Possible values are:
            - 'Nonlinear'
            - 'Parabola'
            - 'Bilinear'
        tension_stress_strain_type : str
            sets section_type of strain_value-stain curve under tension
            Possible values are:
            - 'Default'
        """
        super().__init__(section_type="slab")
        self._f_cm = float(f_cm)
        self._f_ctm = make_float(f_ctm)
        self._use_tension = use_tension
        self._compression_stress_strain_type = compression_stress_strain_type
        self._tension_stress_strain_type = tension_stress_strain_type
        self._compression = self.__set_compression()
        self._tension = self.__set_tension()
        self._stress_strain = self.__build_stress_strain()

    def __repr__(self):
        return (
            f"Concrete(f_cm={self.f_cm}, "
            f"f_ctm={self._f_ctm}, "
            f"use_tension={self.use_tension}, "
            f"compression_stress_strain_type={self.compression_stress_strain_type}), "
            f"tension_stress_strain_type={self.tension_stress_strain_type})"
        )

    @str_start_end
    def __str__(self):
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_elastic_values(),
            self._print_compressive_values(),
            self._print_tensile_values(),
            self._print_stress_strains(),
        ]
        return print_chapter(text)

    def _print_elastic_values(self) -> str:
        return print_sections(
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
                self.compression.c, self.compression.cu
            ),
        ]
        return print_sections(text)

    def _print_tensile_values(self) -> str:
        text = [
            "Tensile strength",
            "----------------",
            "f_ctm = {:.1f} N/mm^2".format(self.tension.f_ctm),
        ]
        return print_sections(text)

    @property
    def compression(self):
        return self._compression

    @property
    def compression_stress_strain_type(self):
        return self._compression_stress_strain_type

    @compression_stress_strain_type.setter
    def compression_stress_strain_type(self, stress_strain_type: str):
        self._compression_stress_strain_type = stress_strain_type
        self.__set_compression()

    @property
    def E_cm(self) -> float:
        return 22000.0 * (self.f_cm / 10) ** 0.3

    @property
    def epsilon_y(self) -> float:
        return 0.4 * self.f_cm / self.E_cm

    @property
    def f_cm(self) -> float:
        return self._f_cm

    @property
    def f_ck(self) -> float:
        return self.f_cm - 8.0

    @property
    def section_type(self) -> str:
        return "slab"

    @property
    def tension(self) -> ConcreteTension:
        return self._tension

    @property
    def tension_stress_strain_type(self) -> str:
        return self._tension_stress_strain_type

    @tension_stress_strain_type.setter
    def tension_stress_strain_type(self, stress_strain_type: str):
        self._tension_stress_strain_type = stress_strain_type
        self.__set_tension()

    @property
    def use_tension(self) -> bool:
        return self._use_tension

    def __set_compression(self) -> ConcreteCompression:
        typ = self.compression_stress_strain_type.replace("-", "").replace(" ", "")
        if typ.upper() == "NONLINEAR":
            return ConcreteCompressionNonlinear(self.f_cm, self.epsilon_y, self.E_cm)
        elif typ.upper() == "PARABOLA":
            return ConcreteCompressionParabolaRectangle(
                self.f_cm, self.epsilon_y, self.E_cm
            )
        elif typ.upper() == "BILINEAR":
            return ConcreteCompressionBiLinear(self.f_cm, self.epsilon_y, self.E_cm)
        else:
            raise ValueError(
                str(typ)
                + ' not a valid value. Valid values are "Nonlinear", "Parabola" or "Bilinear"'
            )

    def __set_tension(self) -> ConcreteTension:
        stress_strain_type = self.tension_stress_strain_type.replace("-", "").replace(
            " ", ""
        )
        if stress_strain_type.upper() == "DEFAULT":
            return ConcreteTension(self.f_cm, self.E_cm, self._f_ctm, self.use_tension)
        else:
            raise ValueError(
                str(stress_strain_type)
                + ' is not a valid value. Valid value is "Default"'
            )

    def __build_stress_strain(self):
        stress_strains = self.compression.stress_strain() + self.tension.stress_strain()
        stress_strains = remove_duplicates(stress_strains)
        stress_strains.sort(key=lambda x: x[1], reverse=False)
        stress_strains = [
            StressStrain(stress_strain[0], stress_strain[1])
            for stress_strain in stress_strains
        ]
        return stress_strains


class Steel(Material):

    """Steel material"""

    def __init__(
        self,
        f_y: float,
        f_u: float = None,
        epsilon_u: float = None,
        E_a: float = 210000.0,
    ):
        super().__init__(section_type="girder")
        self._f_y = float(f_y)
        self._f_u = make_float(f_u)
        self._epsilon_u = make_float(epsilon_u)
        self._E_a = make_float(E_a)
        self._stress_strain = self.__build_stress_strain()

    def __repr__(self):
        return (
            f"Steel(f_y={self.f_y}, "
            f"f_u={self.f_u}, "
            f"epsilon_u={self.epsilon_u}, "
            f"E_a={self.E_a})"
        )

    @str_start_end
    def __str__(self):
        text = [
            self.__class__.__name__,
            len(self.__class__.__name__) * "=",
            "section-section_type: " + self.section_type,
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
            "section_type: " + self.stress_strain_type,
            "   stress  |   strain_value  ",
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
        if self._f_u is not None and self._epsilon_u is not None:
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
        return positive_sign(self.stress_strain_standard())

    @property
    def compression_stress_strain(self):
        return negative_sign(self.stress_strain_standard())

    def __build_stress_strain(self):
        stress_strains = self.compression_stress_strain + self.tension_stress_strain
        stress_strains.sort()
        stress_strains = remove_duplicates(stress_strains)
        return [
            StressStrain(stress_strain[0], stress_strain[1])
            for stress_strain in stress_strains
        ]


class Reinforcement(Steel):

    """Reinforcement material"""

    @property
    def section_type(self):
        return "slab"