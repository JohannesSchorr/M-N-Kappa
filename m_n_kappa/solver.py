from .general import str_start_end
from .function import Polynominal, Linear

import logging
import logging.config
import yaml
import pathlib

with open(pathlib.Path(__file__).parent.absolute() / "logging-config.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


class Solver:

    """
    Meta Solver-Class

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_target_value",
        "_maximum_variable",
        "_minimum_variable",
        "_function",
        "_sorted_data",
        "_x_n_plus_1",
    )

    def __init__(self, data: list, target, variable, target_value: float = 0.0):
        """
        Parameters
        ----------
        data : list
            data containing target and variable keys
        target : str or int
            key of the target (e.g. str for dictionaries or int for lists)
        variable : str or int
            variable of the target (e.g. str for dictionaries or int for lists)
        target_value : float
            value to meet by the target
        """
        self._data = data
        self._target = target
        self._variable = variable
        self._target_value = target_value
        if len(self._data) > 1:
            self._maximum_variable = self._compute_maximum_variable()
            self._minimum_variable = self._compute_minimum_variable()
        self._sorted_data = self._sort_data()
        self._prepare()
        logger.info(f'Created {self.__repr__()}')

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" \
               f"data=data, " \
               f"target={self.target}, " \
               f"variable={self.variable}, " \
               f"target_value={self.target_value})"

    @str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_initial_value(),
            self._print_result(),
        ]
        return "\n".join(text)

    def _print_title(self) -> str:
        return "\n".join(
            [f"{self.__class__.__name__}", len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return "\n".join(["Initialization", "--------------", self.__repr__()])

    def _print_initial_value(self) -> str:
        return "\n".join(
            ["Initial Value", "-------------", "x_n = {:.2f}".format(self.x_n)]
        )

    def _print_result(self) -> str:
        return "\n".join(["Result", "------", "x_n+1 = {:.2f}".format(self.compute())])

    @property
    def data(self) -> list:
        """passed data"""
        return self._data

    @property
    def maximum_variable(self) -> float:
        """maximum variable value given in ``data``"""
        return self._maximum_variable

    @property
    def minimum_variable(self) -> float:
        """minimum variable value given in ``data``"""
        return self._minimum_variable

    @property
    def target(self):
        """key of the target in ``data``"""
        return self._target

    @property
    def target_value(self):
        """value of the target"""
        return self._target_value

    @property
    def variable(self):
        """key of the variable in ``data``"""
        return self._variable

    @property
    def x_n(self) -> float:
        """lastly computed variable value"""
        return self._sorted_data[0][self.variable]

    @property
    def x_n_plus_1(self) -> float:
        """new computed value"""
        return self._x_n_plus_1

    def compute(self, use_fallback: bool = False) -> float:
        pass

    def _prepare(self):
        pass

    def _sort_data(self) -> list:
        """
        sort the data by the target value and get the two target-values greater zero
        and the two target values smaller zero, if available
        """
        #  self._data.sort(key=lambda x: abs(x[self.target]))
        gt_zero = list(filter(lambda x: x[self.target] > 0.0, self.data))
        lt_zero = list(filter(lambda x: x[self.target] < 0.0, self.data))
        if len(gt_zero) > 2:
            gt_zero.sort(key=lambda x: abs(x[self.target]))
            gt_zero = gt_zero[:2]
        if len(lt_zero) > 2:
            lt_zero.sort(key=lambda x: abs(x[self.target]))
            lt_zero = lt_zero[:2]
        new_data = gt_zero + lt_zero
        new_data.sort(key=lambda x: abs(x[self.target]))
        return new_data

    def _set_variable_boundaries(self) -> None:
        if len(self._data) > 1:
            self._maximum_variable = self._compute_maximum_variable()
            self._minimum_variable = self._compute_minimum_variable()

    def _compute_maximum_variable(self) -> float:
        """compute the maximal variable value"""
        return max(self._data, key=lambda x: x[self.variable])[self.variable]

    def _compute_minimum_variable(self) -> float:
        """compute the minimum variable value"""
        return min(self._data, key=lambda x: x[self.variable])[self.variable]


class Bisection(Solver):

    """Bisection solver"""

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_target_value",
        "_maximum_variable",
        "_minimum_variable",
    )

    def compute(self, use_fallback: bool = False) -> float:
        variables = [data_point[self.variable] for data_point in self.data]
        logger.debug(f'{variables=}')
        for factor in [0.5, 0.25, 0.75, 0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]:
            new_variable = self._compute_with(factor)
            if new_variable not in variables:
                logger.debug(new_variable)
                return new_variable

    def _compute_with(self, factor: float = 0.5):
        return factor * (self._min_under_zero_variable() + self._min_over_zero_variable())

    def print_values(self) -> str:
        return (
            f"min over zero: {self._min_over_zero_variable()} | "
            f"min under zero: {self._min_under_zero_variable()} | "
            f"mean: {self.compute()}"
        )

    def _min_over_zero_variable(self) -> float:
        return min(self._data_with_target_over_zero(), key=lambda x: x[self.target])[
            self.variable
        ]

    def _min_under_zero_variable(self) -> float:
        return max(self._data_with_target_under_zero(), key=lambda x: x[self.target])[
            self.variable
        ]

    def _data_with_target_over_zero(self) -> list:
        return list(filter(lambda x: x[self.target] > 0.0, self.data))

    def _data_with_target_under_zero(self) -> list:
        return list(filter(lambda x: x[self.target] < 0.0, self.data))


class Newton(Solver):
    """Solver using the newton method"""

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_target_value",
        "_maximum_variable",
        "_minimum_variable",
        "_function",
        "_x_n_plus_1",
    )

    @property
    def function(self):
        return self._function

    @property
    def x_n_plus_1(self) -> float:
        return self._x_n_plus_1

    def compute(self, use_fallback: bool = False) -> float:
        self._x_n_plus_1 = self.solve()
        if self.is_value_in_range() and self.value_has_changed() and not use_fallback:
            return self.x_n_plus_1
        else:
            return self.fallback()

    def is_value_in_range(self) -> bool:
        """check if computed value is between maximum and minimum variable value"""
        if self.minimum_variable <= self.x_n_plus_1 <= self.maximum_variable:
            return True
        else:
            logger.debug(f'Value {self.x_n_plus_1=} is not in range. '
                  f'x_n: {self.x_n}, '
                  f'Minimum: {self.minimum_variable=}, '
                  f'Maximum: {self.maximum_variable=},\n'
                  f'Data: {self.data}')
            return False

    def value_has_changed(self) -> bool:
        if self.x_n != 0.0:
            denominator = self.x_n
        else:
            denominator = self.x_n_plus_1
        if abs(self.x_n_plus_1 - self.x_n / denominator) < 0.0001:
            logger.info(f'value has not changed {self.x_n_plus_1=}, {self.x_n=}')
            return False
        else:
            return True

    def fallback(self) -> float:
        logger.info("Fallback: Bisection")
        bisection = Bisection(self.data, self.target, self.variable)
        return bisection.compute()

    def solve(self) -> float:
        return self.x_n - (self.solved_function() / self.solved_derivate())

    def solved_function(self):
        return self.function.function(variable_value=self.x_n)

    def solved_derivate(self):
        return self.function.derivate(variable_value=self.x_n)

    def _prepare(self):
        self._set_function()

    def _set_function(self):
        if len(self._sorted_data) > 2:
            self._function = Polynominal(
                data=self._sorted_data, variable=self.variable, target=self.target
            )
        else:
            self._function = Linear(
                data=self._sorted_data, variable=self.variable, target=self.target
            )