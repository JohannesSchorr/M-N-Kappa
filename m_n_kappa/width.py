import math
import decimal

"""
References
----------
Kuhlmann, U.; Rieg, A. Mittragende Betongurtbreite niedriger Verbundträger, AiF-Forschungsvorhaben-Nr. 13460 N, 2004

"""


class StateMeta:

    __slot__ = "_slab_width", "_beam_length", "_mu", "_sequences"

    def __init__(
        self,
        slab_width: float,
        beam_length: float,
        mu: float = 0.2,
        sequences: int = 10,
    ):
        self._slab_width = slab_width
        self._beam_length = beam_length
        self._mu = mu
        self._sequences = sequences

    @property
    def slab_width(self):
        return self._slab_width

    @property
    def beam_length(self):
        return self._beam_length

    @property
    def b_over_l(self):
        return self.slab_width / self.beam_length

    @property
    def mu(self):
        """poisson's ratio"""
        return self._mu

    @property
    def sequences(self):
        """in case of Fourier-Transformation the used number of sequences"""
        return self._sequences

    @property
    def alpha(self):
        """helper function from Kuhlmann, Rieg (2004), Eq. 5-39"""
        return self.pi * self.slab_width / self.beam_length

    @property
    def pi(self):
        return math.pi

    def sin(self, value: float) -> float:
        return math.sin(value)

    def sinh(self, value: float) -> float:
        return math.sinh(value)

    def cos(self, value: float) -> float:
        return math.cos(value)

    def cosh(self, value: float) -> float:
        return math.cosh(value)

    def _nominator_sum(self, position):
        return sum(self._nominator_list(position))

    def _nominator_list(self, position):
        return [
            self._nominator(position, sequence) for sequence in range(1, self.sequences)
        ]

    def _nominator(self, position, sequence):
        raise NotImplementedError()

    def _determinator_sum(self, position):
        return sum(self._determinator_list(position))

    def _determinator_list(self, position):
        return [
            self._determinator(position, sequence)
            for sequence in range(1, self.sequences)
        ]

    def _determinator(self, position, sequence: int):
        raise NotImplementedError()

    def ratio_beff_to_b(self, position: float):
        raise NotImplementedError()

    def b_eff(self, position):
        return float(self.slab_width * self.ratio_beff_to_b(self, position))


class StateMetaDecimal(StateMeta):

    """compute all relevant numbers in decimal.Decimal()'s"""

    def __init__(
        self,
        slab_width: float,
        beam_length: float,
        mu: float = 0.2,
        sequences: int = 10,
    ):
        self._slab_width = decimal.Decimal(slab_width)
        self._beam_length = decimal.Decimal(beam_length)
        self._mu = decimal.Decimal(mu)
        self._sequences = sequences

    @property
    def pi(self):
        return decimal.Decimal(math.pi)

    def sin(self, value) -> decimal.Decimal:
        return decimal.Decimal(math.sin(float(value)))

    def sinh(self, value: float) -> decimal.Decimal:
        """
        References
        ----------
        url='https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus', visite on: 29/05/2022
        """
        return decimal.Decimal(0.5) * (
            decimal.Decimal(value).exp() - decimal.Decimal((-1) * value).exp()
        )

    def cos(self, value) -> decimal.Decimal:
        return decimal.Decimal(math.cos(float(value)))

    def cosh(self, value: float) -> decimal.Decimal:
        """
        References
        ----------
        url='https://de.wikipedia.org/wiki/Sinus_hyperbolicus_und_Kosinus_hyperbolicus', visite on: 29/05/2022
        """
        return decimal.Decimal(0.5) * (
            decimal.Decimal(value).exp() + decimal.Decimal((-1) * value).exp()
        )


class DistinguishWebNumber:

    """meta-class"""

    @property
    def one_web(self):
        return self._one_web

    @property
    def multiple_webs(self):
        return self._multiple_webs


class DistinguishLoading:

    """meta-class"""

    @property
    def harmonic(self):
        return self._harmonic

    @property
    def line(self):
        return self._line

    @property
    def single(self):
        return self._single


class DistinguishState:

    """meta-class"""

    @property
    def membran(self):
        return self._membran

    @property
    def bending(self):
        return self._bending


