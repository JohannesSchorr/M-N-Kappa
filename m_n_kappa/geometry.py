from abc import ABC, abstractmethod
from dataclasses import dataclass

from .general import (
    print_sections,
    str_start_end,
    StrainPosition,
    EffectiveWidths,
    interpolation,
)
from .material import Material
from .section import Section
from .crosssection import Crosssection

"""
Geometries
##########

Basic geometries providing parameters like area, centroid, etc.

Currently available basic geometries
------------------------------------
  - Rectangle
  - Circle 
  - Trapezoid
  
Currently available composed geometries
---------------------------------------
  - IProfile
  - RebarLayer
  - UPEProfile
"""


class ComposedGeometry:

    """
    Geometry consisting of several basic geometries

    such as:
    - RebarLayer: consists of several circular geometries
    - profile: T-profile consists of two flanges and one web
    """
    def __init__(self):
        self._geometries = []

    def __add__(self, other):
        return self._build(other)

    def __radd__(self, other):
        return self._build(other)

    def __mul__(self, other):
        return self._build(other)

    def _build(self, other):
        if isinstance(other, Material):
            sections = [
                Section(geometry=geometry, material=other)
                for geometry in self.geometries
            ]
            return Crosssection(sections)
        elif isinstance(other, Geometry):
            new_geometry = ComposedGeometry()
            new_geometry._geometries = self.geometries
            new_geometry._geometries.append(other)
            return new_geometry
        elif isinstance(other, ComposedGeometry):
            new_geometry = ComposedGeometry()
            new_geometry._geometries = self.geometries + other.geometries
            return new_geometry
        else:
            raise TypeError(
                f'unsupported operand type(s) for +: "{type(self)}" and "{type(other)}"'
            )

    @property
    def geometries(self) -> list:
        return self._geometries


class Geometry(ABC):

    """basic geometry class"""

    def __add__(self, other):
        return self._build(other)

    def __radd__(self, other):
        return self._build(other)

    def __mul__(self, other):
        return self._build(other)

    def _build(self, other):
        """builds depending on the input-type a :py:class:`ComposedGeometry` or a :py:class:`Section`"""
        if isinstance(other, Geometry):
            new_geometry = ComposedGeometry()
            new_geometry._geometries = [self, other]
            return new_geometry
        elif isinstance(other, ComposedGeometry):
            new_geometry = other
            new_geometry._geometries.append(self)
            return new_geometry
        elif isinstance(other, Material):
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
    def split(
        self, at_points: list[StrainPosition], max_widths: EffectiveWidths = None
    ):
        ...

    @property
    @abstractmethod
    def edges(self) -> list[float]:
        """vertical edges"""
        ...

    @property
    @abstractmethod
    def sides(self) -> list[float]:
        """horizontal edges"""
        ...


def check_width(
    width: float = None, left_edge: float = None, right_edge: float = None
) -> tuple:
    """
    make sure all properties corresponding with the width are filled:
      - width
      - left_edge
      - right_edge
    """
    if left_edge is not None and right_edge is not None:
        if left_edge > right_edge:
            left_edge, right_edge = right_edge, left_edge
    if width is not None and left_edge is None and right_edge is None:
        left_edge = -0.5 * width
        right_edge = 0.5 * width
    elif width is None and left_edge is not None and right_edge is not None:
        width = abs(left_edge - right_edge)
    elif width is not None and left_edge is None and right_edge is not None:
        left_edge = right_edge - width
    elif width is not None and left_edge is not None and right_edge is None:
        right_edge = left_edge + width
    elif width is not None and left_edge is not None and right_edge is not None:
        if abs(left_edge - right_edge) != width:
            raise ValueError(
                f"abs(left_edge - right_edge) = abs({left_edge} - {right_edge}) != width = {width}. "
                f"Please check/adapt input-values."
            )
    else:
        raise ValueError(
            "At least two of arguments 'width', 'right_edge' and 'left_edge' must be given."
        )
    return width, left_edge, right_edge


