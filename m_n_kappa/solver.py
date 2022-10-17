from .general import str_start_end
from .function import Polynominal, Linear


class Solver:

    """Meta Solver-Class"""

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_target_value",
        "_maximum_variable",
        "_minimum_variable",
        "_function",
    )

    def __init__(self, data: list, target, variable, target_value: float = 0.0):
        """
        Initilization

        Parameters
        ----------
        data : list
                data containing target and variable keys
        target : str or int
                key of the target (eg. str for dictionaries or int for lists)
        variable : str or int
                variable of the target (eg. str for dictionaries or int for lists)
        target_value : float
                value to meet by the target
        """
        self._data = data
        self._target = target
        self._variable = variable
        self._target_value = target_value
        self._set_variable_boundaries()
        self._sort_data()
        self._prepare()

    def __repr__(self):
        return f"{self.__class__.__name__}(data=data, target={self.target}, variable={self.variable}, target_value={self.target_value})"

    @str_start_end
    def __str__(self):
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
        return self._data

    @property
    def maximum_variable(self) -> float:
        return self._maximum_variable

    @property
    def minimum_variable(self) -> float:
        return self._minimum_variable

    @property
    def target(self):
        return self._target

    @property
    def target_value(self):
        return self._target_value

    @property
    def variable(self):
        return self._variable

    @property
    def x_n(self):
        return self.data[0][self.variable]

    def compute(self):
        pass

    def _prepare(self):
        pass

    def _sort_data(self) -> None:
        self._data.sort(key=lambda x: abs(x[self.target]))

    def _set_variable_boundaries(self):
        if len(self._data) > 1:
            self._set_maximum_variable()
            self._set_minimum_variable()

    def _set_maximum_variable(self) -> None:
        self._maximum_variable = max(self._data, key=lambda x: x[self.variable])[
            self.variable
        ]

    def _set_minimum_variable(self) -> None:
        self._minimum_variable = min(self._data, key=lambda x: x[self.variable])[
            self.variable
        ]


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

    def compute(self) -> float:
        print(
            "min over zero:",
            self._min_over_zero_variable(),
            "| min under zero:",
            self._min_under_zero_variable(),
            "| mean:",
            0.5 * (self._min_under_zero_variable() + self._min_over_zero_variable()),
        )
        return 0.5 * (self._min_under_zero_variable() + self._min_over_zero_variable())

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

    @property
    def function(self):
        return self._function

    @property
    def x_n_plus_1(self) -> float:
        return self._x_n_plus_1

    def compute(self) -> float:
        self._x_n_plus_1 = self.solve()
        if self.minimum_variable <= self.x_n_plus_1 <= self.maximum_variable:
            return self.x_n_plus_1
        else:
            return self.fallback()

    def fallback(self) -> float:
        print("Fallback: Bisection")
        bisec = Bisection(self.data, self.target, self.variable)
        return bisec.compute()

    def solve(self) -> float:
        return self.x_n - (self.solved_function() / self.solved_derivate())

    def solved_function(self):
        return self.function.function(variable_value=self.x_n)

    def solved_derivate(self):
        return self.function.derivate(variable_value=self.x_n)

    def _prepare(self):
        self._set_function()

    def _set_function(self):
        if len(self.data) > 2:
            self._function = Polynominal(
                data=self.data, variable=self.variable, target=self.target
            )
        else:
            self._function = Linear(
                data=self.data, variable=self.variable, target=self.target
            )


if __name__ == "__main__":

    data = [
        [0, 2],
        [-5, -3],
        # [4, 1],
    ]

    solver = Bisection(data=data, target=1, variable=0)
    print(solver)

    solver = Newton
    solver = solver(data=data, target=1, variable=0)
    print(solver)