class MembranStateHarmonicLoadingMultipleWebs(StateMeta):
    """
    Membran State of a composite girder with multiple webs under harmonic loading

    see Sec. 5.2.2.1 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self):
        """see Eq. 5-25 in Kuhlmann, Rieg (2004)"""
        return (
            (-1.0)
            * (2.0 / self.pi)
            * (1.0 / self.b_over_l)
            * (
                (self.sinh(self.pi * self.b_over_l)) ** (2.0)
                / (
                    self.pi * self.b_over_l
                    - 3.0
                    * self.sinh(self.pi * self.b_over_l)
                    * self.cosh(self.pi * self.b_over_l)
                )
            )
        )


class MembranStateHarmonicLoadingOneWeb(StateMeta):
    """
    Membran State of a composite girder with one web under harmonic loading

    References
    ----------
            see Sec. 5.2.2.2 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self):
        """
        see Eq. 5-46 in Kuhlmann, Rieg (2004)

        Change-Log
        ----------
                minus-sign was deleted, validated by testing and comparing with Fig. 5-4 in Kuhlmann, Rieg (2004)
        """
        return (
            # (-1.) *
            (2.0 / self.pi)
            * (1.0 / self.b_over_l)
            * (1.0 / (self._A() + 2.0 * self._B()))
        )

    def _A(self) -> float:
        """see Eq. 5-37 in Kuhlmann, Rieg (2004)"""
        return (
            (1.0 + self.mu) * (self.sinh(self.alpha)) ** (2.0)
            + (1.0 - self.mu) * (self.alpha ** (2.0))
        ) / (self.alpha + self.sinh(self.alpha) * self.cosh(self.alpha))

    def _B(self) -> float:
        """
        see Eq. 5-38 in Kuhlmann, Rieg (2004)

        Change-Log
        ----------
                minus-sign was deleted, validated by testing and comparing with Fig. 5-4 in Kuhlmann, Rieg (2004)
        """
        return (
            # (-1.) *
            ((1.0 + self.mu) + (1.0 - self.mu) * (self.cosh(self.alpha)) ** (2.0))
            / (self.alpha + self.sinh(self.alpha) * self.cosh(self.alpha))
        )


class MembranStateHarmonicLoading(DistinguishWebNumber):
    """
    Membran State of a composite girder under harmonic loading

    References
    ----------
            see Sec. 5.2.2 in Kuhlmann, Rieg (2004)
    """

    def __init__(self, slab_width, beam_length, mu: float = 0.2, sequences: int = None):
        self._one_web = MembranStateHarmonicLoadingOneWeb(
            slab_width, beam_length, mu, sequences
        )
        self._multiple_webs = MembranStateHarmonicLoadingMultipleWebs(
            slab_width, beam_length, mu, sequences
        )


class MembranStateLineLoadingMultipleWebs(StateMetaDecimal):
    """
    Membran State of a composite girder with multiple webs under line load

    References
    ----------
            see Sec. 5.2.3.2 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self, position: float):
        """see Eq. 5-49 in Kuhlmann, Rieg (2004)"""
        position = decimal.Decimal(position)
        return float(
            (-1)
            * (2 / self.pi)
            * (1 / self.b_over_l)
            * self._nominator_sum(position)
            / self._determinator_sum(position)
        )

    def alpha_k(self, sequence):
        """see Eq. 5-46 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal((2 * sequence - 1) * self.pi / self.beam_length)

    def _nominator(self, position: float, sequence: int):
        """see Eq. 5-49 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (3))
            * self.cos(self.alpha_k(sequence) * position)
        )

    def _determinator(self, position: float, sequence: int):  #
        """see Eq. 5-49 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (2))
            * self.cos(self.alpha_k(sequence) * position)
            * (
                self._A(sequence) * self.cosh(self.alpha_k(sequence) * self.slab_width)
                + self._B(sequence)
            )
        )

    def _A(self, sequence: int):
        """see Eq. 5-50 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * self.slab_width
        return decimal.Decimal(
            decimal.Decimal(1 / (2 * sequence - 1))
            * (
                (1 + self.mu) * alpha_k * self.cosh(alpha_k)
                - (1 - self.mu) * self.sinh(alpha_k)
            )
            / (self.sinh(alpha_k) ** (2))
        )

    def _B(self, sequence: int):
        """see Eq. 5-51 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * self.slab_width
        return decimal.Decimal(
            (-1)
            * decimal.Decimal(1 / (2 * sequence - 1))
            * (1 + self.mu)
            * (alpha_k * self.sinh(alpha_k) + 2 * self.cosh(alpha_k))
            / (self.sinh(alpha_k))
        )