class Rectangle(Geometry):
    """
    Represents a rectangle
    """

    def __init__(
        self,
        top_edge: float,
        bottom_edge: float,
        width: float = None,
        left_edge: float = None,
        right_edge: float = None,
    ):
        """
        Neither two of the following arguments 'width', 'right_edge' and 'left_edge' must be given.
        But if only argument 'width' is given left and right edge apply to 0.5*width

        Parameters
        ----------
        top_edge : float
            top-edge of the rectangle
        bottom_edge : float
            bottom-edge of the rectangle
        width : float
            width of the rectangle (Default: None).
        left_edge : float
            left-edge of the rectangle (Default: None).
        right_edge : float
            right-edge of the rectangle (Default: None)
        """
        self._top_edge = top_edge
        self._bottom_edge = bottom_edge
        self._width = width
        self._left_edge = left_edge
        self._right_edge = right_edge
        self._check_input_values()
        self._width, self._left_edge, self._right_edge = check_width(
            self.width, self.left_edge, self.right_edge
        )

    def _check_input_values(self) -> None:
        """rearrange input-values to match the needed arrangement"""
        if self.bottom_edge < self.top_edge:
            self._top_edge, self._bottom_edge = self.bottom_edge, self.top_edge
        if (
            self.left_edge is not None
            and self.right_edge is not None
            and self.right_edge < self.left_edge
        ):
            self._left_edge, self._right_edge = self.right_edge, self.left_edge

    def __eq__(self, other):
        return (
            self.top_edge == other.top_edge
            and self.bottom_edge == other.bottom_edge
            and self.width == other.width
            and self.left_edge == other.left_edge
            and self.right_edge == other.right_edge
        )

    def __repr__(self) -> str:
        return (
            f"Rectangle("
            f"top_edge={self.top_edge:.2f}, "
            f"bottom_edge={self.bottom_edge:.2f}, "
            f"width={self.width:.2f}, "
            f"left_edge={self.left_edge:.2f}, "
            f"right_edge={self.right_edge:.2f})"
        )

    @str_start_end
    def __str__(self) -> str:
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
            f"Area: {self.area:.2f}",
            f"Centroid: {self.centroid:.2f}",
        ]
        return print_sections(text)

    @property
    def top_edge(self):
        return self._top_edge

    @property
    def bottom_edge(self):
        return self._bottom_edge

    @property
    def right_edge(self) -> float:
        return self._right_edge

    @property
    def left_edge(self) -> float:
        return self._left_edge

    @property
    def edges(self):
        return [self.top_edge, self.bottom_edge]

    @property
    def sides(self) -> list[float]:
        return [self.left_edge, self.right_edge]

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

    def split(
        self, at_points: list[StrainPosition], max_widths: EffectiveWidths = None
    ) -> list[Geometry]:
        """
        splitting the rectangle horizontally in smaller rectangles

        Parameters
        ----------
        at_points : list[StrainPosition]
            points where the rectangle is split into smaller rectangles
        max_widths: EffectiveWidths
            widths under consideration of bending or membran loading

        Returns
        -------
        list[Rectangle]
            rectangles assembling to the original rectangle
        """
        rectangles = []
        at_points.sort(key=lambda x: x.position)
        top_edge = StrainPosition(at_points[0].strain, self.top_edge, at_points[0].material)
        for bottom_edge in at_points:
            if self.top_edge < bottom_edge.position < self.bottom_edge:
                if bottom_edge.strain == 0.0:
                    edge = top_edge
                else:
                    edge = bottom_edge
                left_edge, right_edge = self.get_horizontal_edges(edge, max_widths)
                rectangles.append(
                    Rectangle(
                        top_edge.position,
                        bottom_edge.position,
                        left_edge=left_edge,
                        right_edge=right_edge,
                    ))
                top_edge = bottom_edge
        if top_edge.strain == 0.0:
            edge = StrainPosition(at_points[-1].strain, self.bottom_edge, at_points[-1].material)
        else:
            edge = top_edge
        left_edge, right_edge = self.get_horizontal_edges(edge, max_widths)
        rectangles.append(Rectangle(top_edge.position, self.bottom_edge, left_edge=left_edge, right_edge=right_edge))
        #print(rectangles)
        return rectangles

    def get_horizontal_edges(
        self, point: StrainPosition, max_widths: EffectiveWidths
    ) -> tuple:
        """
        Get the horizontal edges of the rectangles considering the effective widths
        as well as real dimensions of the rectangle

        Parameters
        ----------
        point : StrainPosition
            position and strain at this position as well as the corresponding material.
            Needed to differentiate between rectangle under tension and under compression.
        max_widths : EffectiveWidths
            effective widths to consider

        Returns
        -------
        tuple[float, float]
            left and right edge considering the effective widths as well as real dimensions of the rectangle
        """
        if max_widths is not None:
            effective_width = max_widths.width(point.material, point.strain)
            right_edge = min(effective_width, self.right_edge)
            left_edge = max(-effective_width, self.left_edge)
            # if right_edge != self.right_edge or left_edge != self.left_edge:
                # print(f"{point.strain}, {point.material}, "
                #      f"{left_edge=:.2f} != {self.left_edge} or "
                #      f"{right_edge=:.2f} != {self.right_edge}")
        else:
            right_edge, left_edge = self.right_edge, self.left_edge
        return left_edge, right_edge


