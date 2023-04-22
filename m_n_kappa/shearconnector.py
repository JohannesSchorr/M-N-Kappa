import operator
from dataclasses import dataclass

from .general import interpolation
from .material import Concrete
from .log import LoggerMethods

log = LoggerMethods(__name__)


@dataclass(slots=True)
class LoadSlip:

    """
    Load-Slip point of a shear connector

    .. versionadded:: 0.2.0

    """

    load: float
    slip: float

    def pair(self) -> list[float, float]:
        """given values as slip"""
        return [self.load, self.slip]


class ShearConnector:

    """
    Base-Class for the shear-connectors

    .. versionadded:: 0.2.0

    Provide basic functionality for defining a shear-connector in :py:mod:`m_n_kappa`.
    """

    def __init__(self, load_slips: list[LoadSlip]):
        """
        Parameters
        ----------
        load_slips : list[:py:class:`~m_n_kappa.LoadSlip`])
            load-slip-relationship of the shear connector
            
        See Also
        --------
        HeadedStud : Headed stud shear connector
        """
        self._load_slips = load_slips
        self._s_max = max(self.load_slips, key=operator.attrgetter('slip')).slip
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(load_slips={self.load_slips})"

    @property
    def load_slips(self) -> list[LoadSlip]:
        """load-slip-relationship"""
        return self._load_slips
    
    @property
    def s_max(self) -> float:
        """Maximum slip of the shear connector"""
        return self._s_max

    def shear_load(self, slip: float) -> float:
        """
        determine the shear-load of the shear connector under a given slip

        Parameters
        ----------
        slip : float
           slip the shear-load is to be determined of

        Returns
        -------
        float
            shear-load of the shear-connector corresponding to the given slip
        """
        for index in range(len(self.load_slips) - 1):
            lower_slip = self.load_slips[index]
            upper_slip = self.load_slips[index + 1]
            if (
                lower_slip.slip < slip <= upper_slip.slip
            ):  # assumes that first slip-value is zero
                return interpolation(slip, lower_slip.pair(), upper_slip.pair())


