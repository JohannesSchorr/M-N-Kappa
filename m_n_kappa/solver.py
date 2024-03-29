import operator

from .general import str_start_end, print_chapter, print_sections
from .function import Polynominal, Linear

from .log import LoggerMethods

log = LoggerMethods(__name__)


class Solver:

    """
    Meta Solver-Class

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_maximum_variable",
        "_minimum_variable",
        "_function",
        "_sorted_data",
        "_x_n",
        "_x_n_plus_1",
    )

    @log.init
    def __init__(
        self, data: list[dict] | list[list], target: str | int, variable: str | int
    ):
        """
        Parameters
        ----------
        data : list[dict] | list[list]
            data containing target and variable keys
        target : str | int
            key of the target (e.g. str for dictionaries or int for lists)
        variable : str | int
            variable of the target (e.g. str for dictionaries or int for lists)
        """
        self._data = data
        self._target = target
        self._variable = variable
        self._x_n = self._compute_x_n()
        if len(self._data) > 1:
            self._maximum_variable = self._compute_maximum_variable()
            self._minimum_variable = self._compute_minimum_variable()
        self._sorted_data = self._sort_data()
        self._prepare()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"data=data, "
            f"target={self.target}, "
            f"variable={self.variable})"
        )

    @str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_data(),
            self._print_initial_value(),
            self._print_result(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [f"{self.__class__.__name__}", len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(["Initialization", "--------------", self.__repr__()])

    def _print_initial_value(self) -> str:
        return print_sections(
            ["Initial Value", "-------------", f"x_n = {self.x_n:.2f}"]
        )

    def _print_result(self) -> str:
        return print_sections(
            [
                "Result",
                "------",
                f"min_under_zero: {self._min_under_zero_variable()} | "
                f"min_over_zero: {self._min_over_zero_variable()}",
            ]
        )

    def _print_data(self) -> str:
        """print the data that has been passed"""
        line = (2 * 10 + 5) * "-"
        text = [
            "Data",
            "----",
            "",
            line,
            f"{self.variable} | {self.target}",
            line,
        ]
        for point in self.data:
            text.append(f"{point[self.variable]:10.2f} | {point[self.target]:10.2f}")
        text.append(line)
        return print_sections(text)

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
    def target(self) -> str | int:
        """key of the target in ``data``"""
        return self._target

    @property
    def variable(self) -> str | int:
        """key of the variable in ``data``"""
        return self._variable

    @property
    def x_n(self) -> float:
        """lastly computed variable value"""
        return self._x_n

    @property
    def x_n_plus_1(self) -> float:
        """new computed value"""
        return self._x_n_plus_1

    def compute(self, use_fallback: bool = False) -> float:
        pass

    def _prepare(self) -> None:
        pass

    def _compute_x_n(self):
        """
        get the variable value that leads to target-value nearest to zero
        """
        sorted_data = sorted(self.data, key=lambda x: abs(x[self.target]))
        return sorted_data[0][self.variable]

    def _sort_data(self) -> list:
        """
        sort the data by the target value and get the two target-values greater zero
        and the two target values smaller zero, if available
        """
        gt_zero = self._target_values_greater_zero()
        lt_zero = self._target_values_smaller_zero()
        if len(gt_zero) > 2:
            gt_zero = self._sort_data_by_target_and_variable(gt_zero)
            gt_zero = gt_zero[:2]
        if len(lt_zero) > 2:
            lt_zero = self._sort_data_by_target_and_variable(lt_zero)
            lt_zero = lt_zero[:2]
        new_data = gt_zero + lt_zero
        new_data.sort(key=lambda x: abs(x[self.target]))
        return new_data

    def _target_values_greater_zero(self) -> list:
        """data-values where ``target``-value is greater zero"""
        return list(filter(lambda x: x[self.target] > 0.0, self.data))

    def _target_values_smaller_zero(self) -> list:
        """data-values where ``target``-value is smaller zero"""
        return list(filter(lambda x: x[self.target] < 0.0, self.data))

    def _compute_maximum_variable(self) -> float:
        """compute the maximal variable value"""
        return max(self._data, key=operator.itemgetter(self.variable))[self.variable]

    def _compute_minimum_variable(self) -> float:
        """compute the minimum variable value"""
        return min(self._data, key=operator.itemgetter(self.variable))[self.variable]

    def _min_over_zero_variable(self) -> float:
        """compute the variable value that has the nearest target value  above zero"""
        data = self._sort_data_by_target_and_variable(
            self._target_values_greater_zero()
        )
        return data[0][self.variable]

    def _min_under_zero_variable(self) -> float:
        """compute the variable value that has the nearest target value below zero"""
        data = self._sort_data_by_target_and_variable(
            self._target_values_smaller_zero()
        )
        return data[0][self.variable]

    def _sort_data_by_target_and_variable(self, data: list) -> list:
        """
        sort the data primarily by ``target`` and secondarily by ``variable``

        Precisely it is not sorted for ``variable``, but for the difference between
        ``variable`` and ``x_n``

        Parameters
        ----------
        data : list[list] | list[data]

        Returns
        -------
        list
            sorted data
        """
        return sorted(
            data, key=lambda x: (abs(x[self.target]), abs(x[self.variable] - self.x_n))
        )


class Bisection(Solver):

    """
    Bisection solver

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_maximum_variable",
        "_minimum_variable",
        "_x_n_plus_1",
        "_x_n",
    )

    @log.init
    def __init__(
        self, data: list[dict] | list[list], target: str | int, variable: str | int
    ):
        """
        Parameters
        ----------
        data : list[dict] | list[list]
            data containing target and variable keys
        target : str | int
            key of the target (e.g. str for dictionaries or int for lists)
        variable : str | int
            variable of the target (e.g. str for dictionaries or int for lists)
        """
        super().__init__(data, target, variable)

    @log.result
    def compute(self, use_fallback: bool = False) -> float:
        """
        Compute a new variable value that leading to a target-value nearer zero

        Parameters
        ----------
        use_fallback : bool
            has no effect, as bisection is the fallback-function

        Returns
        -------
        float
            new variable-value leading to a target-value nearer zero than the values in ``data``
        """
        variables = [data_point[self.variable] for data_point in self.data]
        log.debug(f"{variables=}")
        factors = [
            0.5,
            0.01,
            0.99,
            0.25,
            0.75,
            0.05,
            0.1,
            0.2,
            0.3,
            0.4,
            0.6,
            0.7,
            0.8,
            0.9,
            0.95,
        ]
        for factor in factors:
            self._x_n_plus_1 = self._compute_with(factor)
            if self.x_n_plus_1 not in variables:
                log.debug(self.__str__())
                return self.x_n_plus_1

    def _compute_with(self, factor: float = 0.5) -> float:
        """
        weighted bisection-procedure

        Method weights between the variable that has the minimum target-value over zero and
        the minimum target-value below zero.
        ``factor`` weights between both values.

        Parameters
        ----------
        factor : float
            weighting-factor, must be greater 0.0 and smaller 1.0 (Default: 0.5)

        Returns
        -------
        float
            computed bisection
        """
        return self._min_under_zero_variable() + factor * (
            self._min_over_zero_variable() - self._min_under_zero_variable()
        )

    def print_values(self) -> str:
        return (
            f"min over zero: {self._min_over_zero_variable()} | "
            f"min under zero: {self._min_under_zero_variable()} | "
            f"mean: {self.compute()}"
        )


