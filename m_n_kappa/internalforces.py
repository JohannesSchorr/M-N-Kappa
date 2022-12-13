from abc import ABC, abstractmethod
from dataclasses import dataclass

from .general import str_start_end

"""
Internal Forces
###############

Provides classes to compute the internal forces of a beam under a specific load

Systems available
-----------------
  - Single Beam
    
    - Single load
    - line load / Uniform load 
"""

# TODO: Multi-span systems


class ABCSingleSpan(ABC):
    """Meta class single span loading conditions shall be derived from"""

    @property
    @abstractmethod
    def length(self) -> float:
        """length of beam-span"""
        ...

    @property
    @abstractmethod
    def maximum_moment(self) -> float:
        """maximum moment by the given load"""
        ...

    @property
    @abstractmethod
    def loading(self) -> float:
        """sum of vertical loads"""
        ...

    @property
    @abstractmethod
    def transversal_shear_support_left(self) -> float:
        """transversal shear value at the left support"""
        ...

    @property
    @abstractmethod
    def transversal_shear_support_right(self) -> float:
        """transversal shear value at the right support"""
        ...

    @property
    @abstractmethod
    def positions(self) -> list[float]:
        """positions of load-introduction"""
        ...

    @abstractmethod
    def moment(self, at_position: float) -> float:
        """moment at the given position_value

        Parameters
        ----------
        at_position : float
            position_value where the moment needs to be computed at

        Returns
        -------
        float
            moment at the given position_value
        """
        ...

    @abstractmethod
    def transversal_shear(self, at_position) -> float:
        """transversal shear at the given position_value

        Parameters
        ----------
        at_position : float
            position_value where the transversal shear needs to be computed at

        Returns
        -------
        float
            transversal shear at the given position_value
        """
        ...

    @abstractmethod
    def positions_of_maximum_moment(self) -> list[float]:
        """position_value of the maximum moment"""
        ...

    def position_of_maximum_deformation(self) -> float:
        """positions-value of the maximum-deformation"""
        return sum(self.positions_of_maximum_moment()) / len(self.positions_of_maximum_moment())

    @abstractmethod
    def load_by(self, moment: float, at_position: float):
        ...

    @abstractmethod
    def load_distribution_factor(self) -> float:
        """
        effect of the load on the distribution on bending moment

        References
        ----------
        Eggert, F. (2019) Einfluss der Verdübelung auf das Trag- und Verformungsverhalten von Verbundträgern mit und
        ohne Profilblech, dissertation, University of Stuttgart, Institute of Structural Design, No. 2019-1, p. 182
        """
        ...


@dataclass
class SingleLoad:
    """container for single load"""

    position_in_beam: float
    value: float

    def moment(self):
        """moment by the single load (load x position_in_beam)"""
        return self.position_in_beam * self.value


class SingleSpan(ABCSingleSpan):
    """ """

    __slots__ = "_length", "_uniform_load", "_loads", "_beam"

    def __init__(self, length: float, loads: list = None, uniform_load: float = None):
        """
        Parameters
        ----------
        length : float
            length of the beam
        loads : list[SingleLoad]
            list of single-loads applied onto the beam
        uniform_load : float
            line load that is applied on the beam over the hole length
        """
        self._length = length
        self._uniform_load = uniform_load
        self._loads = loads
        self._beam = self.__get_beam_class()

    def __str__(self):
        return self.beam.__str__()

    @property
    def beam(self):
        return self._beam

    @property
    def length(self) -> float:
        return self._length

    @property
    def loading(self) -> float:
        return self.beam.loading

    @property
    def maximum_moment(self) -> float:
        return self.beam.maximum_moment

    @property
    def transversal_shear_support_left(self) -> float:
        return self.beam.transversal_shear_support_left

    @property
    def transversal_shear_support_right(self) -> float:
        return self.beam.transversal_shear_support_right

    @property
    def positions(self) -> list[float]:
        return self.beam.positions

    def moment(self, at_position) -> float:
        return self.beam.moment(at_position)

    def transversal_shear(self, at_position) -> float:
        return self.beam.transversal_shear(at_position)

    def positions_of_maximum_moment(self) -> list[float]:
        return self.beam.positions_of_maximum_moment()

    def load_by(self, moment: float, at_position: float) -> float:
        """load that leads to given moment at the given position_value"""
        return self.beam.load_by(moment, at_position)

    def _is_uniform_load(self) -> bool:
        if self._uniform_load is not None:
            return True
        else:
            return False

    def _is_single_loads(self) -> bool:
        if self._loads is not None:
            return True
        else:
            return False

    def __get_beam_class(self) -> ABCSingleSpan:
        if self._is_uniform_load():
            return SingleSpanUniformLoad(self.length, self._uniform_load)
        elif self._is_single_loads():
            return SingleSpanSingleLoads(self.length, self._loads)
        else:
            raise ValueError()

    def load_distribution_factor(self) -> float:
        return self.beam.load_distribution_factor()