class MembranStateLineLoadingOneWeb(StateMetaDecimal):
    """
    Membran State of a composite girder with a single web under line load

    References
    ----------
            see Sec. 5.2.3.3 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self, position):
        """see Eq. 5-58 in Kuhlmann, Rieg (2004)"""
        position = decimal.Decimal(position)
        return float(
            (2 / self.pi)
            * decimal.Decimal(1 / self.b_over_l)
            * (self._nominator_sum(position) / self._determinator_sum(position))
        )

    def _alpha_k(self, sequence):
        """see Eq. 5-53 in Kuhlmann, Rieg (2004)"""
        return (2 * sequence - 1) * self.pi / self.beam_length

    def _nominator(self, position, sequence):
        """see Eq. 5-58 in Kuhlmann, Rieg (2004)"""
        alpha_k = self._alpha_k(sequence) * position
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (3))
            * self.cos(alpha_k)
        )

    def _determinator(self, position, sequence):
        """see Eq. 5-58 in Kuhlmann, Rieg (2004)"""
        alpha_k = self._alpha_k(sequence) * position
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (2))
            * self.cos(alpha_k)
            * (self._A(sequence) + 2 * self._B(sequence))
        )

    def _A(self, sequence):
        """see Eq. 5-59 in Kuhlmann, Rieg (2004)"""
        alpha_k = self._alpha_k(sequence) * self.slab_width
        return (
            (1 - self.mu) * self.sinh(alpha_k) ** (2) + (1 + self.mu) * alpha_k ** (2)
        ) / (alpha_k + self.sinh(alpha_k) * self.cosh(alpha_k))

    def _B(self, sequence):
        """see Eq. 5-60 in Kuhlmann, Rieg (2004)"""
        alpha_k = self._alpha_k(sequence) * self.slab_width
        return ((1 - self.mu) + (1 + self.mu) * self.cosh(alpha_k) ** (2)) / (
            alpha_k + self.sinh(alpha_k) * self.cosh(alpha_k)
        )


class MembranStateLineLoading(DistinguishWebNumber):
    """
    Membran State of a composite girder under line load

    References
    ----------
            see Sec. 5.2.3 in Kuhlmann, Rieg (2004)
    """

    def __init__(self, slab_width, beam_length, mu: float = 0.2, sequences: int = 55):
        self._one_web = MembranStateLineLoadingOneWeb(
            slab_width, beam_length, mu, sequences
        )
        self._multiple_webs = MembranStateLineLoadingMultipleWebs(
            slab_width, beam_length, mu, sequences
        )


class MembranStateSingleLoadOneWeb(StateMetaDecimal):
    """
    Membran State of a composite girder with a single web under a single load

    References
    ----------
      see Sec. 5.2.4.2 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self, position):
        """see Eq. 5-68 in Kuhlmann, Rieg (2004)"""
        position = decimal.Decimal(position)
        return float(
            (-1)
            * (1 / self.pi)
            * (1 / self.b_over_l)
            * (self._nominator_sum(position) / self._determinator_sum(position))
        )

    def _nominator(self, position, sequence):
        """see Eq. 5-68 in Kuhlmann, Rieg (2004)"""
        alpha_x = (2 * sequence - 1) * self.alpha * position
        return decimal.Decimal(1 / (2 * sequence - 1) ** (2)) * self.cos(alpha_x)

    def _determinator(self, position, sequence):
        """see Eq. 5-68 in Kuhlmann, Rieg (2004)"""
        alpha_x = (2 * sequence - 1) * self.alpha * position
        return (
            decimal.Decimal(1 / (2 * sequence - 1))
            * self.cos(alpha_x)
            * (self._A(sequence) + 2 * self._B(sequence))
        )

    def _A(self, sequence):
        """see Eq. 5-69 in Kuhlmann, Rieg (2004)"""
        alpha_k = (2 * sequence - 1) * self.alpha * self.slab_width
        return (
            (1 - self.mu) * self.sinh(alpha_k) ** (2) + (1 + self.mu) * alpha_k ** (2)
        ) / (alpha_k + self.sinh(alpha_k) * self.cosh(alpha_k))

    def _B(self, sequence):
        """see Eq. 5-70 in Kuhlmann, Rieg (2004)"""
        alpha_k = (2 * sequence - 1) * self.alpha * self.slab_width
        return ((1 - self.mu) + (1 + self.mu) * self.cosh(alpha_k) ** (2)) / (
            alpha_k + self.sinh(alpha_k) * self.cosh(alpha_k)
        )