class Newton(Solver):
    """
    Solver using the newton method

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_data",
        "_target",
        "_variable",
        "_maximum_variable",
        "_minimum_variable",
        "_function",
        "_x_n_plus_1",
        "_x_n",
    )

    @log.init
    def __init__(
        self, data: list[dict] | list[list], target: str | int, variable: str | int
    ):
        """
        Parameters
        ----------
        data : list[dict] | list[list]
            data containing target and variable keys
        target : str | int
            key of the target (e.g. str for dictionaries or int for lists)
        variable : str | int
            variable of the target (e.g. str for dictionaries or int for lists)
        """
        super().__init__(data, target, variable)

    @property
    def function(self):
        """function to compute ``x_n_plus_1``"""
        return self._function

    @log.result
    def compute(self, use_fallback: bool = False) -> float:
        """
        compute a new value using the newton algorithm

        In case the newton algorithm does not lead to an optimization of the variable value
        then bi-section will be used as fallback.
        Optimization means improvement of variable-value leading to a target-value nearer zero.

        Parameters
        ----------
        use_fallback : bool
            use the fallback algorithm (i.e. :py:class:`~m_n_kappa.solve.Bisection`)

        Returns
        -------
        float
            computed new value leading to target-value nearer zero

        See Also
        --------
        Bisection : :py:class:`~m_n_kappa.solver.Solver`-class using bi-sectional approach
        """
        if use_fallback:
            return self._fallback()
        self._x_n_plus_1 = self._solve()
        if not self._is_between_nearest_values():
            log.info(
                f"Newton-algorithm gives {self.x_n_plus_1}. "
                f"Not between {self._min_under_zero_variable()} and "
                f"{self._min_over_zero_variable()}. Use fallback."
            )
            self._x_n_plus_1 = self._fallback()
        return self.x_n_plus_1

    def _is_between_nearest_values(self) -> bool:
        """is the newly computed value between the minimum smaller and greater value"""
        min_values = [self._min_under_zero_variable(), self._min_over_zero_variable()]
        if min(min_values) < self.x_n_plus_1 < max(min_values):
            return True
        else:
            return False

    def _fallback(self) -> float:
        """fallback mechanism"""
        log.info("Fallback: Bisection")
        bisection = Bisection(self.data, self.target, self.variable)
        return bisection.compute()

    def _solve(self) -> float:
        """
        solves the equation of the newton algorithm

        .. math::

           x_\\mathrm{n+1} = x_\\mathrm{n} - \\frac{f(x_\\mathrm{n})}{f'(x_\\mathrm{n})}

        """
        return self.x_n - (self._solved_function() / self._solved_derivate())

    def _solved_function(self):
        """function to find zero crossing computed using :math:`x_\\mathrm{n}`"""
        return self.function.function(variable_value=self.x_n)

    def _solved_derivate(self):
        """derivate of the function to find zero crossing computed using :math:`x_\\mathrm{n}`"""
        return self.function.derivate(variable_value=self.x_n)

    def _prepare(self):
        """set the function to be computed"""
        if len(self._sorted_data) > 2:
            self._function = Polynominal(
                data=self._sorted_data, variable=self.variable, target=self.target
            )
            log.debug('Set function "Polynominal"')
        else:
            self._function = Linear(
                data=self._sorted_data, variable=self.variable, target=self.target
            )
            log.debug('Set function "Linear"')
