from abc import ABC, abstractmethod
from dataclasses import dataclass

from .general import print_sections, str_start_end
from .material import Material
from .section import Section
from .crosssection import Crosssection

"""
Geometries
##########

Basic geometries providing parameters like area, centroid, etc.

Currently available
-------------------
  - Rectangle
  - Circle 
  - Trapezoid
"""


class Geometry(ABC):

    """basic geometry class"""

    def __add__(self, other: Material) -> Section:
        return self._build_section(other)

    def __radd__(self, other: Material) -> Section:
        return self._build_section(other)

    def __mul__(self, other: Material) -> Section:
        return self._build_section(other)

    def _build_section(self, other: Material) -> Section:
        if isinstance(other, Material):
            return Section(geometry=self, material=other)
        else:
            raise TypeError(
                f'unsupported operand type(s) for +: "{type(self)}" and "{type(other)}"'
            )

    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def centroid(self) -> float:
        ...

    # @abstractmethod
    # def width(self):
    # 	...

    @abstractmethod
    def split(self, at_points):
        ...

    @abstractmethod
    def edges(self) -> list[float]:
        ...


class Rectangle(Geometry):
    """
    Represents a rectangle
    """

    def __init__(self, top_edge: float, bottom_edge: float, width: float):
        self._top_edge = top_edge
        self._bottom_edge = bottom_edge
        self._width = width

    def __eq__(self, other):
        return (
            self.top_edge == other.top_edge
            and self.bottom_edge == other.bottom_edge
            and self.width == other.width
        )

    def __repr__(self):
        return f"Rectangle(top_edge={self.top_edge}, bottom_edge={self.bottom_edge}, width={self.width})"

    @str_start_end
    def __str__(self):
        text = [
            "Rectangle",
            "=========",
            "",
            "Initialization",
            "--------------",
            self.__repr__(),
            "",
            "Properties",
            "----------",
            "Area: {:.2f}".format(self.area),
            "Centroid: {:.2f}".format(self.centroid),
        ]
        return "\n".join(text)

    @property
    def top_edge(self):
        return self._top_edge

    @property
    def bottom_edge(self):
        return self._bottom_edge

    @property
    def edges(self):
        return [self.top_edge, self.bottom_edge]

    @property
    def height(self):
        return abs(self.top_edge - self.bottom_edge)

    @property
    def width(self):
        return self._width

    @property
    def area(self):
        return self.width * self.height

    @property
    def centroid(self):
        return self.top_edge + 0.5 * self.height

    @property
    def width_slope(self) -> float:
        return 0.0

    @property
    def width_interception(self) -> float:
        return self.width

    def split(self, at_points: list) -> list[Geometry]:
        top_edge = self.top_edge
        rectangles = []
        at_points.sort()
        for point in at_points:
            if self.top_edge < point < self.bottom_edge:
                rectangles.append(Rectangle(top_edge, point, self.width))
                top_edge = point
        rectangles.append(Rectangle(top_edge, self.bottom_edge, self.width))
        return rectangles


class Circle(Geometry):
    """
    Represents a circle
    """

    def __init__(self, diameter: float, centroid: float):
        self._diameter = diameter
        self._centroid = centroid

    def __eq__(self, other) -> bool:
        return self.diameter == other.diameter and self.centroid == other.centroid

    def __repr__(self):
        return f"Circle(diameter={self.diameter}, centroid={self.centroid})"

    @str_start_end
    def __str__(self):
        text = [
            "Circle",
            "======",
            "",
            "Initialization",
            "--------------",
            self.__repr__(),
            "",
            "Properties",
            "----------",
            "Area: {:.2f}".format(self.area),
            "Centroid {:.2f}".format(self.centroid),
        ]
        return "\n".join(text)

    @property
    def diameter(self):
        return self._diameter

    @property
    def centroid(self):
        return self._centroid

    @property
    def area(self):
        return 3.145 * (0.5 * self.diameter) ** 2.0

    def split(self, at_points: list) -> list:
        return [self]  # [Circle(self.diameter, self.centroid)]

    @property
    def edges(self) -> list:
        return [self.centroid]

    @property
    def top_edge(self):
        return self.centroid - 0.5 * self.diameter

    @property
    def bottom_edge(self):
        return self.centroid + 0.5 * self.diameter

    @property
    def height(self) -> float:
        return 0.0