@dataclass
class Moment:
    """container for moment at position_value"""

    position_in_beam: float
    value: float


class SingleSpanSingleLoads(ABCSingleSpan):
    """single span with single load(s)"""

    __slots__ = "_length", "_loads"

    def __init__(self, length: float, loads: list[SingleLoad]):
        """
        Parameters
        ----------
        length : float
            length of the beam-span
        loads : list[SingleLoad]
            loads applied to the beam
        """
        self._length = length
        self._loads = loads

    def __repr__(self) -> str:
        return f"SingleSpanSingleLoads(length={self.length}, loads={self.loads})"

    @str_start_end
    def __str__(self) -> str:
        text = [
            "Single span with single loads",
            "-----------------------------",
            "",
            "Properties",
            "----------",
            f"length = {self.length}",
            f"loads = {self.loads} | loading = {self.loading:.2f}",
            f"transversal shear: column left = {self.transversal_shear_support_left:.2f} |"
            f" column right = {self.transversal_shear_support_right:.2f}",
            f"Maximum Moment = {self.maximum_moment}",
        ]
        return "\n".join(text)

    @property
    def length(self) -> float:
        return self._length

    @property
    def loads(self) -> list[SingleLoad]:
        return self._loads

    @property
    def maximum_moment(self) -> float:
        return self._maximum_moment_value()

    @property
    def transversal_shear_support_left(self) -> float:
        return self._loading() + self._column_right()

    @property
    def transversal_shear_support_right(self) -> float:
        return self._column_right()

    @property
    def loading(self) -> float:
        return self._loading()

    @property
    def positions(self) -> list[float]:
        return [load.position_in_beam for load in self.loads]

    def moment(self, at_position: float) -> float:
        return self._moment(at_position)

    def positions_of_maximum_moment(self) -> list[float]:
        return self._maximum_moment_positions()

    def transversal_shear(self, at_position) -> float:
        return self._transversal_shear(at_position)

    def load_by(self, moment: float, at_position: float):
        return self.load_by_factor(moment, at_position)

    def load_by_factor(self, moment: float, at_position: float):
        moment_1 = self.moment(at_position)
        moment_2 = self.single_span_with_factor(10.0).moment(at_position)
        factor = 1.0 + (moment - moment_1) * (10.0 - 1.0) / (moment_2 - moment_1)
        return self.single_span_with_factor(factor)

    def single_span_with_factor(self, factor: float):
        return SingleSpanSingleLoads(self.length, self.single_loads_with_factor(factor))

    def single_span_with_value(self, value: float):
        return SingleSpanSingleLoads(self.length, self.single_loads_with_value(value))

    def single_loads_with_factor(self, factor: float) -> list[SingleLoad]:
        """single loads multiplied with the given factor"""
        return [
            SingleLoad(load.position_in_beam, load.value * factor)
            for load in self.loads
        ]

    def single_loads_with_value(self, value: float) -> list[SingleLoad]:
        """single loads plus given value"""
        return [
            SingleLoad(load.position_in_beam, load.value + value) for load in self.loads
        ]

    def _column_right(self) -> float:
        return (-1.0) * self._load_moments() / self.length

    def _load_moments(self) -> float:
        return sum([load.moment() for load in self.loads])

    def _loading(self) -> float:
        return sum(self._single_loads())

    def _moment(self, at_position: float) -> float:
        moment = self.transversal_shear_support_left * at_position
        for load in self.loads:
            if load.position_in_beam < at_position:
                moment -= load.value * (at_position - load.position_in_beam)
        return moment

    def moment_by(self, load: SingleLoad, at_position: float) -> float:
        return (at_position - load.position_in_beam) * load.value

    def _moments(self) -> list[Moment]:
        return [
            Moment(load.position_in_beam, self._moment(load.position_in_beam))
            for load in self.loads
        ]

    def _maximum_moment(self) -> list[Moment]:
        moments = self._moments()
        moments.sort(key=lambda x: x.value, reverse=True)
        maximum_moments = list(filter(lambda x: round(x.value, 5) == round(moments[0].value, 5), moments))
        return maximum_moments

    def _maximum_moment_value(self) -> float:
        return self._maximum_moment()[0].value

    def _maximum_moment_positions(self) -> list[float]:
        maximum_moment_positions = [moment.position_in_beam for moment in self._maximum_moment()]
        maximum_moment_positions.sort()
        return maximum_moment_positions

    def _single_loads(self) -> list[float]:
        return [load.value for load in self.loads]

    def _transversal_shear(self, at_position: float) -> float:
        shear = self.transversal_shear_support_left
        for load in self.loads:
            if load.position_in_beam < at_position:
                shear -= load.value
        return shear

    def load_distribution_factor(self) -> float:
        if len(self.loads) == 1 and self.loads[0].position_in_beam == 0.5 * self.length:
            return 0.5
        elif len(self.loads) > 1 and self.length-self.loads[-1].position_in_beam == self.loads[0].position_in_beam:
            load_distance = abs(self.loads[0].position_in_beam - self.loads[-1].position_in_beam)
            a = - 0.5 * (load_distance - self.length)
            return 1. - (a / self.length)