class BendingStateHarmonicLoadingMultipleWebs(StateMeta):
    """
    Bending state of a composite girder with multiple webs under harmonic loading

    References
    ----------
      see Sec. 5.3.2.1 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self):
        """see Eq. 5-93 in Kuhlmann, Rieg (2004)"""
        return (
            (-1.0)
            * (2.0 / self.pi)
            * (1.0 / self.b_over_l)
            * (1.0 / ((1.0 - self.mu) * self._A() - 2.0 * self.mu * self._B()))
        )

    def _A(self):
        """see Eq. 5-93 in Kuhlmann, Rieg (2004)"""
        return (
            (1.0 / (1.0 - self.mu))
            * (
                4.0
                + (3.0 + self.mu) * (1.0 - self.mu) * self.sinh(self.alpha) ** (2.0)
                + (1.0 - self.mu) ** (2.0) * self.alpha ** (2.0)
            )
            / (
                (1.0 - self.mu) * self.alpha
                - (3.0 + self.mu) * self.sinh(self.alpha) * self.cosh(self.alpha)
            )
        )

    def _B(self):
        """see Eq. 5-93 in Kuhlmann, Rieg (2004)"""
        return (
            (-1.0)
            * (2.0 + (3.0 + self.mu) * self.sinh(self.alpha) ** (2.0))
            / (
                (1.0 - self.mu) * self.alpha
                - (3.0 + self.mu) * self.sinh(self.alpha) * self.cosh(self.alpha)
            )
        )


class BendingStateHarmonicLoadingOneWeb(StateMeta):
    """
    Bending state of composite girder with single web under harmonic loading

    References
    ----------
      see Sec. 5.3.2.2 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self):
        """see Eq. 5-105 in Kuhlmann, Rieg (2004)"""
        return (
            (2.0 / self.pi)
            * (1.0 / self.b_over_l)
            * (
                (1.0 - self.mu) * (self.alpha)
                + (1.0 + self.mu) * self.sinh(self.alpha) * self.cosh(self.alpha)
            )
            / (self.sinh(self.alpha)) ** (2.0)
        )


class BendingStateHarmonicLoading(DistinguishWebNumber):
    """
    Bending state of composite girder under harmonic loading

    References
    ----------
      see Sec. 5.3.2 in Kuhlmann, Rieg (2004)
    """

    def __init__(self, slab_width, beam_length, mu: float = 0.2, sequences: int = 1):
        self._one_web = BendingStateHarmonicLoadingOneWeb(
            slab_width, beam_length, mu, sequences
        )
        self._multiple_webs = BendingStateHarmonicLoadingMultipleWebs(
            slab_width, beam_length, mu, sequences
        )


