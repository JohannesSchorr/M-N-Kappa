from abc import ABC, abstractmethod

from .general import print_sections, print_chapter, str_start_end


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
    def __init__(self, data: list, variable, target):
        self._data = data
        self._variable = variable
        self._target = target
        self._x = self._x_values()
        self._y = self._y_values()
        self._set_constants()

    def __repr__(self):
        return f"{self.__class__.__name__}(data=data[[variable, target]], variable={self.variable}, target={self.target})"

    @str_start_end
    def __str__(self):
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

    def integration(self, variable_value: float):
        pass

    def _function_repr(self):
        return ""

    def _derivate_repr(self):
        return ""

    def _integration_repr(self):
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

    @property
    def intersection(self):
        return self._intersection

    @property
    def slope(self):
        return self._slope

    def derivate(self, variable_value: float):
        return self.slope

    def function(self, variable_value: float):
        return self.slope * variable_value + self.intersection

    def integration(self, variable_value: float, constant: float = 0.0):
        return (
            (1.0 / 2.0) * self.slope * variable_value ** (2.0)
            + self.intersection * variable_value
            + constant
        )

    def _base(self):
        return self._x[0] - self._x[1]

    def _numerator(self):
        return self._y[0] - self._y[1]

    def _derivate_repr(self):
        return "{:.2f}".format(self.slope)

    def _function_repr(self):
        return "{:.2f} x + {:.2f}".format(self.slope, self.intersection)

    def _integration_repr(self):
        return "1/2 * {:.2f} x^2 + {:.2f} x".format(self.slope, self.intersection)

    def _set_constants(self):
        self.__set_slope()
        self.__set_intersection()

    def __set_slope(self):
        self._slope = self._numerator() / self._base()

    def __set_intersection(self):
        self._intersection = self._y[0] - self._x[0] * self.slope


class Polynominal(General):
    """f(x) = y = ax^2 + bx + c"""

    __slots__ = "_a", "_b", "_c", "_data", "_variable", "_target", "_x", "_y"

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def c(self):
        return self._c

    def derivate(self, variable_value: float):
        return 2.0 * self.a * variable_value + self.b

    def function(self, variable_value: float):
        return self.a * variable_value ** (2.0) + self.b * variable_value + self.c

    def integration(self, variable_value: float, constant: float = 0.0):
        return (
            (1.0 / 3.0) * self.a * variable_value ** (3.0)
            + (1.0 / 2.0) * self.b * variable_value ** (2.0)
            + self.c * variable_value
            + constant
        )

    def _derivate_repr(self):
        return "2 {:.2f} x + {:.2f}".format(self.a, self.b)

    def _function_repr(self):
        return "{:.2f} x^2 + {:.2f} x + {:.2f}".format(self.a, self.b, self.c)

    def _integration_repr(self):
        return "(1/3) {:.2f} x^3 + (1/2) {:.2f} x^2 + {:.2f} x".format(
            self.a, self.b, self.c
        )

    def _set_constants(self):
        self.__set_a()
        self.__set_b()
        self.__set_c()

    def __set_a(self):
        self._a = (self.y[2] - self.y[0]) / (
            (self.x[2] - self.x[0]) * (self.x[2] - self.x[1])
        ) - (self.y[1] - self.y[0]) / (
            (self.x[1] - self.x[0]) * (self.x[2] - self.x[1])
        )

    def __set_b(self):
        self._b = ((self.y[1] - self.y[0]) / (self.x[1] - self.x[0])) - (
            self.x[1] + self.x[0]
        ) * self.a

    def __set_c(self):
        self._c = self.y[0] - self.x[0] ** (2.0) * self.a - self.x[0] * self.b