class SingleSpanUniformLoad(ABCSingleSpan):
    """single span with uniform load"""

    def __init__(self, length: float, load: float):
        """
        Parameters
        ----------
        length : float
            length of the beam-span
        load : float
            line-load the beam is uniformly loaded with
        """
        self._length = length
        self._load = load

    def __repr__(self) -> str:
        return f"SingleSpanUniformLoad(length={self.length}, load={self.load})"

    @str_start_end
    def __str__(self):
        text = [
            "Single span with uniform load",
            "-----------------------------",
            "",
            "Properties",
            "----------",
            f"length = {self.length}",
            f"load = {self.load} | loading = {self.loading}",
            f"transversal shear: column left = {self.transversal_shear_support_left} | "
            + "column right = {self.transversal_shear_support_right}",
            f"Maximum Moment = {self.maximum_moment}",
        ]
        return "\n".join(text)

    @property
    def length(self) -> float:
        """length of the beam span"""
        return self._length

    @property
    def load(self) -> float:
        """line load the beam is loaded with"""
        return self._load

    @property
    def loading(self):
        """total load of the beam span"""
        return self._loading()

    @property
    def maximum_moment(self):
        return self._maximum_moment()

    @property
    def transversal_shear_support_left(self):
        return self._support_transversal_shear()

    @property
    def transversal_shear_support_right(self):
        return (-1) * self._support_transversal_shear()

    @property
    def positions(self) -> list[float]:
        return []

    def moment(self, at_position: float):
        return self._moment(at_position)

    def transversal_shear(self, at_position: float):
        return self._transversal_shear(at_position)

    def load_by_moment(self, maximum_moment) -> float:
        """compute load by given maximum moment"""
        return maximum_moment * 8.0 / (self.length ** 2.0)

    def load_by(self, moment: float, at_position: float) -> ABCSingleSpan:
        load = moment / (0.5 * (self.length * at_position - at_position ** 2.0))
        return SingleSpanUniformLoad(self.length, load)

    def positions_of_maximum_moment(self) -> list[float]:
        """position_value where the moment is the maximum"""
        return [0.5 * self.length]

    def _support_transversal_shear(self):
        return 0.5 * self.loading

    def _loading(self):
        return self.length * self.load

    def _moment(self, at_position: float):
        return (
            self._support_transversal_shear() * at_position
            - 0.5 * self.load * at_position ** 2.0
        )

    def _maximum_moment(self):
        return self.load * self.length ** 2.0 / 8.0

    def _transversal_shear(self, at_position):
        return self._support_transversal_shear() - self.load * at_position

    def load_distribution_factor(self) -> float:
        return 2. / 3.