class Circle(Geometry):
    """
    Circle

    Parameters
    ----------
    diameter: float
        diameter of the circle
    centroid_y: float
        position of centroid of the circle in vertical direction
    centroid_z: float
        position of centroid of the circle in horizontal direction
    """

    def __init__(self, diameter: float, centroid_y: float, centroid_z: float):
        self._diameter = diameter
        self._centroid_y = centroid_y
        self._centroid_z = centroid_z

    def __eq__(self, other) -> bool:
        return (
            self.diameter == other.diameter
            and self.centroid_y == other.centroid_y
            and self.centroid_z == other.centroid_z
        )

    def __repr__(self) -> str:
        return (
            f"Circle("
            f"diameter={self.diameter}, "
            f"centroid_y={self._centroid_y}, "
            f"centroid_z={self._centroid_z})"
        )

    @str_start_end
    def __str__(self) -> str:
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
            f"Area: {self.area:.2f}",
            f"Centroid: ({self.centroid_y:.2f}, {self.centroid_y:.2f})",
        ]
        return "\n".join(text)

    @property
    def diameter(self):
        return self._diameter

    @property
    def centroid(self):
        return self._centroid_y

    @property
    def centroid_y(self):
        return self._centroid_y

    @property
    def centroid_z(self):
        return self._centroid_z

    @property
    def area(self):
        return 3.145 * (0.5 * self.diameter) ** 2.0

    @property
    def edges(self) -> list[float]:
        return [self.centroid_y]

    @property
    def sides(self) -> list[float]:
        return [self.centroid_z]

    @property
    def top_edge(self):
        return self.centroid_y - 0.5 * self.diameter

    @property
    def bottom_edge(self):
        return self.centroid_y + 0.5 * self.diameter

    @property
    def height(self) -> float:
        return 0.0

    def split(
        self, at_points: list[StrainPosition], max_widths: EffectiveWidths = None
    ) -> list:
        if max_widths is None:
            return [self]
        elif self._is_in_effective_width(at_points, max_widths):
            return [self]  # [Circle(self.diameter, self.centroid)]
        else:
            return []

    def _is_in_effective_width(
        self, points: list[StrainPosition], max_widths: EffectiveWidths
    ) -> bool:
        """checks if centroid of circle is within the effective width"""
        for point_index in range(len(points)):
            two_points = [
                points[point_index].position,
                points[point_index + 1].position,
            ]
            if min(two_points) <= self.centroid_y <= max(two_points):
                width = max_widths.width(
                    points[0].material,
                    sum([points[point_index].strain, points[point_index + 1].strain]),
                )
                return -width <= self.centroid_z <= width
            else:
                return False


