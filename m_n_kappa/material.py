import operator
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from bisect import bisect

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

from .log import LoggerMethods

log = LoggerMethods(__name__)


def make_float(value):
    if value is None:
        return None
    else:
        return float(value)


@dataclass(slots=True)
class StressStrain:

    """
    container for a stress-strain-point

    .. versionadded:: 0.1.0

    Parameters
    ----------
    stress : float
        stress of the point
    strain : float
        strain of the point
    """

    stress: float = field(compare=True)
    strain: float = field(compare=True)

    def __post_init__(self):
        self.stress = round(self.stress, 7)
        self.strain = round(self.strain, 7)
        log.info(f"Created {self.__repr__()}")

    def pair(self) -> list[float]:
        """stress-strain-point as list"""
        return [self.stress, self.strain]


class Material:

    """
    Provides basic functionality for materials

    .. versionadded: 0.1.0

    In case custom-type materials are created these must inherit from this class.
    """

    @log.init
    def __init__(self, section_type: str, stress_strain: list[StressStrain] = None):
        """
        Parameters
        ----------
        stress_strain : list[:py:class:`~m_n_kappa.material.StressStrain`]
            list with stress-strain_value-relationship
        section_type : str
            section_type of section this material is ordered to.
            Possible values are:
            - slab
            - girder

        See Also
        --------
        Concrete : material-behaviour of concrete
        Steel: material-behaviour of steel
        Reinforcement : material-behaviour of reinforcement

        Examples
        --------

        **Base class**

        All material-models needs inheritance from :py:class:`~m_n_kappa.material.Material` to achieve basic
        functionality.

        Stress-strain-points in the stress-strain-relationships need to be defined
        by :py:class:`~m_n_kappa.material.StressStrain`.

        **Adding new materials**

        A new material must inherit from :py:class:`~m_n_kappa.material.Material`.

        The following code implements an arbitrary material model that act linear-elastic under compression
        and ideal-plastic under tension loading.

        Two class-properties must be defined after initialization of the material:

        1. ``stress_strain`` (``_stress_strain`` at initialization): stress-strain-relationship as a list
           of :py:class:`~m_n_kappa.material.StressStrain`
        2. ``section_type``: defining the section-type this material is applied to. Possible values are:

           - ``'girder'``
           - ``'slab'``

        .. testcode::

            from m_n_kappa.material import Material, StressStrain

            class Arbitrary(Material):

                \"""arbitrary material\"""

                def __init__(self):
                    self._stress_strain = [
                        StressStrain(stress=-10.0, strain=-0.001),
                        StressStrain(stress=0.0, strain=0.0),
                        StressStrain(stress=10.0, strain=0.001),
                        StressStrain(stress=10.0, strain=0.01),
                    ]

                @property
                def section_type(self):
                    return "girder"
        """
        self._stress_strain = stress_strain
        self._section_type = section_type
        self._stress_ascending_strain = sorted(
            self.stress_strain, key=operator.attrgetter("strain")
        )

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
            "   stress  |   strain_value  ",
            "-----------------------",
            self._print_stress_strain_points(strain_precision=7),
            "-----------------------",
        ]
        return print_sections(text)

    def _print_stress_strain_points(self, stress_precision: int = 2, strain_precision: int = 5) -> str:
        return print_sections(
            [
                f" {point.stress:9.{stress_precision}f} | {point.strain:9.{strain_precision}f}"
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
        return self._stress_ascending_strain[-1].strain

    @property
    def minimum_strain(self) -> float:
        """minimum strain_value in the stress-strain_value-relationship"""
        return self._stress_ascending_strain[0].strain

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
        return [stress_strain.strain for stress_strain in self._stress_ascending_strain]

    @property
    def stresses(self) -> list:
        """stresses from the stress-strain_value-relationship"""
        return [stress_strain.stress for stress_strain in self._stress_ascending_strain]

    def get_intermediate_strains(
        self, strain_1: float, strain_2: float = 0.0, include_strains: bool = False
    ) -> list:
        """
        determine material points with strains between zero and given strain_value

        Parameters
        ----------
        strain_1 : float
            1st strain-value
        strain_2 : float
            2nd strain-value (Default: 0.0)
        include_strains : bool
            includes the boundary strain values (Default: False)

        Returns
        -------
        list[float]
            determine material points with strains between zero and given strain_value
        """
        material_index_1 = self._get_material_index(strain_1)
        material_index_2 = self._get_material_index(strain_2)
        min_index, max_index = self._order_material_indexes(
            material_index_2, material_index_1
        )
        if include_strains:
            if self.strains[min_index - 1] == strain_1:
                min_index -= 1
            if self.strains[max_index] == strain_2:
                max_index += 1
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
            stress corresponding to the given strain-value in the material-model

        Raises
        ------
        ValueError
            when strain is outside the boundary values of the material-model
        """
        material_index = self._get_material_index(strain)
        if material_index is None:
            raise ValueError(f"No material-index found for {strain=},\n" f"{self.__str__()}")
        return self._interpolate_stress(strain, material_index)

    def sort_strains(self, reverse: bool = False) -> None:
        """sorts stress-strain_value-relationship depending on strains

        Parameters
        ----------
        reverse : bool
            - ``True``: sorts strains descending
            - ``False``: sorts strains ascending (Default)
        """
        self._stress_strain.sort(key=operator.attrgetter("strain"), reverse=reverse)

    def sort_strains_ascending(self) -> None:
        """sorts stress-strain_value-relationship so strains are ascending"""
        self.sort_strains(reverse=False)

    def sort_strains_descending(self) -> None:
        """sorts stress-strain_value-relationship so strains are descending"""
        self.sort_strains(reverse=True)

    def _get_material_index(self, strain_value: float) -> int:
        """
        Determine the index of the value in the stress-strain-curve that is
        leftmost smaller than ``strain_value``

        Parameters
        ----------
        strain_value : float
            strain-value the index is looked for

        Returns
        -------
        int
            index of the first-smallest stress-strain-value as the given one
        """
        strain_value = self.__round_strain(strain_value)
        if (
            self._stress_ascending_strain[0].strain
            < strain_value
            < self._stress_ascending_strain[-1].strain
        ):
            return (
                bisect(
                    self._stress_ascending_strain,
                    strain_value,
                    key=operator.attrgetter("strain"),
                )
                - 1
            )
        elif strain_value == self._stress_ascending_strain[0].strain:
            return 0
        elif strain_value == self._stress_ascending_strain[-1].strain:
            return len(self._stress_ascending_strain) - 2
        else:
            log.critical(
                f"No stress-strain_value-pair found in {self.__class__.__name__} for {strain_value=}\n"
            )

    def _get_material_stress_by_index(self, index: int) -> float:
        return self.stress_strain[index].stress

    @staticmethod
    def _order_material_indexes(zero_index: int, strain_index: int) -> tuple[int, int]:
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
        if material_index is None:
            raise TypeError(
                f"List indices must be integers or slices, not NoneType.\n"
                f"Material: {self.__str__()}"
            )
        return interpolation(
            position_value=strain,
            first_pair=self._stress_ascending_strain[material_index].pair(),
            second_pair=self._stress_ascending_strain[material_index + 1].pair(),
        )


class ConcreteCompression(ABC):
    """
    Meta-class for concrete under compression

    .. versionadded:: 0.1.0

    Several models are given to describe concrete under compression.
    This class works as basis for implementing these models and
    give them a similar interface.
    """

    __slots__ = "_f_cm", "_yield_strain", "_E_cm"

    @log.init
    def __init__(self, f_cm: float, yield_strain: float, E_cm: float):
        """
        Parameters
        ----------
        f_cm : float
            mean concrete cylinder compressive strength :math:`f_\\mathrm{cm}`
        yield_strain : float
            strain up to which the concrete is assumed to be linear-elastic :math:`\\varepsilon_\\mathrm{y}`
        E_cm : float
            mean elasticity modulus of concrete :math:`E_\\mathrm{cm}`

        See Also
        --------
        ConcreteCompressionNonlinear : Non-linear behaviour of concrete under compression
        ConcreteCompressionParabolaRectangle : Parabola-rectangle behaviour of concrete under compression
        ConcreteCompressionBiLinear: Bi-linear behaviour of concrete under compression
        """
        self._f_cm = float(f_cm)
        self._yield_strain = float(yield_strain)
        self._E_cm = float(E_cm)

    @property
    def E_cm(self) -> float:
        """mean elasticity modulus of concrete :math:`E_\\mathrm{cm}`"""
        return self._E_cm

    @property
    def yield_strain(self) -> float:
        """strain up to which the concrete is assumed to be linear-elastic :math:`\\varepsilon_\\mathrm{y}`"""
        return self._yield_strain

    @property
    def f_cm(self) -> float:
        """mean concrete cylinder compressive strength :math:`f_\\mathrm{cm}`"""
        return self._f_cm

    @property
    def f_ck(self) -> float:
        """characteristic concrete cylinder compressive strength :math:`f_\\mathrm{ck}`"""
        return self.f_cm - 8.0

    @property
    @abstractmethod
    def c(self) -> float:
        """strain-value at peak stress :math:`\\varepsilon_\\mathrm{c}`"""
        ...

    @property
    @abstractmethod
    def cu(self) -> float:
        """strain-value at failure :math:`\\varepsilon_\\mathrm{cu}`"""
        ...

    @property
    @abstractmethod
    def strains(self) -> list:
        """strains a corresponding stress-point is to be computed"""
        ...

    @abstractmethod
    def stress(self, strain: float) -> float:
        """
        method to compute the stress for the given ``strain``

        Parameters
        ----------
        strain : float
            strain to compute a corresponding stress-point

        Returns
        -------
        float
            stress-point to the given ``strain``
        """
        ...

    def stress_strain(self) -> list:
        """stress-strain points of the material"""
        stress_strain = []  # [[0.0, 0.0]]
        for epsilon in self.strains:
            stress_strain.append([self.stress(epsilon), epsilon])
        return negative_sign(stress_strain)


class ConcreteCompressionNonlinear(ConcreteCompression):

    """
    non-linear concrete behaviour according to EN 1992-1-1 [1]_

    .. versionadded:: 0.1.0
    """

    @log.init
    def __init__(self, f_cm: float, yield_strain: float, E_cm: float):
        """
        Parameters
        ----------
        f_cm : float
            mean concrete cylinder compressive strength :math:`f_\\mathrm{cm}`
        yield_strain : float
            strain up to which the concrete is assumed to be linear-elastic :math:`\\varepsilon_\\mathrm{y}`
        E_cm : float
            mean elasticity modulus of concrete :math:`E_\\mathrm{cm}`


        See Also
        --------
        ConcreteCompressionParabolaRectangle : Describes parabola rectangle behaviour of concrete under compression
        ConcreteCompressionBiLinear : describes bi-linear behaviour of concrete under compression

        Notes
        -----
        The formula for computation of the non-linear behaviour of concrete by EN 1992-1-1 [1]_, Formula 3.14
        is given as follows. Formula :math:numref:`eq:material.concrete.nonlinear` is valid in the range
        :math:`0 < |\\varepsilon| < |\\varepsilon_\\mathrm{c}|`. The here given values are all absolute values.
        As this model applies to the compression-range all values must be multiplied by (-1).

        .. math::
           :label: eq:material.concrete.nonlinear

           \\sigma_\\mathrm{c} = \\frac{k \\cdot \\eta - \\eta^{2}}{1.0 + (k - 2) \\cdot \\eta)} \\cdot f_\\mathrm{cm}

        where

        .. math::
           :label: eq:material.concrete.nonlinear_helper

           \\eta & = \\frac{\\varepsilon}{\\varepsilon_\\mathrm{c}}

           k & = 1.05 \\cdot E_\\mathrm{cm} \\cdot \\frac{|\\varepsilon_\\mathrm{c}|}{f_\\mathrm{cm}}

           \\varepsilon_\\mathrm{c}(Permil) & = 0.7 \\cdot f_\\mathrm{cm}^{0.31} \\leq 2.8

           \\varepsilon_\\mathrm{cu}(Permil) & = 2.8 + 27.0 \\cdot \\left[\\frac{
           98.0 - f_\\mathrm{cm}}{100.0} \\right]^{4} \\leq 3.5

        where :math:`\\varepsilon_\\mathrm{c}` is the strain at peak stress and :math:`\\varepsilon_\\mathrm{cu}`
        is the strain at failure.

        .. figure:: ../images/material_concrete_nonlinear-light.svg
           :class: only-light
        .. figure:: ../images/material_concrete_nonlinear-dark.svg
           :class: only-dark

           Non-linear stress-strain relationship of concrete by EN 1992-1-1 [1]_, Fig. 3.2

        References
        ----------
        .. [1] EN 1992-1-1: Eurocode 2 - Design of concrete structures -
           Part 1-1: General rules and rules for buildings, European Committee of Standardization (CEN),
           April 2004

        Examples
        --------
        The non-linear stress-strain relationship of concrete under compression is computed as follows.

        >>> from m_n_kappa.material import ConcreteCompressionNonlinear
        >>> f_cm = 30.0 # mean concrete compressive strength
        >>> E_cm = 33000 # modulus of elasticity of concrete
        >>> concrete = ConcreteCompressionNonlinear(f_cm=f_cm, yield_strain=0.4*f_cm/E_cm, E_cm=E_cm)
        >>> concrete.stress_strain()
        [[-10.980238020734609, -0.0003636363636363636], [-20.067768095243533, -0.0007830092214998742], \
[-28.832492515864047, -0.0015660184429997484], [-30.0, -0.0020091188530299217], \
[-27.130958857945092, -0.0027545594265149607], [-19.399627516017674, -0.0035]]
        """
        super().__init__(f_cm, yield_strain, E_cm)

    @property
    def c(self) -> float:
        """
        strain at peak stress :math:`\\varepsilon_\\mathrm{c}`
        (see Formula :math:numref:`eq:material.concrete.nonlinear_helper`)
        """
        return min(0.7 * self.f_cm**0.31, 2.8) * 0.001

    @property
    def cu(self) -> float:
        """
        failure strain of concrete :math:`\\varepsilon_\\mathrm{cu}`
        (see Formula :math:numref:`eq:material.concrete.nonlinear_helper`)
        """
        return 0.001 * min(
            (2.8 + 27.0 * ((98.0 - float(self.f_cm)) / 100.0) ** 4.0), 3.5
        )

    @property
    def strains(self) -> list[float]:
        """
        Strain-values where stresses are computed.

        Current strain-values are:

        - :math:`\\varepsilon_\\mathrm{y}`
        - :math:`0.33 \\cdot (\\varepsilon_\\mathrm{y} + \\varepsilon_\\mathrm{c})`
        - :math:`0.66 \\cdot (\\varepsilon_\\mathrm{y} + \\varepsilon_\\mathrm{c})`
        - :math:`\\varepsilon_\\mathrm{c}`
        - :math:`0.5 \\cdot (\\varepsilon_\\mathrm{c} + \\varepsilon_\\mathrm{cu})`
        - :math:`\\varepsilon_\\mathrm{cu}`
        """
        return [
            self.yield_strain,
            0.33 * (self.yield_strain + self.c),
            0.66 * (self.yield_strain + self.c),
            self.c,
            0.5 * (self.c + self.cu),
            self.cu,
        ]

    def eta(self, strain):
        """
        ratio between strain and strain at peak stress :math:`\\eta`
        (see Formula :math:numref:`eq:material.concrete.nonlinear_helper`)
        """
        return strain / self.c

    def k(self):
        """helper-function (see Formula :math:numref:`eq:material.concrete.nonlinear_helper`)"""
        return 1.05 * self.E_cm * abs(self.c) / self.f_cm

    def stress(self, strain: float) -> float:
        """
        computation of stresses according to formula :math:numref:`eq:material.concrete.nonlinear`

        Parameters
        ----------
        strain : float
            strain to compute corresponding stress

        Returns
        -------
        float
            stress to the given ``strain``
        """
        if self.yield_strain <= strain <= self.cu:
            eta = self.eta(strain)
            k = self.k()
            return self.f_cm * ((k * eta - eta**2.0) / (1.0 + (k - 2) * eta))
        else:
            return 0.0


class ConcreteCompressionParabolaRectangle(ConcreteCompression):

    """
    parabola-rectangle behaviour of concrete under compression according to EN 1992-1-1 [1]_

    .. versionadded:: 0.1.0
    """

    @log.init
    def __init__(self, f_cm: float, E_cm: float):
        """
        Parameters
        ----------
        f_cm : float
            mean concrete cylinder compressive strength :math:`f_\\mathrm{cm}`
        E_cm : float
            mean elasticity modulus of concrete :math:`E_\\mathrm{cm}`

        See Also
        --------
        ConcreteCompressionNonlinear : Describes non-linear behaviour of concrete under compression
        ConcreteCompressionBiLinear : describes bi-linear behaviour of concrete under compression

        Notes
        -----
        The formula for computation of the parabola-rectangle behaviour of concrete by EN 1992-1-1 [1]_, Formula 3.17
        is given as follows. Formula :math:numref:`eq:material.concrete.parabola_rectangle` is valid in the range
        :math:`0 < |\\varepsilon| < |\\varepsilon_\\mathrm{c}|`. The here given values are all absolute values.
        As this model applies to the compression-range all values must be multiplied by (-1).

        .. math::
           :label: eq:material.concrete.parabola_rectangle

           \\sigma_\\mathrm{c} & = f_\\mathrm{c} \\cdot \\left[1 - \\left(1 -
           \\frac{\\varepsilon}{\\varepsilon_\\mathrm{c}} \\right)^{n} \\right] & &
           \\text{ for } 0 \\leq \\varepsilon \\leq \\varepsilon_\\mathrm{c}

           \\sigma_\\mathrm{c} & = f_\\mathrm{c} & & \\text{ for } \\varepsilon_\\mathrm{c} \\leq \\varepsilon
           \\leq \\varepsilon_\\mathrm{cu}

        where

        .. math::
           :label: eq:material.concrete.parabola_rectangle_helper

           \\text{ for } f_\\mathrm{ck} \\leq 50 \\text{ N/mm :sup:`2`}: &

           & \\varepsilon_\\mathrm{c}(Permil) = 2.0

           & \\varepsilon_\\mathrm{cu}(Permil) = 3.5

           & n = 2.0

           \\text{for } f_\\mathrm{ck} \\geq 50 \\text{ N/mm :sup:`2`} &

           & \\varepsilon_\\mathrm{c}(Permil) = 2.0 + 0.085 \\cdot (f_\\mathrm{ck} - 50)^{0.53}

           & \\varepsilon_\\mathrm{cu}(Permil) = 2.6 + 35 \\left[\\frac{90-f_\\mathrm{ck}}{100} \\right]^{4}

           & n = 1.4 + 23.4 \\cdot \\left[ \\frac{90-f_\\mathrm{ck}}{100} \\right]

        where :math:`\\varepsilon_\\mathrm{c}` is the strain at peak stress and :math:`\\varepsilon_\\mathrm{cu}`
        is the strain at failure.

        .. figure:: ../images/material_concrete_parabola_rectangle-light.svg
           :class: only-light
        .. figure:: ../images/material_concrete_parabola_rectangle-dark.svg
           :class: only-dark

           Parabola-rectangle relationship of concrete by EN 1992-1-1 [1]_, Fig. 3.3

        References
        ----------
        .. [1] EN 1992-1-1: Eurocode 2 - Design of concrete structures -
           Part 1-1: General rules and rules for buildings, European Committee of Standardization (CEN),
           April 2004

        Examples
        --------
        The stress-strain relationship of concrete under compression is computed as follows.

        >>> from m_n_kappa.material import ConcreteCompressionParabolaRectangle
        >>> f_cm = 30.0 # mean concrete compressive strength
        >>> E_cm = 33000 # modulus of elasticity of concrete
        >>> concrete = ConcreteCompressionParabolaRectangle(f_cm=f_cm, E_cm=E_cm)
        >>> concrete.stress_strain()
        [[-9.625, -0.0005], [-16.5, -0.001], [-20.625, -0.0015], [-22.0, -0.002], [-22.0, -0.0035]]
        """
        super().__init__(f_cm, 0.0, E_cm)

    @property
    def c(self) -> float:
        """
        strain at peak stress :math:`\\varepsilon_\\mathrm{c}`
        (see Formula :math:numref:`eq:material.concrete.parabola_rectangle_helper`)
        """
        if self.f_ck <= 50:
            return 0.001 * 2.0
        else:
            return 0.001 * (2.0 + (0.085 * (float(self.f_ck) - 50.0) ** 0.53))

    @property
    def cu(self) -> float:
        """
        failure strain of concrete :math:`\\varepsilon_\\mathrm{cu}`
        (see Formula :math:numref:`eq:material.concrete.parabola_rectangle_helper`)
        """
        return 0.001 * min(
            (2.6 + 35.0 * ((90.0 - float(self.f_ck)) / 100.0) ** 4.0), 3.5
        )

    @property
    def n(self) -> float:
        """
        exponent in formula :math:numref:`eq:material.concrete.parabola_rectangle`
        given in formula :math:numref:`eq:material.concrete.parabola_rectangle_helper`
        """
        return min(1.4 + 23.4 * ((90.0 - self.f_ck) / 100.0) ** 4.0, 2.0)

    @property
    def strains(self) -> list:
        """
        Strain-values where stresses are computed.

        Current strain-values are:

        - :math:`0.25 \\cdot \\varepsilon_\\mathrm{c}`
        - :math:`0.50 \\cdot \\varepsilon_\\mathrm{c}`
        - :math:`0.75 \\cdot \\varepsilon_\\mathrm{c}`
        - :math:`\\varepsilon_\\mathrm{c}`
        - :math:`\\varepsilon_\\mathrm{cu}`
        """
        return [0.25 * self.c, 0.5 * self.c, 0.75 * self.c, self.c, self.cu]

    def stress(self, strain: float) -> float:
        """
        computation of stresses according to formula :math:numref:`eq:material.concrete.parabola_rectangle`

        Parameters
        ----------
        strain : float
            strain to compute corresponding stress

        Returns
        -------
        float
            stress to the given ``strain``
        """
        if 0.0 <= strain <= self.c:
            return self.f_ck * (1 - (1 - strain / self.c) ** self.n)
        elif self.c < strain <= self.cu:
            return self.f_ck
        else:
            return 0.0


class ConcreteCompressionBiLinear(ConcreteCompression):
    """
    bi-linear behaviour of concrete under compression according to EN 1992-1-1 [1]_

    .. versionadded:: 0.1.0
    """

    @log.init
    def __init__(self, f_cm: float):
        """
        Parameters
        ----------
        f_cm : float
            mean concrete cylinder compressive strength :math:`f_\\mathrm{cm}`

        See Also
        --------
        ConcreteCompressionNonlinear : Describes non-linear behaviour of concrete under compression
        ConcreteCompressionParabolaRectangle : Describes parabola rectangle behaviour of concrete under compression

        Notes
        -----
        Strain at peak stress :math:`\\varepsilon_\\mathrm{c}` and strain at failure :math:`\\varepsilon_\\mathrm{cu}`
        are computed as follows according to EN 1992-1-1 [1]_, Tab. 3.1

        .. math::
           :label: eq:material.concrete.bi_linear_helper

           \\varepsilon_\\mathrm{c}(Permil) & = 1.75 + 0.55 \\cdot \\frac{f_\\mathrm{ck} - 50.0}{40.0} \\leq 1.75

           \\varepsilon_\\mathrm{cu}(Permil) & = 2.6 + 35.0 \\cdot \\left(\\frac{90.0 -
           f_\\mathrm{ck}}{100} \\right)^{4} \\leq 3.5


        .. figure:: ../images/material_concrete_bilinear-light.svg
           :class: only-light
        .. figure:: ../images/material_concrete_bilinear-dark.svg
           :class: only-dark

           Bi-linear stress-strain relationship of concrete by EN 1992-1-1 [1]_, Fig. 3.4


        References
        ----------
        .. [1] EN 1992-1-1: Eurocode 2 - Design of concrete structures -
           Part 1-1: General rules and rules for buildings, European Committee of Standardization (CEN),
           April 2004

        Examples
        --------
        The stress-strain relationship of concrete under compression is computed as follows.

        >>> from m_n_kappa.material import ConcreteCompressionBiLinear
        >>> f_cm = 30.0 # mean concrete compressive strength
        >>> E_cm = 33000 # modulus of elasticity of concrete
        >>> concrete = ConcreteCompressionBiLinear(f_cm=f_cm)
        >>> concrete.stress_strain()
        [[-22.0, -0.00175], [-22.0, -0.0035]]
        """
        super().__init__(f_cm=f_cm, yield_strain=0.0, E_cm=0.0)

    @property
    def c(self) -> float:
        """
        strain at peak stress :math:`\\varepsilon_\\mathrm{c}`
        (see Formula :math:numref:`eq:material.concrete.bi_linear_helper`)
        """
        return 0.001 * max((1.75 + 0.55 * ((self.f_ck - 50.0) / 40.0)), 1.75)

    @property
    def cu(self) -> float:
        """
        failure strain of concrete :math:`\\varepsilon_\\mathrm{cu}`
        (see Formula :math:numref:`eq:material.concrete.parabola_rectangle_helper`)
        """
        return 0.001 * min((2.6 + 35.0 * ((90.0 - self.f_ck) / 100) ** 4.0), 3.5)

    @property
    def strains(self) -> list:
        """
        Strain-values where stresses are computed.

        Current strain-values are:

        - :math:`\\varepsilon_\\mathrm{c}`
        - :math:`\\varepsilon_\\mathrm{cu}`
        """
        return [self.c, self.cu]

    def stress(self, strain: float) -> float:
        """
        computation of stresses according to formula :math:numref:`eq:material.concrete.parabola_rectangle`

        Parameters
        ----------
        strain : float
            strain to compute corresponding stress

        Returns
        -------
        float
            stress to the given ``strain``
        """
        if 0.0 <= strain < self.c:
            return self.f_ck * (self.c - strain) / self.c
        elif self.c <= strain <= self.cu:
            return self.f_ck
        else:
            return 0.0


class ConcreteTension:

    """
    define concrete tensile behaviour

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_f_cm",
        "_E_cm",
        "_f_ctm",
        "_g_f",
        "_use_tension",
        "_consider_opening_behaviour",
    )

    @log.init
    def __init__(
        self,
        f_cm: float,
        E_cm: float,
        f_ctm: float = None,
        g_f: float = None,
        use_tension: bool = True,
        consider_opening_behaviour: bool = True,
    ):
        """
        Parameters
        ----------
        f_cm : float
            mean cylinder concrete compressive strength :math:`f_\\mathrm{cm}`
        E_cm : float
            mean modulus of elasticity of concrete :math:`E_\\mathrm{cm}`
        f_ctm : float
            mean tensile concrete tensile strength :math:`f_\\mathrm{ctm}` (Default: None)
        g_f : float
            fracture energy of concrete :math:`G_\\mathrm{f}` (Default: None)
        use_tension: bool
            - ``True``: compute tensile behaviour (Default)
            - ``False``: no tensile behaviour computed
        consider_opening_behaviour: bool
            if ``True`` considers the crack opening under tension

        Notes
        -----
        If not given the concrete tensile strength :math:`f_\\mathrm{ctm}` may be computed according to
        EN 1992-1-1 [1]_, Tab. 3.1

        .. math::
           :label: eq:material.concrete.tension

           f_\\mathrm{ctm} & = 0.3 \\cdot f_\\mathrm{ck}^{2/3} \\leq C50/50

           f_\\mathrm{ctm} & = 2.12 \\cdot \\ln(1 + 0.1 \\cdot f_\\mathrm{cm}) > C50/60


        .. figure:: ../images/material_concrete_tension-light.svg
           :class: only-light
        .. figure:: ../images/material_concrete_tension-dark.svg
           :class: only-dark

           Stress-strain relationship of concrete under tension

        References
        ----------
        .. [1] EN 1992-1-1: Eurocode 2 - Design of concrete structures -
           Part 1-1: General rules and rules for buildings, European Committee of Standardization (CEN),
           April 2004

        .. [2] fib Model Code for Concrete Structures, International Federation for Structural Concrete,
           Ernst & Sohn GmbH & Co. KG, 2013, p. 78, Eq. 5.1-9

        Examples
        --------
        In case no tension is to be considered :py:class:`ConcreteTension` is initialized as follows.

        >>> from m_n_kappa.material import ConcreteTension
        >>> no_tension = ConcreteTension(f_cm=38, E_cm=33000, use_tension=False)
        >>> no_tension.stress_strain()
        [[0.0, 10.0]]

        The single tension point ``[[0.0, 10.0]]`` is needed otherwise the computation fails as soon as the concrete
        is loaded by tension and effects like redistribution of tensile stresses into rebars.

        If the tensile-capacity of the condrete is needed no parameter must be given  as ``use_tension=True`` is
        the default.

        >>> consider_tension = ConcreteTension(f_cm=38, E_cm=33000)
        >>> consider_tension.stress_strain()
        [[2.896468153816889, 8.777176223687542e-05], [0.5792936307633778, 0.1723892594303201], \
[0.0, 0.8619462971516005], [0.0, 10.0]]

        Under the hood :mod:`m_n_kappa` automatically computes the concrete tensile strength :math:`f_\\mathrm{ctm}`

        >>> consider_tension.f_ctm
        2.896468153816889

        Furthermore, the crack opening behaviour according to fib Model Code 2010 [2]_ is considered.
        If this shall not be considered :py:class:`ConcreteTension` may be initialized as follows.

        >>> consider_tension = ConcreteTension(f_cm=38, E_cm=33000, consider_opening_behaviour=False)
        >>> consider_tension.stress_strain()
        [[2.896468153816889, 8.777176223687542e-05], [0.0, 8.877176223687542e-05], [0.0, 10.0]]
        """
        self._f_cm = f_cm
        self._E_cm = E_cm
        self._f_ctm = f_ctm
        self._g_f = g_f
        self._use_tension = use_tension
        self._consider_opening_behaviour = consider_opening_behaviour

    @property
    def f_cm(self):
        """mean cylinder concrete compressive strength :math:`f_\\mathrm{cm}`"""
        return self._f_cm

    @property
    def f_ck(self):
        """characteristic cylinder concrete compressive strength :math:`f_\\mathrm{ck}`"""
        return self._f_cm - 8.0

    @property
    def E_cm(self):
        """mean modulus of elasticity of concrete :math:`E_\\mathrm{cm}`"""
        return self._E_cm

    @property
    def yield_strain(self):
        """strain at peak stresses :math:`\\varepsilon_\\mathrm{y} = f_\\mathrm{ctm} / E_\\mathrm{cm}`"""
        return self.f_ctm / self.E_cm

    @property
    def fracture_energy(self) -> float:
        """
        Fracture energy of concrete :math:`G_\\mathrm{F}` in N/mm (Newton per millimeter)

        Notes
        -----
        The formula assumes that the mean concrete compressive strength :math:`f_\\mathrm{cm}` is given in
        N/mm :sup:`2`.
        """
        return 0.001 * 73.0 * self.f_cm * 0.18

    @property
    def f_ctm(self) -> float:
        """
        concrete tensile strength :math:`f_\\mathrm{ctm}`.
        If not given by input :math:`f_\\mathrm{ctm}` is computed by Formula :math:numref:`eq:material.concrete.tension`
        """
        if self._f_ctm is None:
            if self.f_ck <= 50.0:
                return 0.3 * self.f_ck ** (2.0 / 3.0)
            else:
                return 2.12 * math.log(1.0 + 0.1 * self.f_cm)
        else:
            return self._f_ctm

    @property
    def use_tension(self) -> bool:
        return self._use_tension

    @property
    def consider_opening_behaviour(self) -> bool:
        """if ``True`` considers the crack opening behaviour according to fib-model-code [2]_"""
        return self._consider_opening_behaviour

    @property
    def w(self) -> float:
        """crack-opening at :math:`0.2 \\cdot f_\\mathrm{ctm}`"""
        return self.fracture_energy / self.f_ctm

    @property
    def wu(self) -> float:
        """crack-opening where no tension is transmitted anymore :math:`w_\\mathrm{u} = 5.0 \\cdot w`"""
        return 5.0 * self.w

    def stress_strain(self) -> list:
        """
        stress-strain-relationship of concrete under tension
        """
        stress_strain = []  # [[0.0, 0.0]]
        if self.use_tension:
            stress_strain.append([self.f_ctm, self.yield_strain])
            if self.consider_opening_behaviour:
                stress_strain.append([0.2 * self.f_ctm, self.w])
                stress_strain.append([0.0, self.wu])
            else:
                stress_strain.append([0.0, self.yield_strain + 0.000001])
        stress_strain.append([0.0, 10.0])
        return positive_sign(stress_strain)