class Trapezoid(Geometry):
    """
    Represents a trapezoidal
    """

    def __init__(
        self, top_edge: float, bottom_edge: float, top_width: float, bottom_width: float
    ):
        self._top_edge = top_edge
        self._bottom_edge = bottom_edge
        self._top_width = top_width
        self._bottom_width = bottom_width

    def __repr__(self):
        return (
            f"Trapezoid(top_edge={self.top_edge}, "
            f"bottom_edge={self.bottom_edge}, "
            f"top_width={self.top_width}, "
            f"bottom_width={self.bottom_width})"
        )

    @str_start_end
    def __str__(self):
        text = [
            "Trapezoid",
            "=========",
            "",
            "Initialization",
            "--------------",
            self.__repr__(),
            "",
            "Properties",
            "----------",
            "Area: {:.2f}".format(self.area),
            "Centroid: {:.2f}".format(self.centroid),
        ]
        return print_sections(text)

    def __eq__(self, other):
        return (
            self.top_edge == other.top_edge
            and self.bottom_edge == other.bottom_edge
            and self.top_width == other.top_width
            and self.bottom_width == other.bottom_width
        )

    @property
    def top_edge(self):
        return self._top_edge

    @property
    def bottom_edge(self):
        return self._bottom_edge

    @property
    def edges(self) -> list:
        return [self.top_edge, self.bottom_edge]

    @property
    def top_width(self):
        return self._top_width

    @property
    def bottom_width(self):
        return self._bottom_width

    @property
    def height(self):
        return abs(self.top_edge - self.bottom_edge)

    @property
    def area(self):
        return 0.5 * self.height * (self.top_width + self.bottom_width)

    @property
    def centroid(self):
        return (
            self.top_edge
            + self.height
            - (
                1.0
                / 3.0
                * self.height
                * (
                    (self.bottom_width + 2.0 * self.top_width)
                    / (self.bottom_width + self.top_width)
                )
            )
        )

    def width(self, vertical_position: float):
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return self.top_width + (vertical_position - self.top_edge) * (
                self.bottom_width - self.top_width
            ) / (self.bottom_edge - self.top_edge)
        else:
            return 0.0

    def split(self, at_points: list) -> list[Geometry]:
        top_edge = self.top_edge
        trapazoids = []
        at_points.sort()
        for point in at_points:
            if self.top_edge < point < self.bottom_edge:
                trapazoids.append(
                    Trapezoid(top_edge, point, self.width(top_edge), self.width(point))
                )
                top_edge = point
        trapazoids.append(
            Trapezoid(
                top_edge, self.bottom_edge, self.width(top_edge), self.bottom_width
            )
        )
        return trapazoids

    @property
    def width_slope(self) -> float:
        return (self.bottom_width - self.top_width) / self.height

    @property
    def width_interception(self) -> float:
        return self.top_width - self.top_edge * self.width_slope


class ComposedGeometry(ABC):

    """
    Geometry consisting of several basic geometries

    such as:
    - RebarLayer: consists of several circular geometries
    - profile: T-profile consists of two flanges and one web
    """

    def __add__(self, other: Material) -> Crosssection:
        return self._build_section(other)

    def __radd__(self, other: Material) -> Crosssection:
        return self._build_section(other)

    def __mul__(self, other) -> Crosssection:
        return self._build_section(other)

    def _build_section(self, other: Material) -> Crosssection:
        if isinstance(other, Material):
            sections = [
                Section(geometry=geometry, material=other)
                for geometry in self.geometries
            ]
            return Crosssection(sections)
        else:
            raise TypeError(
                f'unsupported operand type(s) for +: "{type(self)}" and "{type(other)}"'
            )

    @property
    @abstractmethod
    def geometries(self) -> list[Geometry]:
        ...