class Trapezoid(Geometry):
    """
    Represents a trapezoidal
    """

    def __init__(
        self,
        top_edge: float,
        bottom_edge: float,
        top_width: float,
        top_left_edge: float = None,
        top_right_edge: float = None,
        bottom_width: float = None,
        bottom_left_edge: float = None,
        bottom_right_edge: float = None,
    ):
        """
        Parameters
        ----------
        top_edge : float
            top-edge of the rectangle
        bottom_edge : float
            bottom-edge of the rectangle
        top_width : float
            width of the trapezoid at the top-edge (Default: None).
        top_left_edge : float
            left-edge position of the trapezoid at the top-edge (Default: None).
        top_right_edge : float
            right-edge position of the trapezoid at the top-edge (Default: None).
        bottom_width : float
            width of the trapezoid at the bottom-edge (Default: None).
        bottom_left_edge : float
            left-edge position of the trapezoid at the bottom-edge (Default: None).
        bottom_right_edge : float
            right-edge position of the trapezoid at the bottom-edge (Default: None).
        """
        self._top_edge = top_edge
        self._bottom_edge = bottom_edge
        self._top_width = top_width
        self._top_left_edge = top_left_edge
        self._top_right_edge = top_right_edge
        self._bottom_width = bottom_width
        self._bottom_left_edge = bottom_left_edge
        self._bottom_right_edge = bottom_right_edge
        self._check_input_values()
        self._top_width, self._top_left_edge, self._top_right_edge = check_width(
            self.top_width, self.top_left_edge, self.top_right_edge
        )
        (
            self._bottom_width,
            self._bottom_left_edge,
            self._bottom_right_edge,
        ) = check_width(
            self.bottom_width, self.bottom_left_edge, self.bottom_right_edge
        )

    def _check_input_values(self) -> None:
        """check input-value to match the needed arrangement"""
        if self.bottom_edge < self.top_edge:
            self._top_edge, self._bottom_edge = self.bottom_edge, self.top_edge
        if (
            self.top_left_edge is not None
            and self.top_right_edge is not None
            and self.top_right_edge < self.top_left_edge
        ):
            self._top_left_edge, self._top_right_edge = (
                self.top_right_edge,
                self.top_left_edge,
            )
        if (
            self.bottom_left_edge is not None
            and self.bottom_right_edge is not None
            and self.bottom_right_edge < self.bottom_left_edge
        ):
            self._bottom_left_edge, self._bottom_right_edge = (
                self.bottom_right_edge,
                self.bottom_left_edge,
            )

    @property
    def top_left_edge(self) -> float:
        return self._top_left_edge

    @property
    def bottom_left_edge(self) -> float:
        return self._bottom_left_edge

    @property
    def top_right_edge(self) -> float:
        return self._top_right_edge

    @property
    def bottom_right_edge(self) -> float:
        return self._bottom_right_edge

    def __repr__(self) -> str:
        return (
            f"Trapezoid(top_edge={self.top_edge}, "
            f"bottom_edge={self.bottom_edge}, "
            f"top_width={self.top_width}, "
            f"bottom_width={self.bottom_width})"
        )

    @str_start_end
    def __str__(self) -> str:
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

    def __eq__(self, other) -> bool:
        return (
            self.top_edge == other.top_edge
            and self.bottom_edge == other.bottom_edge
            and self.top_width == other.top_width
            and self.bottom_width == other.bottom_width
        )

    @property
    def top_edge(self) -> float:
        return self._top_edge

    @property
    def bottom_edge(self) -> float:
        return self._bottom_edge

    @property
    def edges(self) -> list:
        return [self.top_edge, self.bottom_edge]

    @property
    def sides(self) -> list[float]:
        return [
            self.top_left_edge,
            self.top_right_edge,
            self.bottom_left_edge,
            self.bottom_right_edge,
        ]

    @property
    def top_width(self) -> float:
        return self._top_width

    @property
    def bottom_width(self) -> float:
        return self._bottom_width

    @property
    def height(self) -> float:
        return abs(self.top_edge - self.bottom_edge)

    @property
    def area(self) -> float:
        return 0.5 * self.height * (self.top_width + self.bottom_width)

    @property
    def centroid(self) -> float:
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

    def width(self, vertical_position: float) -> float:
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return interpolation(
                position_value=vertical_position,
                first_pair=[self.top_edge, self.top_width],
                second_pair=[self.bottom_edge, self.bottom_width],
            )
        else:
            return 0.0

    def left_edge(self, vertical_position: float) -> float:
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return interpolation(
                position_value=vertical_position,
                first_pair=[self.top_edge, self.top_left_edge],
                second_pair=[self.bottom_edge, self.bottom_left_edge],
            )
        else:
            return 0.0

    def right_edge(self, vertical_position: float) -> float:
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return interpolation(
                position_value=vertical_position,
                first_pair=[self.top_edge, self.top_right_edge],
                second_pair=[self.bottom_edge, self.bottom_right_edge],
            )
        else:
            return 0.0

    def split(
        self, at_points: list[StrainPosition], max_widths: EffectiveWidths = None
    ) -> list[Geometry]:
        """
        split trapezoid at the given points and if needed to

        Parameters
        ----------
        at_points
        max_widths

        Returns
        -------
        list[Trapezoid]
            trapezoid split at the material-points into sub-trapezoids
        """
        top_edge = self.top_edge
        trapazoids = []
        at_points.sort(key=lambda x: x.position)
        for point in at_points:
            if self.top_edge < point.position < self.bottom_edge:
                trapazoids.append(
                    Trapezoid(
                        top_edge=top_edge,
                        bottom_edge=point.position,
                        top_width=self.width(top_edge),
                        top_left_edge=self.left_edge(top_edge),
                        bottom_width=self.width(point.position),
                        bottom_left_edge=self.left_edge(point.position),
                    )
                )
                top_edge = point.position
        trapazoids.append(
            Trapezoid(
                top_edge=top_edge,
                bottom_edge=self.bottom_edge,
                top_width=self.width(top_edge),
                top_left_edge=self.left_edge(top_edge),
                bottom_width=self.bottom_width,
                bottom_left_edge=self.bottom_left_edge,
            )
        )
        return trapazoids

    @property
    def width_slope(self) -> float:
        return (self.bottom_width - self.top_width) / self.height

    @property
    def width_interception(self) -> float:
        return self.top_width - self.top_edge * self.width_slope


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
    centroid_z: float
        horizontal position of the centroid of the I-profile (Default: 0)

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
    centroid_z: float = 0.0
    geometries: list = None

    def __post_init__(self):
        self.geometries = []
        if self.has_bottom_flange and self.t_fu is None and self.t_fo is not None:
            self.t_fu = self.t_fo
        if self.has_bottom_flange and self.b_fu is None and self.b_fo is not None:
            self.b_fu = self.b_fo
        self._add_top_flange()
        self._add_web()
        self._add_bottom_flange()

    def _add_top_flange(self):
        """add top-flange to geometry if wanted and geometric values are given"""
        if self.has_top_flange and self.t_fo is not None and self.b_fo is not None:
            self.geometries.append(
                Rectangle(
                    top_edge=self.top_edge,
                    bottom_edge=self.top_edge + self.t_fo,
                    width=self.b_fo,
                    left_edge=self.centroid_z - 0.5 * self.b_fo,
                )
            )

    def _add_web(self) -> None:
        """add web to the geometry of the profile"""
        self.geometries.append(
            Rectangle(
                top_edge=self.top_edge + self.t_fo,
                bottom_edge=self.top_edge + self.t_fo + self.h_w,
                width=self.t_w,
                left_edge=self.centroid_z - 0.5 * self.t_w,
            )
        )

    def _add_bottom_flange(self) -> None:
        """add bottom-flange to geometry if wanted and geometric values are given"""
        if self.has_bottom_flange and self.t_fu is not None and self.b_fu is not None:
            self.geometries.append(
                Rectangle(
                    top_edge=self.top_edge + self.t_fo + self.h_w,
                    bottom_edge=self.top_edge + self.t_fo + self.h_w + self.t_fu,
                    width=self.b_fu,
                    left_edge=self.centroid_z - 0.5 * self.b_fu,
                )
            )