class Concrete(Material):

    """
    Concrete material

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_f_cm",
        "_f_ctm",
        "_use_tension",
        "_compression_stress_strain_type",
        "_tension_stress_strain_type",
        "_compression",
        "_tension",
        "_stress_strain",
    )

    @log.init
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
            mean concrete cylinder compression strength :math:`f_\\mathrm{cm}`
        f_ctm : float
            mean tensile strength :math:`f_\\mathrm{ctm}` (Default: None)
        use_tension : bool
            - ``True``: considers tension (Default)
            - ``False``: does not consider tension
        compression_stress_strain_type : str
            sets section_type of stress-strain_value curve under compression.
            Possible values are:

            - ``'Nonlinear'`` (Default)
            - ``'Parabola'``
            - ``'Bilinear'``

        tension_stress_strain_type : str
            sets section_type of strain_value-stain curve under tension
            Possible values are:

            - ``'Default'``
            - ``'consider opening behaviour'``

        See Also
        --------
        Steel: material-behaviour of steel
        Reinforcement : material-behaviour of reinforcement

        Notes
        -----
        For Details regarding the computation of these relastionships check out the corresponding classes.

        **Concrete under compression**

        Following stress-strain-relationships may be chosen to describe the behaviour of concrete under compression.

        .. grid:: 1 2 3 3

           .. grid-item::

              .. figure:: ../images/material_concrete_nonlinear-light.svg
                 :class: only-light
              .. figure:: ../images/material_concrete_nonlinear-dark.svg
                 :class: only-dark

                 ``Nonlinear`` stress-strain-relationship of concrete under compression acc. EN 1992-1-1 [1]_

           .. grid-item::

              .. figure:: ../images/material_concrete_parabola_rectangle-light.svg
                 :class: only-light
              .. figure:: ../images/material_concrete_parabola_rectangle-dark.svg
                 :class: only-dark

                 ``Parabola``-Rectangle stress-strain-relationship of concrete under compression acc. EN 1992-1-1 [1]_

           .. grid-item::

              .. figure:: ../images/material_concrete_bilinear-light.svg
                 :class: only-light
              .. figure:: ../images/material_concrete_bilinear-dark.svg
                 :class: only-dark

                 ``Bilinear`` stress-strain-relationship of concrete under compression acc. EN 1992-1-1 [1]_

        Classes:

        - ``Nonlinear``: :py:class:`~m_n_kappa.material.ConcreteCompressionNonlinear`
        - ``Parabola``: :py:class:`~m_n_kappa.material.ConcreteCompressionParabolaRectangle`
        - ``Bilinear``: :py:class:`~m_n_kappa.material.ConcreteCompressionBiLinear`

        **Concrete under tension**

        .. figure:: ../images/material_concrete_tension-light.svg
           :class: only-light
        .. figure:: ../images/material_concrete_tension-dark.svg
           :class: only-dark

           Stress-strain-relationship of concrete under tension
           (Class :py:class:`~m_n_kappa.material.ConcreteTension`)

        References
        ----------
        .. [1] EN 1992-1-1: Eurocode 2 - Design of concrete structures -
           Part 1-1: General rules and rules for buildings, European Committee of Standardization (CEN),
           April 2004

        .. [2] fib Model Code for Concrete Structures, International Federation for Structural Concrete,
           Ernst & Sohn GmbH & Co. KG, 2013, p. 78, Eq. 5.1-9

        Examples
        --------
        A ``Nonlinear`` concrete stress-strain-relationship neglecting the tensile behaviour of concrete is computed as
        follows.

        >>> from m_n_kappa import Concrete
        >>> nonlinear_no_tension = Concrete(f_cm=30.0, use_tension=False)
        >>> nonlinear_no_tension.stress_strain
        [StressStrain(stress=-16.9202915, strain=-0.0035), \
StressStrain(stress=-26.5783275, strain=-0.0027546), \
StressStrain(stress=-30.0, strain=-0.0020091), \
StressStrain(stress=-28.8050612, strain=-0.0015849), \
StressStrain(stress=-19.6170303, strain=-0.0007925), \
StressStrain(stress=-11.1281632, strain=-0.0003923), \
StressStrain(stress=0.0, strain=0.0), \
StressStrain(stress=0.0, strain=10.0)]

        Whereas a ``Parabola``-Rectangle-behaviour is computed as follows.

        >>> parabola_no_tension = Concrete(f_cm=30.0, use_tension=False,
        ...                                compression_stress_strain_type='Parabola')
        >>> parabola_no_tension.stress_strain
        [StressStrain(stress=-22.0, strain=-0.0035), \
StressStrain(stress=-22.0, strain=-0.002), \
StressStrain(stress=-20.625, strain=-0.0015), \
StressStrain(stress=-16.5, strain=-0.001), \
StressStrain(stress=-9.625, strain=-0.0005), \
StressStrain(stress=0.0, strain=0.0), \
StressStrain(stress=0.0, strain=10.0)]

        And a ``Bilinear`` is computed as follows

        >>> bilinear_no_tension = Concrete(f_cm=30.0, use_tension=False,
        ...                                compression_stress_strain_type='Bilinear')
        >>> bilinear_no_tension.stress_strain
        [StressStrain(stress=-22.0, strain=-0.0035), \
StressStrain(stress=-22.0, strain=-0.00175), \
StressStrain(stress=0.0, strain=0.0), \
StressStrain(stress=0.0, strain=10.0)]

        In case tension is to be considered the following expression is okay (with ``Nonlinear`` compression behaviour).

        >>> with_tension = Concrete(f_cm=30.0)
        >>> with_tension.stress_strain
        [StressStrain(stress=-16.9202915, strain=-0.0035), \
StressStrain(stress=-26.5783275, strain=-0.0027546), \
StressStrain(stress=-30.0, strain=-0.0020091), \
StressStrain(stress=-28.8050612, strain=-0.0015849), \
StressStrain(stress=-19.6170303, strain=-0.0007925), \
StressStrain(stress=-11.1281632, strain=-0.0003923), \
StressStrain(stress=0.0, strain=0.0), \
StressStrain(stress=2.3554273, strain=7.7e-05), \
StressStrain(stress=0.0, strain=7.8e-05), \
StressStrain(stress=0.0, strain=10.0)]

        Furthermore, the crack-opening of the conrete and its effect on the tensile behaviour may be considered by
        adding ``tension_stress_strain_type='consider opening behaviour'`` that is derived
        from fib Model Code 2010 [2]_.

        >>> with_tension_opening = Concrete(f_cm=30.0,
        ...                        tension_stress_strain_type='consider opening behaviour')
        >>> with_tension_opening.stress_strain
        [StressStrain(stress=-16.9202915, strain=-0.0035), \
StressStrain(stress=-26.5783275, strain=-0.0027546), \
StressStrain(stress=-30.0, strain=-0.0020091), \
StressStrain(stress=-28.8050612, strain=-0.0015849), \
StressStrain(stress=-19.6170303, strain=-0.0007925), \
StressStrain(stress=-11.1281632, strain=-0.0003923), \
StressStrain(stress=0.0, strain=0.0), \
StressStrain(stress=2.3554273, strain=7.7e-05), \
StressStrain(stress=0.4710855, strain=0.1673582), \
StressStrain(stress=0.0, strain=0.8367908), \
StressStrain(stress=0.0, strain=10.0)]
        """
        self._f_cm = float(f_cm)
        self._f_ctm = make_float(f_ctm)
        self._use_tension = use_tension
        self._compression_stress_strain_type = compression_stress_strain_type
        self._tension_stress_strain_type = tension_stress_strain_type
        self._compression = self.__set_compression()
        self._tension = self.__set_tension()
        super().__init__(
            section_type="slab", stress_strain=self.__build_stress_strain()
        )

    def __repr__(self) -> str:
        return (
            f"Concrete(f_cm={self._f_cm}, "
            f"f_ctm={self._f_ctm}, "
            f"use_tension={self._use_tension}, "
            f"compression_stress_strain_type={self._compression_stress_strain_type}), "
            f"tension_stress_strain_type={self._tension_stress_strain_type})"
        )

    @str_start_end
    def __str__(self) -> str:
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
                f"E_cm = {self.E_cm:.1f} N/mm^2, | epsilon_y={self.epsilon_y:.4f}",
            ]
        )

    def _print_compressive_values(self) -> str:
        text = [
            "Compressive strength",
            "--------------------",
            f"f_ck = {self.f_ck:.1f} N/mm^2 | f_cm = {self.f_cm:.1f} N/mm^2",
            f"epsilon_c = {self.compression.c:.4f} | epsilon_cu = {self.compression.cu:.4f}",
        ]
        return print_sections(text)

    def _print_tensile_values(self) -> str:
        text = [
            "Tensile strength",
            "----------------",
            f"f_ctm = {self.tension.f_ctm:.1f} N/mm^2",
        ]
        return print_sections(text)

    @property
    def compression(self) -> ConcreteCompression:
        """concrete under compression"""
        return self._compression

    @property
    def compression_stress_strain_type(self) -> str:
        """chosen stress-strain-type for concrete under compression"""
        return self._compression_stress_strain_type

    @compression_stress_strain_type.setter
    def compression_stress_strain_type(self, stress_strain_type: str) -> None:
        """set new stress-strain-type for concrete under compression"""
        self._compression_stress_strain_type = stress_strain_type
        self.__set_compression()

    @property
    def E_cm(self) -> float:
        """modulus of elasticity of concrete :math:`E_\\mathrm{cm}` acc. EN 1992-1-1 [1]_"""
        return 22000.0 * (self.f_cm / 10) ** 0.3

    @property
    def epsilon_y(self) -> float:
        """yield strain of concrete under compression :math:`0.4 \\cdot f_\\mathrm{cm} / E_\\mathrm{cm}`"""
        return 0.4 * self.f_cm / self.E_cm

    @property
    def f_cm(self) -> float:
        """mean concrete compressive strength :math:`f_\\mathrm{cm}`"""
        return self._f_cm

    @property
    def f_ck(self) -> float:
        """mean concrete compressive strength :math:`f_\\mathrm{ck} = f_\\mathrm{cm}-8`"""
        return self.f_cm - 8.0

    @property
    def section_type(self) -> str:
        return "slab"

    @property
    def tension(self) -> ConcreteTension:
        """concrete under tension"""
        return self._tension

    @property
    def tension_stress_strain_type(self) -> str:
        """chosen stress-strain-type for concrete under tension"""
        return self._tension_stress_strain_type

    @tension_stress_strain_type.setter
    def tension_stress_strain_type(self, stress_strain_type: str) -> None:
        """set new stress-strain-type for concrete under tension"""
        self._tension_stress_strain_type = stress_strain_type
        self.__set_tension()

    @property
    def use_tension(self) -> bool:
        """defines usage of tension"""
        return self._use_tension

    def __set_compression(self) -> ConcreteCompression:
        """sets concrete under compression according to user-input"""
        typ = self.compression_stress_strain_type.replace("-", "").replace(" ", "")
        typ = typ.upper()
        if typ == "NONLINEAR":
            return ConcreteCompressionNonlinear(self.f_cm, self.epsilon_y, self.E_cm)
        elif typ == "PARABOLA":
            return ConcreteCompressionParabolaRectangle(self.f_cm, self.epsilon_y)
        elif typ == "BILINEAR":
            return ConcreteCompressionBiLinear(self.f_cm)
        else:
            raise ValueError(
                str(typ)
                + ' not a valid value. Valid values are "Nonlinear", "Parabola" or "Bilinear"'
            )

    def __set_tension(self) -> ConcreteTension:
        """sets concrete under tension according to user-input"""
        stress_strain_type = self.tension_stress_strain_type.replace("-", "").replace(
            " ", ""
        )
        if stress_strain_type.upper() == "DEFAULT":
            return ConcreteTension(
                self.f_cm,
                self.E_cm,
                self._f_ctm,
                use_tension=self.use_tension,
                consider_opening_behaviour=False,
            )
        elif stress_strain_type.upper() == "CONSIDEROPENINGBEHAVIOUR":
            return ConcreteTension(
                self.f_cm,
                self.E_cm,
                self._f_ctm,
                use_tension=self.use_tension,
                consider_opening_behaviour=True,
            )
        else:
            raise ValueError(
                str(stress_strain_type)
                + ' is not a valid value. Valid value is "Default" or "Consider Opening behaviour"'
            )

    def __build_stress_strain(self) -> list[StressStrain]:
        """builds the stress-strain-curve of the concrete"""
        stress_strains = self.compression.stress_strain() + self.tension.stress_strain()
        stress_strains.append([0.0, 0.0])
        stress_strains = remove_duplicates(stress_strains)
        stress_strains.sort(key=operator.itemgetter(1), reverse=False)
        stress_strains = [
            StressStrain(stress_strain[0], stress_strain[1])
            for stress_strain in stress_strains
        ]
        return stress_strains