@dataclass
class IProfile(ComposedGeometry):

    """
    I-Profile composed of class Rectangles

    Parameters
    ----------
    top_edge: float
        top_edge of the I-profile
    t_w: float
        web-thickness of the I-profile
    h_w: float
        web-height of the I-profile
    t_fo: float = None
        thickness of the top-flange
    b_fo: float = None
        width of the top-flange
    t_fu: float = None
        thickness of the bottom-flange
    b_fu: float = None
        width of the bottom-flange
    has_top_flange: bool = True
        decide if I-profile has a top-flange (Default: True).
        If False: no top-flange is considered
    has_bottom_flange: bool = True
        decide if I-profile has a bottom-flange (Default: True)
        if False: no top-flange is considered

    Example(s):
    -----------
    - HEB 200 -> IProfile(top_edge=0., t_fo=15.5, b_fo=200.0, t_w=9.5, h_w=169.0)
    """

    top_edge: float
    t_w: float
    h_w: float
    t_fo: float = None
    b_fo: float = None
    t_fu: float = None
    b_fu: float = None
    has_top_flange: bool = True
    has_bottom_flange: bool = True
    geometries: list = None

    def __post_init__(self):
        self.geometries = []
        if self.has_bottom_flange and self.t_fu is None and self.t_fo is not None:
            self.t_fu = self.t_fo
        if self.has_bottom_flange and self.b_fu is None and self.b_fo is not None:
            self.b_fu = self.b_fo
        if self.has_top_flange and self.t_fo is not None and self.b_fo is not None:
            self.geometries.append(
                Rectangle(self.top_edge, self.top_edge + self.t_fo, self.b_fo)
            )
        self.geometries.append(
            Rectangle(
                self.top_edge + self.t_fo,
                self.top_edge + self.t_fo + self.h_w,
                self.t_w,
            )
        )
        if self.has_bottom_flange and self.t_fu is not None and self.b_fu is not None:
            self.geometries.append(
                Rectangle(
                    self.top_edge + self.t_fo + self.h_w,
                    self.top_edge + self.t_fo + self.h_w + self.t_fu,
                    self.b_fu,
                )
            )


@dataclass
class RebarLayer(ComposedGeometry):

    """
    rebar-layer composed of several reinforcement-bars of class Circle

    Parameters
    ----------
    rebar_diameter: float
        diameter of rebars in the layer
    centroid: float
        position of the centroid in vertical direction
    rebar_number: int = None
        number of rebars within the layer (Alternative to argument 'width')
    width: float = None
        width of the rebar-layer (together with 'rebar_horizontal_distance' alternative to argument 'rebar_number').
        In case 'rebar_number' is defined, the argument 'width' as well as 'rebar_horizontal_distance' value is ignored.
    rebar_horizontal_distance : float
        distance between the rebars in horizontal direction (Default: None).
        See description in argument 'width'.

    Example
    -------
    - RebarLayer(rebar_diameter: 12.0, centroid=10.0, rebar_number=10)
      Creates 10 circles with diameter 12 and a vertical position of 10
    """

    rebar_diameter: float
    centroid: float
    rebar_number: int = None
    width: float = None
    rebar_horizontal_distance: float = None
    geometries: list = None

    def __post_init__(self):
        if self.rebar_number is None and (
            self.width is None or self.rebar_horizontal_distance is None
        ):
            raise ValueError(
                "Neither argument 'rebar_number' or 'width' and "
                "'rebar_horizontal_distance' must be defined"
            )
        if self.rebar_number is None:
            self.rebar_number = int(self.width / self.rebar_horizontal_distance)
        self.geometries = []
        for _ in range(self.rebar_number):
            self.geometries.append(Circle(self.rebar_diameter, self.centroid))


@dataclass
class UPEProfile(ComposedGeometry):

    """
    UPE-Profile composed of class Rectangles

    Parameters
    ----------
    top_edge :

    Example
    -------
    - UPE 200:
    """

    top_edge: float
    t_f: float
    b_f: float
    t_w: float
    h_w: float = None
    h: float = None
    geometries: list = None

    def __post_init__(self):
        if self.h_w is None and self.h is None:
            raise ValueError(
                'neither argument "h_w" (web-height) or "h" (profile-height) must be defined'
            )
        if self.h_w is None:
            self.h_w = self.h - 2.0 * self.t_f
        self.geometries = [
            Rectangle(self.top_edge, self.top_edge + self.b_f, self.t_f),
            Rectangle(self.top_edge, self.top_edge + self.t_w, self.h_w),
            Rectangle(self.top_edge, self.top_edge + self.b_f, self.t_f),
        ]