@dataclass
class RebarLayer(ComposedGeometry):

    """
    rebar-layer composed of several reinforcement-bars of :py:class:`Circle`

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
    left_edge: float = None
    right_edge: float = None
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
        if self.width is None:
            self.width = float(self.rebar_number - 1) * self.rebar_horizontal_distance
        if self.rebar_horizontal_distance is None:
            self.rebar_horizontal_distance = float(self.width / self.rebar_number)
        self.width, self.left_edge, self.right_edge = check_width(self.width, self.left_edge, self.right_edge)

        self.geometries = []
        for index in range(self.rebar_number):
            centroid_z = index * self.rebar_horizontal_distance + self.left_edge
            self.geometries.append(
                Circle(
                    diameter=self.rebar_diameter,
                    centroid_y=self.centroid,
                    centroid_z=centroid_z,
                ))


@dataclass
class UPEProfile(ComposedGeometry):

    """
    UPE-Profile composed of class Rectangles

    Parameters
    ----------
    top_edge : float
        top-edge of the rectangle
    t_f: float
        flange-thickness
    b_f: float
        flange-width
    t_w: float
        web-thickness
    h_w: float = None
        web-height (Default: None). Alternative argument 'h' must be given, otherwise an exception will be risen.
    h: float = None
        overall height of the steel-profile (Default: None). Alternative arguments 'h_w' and 't_f' must be given.
    centroid_z: float
        horizontal position of the centroid of the I-profile (Default: 0.0)

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
    centroid_z: float = 0.0
    geometries: list = None

    def __post_init__(self):
        if self.h_w is None and self.h is None:
            raise ValueError(
                'neither argument "h_w" (web-height) or "h" (profile-height) must be defined'
            )
        if self.h_w is None:
            self.h_w = self.h - 2.0 * self.t_f
        self.geometries = [
            self._left_flange(),
            self._web(),
            self._right_flange(),
        ]

    def _left_flange(self) -> Rectangle:
        return Rectangle(
            top_edge=self.top_edge,
            bottom_edge=self.top_edge + self.b_f,
            width=self.t_f,
            left_edge=self.centroid_z - 0.5 * self.h_w - self.t_f,
        )

    def _web(self) -> Rectangle:
        return Rectangle(
            top_edge=self.top_edge,
            bottom_edge=self.top_edge + self.t_w,
            width=self.h_w,
            left_edge=self.centroid_z - 0.5 * self.h_w,
        )

    def _right_flange(self) -> Rectangle:
        return Rectangle(
            top_edge=self.top_edge,
            bottom_edge=self.top_edge + self.b_f,
            width=self.t_f,
            left_edge=self.centroid_z + 0.5 * self.h_w,
        )