class Steel(Material):

    """
    Steel material

    .. versionadded:: 0.1.0

    Provides a stress-strain material behaviour of structural steel material.
    It is assumed that steel has the same behaviour under tension and under compression.
    """

    __slots__ = "_f_y", "_f_u", "_failure_strain", "_E_a", "_stress_strain"

    @log.init
    def __init__(
        self,
        f_y: float = None,
        f_u: float = None,
        failure_strain: float = None,
        E_a: float = 210000.0,
    ):
        """
        .. note::

           Assumes Newton (N) and Millimeter (mm) as basic units.
           In case other units are used appropriate value for modulus of elasticity `E_a` must be provided.

        Parameters
        ----------
        f_y : float
            yield strength :math:`f_\\mathrm{y}` (Default: None)
        f_u : float
            tensile strength :math:`f_\\mathrm{u}` (Default: None)
        failure_strain : float
            tensile strain :math:`\\varepsilon_\\mathrm{u}` (Default: None)
        E_a : float
            modulus of elasticity :math:`E_\\mathrm{a}` (Default: 210000 N/mm :sup:`2`)
        See Also
        --------
        Concrete : material-behaviour of concrete
        Reinforcement : material-behaviour of reinforcement

        Notes
        -----
        .. grid:: 1 2 3 3

           .. grid-item::

              .. figure:: ../images/material_steel_elastic-light.svg
                 :class: only-light
              .. figure:: ../images/material_steel_elastic-dark.svg
                 :class: only-dark

                 Elastic stress-strain-relationship of steel

           .. grid-item::

              .. figure:: ../images/material_steel_bilinear-light.svg
                 :class: only-light
              .. figure:: ../images/material_steel_bilinear-dark.svg
                 :class: only-dark

                 Bi-linear stress-strain-relationship of steel

           .. grid-item::

              .. figure:: ../images/material_steel_trilinear-light.svg
                 :class: only-light
              .. figure:: ../images/material_steel_trilinear-dark.svg
                 :class: only-dark

                 Bi-linear stress-strain-relationship with hardening of steel

        Examples
        --------
        The stress-strain-relationships consists always of a number of :py:class:`~m_n_kappa.material.StressStrain`
        points.
        Three forms of the stress-strain relationship are possible:

        1. ``f_u = None`` and ``epsilon_u = None``: Linear-elastic behaviour.

        >>> from m_n_kappa import Steel
        >>> elastic_steel = Steel()
        >>> elastic_steel.stress_strain
        [StressStrain(stress=-210000.0, strain=-1.0), \
StressStrain(stress=-0.0, strain=-0.0), \
StressStrain(stress=210000.0, strain=1.0)]

        2. ``f_u = None``: Bi-linear behaviour where ``f_u = f_y``

        >>> bilinear_steel = Steel(f_y=355, failure_strain=0.15)
        >>> bilinear_steel.stress_strain
        [StressStrain(stress=-355.0, strain=-0.15), \
StressStrain(stress=-355.0, strain=-0.0016905), \
StressStrain(stress=-0.0, strain=-0.0), \
StressStrain(stress=355.0, strain=0.0016905), \
StressStrain(stress=355.0, strain=0.15)]

        3. All values are not none:
           Bi-linear behaviour with following stress-strain points
           (:math:`f_\\mathrm{y}` | :math:`\\varepsilon_\\mathrm{y}`),
           (:math:`f_\\mathrm{u}` | :math:`\\varepsilon_\\mathrm{u}`).
           Where the strain at yield is computed like :math:`\\varepsilon_\\mathrm{y} = f_\\mathrm{y} / E_\\mathrm{a}`

        >>> steel = Steel(f_y=355, f_u=400, failure_strain=0.15)
        >>> steel.stress_strain
        [StressStrain(stress=-400.0, strain=-0.15), \
StressStrain(stress=-355.0, strain=-0.0016905), \
StressStrain(stress=-0.0, strain=-0.0), \
StressStrain(stress=355.0, strain=0.0016905), \
StressStrain(stress=400.0, strain=0.15)]

        """
        self._f_y = make_float(f_y)
        self._f_u = make_float(f_u)
        self._failure_strain = make_float(failure_strain)
        self._E_a = make_float(E_a)
        super().__init__(
            section_type="girder", stress_strain=self.__build_stress_strain()
        )

    def __repr__(self):
        return (
            f"Steel(f_y={self.f_y}, "
            f"f_u={self.f_u}, "
            f"failure_strain={self.failure_strain}, "
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
            text.append(f"f_y: {self.f_y:.1f} N/mm^2 | epsilon_y: {self.epsilon_y:.5f}")
        if self.__is_plastic:
            text.append(
                f"f_u: {self.f_u:.1f} N/mm^2 | failure_strain: {self.failure_strain:.5f}"
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
            text.append(f" {point.stress:9.1f} | {point.strain:9.5f}")
        return "\n".join(text)

    @property
    def section_type(self) -> str:
        return "girder"

    @property
    def __is_elastic(self) -> bool:
        """determines if passed arguments allow an elastic stress-strain relationship"""
        if self.f_y is None or self.failure_strain is None:
            return True
        else:
            return False

    @property
    def __is_ideal_plastic(self) -> bool:
        """determines if passed arguments allow a ideal-plastic stress-strain relationship"""
        if (
            self.f_y is not None
            and self.failure_strain is not None
            and self.f_u is None
        ):
            return True
        else:
            return False

    @property
    def __is_plastic(self) -> bool:
        """determines if passed arguments allow a plastic stress-strain relationship"""
        if (
            self.f_y is not None
            and self.failure_strain is not None
            and self.f_u is not None
        ):
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
        """yield strength :math:`f_\\mathrm{y}`"""
        return self._f_y

    @property
    def f_u(self) -> float:
        if self._f_u is not None and self._failure_strain is not None:
            return self._f_u

    @property
    def failure_strain(self) -> float:
        """tensile strain :math:`\\varepsilon_\\mathrm{u}`"""
        return self._failure_strain

    @property
    def E_a(self) -> float:
        """modulus of elasticity :math:`E_\\mathrm{a}`"""
        return self._E_a

    @property
    def epsilon_y(self) -> float:
        """yield strength :math:`f_\\mathrm{y}`"""
        if self.f_y is not None:
            return self.f_y / self.E_a

    def stress_strain_standard(self) -> list:
        """standard stress-strain-relationship"""
        stress_strain = [
            [0.0, 0.0],
        ]
        if self.__is_elastic:
            stress_strain.append([self.E_a, 1.0])
        else:
            stress_strain.append([self.f_y, self.epsilon_y])
        if self.__is_ideal_plastic:
            stress_strain.append([self.f_y, self.failure_strain])
        if self.__is_plastic:
            stress_strain.append([self.f_u, self.failure_strain])
        return stress_strain

    @property
    def tension_stress_strain(self) -> list:
        """stress-strain-relationship under tension (positive sign)"""
        return positive_sign(self.stress_strain_standard())

    @property
    def compression_stress_strain(self) -> list:
        """stress-strain-relationship under compression (negative sign)"""
        return negative_sign(self.stress_strain_standard())

    def __build_stress_strain(self) -> list[StressStrain]:
        """builds the full stress-strain-curve"""
        stress_strains = self.compression_stress_strain + self.tension_stress_strain
        stress_strains.sort()
        stress_strains = remove_duplicates(stress_strains)
        return [
            StressStrain(stress_strain[0], stress_strain[1])
            for stress_strain in stress_strains
        ]


class Reinforcement(Steel):

    """
    Reinforcement material

    .. versionadded: 0.1.0
    """

    __slots__ = "_f_y", "_f_u", "_failure_strain", "_E_a", "_stress_strain"

    @log.init
    def __init__(
        self,
        f_s: float = None,
        f_su: float = None,
        failure_strain: float = None,
        E_s: float = 200000.0,
    ):
        """
        Parameters
        ----------
        f_s : float
            Yield strength of the reinforcement :math:`f_\\mathrm{s}` (Default: None)
        f_su : float
            Tensile strength of the reinforcement :math:`f_\\mathrm{su}` (Default: None)
        failure_strain : float
            Tensile strain of the reinforcement :math:`\\varepsilon_\\mathrm{su}` (Default: None)
        E_s  : float
            Modulus of elasticity of the reinforcement :math:`E_\\mathrm{s}` (Default: 200000 N/mm :sup:`2`)

        See Also
        --------
        Concrete : material-behaviour of concrete
        Steel: material-behaviour of steel

        Examples
        --------
        1. ``f_su = None`` and ``epsilon_su = None``: Linear-elastic behaviour.

        >>> from m_n_kappa import Reinforcement
        >>> elastic_reinforcement = Reinforcement()
        >>> elastic_reinforcement.stress_strain
        [StressStrain(stress=-200000.0, strain=-1.0), \
StressStrain(stress=-0.0, strain=-0.0), \
StressStrain(stress=200000.0, strain=1.0)]

        2. ``f_su = None``: Bi-linear behaviour where ``f_su = f_s``

        >>> bilinear_reinforcement = Reinforcement(f_s=500.0, failure_strain=0.25)
        >>> bilinear_reinforcement.stress_strain
        [StressStrain(stress=-500.0, strain=-0.25), \
StressStrain(stress=-500.0, strain=-0.0025), \
StressStrain(stress=-0.0, strain=-0.0), \
StressStrain(stress=500.0, strain=0.0025), \
StressStrain(stress=500.0, strain=0.25)]

        3. All values are not none:
           Bi-linear behaviour with following stress-strain points
           (:math:`f_\\mathrm{s}` | :math:`\\varepsilon_\\mathrm{s}`),
           (:math:`f_\\mathrm{su}` | :math:`\\varepsilon_\\mathrm{su}`).
           Where the strain at yield is computed like :math:`\\varepsilon_\\mathrm{s} = f_\\mathrm{s} / E_\\mathrm{s}`

        >>> reinforcement = Reinforcement(f_s=500.0, f_su=550.0, failure_strain=0.25)
        >>> reinforcement.stress_strain
        [StressStrain(stress=-550.0, strain=-0.25), \
StressStrain(stress=-500.0, strain=-0.0025), \
StressStrain(stress=-0.0, strain=-0.0), \
StressStrain(stress=500.0, strain=0.0025), \
StressStrain(stress=550.0, strain=0.25)]

        """
        super().__init__(f_s, f_su, failure_strain, E_s)

    @property
    def section_type(self):
        return "slab"

    @property
    def f_s(self) -> float:
        """Yield strength of the reinforcement :math:`f_\\mathrm{s}`"""
        return self.f_y

    @property
    def f_su(self) -> float:
        """Tensile strength of the reinforcement :math:`f_\\mathrm{su}`"""
        return self.f_u

    @property
    def failure_strain(self) -> float:
        """Failure-strain of reinforcement :math:`\\varepsilon_\\mathrm{su}`"""
        return self._failure_strain

    @property
    def E_s(self) -> float:
        """Modulus of elasticity of the reinforcement :math:`E_\\mathrm{s}`"""
        return self.E_a
