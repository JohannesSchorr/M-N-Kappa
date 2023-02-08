from abc import ABC, abstractmethod

from .general import print_sections, print_chapter, str_start_end

from .log import LoggerMethods

log = LoggerMethods(__name__)


class Function(ABC):
    @abstractmethod
    def derivate(self, variable_value: float):
        ...

    @abstractmethod
    def function(self, variable_value: float):
        ...

    @abstractmethod
    def integration(self, variable_value: float):
        ...

    def _set_constants(self):
        ...

    def __function_repr(self):
        ...

    def __derivate_repr(self):
        ...

    def __integration_repr(self):
        ...


class General(Function):

    @log.init
    def __init__(self, data: list, variable, target):
        self._data = data
        self._variable = variable
        self._target = target
        self._x = self._x_values()
        self._y = self._y_values()
        self._set_constants()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"data=data[[variable, target]], "
            f"variable={self.variable}, target={self.target})"
        )

    @str_start_end
    def __str__(self) -> str:
        text = [
            self._print_title(),
            self._print_initialization(),
            self._print_function(),
            self._print_derivate(),
            self._print_integration(),
        ]
        return print_chapter(text)

    def _print_title(self) -> str:
        return print_sections(
            [self.__class__.__name__, len(self.__class__.__name__) * "="]
        )

    def _print_initialization(self) -> str:
        return print_sections(["Initialization", "--------------", self.__repr__()])

    def _print_function(self) -> str:
        return print_sections(
            ["Function", "--------", "f(x) = " + self._function_repr()]
        )

    def _print_derivate(self) -> str:
        return print_sections(
            ["Derivate", "--------", "f'(x) = " + self._derivate_repr()]
        )

    def _print_integration(self) -> str:
        return print_sections(
            ["Integration", "-----------", "F(x) = " + self._integration_repr()]
        )

    @property
    def data(self) -> list:
        return self._data

    @property
    def variable(self):
        return self._variable

    @property
    def target(self):
        return self._target

    @property
    def x(self) -> list:
        return self._x

    @property
    def y(self) -> list:
        return self._y

    def derivate(self, variable_value: float):
        pass

    def function(self, variable_value: float):
        pass

    def get_derivate_function(self):
        return self.derivate

    def get_function(self):
        return self.function

    def get_integration(self):
        return self.integration

    def integration(self, variable_value: float) -> float:
        pass

    def _function_repr(self) -> str:
        return ""

    def _derivate_repr(self) -> str:
        return ""

    def _integration_repr(self) -> str:
        return ""

    def _set_constants(self):
        pass

    def _x_values(self) -> list:
        return self.__values(self.variable)

    def _y_values(self) -> list:
        return self.__values(self.target)

    def __values(self, column) -> list:
        return [point[column] for point in self.data]


class Linear(General):

    __slots__ = "_intersection", "_slope", "_data", "_variable", "_target", "_x", "_y"

    @log.init
    def __init__(self, data: list, variable, target):
        super().__init__(data, variable, target)

    @property
    def intersection(self) -> float:
        return self._intersection

    @property
    def slope(self) -> float:
        return self._slope

    def derivate(self, variable_value: float) -> float:
        return self.slope

    def function(self, variable_value: float) -> float:
        return self.slope * variable_value + self.intersection

    def integration(self, variable_value: float, constant: float = 0.0) -> float:
        return (
            (1.0 / 2.0) * self.slope * variable_value**2.0
            + self.intersection * variable_value
            + constant
        )

    def _base(self) -> float:
        return self._x[0] - self._x[1]

    def _numerator(self) -> float:
        return self._y[0] - self._y[1]

    def _derivate_repr(self) -> str:
        return f"{self.slope:.2f}"

    def _function_repr(self) -> str:
        return f"{self.slope:.2f} x + {self.intersection:.2f}"

    def _integration_repr(self) -> str:
        return f"1/2 * {self.slope:.2f} x^2 + {self.intersection:.2f} x"

    def _set_constants(self) -> None:
        self.__set_slope()
        self.__set_intersection()

    def __set_slope(self) -> None:
        self._slope = self._numerator() / self._base()

    def __set_intersection(self) -> None:
        self._intersection = self._y[0] - self._x[0] * self.slope


class Polynominal(General):
    """f(x) = y = ax^2 + bx + c"""

    __slots__ = "_a", "_b", "_c", "_data", "_variable", "_target", "_x", "_y"

    @property
    def a(self) -> float:
        return self._a

    @property
    def b(self) -> float:
        return self._b

    @property
    def c(self) -> float:
        return self._c

    def derivate(self, variable_value: float) -> float:
        return 2.0 * self.a * variable_value + self.b

    def function(self, variable_value: float) -> float:
        return self.a * variable_value**2.0 + self.b * variable_value + self.c

    def integration(self, variable_value: float, constant: float = 0.0) -> float:
        return (
            (1.0 / 3.0) * self.a * variable_value**3.0
            + (1.0 / 2.0) * self.b * variable_value**2.0
            + self.c * variable_value
            + constant
        )

    def _derivate_repr(self) -> str:
        return f"2 {self.a:.2f} x + {self.b:.2f}"

    def _function_repr(self) -> str:
        return f"{self.a:.2f} x^2 + {self.b:.2f} x + {self.c:.2f}"

    def _integration_repr(self) -> str:
        return f"(1/3) {self.a:.2f} x^3 + (1/2) {self.b:.2f} x^2 + {self.c:.2f} x"

    def _set_constants(self) -> None:
        self.__set_a()
        self.__set_b()
        self.__set_c()

    def __set_a(self) -> None:
        if self.x[0] == self.x[1] or self.x[0] == self.x[2] or self.x[1] == self.x[2]:
            raise ZeroDivisionError(self.data)
        self._a = (self.y[2] - self.y[0]) / (
            (self.x[2] - self.x[0]) * (self.x[2] - self.x[1])
        ) - (self.y[1] - self.y[0]) / (
            (self.x[1] - self.x[0]) * (self.x[2] - self.x[1])
        )

    def __set_b(self) -> None:
        self._b = ((self.y[1] - self.y[0]) / (self.x[1] - self.x[0])) - (
            self.x[1] + self.x[0]
        ) * self.a

    def __set_c(self) -> None:
        self._c = self.y[0] - self.x[0] ** 2.0 * self.a - self.x[0] * self.b