class BendingStateLineLoadingMultipleWebs(StateMetaDecimal):
    """
    Bending State of composite girder with multiple webs under line loading

    References
    ----------
      see Sec. 5.3.3.2 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self, position: float):
        """see Eq. 5-114 in Kuhlmann, Rieg (2004)"""
        position = decimal.Decimal(position)
        return float(
            (2 / self.pi)
            * (1 / self.b_over_l)
            * (self._nominator_sum(position) / self._determinator_sum(position))
        )

    def _alpha_k(self, sequence: int):
        return (2 * sequence - 1) * self.pi / self.beam_length

    def _nominator(self, position, sequence):
        """see Eq. 5-114 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (3))
            * self.cos(self._alpha_k(sequence) * position)
        )

    def _determinator(self, position, sequence):
        """see Eq. 5-114 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (2))
            * (
                (1 - self.mu)
                * self._A(sequence)
                * self.cosh(self._alpha_k(sequence) * self.slab_width)
                + self._B(sequence)
            )
        )

    def _A(self, sequence):
        """see Eq. 5-115 in Kuhlmann, Rieg (2004)"""
        alpha_k = self._alpha_k(sequence) * self.slab_width
        return (alpha_k * self.cosh(alpha_k) + self.sinh(alpha_k)) / (
            self.sinh(alpha_k) ** (2)
        )

    def _B(self, sequence):
        """see Eq. 5-116 in Kuhlmann, Rieg (2004)"""
        alpha_k = self._alpha_k(sequence) * self.slab_width
        return (-1) * (
            (
                (1 - self.mu) * alpha_k * self.sinh(alpha_k)
                - 2 * self.mu * self.cosh(alpha_k)
            )
            / (self.sinh(alpha_k))
        )


class BendingStateLineLoadingOneWeb(StateMetaDecimal):
    """
    Bending state of composite girder with single web under line loading

    References
    ----------
      see Sec. 5.3.3.3 in Kuhlmann, Rieg (2004)"""

    def ratio_beff_to_b(self, position: float):
        """see Eq. 5-126 in Kuhlmann, Rieg (2004)"""
        position = decimal.Decimal(position)
        return float(
            (-1)
            * (2 / self.pi)
            * (1 / self.b_over_l)
            * self._nominator_sum(position)
            / self._determinator_sum(position)
        )

    def alpha_k(self, sequence: int):
        return (2 * sequence - 1) * self.pi / self.beam_length

    def _nominator(self, position, sequence):
        """see Eq. 5-126 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (3))
            * self.cos(self.alpha_k(sequence) * position)
        )

    def _determinator(self, position, sequence):
        """see Eq. 5-126 in Kuhlmann, Rieg (2004)"""
        return decimal.Decimal(
            (-1) ** (sequence - 1)
            * decimal.Decimal(1 / (2 * sequence - 1) ** (2))
            * self.cos(self.alpha_k(sequence) * position)
            * ((1 - self.mu) * self._A(sequence) + 2 * self.mu * self._B(sequence))
        )

    def _A(self, sequence: int):
        """see Eq. 5-127 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * self.slab_width
        return decimal.Decimal(
            (1 / (1 - self.mu))
            * (
                (
                    (3 + self.mu) * (1 - self.mu) * self.cosh(alpha_k) ** (2)
                    + (1 + self.mu) ** (2)
                    + (1 - self.mu) ** (2) * alpha_k ** (2)
                )
                / (
                    (1 - self.mu) * alpha_k
                    - (3 + self.mu) * self.sinh(alpha_k) * self.cosh(alpha_k)
                )
            )
        )

    def _B(self, sequence: int):
        """see Eq. 5-128 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * self.slab_width
        return decimal.Decimal(
            ((3 + self.mu) * self.cosh(alpha_k) - (1 + self.mu))
            / (
                (1 + self.mu) * alpha_k
                - (3 + self.mu) * self.sinh(alpha_k) * self.cosh(alpha_k)
            )
        )


class BendingStateLineLoading(DistinguishWebNumber):
    """
    Bending State of composite girder under line loading

    References
    ----------
      see Sec. 5.3.3 in Kuhlmann, Rieg (2004)"""

    def __init__(
        self,
        slab_width: float,
        beam_length: float,
        mu: float = 0.2,
        sequences: int = 10,
    ):
        self._one_web = BendingStateLineLoadingOneWeb(
            slab_width, beam_length, mu, sequences
        )
        self._multiple_webs = BendingStateLineLoadingMultipleWebs(
            slab_width, beam_length, mu, sequences
        )