class HeadedStud(ShearConnector):

    """
    Headed stud shear-connector

    .. versionadded:: 0.2.0
    """

    def __init__(
        self,
        d: float,
        h_sc: float,
        f_u: float,
        f_cm: float,
        s_max: float = 6.0,
        h_p: float = None,
        b_o: float = None,
        n_r: int = 1,
    ):
        """
        Parameters
        ----------
        d : float
           diameter of the shank of the headed stud
        h_sc : float
           height of the headed stud
        f_u : float
           tensile strength of the headed stud
        f_cm : float
           mean concrete strength of the concrete surrounding the headed stud
        s_max : float
           maximum slip of the headed stud at failure (Default: 6 mm)
        h_p : float
           height of a profiled steel sheeting (Default: None)
        b_o : float
           decisive width of a profiled steel sheeting (Default: None)
        n_r : int
           number of headed studs in a row (Default: 1)

        References
        ----------
        .. [1] Roik, K.-H.; Hanswille, G.; Lanna, A., *Hintergrundbericht zu EUROCODE 4, Abschnitt 6.3.2 Bolzenduebel
             research report RS II 1-674102 - 8630, 1988
        """
        self._d = d
        self._h_sc = h_sc
        self._f_u = f_u
        self._f_cm = f_cm
        self._s_max = s_max
        self._h_p = h_p
        self._b_o = b_o
        self._n_r = n_r
        self._concrete = Concrete(f_cm)
        self._P = self._compute_P()
        super().__init__(self._define_load_slips())

    @property
    def d(self) -> float:
        """diameter of the shank of the headed stud"""
        return self._d

    @property
    def h_sc(self) -> float:
        """height of the headed stud"""
        return self._h_sc

    @property
    def f_u(self) -> float:
        """tensile strength of the headed stud"""
        return self._f_u

    @property
    def f_cm(self) -> float:
        """mean concrete strength of the concrete surrounding the headed stud"""
        return self._f_cm

    @property
    def s_max(self) -> float:
        """maximum slip of the headed stud at failure"""
        return self._s_max

    @property
    def P(self) -> float:
        """maximum shear resistance of the headed stud"""
        return self._P

    @property
    def h_p(self) -> float:
        """height of a profiled steel sheeting"""
        return self._h_p

    @property
    def b_o(self) -> float:
        """decisive width of a profiled steel sheeting"""
        return self._b_o

    @property
    def n_r(self) -> float:
        """number of headed studs in a row"""
        return self._n_r

    def P_sm(self) -> float:
        """
        mean shear resistance of the headed stud considering steel-failure according to
        Roik et al. [1]_.

        Notes
        -----
        The mean shear connector resistance of a headed studs considering steel failure :math:`P_\\mathrm{sm}` is

        .. math::

           P_\\mathrm{sm} = \\frac{\\pi \\cdot d}{4} \\cdot f_\\mathrm{u}

        where :math:`d` is the diameter of the shank of the headed stud and
        :math:`f_\\mathrm{u}` is the tensile strength of the headed stud.
        """
        return 0.25 * 3.145 * self.d**2 * self.f_u

    def P_cm(self) -> float:
        """
        mean shear resistance of the headed stud considering concrete-failure according to
        Roik et al. [1]_.

        Notes
        -----
        The mean shear connector resistance of a headed studs considering concrete failure :math:`P_\\mathrm{cm}` is

        .. math::

           P_\\mathrm{cm} = 0.372 \\cdot \\alpha \\cdot d^{2} \\cdot \\sqrt{f_\\mathrm{cm} \\cdot E_\\mathrm{cm}}

        where :math:`d` is the diameter of the shank of the headed stud,
        :math:`f_\\mathrm{cm}` is the mean concrete cylinder compressive strength,
        :math:`\\alpha` considers the effect of the :math:`d / h_\\mathrm{sc}``-ratio on
        the shear resistance and :math:`E_\\mathrm{cm}` is the secant-modulus of the used concrete.
        """
        return (
            0.372
            * self.alpha()
            * self.d**2
            * (self.f_cm * self._concrete.E_cm) ** 0.5
        )

    def alpha(self) -> float:
        """factor considering the effect of :math:`d / h_\\mathrm{sc}` on the shear resistance"""
        h_sc_to_d = self.h_sc / self.d
        if h_sc_to_d > 4.0:
            return 1.0
        else:
            return 0.2 * (1.0 + h_sc_to_d)

    def k_t(self) -> float:
        """
        Reduction factor considering effect of profiled steel sheeting running perpendicular
        to the given beam on the shear resistance of the headed stud.

        Notes
        -----

        .. math::

           k_\\mathrm{t} = \\frac{0.7}{n_\\mathrm{r}} \\cdot \\frac{b_\\mathrm{o}}{h_\\mathrm{p}}
           \\left( \\frac{h_\\mathrm{sc}}{h_\\mathrm{p}} - 1 \\right) \\leq 1

        where :math:`n_\\mathrm{r}` is the number of headed studs in a row,
        :math:`b_\\mathrm{o}` is the decisive concrete with in the trough of the profiled steel sheeting,
        :math:`h_\\mathrm{p}` is the height of the profiled steel sheeting and :math:`h_\\mathrm{sc}` is
        the height of the headed stud.

        Returns
        -------
        float
            reduction factor
        """
        return min(
            0.7 / self.n_r * self.b_o / self.h_p * (self.h_sc / self.h_p - 1), 1.0
        )

    def _compute_P(self) -> float:
        """compute the maximum shear resistance of the headed stud"""
        P = min(self.P_sm(), self.P_cm())
        if self.h_p is None or self.b_o is None:
            return P
        else:
            return P * self.k_t()

    def _define_load_slips(self) -> list[LoadSlip]:
        """define the load-slip-relationship of the shear connector"""
        return [LoadSlip(0.0, 0.0), LoadSlip(self.P, 0.5), LoadSlip(self.P, self.s_max)]
