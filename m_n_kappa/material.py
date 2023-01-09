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
    stress: float
    strain: float

    def pair(self) -> list[float]:
        """stress-strain-point as list"""
        return [self.stress, self.strain]


class Material:

    """
    Provides basic functionality for materials

    .. versionadded: 0.1.0

    In case custom-type materials are created these must inherit from this class.
    """

    def __init__(self, section_type: str, stress_strain: list[StressStrain] = None):
        """
        Parameters
        ----------
        stress_strain : list[:py:class:`~m_n_kappa.material.StressStrain´]
            list with stress-strain_value-relationship
        section_type : str
            section_type of section this material is ordered to.
            Possible values are:
            - slab
            - girder

        Examples
        --------

        **Base class**

        All material-models needs inheritance from :py:class:`~m_n_kappa.material.Material` to achieve basic
        functionality.

        Stress-strain-points in the stress-strain-relationships need to be defined
        by :py:class:`m_n_kappa.material.StressStrain`.

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

        Raises
        ------
        ValueError
            when strain is outside the boundary values of the material-model
        """
        material_index = self._get_material_index(strain)
        if material_index is None:
            raise ValueError(
                f"{strain=} -> None,\n"
                f"{self.__str__()}"
            )
        return self._interpolate_stress(strain, material_index)

    def sort_strains(self, reverse: bool = False) -> None:
        """sorts stress-strain_value-relationship depending on strains

        Parameters
        ----------
        reverse : bool
            - ``True``: sorts strains descending
            - ``False``: sorts strains ascending (Default)
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
        if material_index is None:
            raise TypeError(f"List indices must be integers or slices, not NoneType.\n"
                            f"Material: {self.__str__()}")
        return interpolation(
            position_value=strain,
            first_pair=self.stress_strain[material_index].pair(),
            second_pair=self.stress_strain[material_index + 1].pair(),
        )


class ConcreteCompression(ABC):
    """
    Meta-class for concrete under compression

    .. versionadded:: 0.1.0

    Several models are given to describe concrete under compression.
    This class works as basis for implementing these models and
    give them a similar interface.
    """
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

           \\sigma_\\mathrm{c} & = f_\\mathrm{c} \\cdot \\left[1 - \\left(1 - \\frac{\\varepsilon}{\\varepsilon_\\mathrm{c}}
           \\right)^{n} \\right] & & \\text{ for } 0 \\leq \\varepsilon \leq \\varepsilon_\\mathrm{c}

           \\sigma_\\mathrm{c} & = f_\\mathrm{c} & & \\text{ for } \\varepsilon_\\mathrm{c} \\leq \\varepsilon \leq \\varepsilon_\\mathrm{cu}

        where

        .. math::
           :label: eq:material.concrete.parabola_rectangle_helper

           \\text{ for } f_\\mathrm{ck} \\leq 50 \\text{ N/mm²}: &

           & \\varepsilon_\\mathrm{c}(Permil) = 2.0

           & \\varepsilon_\\mathrm{cu}(Permil) = 3.5

           & n = 2.0

           \\text{for } f_\\mathrm{ck} \\geq 50 \\text{ N/mm²} &

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
        return [0.25 * self.c, 0.5 * self.c, 0.75*self.c, self.c, self.cu]

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

           \\varepsilon_\\mathrm{cu}(Permil) & = 2.6 + 35.0 \\cdot \\left(\\frac{90.0 - f_\\mathrm{ck}}{100} \\right)^{4} \\leq 3.5


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
            cylinder concrete compressive strength :math:`f_\\mathrm{cm}`
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

        """
        self._f_cm = f_cm
        self._E_cm = E_cm
        self._f_ctm = f_ctm
        self._g_f = g_f
        self._use_tension = use_tension
        self._consider_opening_behaviour = consider_opening_behaviour

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
    def fracture_energy(self) -> float:
        """
        Fracture energy of concrete :math:`G_\\mathrm{F}` in N/mm (Newton per millimeter)

        .. note::

            The formula assumes that the mean concrete compressive strength :math:`f_\\mathrm{cm}` is given in
            N/mm².

        .. seealso::

            fib Model Code for Concrete Structures, International Federation for Structural Concrete,
            Ernst & Sohn GmbH & Co. KG, 2013, p. 78, Eq. 5.1-9
        """
        return 0.001 * 73.0 * self.f_cm * 0.18

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
        stress_strain = []  # [[0.0, 0.0]]
        if self.use_tension:
            stress_strain.append([self.f_ctm, self.yield_strain])
        if self.consider_opening_behaviour:
            stress_strain.append([0.2*self.f_ctm, self.fracture_energy / self.f_ctm])
            stress_strain.append([0.0, 5.0 * self.fracture_energy / self.f_ctm])
        else:
            stress_strain.append([0.0, self.yield_strain + 0.000001])
        stress_strain.append([0.0, 10.0])
        return positive_sign(stress_strain)

    @property
    def use_tension(self) -> bool:
        return self._use_tension

    @property
    def consider_opening_behaviour(self) -> bool:
        return self._consider_opening_behaviour


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

    def __repr__(self) -> str:
        return (
            f"Concrete(f_cm={self.f_cm}, "
            f"f_ctm={self._f_ctm}, "
            f"use_tension={self.use_tension}, "
            f"compression_stress_strain_type={self.compression_stress_strain_type}), "
            f"tension_stress_strain_type={self.tension_stress_strain_type})"
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
        return self._compression

    @property
    def compression_stress_strain_type(self) -> str:
        return self._compression_stress_strain_type

    @compression_stress_strain_type.setter
    def compression_stress_strain_type(self, stress_strain_type: str) -> None:
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
    def tension_stress_strain_type(self, stress_strain_type: str) -> None:
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
            return ConcreteTension(
                self.f_cm,
                self.E_cm,
                self._f_ctm,
                self.use_tension,
                consider_opening_behaviour=False
            )
        elif stress_strain_type.upper() == "CONSIDEROPENINGBEHAVIOUR":
            return ConcreteTension(
                self.f_cm,
                self.E_cm,
                self._f_ctm,
                self.use_tension,
                consider_opening_behaviour=True
            )
        else:
            raise ValueError(
                str(stress_strain_type)
                + ' is not a valid value. Valid value is "Default"'
            )

    def __build_stress_strain(self) -> list[StressStrain]:
        stress_strains = self.compression.stress_strain() + self.tension.stress_strain()
        stress_strains.append([0.0, 0.0])
        stress_strains = remove_duplicates(stress_strains)
        stress_strains.sort(key=lambda x: x[1], reverse=False)
        stress_strains = [
            StressStrain(stress_strain[0], stress_strain[1])
            for stress_strain in stress_strains
        ]
        return stress_strains


class Steel(Material):

    """
    Steel material

    Provides a stress-strain material behaviour of structural steel material.
    Three forms of the stress-strain relationship are possible:

       1. ``f_u = None`` and ``epsilon_u = None``:
          Linear-elastic behaviour.

       2. ``f_u = None``:
          Bi-linear behaviour where ``f_u = f_y``
       3. All values are not none:
          Bi-linear behaviour with following stress-strain points
          (:math:`f_\\mathrm{y}` | :math:`\\varepsilon_\\mathrm{y}`),
          (:math:`f_\\mathrm{u}` | :math:`\\varepsilon_\\mathrm{u}`).
          Where the strain at yield is computed like :math:`\\varepsilon_\\mathrm{y} = f_\\mathrm{y} / E_\\mathrm{a}`

    .. note::

       Assumes Newton (N) and Millimeter (mm) as basic units.
       In case other units are used appropriate value for modulus of elasticity `E_a` must be provided.
    """

    def __init__(
        self,
        f_y: float,
        f_u: float = None,
        epsilon_u: float = None,
        E_a: float = 210000.0,
    ):
        """
        Parameters
        ----------
        f_y : float
            yield strength :math:`f_\\mathrm{y}`
        f_u : float
            tensile strength :math:`f_\\mathrm{u}` (Default: None)
        epsilon_u : float
            tensile strain :math:`\\varepsilon_\\mathrm{u}` (Default: None)
        E_a : float
            modulus of elasticity :math:`E_\\mathrm{a}` (Default: 210000 N/mm²)
        """
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

    """
    Reinforcement material

    Inherits from :py:class:`Steel`.
    """

    def __init__(self, f_s: float, f_su: float = None, epsilon_su: float = None, E_s: float = 200000.0):
        """
        Parameters
        ----------
        f_s : float
            Yield strength of the reinforcement :math:`f_\\mathrm{s}`
        f_su : float
            Tensile strength of the reinforcement :math:`f_\\mathrm{su}` (Default: None)
        epsilon_su : float
            Tensile strain of the reinforcement :math:`\\varepsilon_\\mathrm{su}` (Default: None)
        E_s  : float
            Modulus of elasticity of the reinforcement :math:`E_\\mathrm{s}` (Default: 200000 N/mm²)
        """
        super().__init__(f_s, f_su, epsilon_su, E_s)

    @property
    def section_type(self):
        return "slab"

    @property
    def f_s(self) -> float:
        return self.f_y

    @property
    def f_su(self) -> float:
        return self.f_u

    @property
    def epsilon_su(self) -> float:
        return self.epsilon_su

    @property
    def E_s(self) -> float:
        return self.E_a