class BendingStateSingleLoadOneWeb(StateMetaDecimal):
    """
    Bending State of composite girder with single web under single load

    References
    ----------
      see Sec. 5.3.4.2 in Kuhlmann, Rieg (2004)
    """

    def ratio_beff_to_b(self, position):
        """see Eq. 5-139 in Kuhlmann, Rieg (2004)"""
        position = decimal.Decimal(position)
        return float(
            (-1)
            * (2 / self.pi)
            * (1 / self.b_over_l)
            * (self._nominator_sum(position) / self._determinator_sum(position))
        )

    def alpha_k(self, sequence):
        """see Eq. 5-134 in Kuhlmann, Rieg (2004)"""
        return (2 * sequence - 1) * self.pi / self.beam_length

    def _nominator(self, position, sequence):
        """see Eq. 5-139 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * position
        return decimal.Decimal(1 / (2 * sequence - 1) ** (2)) * self.cos(alpha_k)

    def _determinator(self, position, sequence):
        """see Eq. 5-139 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * position
        return (
            decimal.Decimal(1 / (2 * sequence - 1))
            * self.cos(alpha_k)
            * ((1 - self.mu) * self._A(sequence) + 2 * self.mu * self._B(sequence))
        )

    def _A(self, sequence):
        """see Eq. 5-140 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * self.slab_width
        return (
            (1 / (1 - self.mu))
            * (
                (
                    4
                    + (3 + self.mu) * (1 - self.mu) * self.sinh(alpha_k) ** (2)
                    + (1 - self.mu) ** (2) * alpha_k ** (2)
                )
            )
            / (
                (1 - self.mu) * alpha_k
                - (3 + self.mu) * self.sinh(alpha_k) * self.cosh(alpha_k)
            )
        )

    def _B(self, sequence):
        """see Eq. 5-141 in Kuhlmann, Rieg (2004)"""
        alpha_k = self.alpha_k(sequence) * self.slab_width
        return ((-1) * (1 + self.mu) + (3 + self.mu) * self.cosh(alpha_k) ** (2)) / (
            (1 - self.mu) * alpha_k
            - (3 + self.mu) * self.sinh(alpha_k) * self.cosh(alpha_k)
        )


class HarmonicLoadingOneWeb(DistinguishState):
    """
    Composite girder with one web under harmonic loading
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._membran = MembranStateHarmonicLoadingOneWeb(slab_width, beam_length, mu)
        self._bending = BendingStateHarmonicLoadingOneWeb(slab_width, beam_length, mu)


class HarmonicLoadingMultipleWebs(DistinguishState):
    """
    Composite girder with multiple webs under harmonic loading
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._membran = MembranStateHarmonicLoadingMultipleWebs(
            slab_width, beam_length, mu
        )
        self._bending = BendingStateHarmonicLoadingMultipleWebs(
            slab_width, beam_length, mu
        )


class LineLoadingOneWeb(DistinguishState):
    """
    Composite girder with one web under line loading
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._membran = MembranStateLineLoadingOneWeb(slab_width, beam_length, mu)
        self._bending = BendingStateLineLoadingOneWeb(slab_width, beam_length, mu)


class LineLoadingMultipleWebs(DistinguishState):
    """
    Composite girder with multiple webs under line loading
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._membran = MembranStateLineLoadingMultipleWebs(slab_width, beam_length, mu)
        self._bending = BendingStateLineLoadingMultipleWebs(slab_width, beam_length, mu)


class SingleLoadOneWeb(DistinguishState):
    """
    Composite girder with one web under single load
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._membran = MembranStateSingleLoadOneWeb(slab_width, beam_length, mu)
        self._bending = BendingStateSingleLoadOneWeb(slab_width, beam_length, mu)


class OneWeb(DistinguishLoading):
    """
    Composite girder with single web
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._single = SingleLoadOneWeb(slab_width, beam_length, mu)
        self._line = LineLoadingOneWeb(slab_width, beam_length, mu)
        self._harmonic = HarmonicLoadingOneWeb(slab_width, beam_length, mu)


class MultipleWebs(DistinguishLoading):
    """
    Composite girder with multiple webs
    """

    def __init__(self, slab_width: float, beam_length: float, mu: float = 0.2):
        self._line = LineLoadingMultipleWebs(slab_width, beam_length, mu)
        self._harmonic = HarmonicLoadingMultipleWebs(slab_width, beam_length, mu)
