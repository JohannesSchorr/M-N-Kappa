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

from .log import LoggerMethods

log = LoggerMethods(__name__)

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
    Geometry consisting of basic geometries

    .. versionadded:: 0.1.0

    Supported basic geometries must inherit :py:class:`Geometry`:

    - :py:class:`~m_n_kappa.Rectangle`
    - :py:class:`~m_n_kappa.Circle`
    - :py:class:`~m_n_kappa.Trapezoid`

    See Also
    --------
    IProfile : composed geometry consisting of several :py:class:`Rectangle` forming an ``I``
    UPEProfile : composed geometry consisting of several :py:class:`Rectangle` forming an ``U``
    RebarLayer : composed geometry consisting of several :py:class:`Circle`

    Examples
    --------
    Building a :py:class:`~m_n_kappa.geometry.ComposedGeometry` is as easy as adding two basic geometries together:

    >>> from m_n_kappa import Rectangle
    >>> rectangle_1 = Rectangle(top_edge=0.0, bottom_edge = 10.0, width=10.0)
    >>> rectangle_2 = Rectangle(top_edge=10.0, bottom_edge = 20.0, width=10.0)
    >>> composed_geometry = rectangle_1 + rectangle_2
    >>> composed_geometry
    ComposedGeometry(geometries=[Rectangle(top_edge=0.00, bottom_edge=10.00, width=10.00, left_edge=-5.00, right_edge=5.00), Rectangle(top_edge=10.00, bottom_edge=20.00, width=10.00, left_edge=-5.00, right_edge=5.00)])

    Adding another basic geometry is also easily done.
    This applies also for adding one composed geometry to another.

    >>> rectangle_3 = Rectangle(top_edge=20.0, bottom_edge = 30.0, width=10.0)
    >>> composed_geometry += rectangle_3
    >>> composed_geometry
    ComposedGeometry(geometries=[Rectangle(top_edge=0.00, bottom_edge=10.00, width=10.00, left_edge=-5.00, right_edge=5.00), Rectangle(top_edge=10.00, bottom_edge=20.00, width=10.00, left_edge=-5.00, right_edge=5.00), Rectangle(top_edge=20.00, bottom_edge=30.00, width=10.00, left_edge=-5.00, right_edge=5.00)])

    The composed geometry is also easily combined by adding a :py:class:`~m_n_kappa.Material`
    like :py:class:`~m_n_kappa.Steel` merging to a :py:class:`~m_n_kappa.Crosssection`

    >>> from m_n_kappa import Steel
    >>> steel = Steel(f_y = 300.0, f_u = 350.0, failure_strain=0.25)
    >>> cross_section = composed_geometry + steel
    >>> cross_section
    Crosssection(sections=sections)

    """

    def __init__(self):
        self._geometries = []

    def __add__(self, other):
        return self._build(other)

    def __radd__(self, other):
        return self._build(other)

    def __mul__(self, other):
        return self._build(other)

    def __repr__(self):
        return f"ComposedGeometry(geometries={self.geometries})"

    def _build(self, other):
        if isinstance(other, Material):
            sections = [
                Section(geometry=geometry, material=other)
                for geometry in self.geometries
            ]
            log.info("Create Crosssection by adding Material")
            return Crosssection(sections)
        elif isinstance(other, Geometry):
            new_geometry = ComposedGeometry()
            new_geometry._geometries = self.geometries
            new_geometry._geometries.append(other)
            log.info("Add Geometry-instance")
            return new_geometry
        elif isinstance(other, ComposedGeometry):
            new_geometry = ComposedGeometry()
            new_geometry._geometries = self.geometries + other.geometries
            log.info("Add other ComposedGeometry")
            return new_geometry
        else:
            raise TypeError(
                f'unsupported operand type(s) for +: "{type(self)}" and "{type(other)}"'
            )

    @property
    def geometries(self) -> list:
        """number of :py:class:`Geometry` instances"""
        return self._geometries


class Geometry(ABC):

    """
    basic geometry class

    .. versionadded:: 0.1.0

    the basic geometries must inherit from this class
    """

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
            log.info("Build ComposedGeometry by adding Geometry-Instance")
            return new_geometry
        elif isinstance(other, ComposedGeometry):
            new_geometry = other
            new_geometry._geometries.append(self)
            log.info("Build ComposedGeometry by adding ComposedGeometry-Instance")
            return new_geometry
        elif isinstance(other, Material):
            log.info("Build section by adding material")
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
    make sure all properties corresponding with the width of a :py:class:`~m_n_kappa.Rectangle` or
    :py:class:`~m_n_kappa.Trapezoid` are fulfilled.

    The corresponding properties are: width, left_edge, right_edge

    .. versionadded: 0.1.0

    Parameters
    ----------
    width: float
        width of the :py:class:`~m_n_kappa.Rectangle` or  :py:class:`~m_n_kappa.Trapezoid` (Default: None)
    left_edge: float
        horizontal position (Y-Axis) of left edge of the :py:class:`~m_n_kappa.Rectangle` or
        :py:class:`~m_n_kappa.Trapezoid` (Default: None)
    right_edge: float = None
        horizontal position (Y-Axis) of the right edge of the :py:class:`~m_n_kappa.Rectangle` or
        :py:class:`~m_n_kappa.Trapezoid` (Default: None)

    Returns
    -------
    width : float
       width of  the :py:class:`~m_n_kappa.Rectangle` or  :py:class:`~m_n_kappa.Trapezoid` obtained from the given
       information
    left_edge : float
        horizontal position (Y-Axis) of left edge of the :py:class:`~m_n_kappa.Rectangle` or
        :py:class:`~m_n_kappa.Trapezoid` obtained from the given information
    right_edge : float
        horizontal position (Y-Axis) of right edge of the :py:class:`~m_n_kappa.Rectangle` or
        :py:class:`~m_n_kappa.Trapezoid` obtained from the given information

    Raises
    ------
    ValueError
        if all input-values are ``None``
    ValueError
        if all input-values are given, but do not meet each other: ``right_edge - left_edge != width``
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

    .. versionadded:: 0.1.0
    """

    __slots__ = (
        "_top_edge",
        "_bottom_edge",
        "_width",
        "_left_edge",
        "_right_edge",
    )

    @log.init
    def __init__(
        self,
        top_edge: float,
        bottom_edge: float,
        width: float = None,
        left_edge: float = None,
        right_edge: float = None,
    ):
        """
        Neither two of the following arguments ``width``, ``right_edge`` and ``left_edge`` must be given.
        If only argument ``width`` is given ``left_edge = -0.5*width``  and ``right_edge = 0.5*width``

        Parameters
        ----------
        top_edge : float
            vertical position of top-edge of the rectangle :math:`z_\\mathrm{top}`
        bottom_edge : float
            vertical position of bottom-edge of the rectangle :math:`z_\\mathrm{bottom}`
        width : float
            width of the rectangle :math:`b` (Default: None)
        left_edge : float
            horizontal position of left-edge of the rectangle :math:`y_\\mathrm{left}` (Default: None).
        right_edge : float
            horizontal position of right-edge of the rectangle :math:`y_\\mathrm{right}` (Default: None)


        .. figure:: ../images/geometry_rectangle-light.svg
           :class: only-light
        .. figure:: ../images/geometry_rectangle-dark.svg
           :class: only-dark

           Rectangle - dimensions

        See Also
        --------
        Circle : creates a circular geometry object
        Trapezoid : creates a trapezoidal geometry object
        IProfile : creates a geometry object comprised of various :py:class:`~m_n_kappa.Rectangle`-objects forming an ``I``
        UPEProfile : creates a geometry object comprised of varous :py:class:`~m_n_kappa.Rectangle`-objects forming an ``U``

        Examples
        --------
        A rectangle object is easily instantiated as follows.

        >>> from m_n_kappa import Rectangle
        >>> rectangle = Rectangle(top_edge=10, bottom_edge=20, width=10)

        In case only ``width`` is passed as argument the centerline of the rectangle is assumed to be a :math:`y = 0`.
        In consequence ``left_edge = -0.5 * width`` and ``right_edge = 0.5 * width``

        >>> rectangle.left_edge, rectangle.right_edge
        (-5.0, 5.0)

        For building a :py:class:`~m_n_kappa.Section` the ``rectangle`` must only be added to a material.

        >>> from m_n_kappa import Steel
        >>> steel = Steel(f_y=355)
        >>> section = rectangle + steel
        >>> type(section)
        <class 'm_n_kappa.section.Section'>

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
            log.info(f"{self.__repr__()} switched values: top_edge and bottom_edge")
        if (
            self.left_edge is not None
            and self.right_edge is not None
            and self.right_edge < self.left_edge
        ):
            self._left_edge, self._right_edge = self.right_edge, self.left_edge
            log.info(f"{self.__repr__()} switched values: left_edge and right_edge")

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
        """vertical position (Z-Axis) of the top-edge of the rectangle :math:`z_\\mathrm{top}`"""
        return self._top_edge

    @property
    def bottom_edge(self):
        """vertical position (Z-Axis) of the bottom-edge of the rectangle :math:`z_\\mathrm{bottom}`"""
        return self._bottom_edge

    @property
    def right_edge(self) -> float:
        """horizontal position (Y-Axis) of the right-edge of the rectangle :math:`y_\\mathrm{right}`"""
        return self._right_edge

    @property
    def left_edge(self) -> float:
        """horizontal position (Y-Axis) of the left-edge of the rectangle :math:`y_\\mathrm{left}`"""
        return self._left_edge

    @property
    def edges(self) -> list[float]:
        """vertical positions (Z-Axis) top- and bottom-edge"""
        return [self.top_edge, self.bottom_edge]

    @property
    def sides(self) -> list[float]:
        """horizontal positions (Y-Axis) of left- and right-edge"""
        return [self.left_edge, self.right_edge]

    @property
    def height(self) -> float:
        """height of the rectangle"""
        return abs(self.top_edge - self.bottom_edge)

    @property
    def width(self) -> float:
        """width of the rectangle"""
        return self._width

    @property
    def area(self) -> float:
        """cross-sectional area of rectangle"""
        return self.width * self.height

    @property
    def centroid(self) -> float:
        """centroid of the rectangle in vertical direction (Z-Axis)"""
        return self.top_edge + 0.5 * self.height

    @property
    def width_slope(self) -> float:
        """slope of the width depending of vertical position :math:`z`"""
        return 0.0

    @property
    def width_interception(self) -> float:
        """interception of the width"""
        return self.width

    def split(
        self, at_points: list[StrainPosition], max_widths: EffectiveWidths = None
    ) -> list[Geometry]:
        """
        splitting the rectangle horizontally in smaller rectangles

        Parameters
        ----------
        at_points : list[:py:class:`~m_n_kappa.StrainPosition`]
            points where the rectangle is split into smaller rectangles
        max_widths: :py:class:`~m_n_kappa.EffectiveWidths`
            widths under consideration of bending or membran loading

        Returns
        -------
        list[Rectangle]
            rectangles assembling to the original rectangle
        """
        rectangles = []
        at_points.sort(key=lambda x: x.position)
        top_edge = StrainPosition(
            at_points[0].strain, self.top_edge, at_points[0].material
        )
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
                    )
                )
                top_edge = bottom_edge
        if top_edge.strain == 0.0:
            edge = StrainPosition(
                at_points[-1].strain, self.bottom_edge, at_points[-1].material
            )
        else:
            edge = top_edge
        left_edge, right_edge = self.get_horizontal_edges(edge, max_widths)
        rectangles.append(
            Rectangle(
                top_edge.position,
                self.bottom_edge,
                left_edge=left_edge,
                right_edge=right_edge,
            )
        )
        log.debug(f"Split {self.__repr__()} into following rectangles: {rectangles}")
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
        else:
            right_edge, left_edge = self.right_edge, self.left_edge
        return left_edge, right_edge


class Circle(Geometry):

    __slots__ = ("_diameter", "_centroid_y", "_centroid_z")

    @log.init
    def __init__(self, diameter: float, centroid_y: float, centroid_z: float):
        """
        Circle

        .. versionadded:: 0.1.0

        applies only for circles that are small compared to the other dimensions of the cross-section

        Parameters
        ----------
        diameter: float
            diameter of the circle :math:`d`
        centroid_y: float
            position of centroid of the circle in horizontal direction :math:`y_\\mathrm{centroid}`
        centroid_z: float
            position of centroid of the circle in vertical direction :math:`z_\\mathrm{centroid}`


        .. figure:: ../images/geometry_circle-dark.svg
           :class: only-dark
           :alt: circle dimensions
        .. figure:: ../images/geometry_circle-light.svg
           :class: only-light
           :alt: circle dimensions

           Circle - dimensions

        See Also
        --------
        Rectangle : creates a rectangular geometry object
        Trapezoid : creates a trapezoidal geometry object
        RebarLayer : creates a number of circular objects representing a layer of reinforcement-bars

        Examples
        --------
        A circle object is easily instantiated as follows.

        >>> from m_n_kappa import Circle
        >>> circle = Circle(diameter=10, centroid_y=10, centroid_z=-10)

        For building a :py:class:`~m_n_kappa.Section` the ``circle`` must only be added to a material.

        >>> from m_n_kappa import Steel
        >>> steel = Steel(f_y=355)
        >>> section = circle + steel
        >>> type(section)
        <class 'm_n_kappa.section.Section'>

        """
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
    def diameter(self) -> float:
        """diameter of the circle :math:`d`"""
        return self._diameter

    @property
    def centroid(self) -> float:
        return self._centroid_z

    @property
    def centroid_y(self):
        """position of centroid of the circle in horizontal direction :math:`y_\\mathrm{centroid}`"""
        return self._centroid_y

    @property
    def centroid_z(self):
        """position of centroid of the circle in vertical direction :math:`z_\\mathrm{centroid}`"""
        return self._centroid_z

    @property
    def area(self):
        """area of the circle"""
        return 3.145 * (0.5 * self.diameter) ** 2.0

    @property
    def edges(self) -> list[float]:
        """edges in vertical direction"""
        return [self.centroid_z]

    @property
    def sides(self) -> list[float]:
        """edges in horizontal direction"""
        return [self.centroid_y]

    @property
    def top_edge(self):
        """vertical position (Z-Axis) of the top-edge of the circle"""
        return self.centroid_z - 0.5 * self.diameter

    @property
    def bottom_edge(self):
        """vertical position (Z-Axis) of the bottom-edge of the circle"""
        return self.centroid_z + 0.5 * self.diameter

    @property
    def height(self) -> float:
        return 0.0

    def split(
        self, at_points: list[StrainPosition], max_widths: EffectiveWidths = None
    ) -> list:
        """check if circle is within effective width

        In case ``max_widths=None`` this circle is returned.
        Otherwise, this circle is only returned if position of the circle is smaller ``max_widths``

        See Also
        --------
        Rectangle.split : method that splits :py:class:`Rectangle` considering strain-points and effective widths in
           a number of smaller rectangle

        Trapezoid.split : method that splits :py:class:`Trapezoid` considering strain-points and effective widths in
           a number of smaller trapezoids

        Parameters
        ----------
        at_points : :py:class:`~m_n_kappa.general.StrainPosition`
            has no effect on splitting process
        max_widths : :py:class:`~m_n_kappa.general.EffectiveWidths`
            criteria to return the circle for further computations (Default: None)

        Returns
        -------
        list[Circle]
            this circles
        """
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
                log.info(f"{self.__repr__()} is within effective width")
                return -width <= self.centroid_z <= width
            else:
                log.info(f"{self.__repr__()} is NOT within effective width")
                return False


class Trapezoid(Geometry):
    """
    Represents a trapezoidal

    .. versionadded:: 0.1.0

    The trapezoid has vertical edges parallel to each other and
    two horizontal edges that are *not parallel* to each other.
    """

    __slots__ = (
        "_top_edge",
        "_bottom_edge",
        "_top_width",
        "_top_left_edge",
        "_top_right_edge",
        "_bottom_width",
        "_bottom_left_edge",
        "_bottom_right_edge",
    )

    @log.init
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
            top-edge of the trapezoid :math:`z_\\mathrm{top}`
        bottom_edge : float
            bottom-edge of the trapezoid :math:`z_\\mathrm{bottom}`
        top_width : float
            width of the trapezoid at the top-edge :math:`b_\\mathrm{top}` (Default: None).
        top_left_edge : float
            left-edge position of the trapezoid at the top-edge :math:`y_\\mathrm{top-left}` (Default: None).
        top_right_edge : float
            right-edge position of the trapezoid at the top-edge :math:`y_\\mathrm{top-right}` (Default: None).
        bottom_width : float
            width of the trapezoid at the bottom-edge :math:`b_\\mathrm{bottom}` (Default: None).
        bottom_left_edge : float
            left-edge position of the trapezoid at the bottom-edge :math:`y_\\mathrm{bottom-left}` (Default: None).
        bottom_right_edge : float
            right-edge position of the trapezoid at the bottom-edge :math:`y_\\mathrm{bottom-right}` (Default: None).


        .. figure:: ../images/geometry_trapezoid-light.svg
           :class: only-light
        .. figure:: ../images/geometry_trapezoid-dark.svg
           :class: only-dark

           Trapezoid - dimensions

        See Also
        --------
        Rectangle : creates a rectangular geometry object
        Circle : creates a circular geometry object

        Examples
        --------
        A trapezoid object is easily instantiated as follows.

        >>> from m_n_kappa import Trapezoid
        >>> trapezoid = Trapezoid(top_edge=0, bottom_edge=10, top_width=10, bottom_width=20)

        In case only ``top_width`` or ``bottom_width`` is passed as argument the centerline of the specific
        width of the trapezoid is assumed to be a :math:`y = 0`.
        In consequence ``top_left_edge = -0.5 * top_width`` and ``top_right_edge = 0.5 * top_width``.
        Similar for the bottom-edge.

        For building a :py:class:`~m_n_kappa.Section` the ``trapezoid`` must only be added to a material.

        >>> from m_n_kappa import Steel
        >>> steel = Steel(f_y=355)
        >>> section = trapezoid + steel
        >>> type(section)
        <class 'm_n_kappa.section.Section'>

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
            log.info(f"{self.__repr__()} switched: top-edge and bottom-edge")
        if (
            self.top_left_edge is not None
            and self.top_right_edge is not None
            and self.top_right_edge < self.top_left_edge
        ):
            self._top_left_edge, self._top_right_edge = (
                self.top_right_edge,
                self.top_left_edge,
            )
            log.info(f"{self.__repr__()} switched: top-left-edge and top-right-edge")
        if (
            self.bottom_left_edge is not None
            and self.bottom_right_edge is not None
            and self.bottom_right_edge < self.bottom_left_edge
        ):
            self._bottom_left_edge, self._bottom_right_edge = (
                self.bottom_right_edge,
                self.bottom_left_edge,
            )
            log.info(
                f"{self.__repr__()} switched: bottom-left-edge and bottom-right-edge"
            )

    @property
    def top_left_edge(self) -> float:
        """left-edge position of the trapezoid at the top-edge :math:`y_\\mathrm{top-left}`"""
        return self._top_left_edge

    @property
    def bottom_left_edge(self) -> float:
        """left-edge position of the trapezoid at the bottom-edge :math:`y_\\mathrm{bottom-left}`"""
        return self._bottom_left_edge

    @property
    def top_right_edge(self) -> float:
        """right-edge position of the trapezoid at the top-edge :math:`y_\\mathrm{top-right}`"""
        return self._top_right_edge

    @property
    def bottom_right_edge(self) -> float:
        """right-edge position of the trapezoid at the bottom-edge :math:`y_\\mathrm{bottom-right}`"""
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
        """vertical position of top-edge of the trapezoid :math:`z_\\mathrm{top}`"""
        return self._top_edge

    @property
    def bottom_edge(self) -> float:
        """vertical position of bottom-edge of the trapezoid :math:`z_\\mathrm{bottom}`"""
        return self._bottom_edge

    @property
    def edges(self) -> list:
        """edges of trapezoid in vertical direction"""
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
        """width of trapezoid on top-edge :math:`b_\\mathrm{top}`"""
        return self._top_width

    @property
    def bottom_width(self) -> float:
        """width of trapezoid on bottom-edge :math:`b_\\mathrm{top}`"""
        return self._bottom_width

    @property
    def height(self) -> float:
        """height of the trapezoid :math:`h`"""
        return abs(self.top_edge - self.bottom_edge)

    @property
    def area(self) -> float:
        """cross-sectional area of the trapezoid"""
        return 0.5 * self.height * (self.top_width + self.bottom_width)

    @property
    def centroid(self) -> float:
        """vertical position of the centroid of the trapezoid"""
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
        """width of trapezoid at given vertical position

        in case ``vertical_position`` is outside of the trapezoid zero is returned

        Parameters
        ----------
        vertical_position : float
            vertical position the width of the trapezoid shall be given

        Returns
        -------
        float
            width of trapezoid at given vertical position
        """
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return interpolation(
                position_value=vertical_position,
                first_pair=[self.top_edge, self.top_width],
                second_pair=[self.bottom_edge, self.bottom_width],
            )
        else:
            return 0.0

    def left_edge(self, vertical_position: float) -> float:
        """left edge at the given vertical position

        in case ``vertical_position`` is outside of the trapezoid, then zero is returned

        Parameters
        ----------
        vertical_position : float
            vertical position the width of the trapezoid shall be given

        Returns
        -------
        float
            horizontal position of the left-edge of trapezoid at given vertical position
        """
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return interpolation(
                position_value=vertical_position,
                first_pair=[self.top_edge, self.top_left_edge],
                second_pair=[self.bottom_edge, self.bottom_left_edge],
            )
        else:
            return 0.0

    def right_edge(self, vertical_position: float) -> float:
        """right edge at the given vertical position

        in case ``vertical_position`` is outside of the trapezoid zero is returned

        Parameters
        ----------
        vertical_position : float
            vertical position the width of the trapezoid shall be given

        Returns
        -------
        float
            horizontal position of the right-edge of trapezoid at given vertical position
        """
        if self.top_edge <= vertical_position <= self.bottom_edge:
            return interpolation(
                position_value=vertical_position,
                first_pair=[self.top_edge, self.top_right_edge],
                second_pair=[self.bottom_edge, self.bottom_right_edge],
            )
        else:
            return 0.0

    @log.result
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
        trapezoids = []
        at_points.sort(key=lambda x: x.position)
        for point in at_points:
            if self.top_edge < point.position < self.bottom_edge:
                trapezoids.append(
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
        trapezoids.append(
            Trapezoid(
                top_edge=top_edge,
                bottom_edge=self.bottom_edge,
                top_width=self.width(top_edge),
                top_left_edge=self.left_edge(top_edge),
                bottom_width=self.bottom_width,
                bottom_left_edge=self.bottom_left_edge,
            )
        )
        return trapezoids

    @property
    def width_slope(self) -> float:
        """change of the width of the trapezoid depending on vertical position"""
        return (self.bottom_width - self.top_width) / self.height

    @property
    def width_interception(self) -> float:
        """theoretical width of the trapezoid at coordinate-origin"""
        return self.top_width - self.top_edge * self.width_slope


@dataclass
class IProfile(ComposedGeometry):

    """
    I-Profile composed of :py:class:`~m_n_kappa.Rectangle` instances

    .. versionadded:: 0.1.0

    Inherits from :py:class:`~m_n_kappa.geometry.ComposedGeometry` and makes a variety of geometries
    possible as the following figure shows.
    In case the desired profile has no bottom-flange choose ``has_bottom_flange=False``.
    Similar if no top-flange is needed then use ``has_top_flange=False``.
    In case top- and bottom flange are similar only passing values to ``t_fo`´ and ``t_fo`` is needed.

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
        If False: no top-flange is created
    has_bottom_flange: bool = True
        decide if I-profile has a bottom-flange (Default: True)
        if False: no top-flange is created
    centroid_y: float
        horizontal position of the centroid of the I-profile (Default: 0)


    .. figure:: ../images/geometry_i-profile-light.svg
       :class: only-light
    .. figure:: ../images/geometry_i-profile-dark.svg
       :class: only-dark

       I-Profile - dimensions - a) asymmetric I-profile, b) without bottom-flange, c) without top-flange,
       d) without top- and bottom-flange


    See Also
    --------
    Rectangle : basic geometry object
    UPEProfile : composed geometry consisting of several :py:class:`Rectangle` forming an ``U``
    RebarLayer : composed geometry consisting of several :py:class:`Circle`

    Example
    -------
    An HEB 200-profile may be composed as follows

    >>> from m_n_kappa import IProfile
    >>> heb200_geometry = IProfile(top_edge=0., t_fo=15.5, b_fo=200.0, t_w=9.5, h_w=169.0)
    >>> heb200_geometry
    IProfile(top_edge=0.0, t_w=9.5, h_w=169.0, t_fo=15.5, b_fo=200.0, t_fu=15.5, b_fu=200.0, has_top_flange=True, \
has_bottom_flange=True, centroid_y=0.0, geometries=[\
Rectangle(top_edge=0.00, bottom_edge=15.50, width=200.00, left_edge=-100.00, right_edge=100.00), \
Rectangle(top_edge=15.50, bottom_edge=184.50, width=9.50, left_edge=-4.75, right_edge=4.75), \
Rectangle(top_edge=184.50, bottom_edge=200.00, width=200.00, left_edge=-100.00, right_edge=100.00)])


    As :py:class:`~m_n_kappa.geometry.IProfile` inherits from :py:class:`~m_n_kappa.geometry.ComposedGeometry`
    it also inherits its functionality tranforming to a :py:class:`m_n_kappa.Crosssection`
    by adding :py:class:`m_n_kappa.Material`.

    >>> from m_n_kappa import Steel
    >>> steel = Steel(f_y = 300.0, f_u = 350.0, failure_strain=0.25)
    >>> cross_section = heb200_geometry + steel
    >>> cross_section
    Crosssection(sections=sections)

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
    centroid_y: float = 0.0
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
        log.info(f"Created {self.__repr__()}")

    def _add_top_flange(self):
        """add top-flange to geometry if wanted and geometric values are given"""
        if self.has_top_flange and self.t_fo is not None and self.b_fo is not None:
            self.geometries.append(
                Rectangle(
                    top_edge=self.top_edge,
                    bottom_edge=self.top_edge + self.t_fo,
                    width=self.b_fo,
                    left_edge=self.centroid_y - 0.5 * self.b_fo,
                )
            )

    def _add_web(self) -> None:
        """add web to the geometry of the profile"""
        self.geometries.append(
            Rectangle(
                top_edge=self.top_edge + self.t_fo,
                bottom_edge=self.top_edge + self.t_fo + self.h_w,
                width=self.t_w,
                left_edge=self.centroid_y - 0.5 * self.t_w,
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
                    left_edge=self.centroid_y - 0.5 * self.b_fu,
                )
            )


@dataclass
class RebarLayer(ComposedGeometry):

    """
    rebar-layer composed of several reinforcement-bars of :py:class:`Circle`

    .. versionadded:: 0.1.0

    Parameters
    ----------
    rebar_diameter: float
        diameter of rebars in the layer
    centroid_z: float
        position of the centroid in vertical direction
    rebar_number: int = None
        number of rebars within the layer (Alternative to argument ``width``)
    width: float = None
        width of the rebar-layer :math:`b` (together with ``rebar_horizontal_distance`` alternative to argument ``rebar_number``).
        In case ``rebar_number`` is defined, the argument ``width`` as well as ``rebar_horizontal_distance`` value is ignored.
    rebar_horizontal_distance : float
        distance between the rebars in horizontal direction :math:`s_\\mathrm{y}` (Default: None).
        See description in argument ``width``.
    left_edge : float
        horizontal position of the centroid of the left-most circle :math:`y_\\mathrm{left}` (Default: None).
    right_edge : float
        horizontal position of the centroid of the right-most circle :math:`y_\\mathrm{right}` (Default: None)
    rebar_horizontal_distance : float
        horizontal-distance between the rebar-centroids :math:`s_\\mathrm{y}` (Default: None)


    .. figure:: ../images/geometry_rebar-layer-light.svg
       :class: only-light
    .. figure:: ../images/geometry_rebar-layer-dark.svg
       :class: only-dark

       Rebar-layer - dimensions


    See Also
    --------
    Circle : basic geometric class
    IProfile : composed geometry consisting of several :py:class:`Rectangle` forming an ``I``
    UPEProfile : composed geometry consisting of several :py:class:`Rectangle` forming an ``U``

    Example
    -------
    The following example creates 10 circles with diameter 12 and a vertical position of 10

    >>> from m_n_kappa import RebarLayer
    >>> rebar_layer = RebarLayer(rebar_diameter=12.0, centroid_z=10.0, rebar_number=10, rebar_horizontal_distance=100)

    Adding a material to ``rebar_layer`` creates a cross-section.

    >>> from m_n_kappa import Reinforcement
    >>> rebar_steel = Reinforcement(f_s=500, f_su=550, failure_strain=0.25)
    >>> rebars = rebar_layer + rebar_steel
    >>> rebars
    Crosssection(sections=sections)

    """

    rebar_diameter: float
    centroid_z: float
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
        self.width, self.left_edge, self.right_edge = check_width(
            self.width, self.left_edge, self.right_edge
        )

        self.geometries = []
        for index in range(self.rebar_number):
            centroid_y = index * self.rebar_horizontal_distance + self.left_edge
            self.geometries.append(
                Circle(
                    diameter=self.rebar_diameter,
                    centroid_y=centroid_y,
                    centroid_z=self.centroid_z,
                )
            )
        log.info(f"Created {self.__repr__()}")


@dataclass
class UPEProfile(ComposedGeometry):

    """
    UPE-Profile composed of class Rectangles forming a reversed ``U``

    .. versionadded:: 0.1.0

    Parameters
    ----------
    top_edge : float
        top-edge of the rectangle :math:`z_\\mathrm{top}`
    t_f: float
        flange-thickness :math:`t_\\mathrm{f}`
    b_f: float
        flange-width :math:`b_\\mathrm{f}`
    t_w: float
        web-thickness :math:`t_\\mathrm{w}`
    h_w: float = None
        web-height :math:`h_\\mathrm{w}` (Default: None).
        Alternative argument ``h`` must be given, otherwise an exception will be risen.
    h: float = None
        overall height of the steel-profile :math:`h` (Default: None).
        Alternative arguments ``h_w`` and ``t_f`` must be given.
    centroid_y: floats
        horizontal position of the centroid of the UPE-profile :math:`y_\\mathrm{centroid}` (Default: 0.0)


    .. figure:: ../images/geometry_upe-light.svg
       :class: only-light
    .. figure:: ../images/geometry_upe-dark.svg
       :class: only-dark

       UPE-Profile - dimensions


    See Also
    --------
    IProfile : composed geometry consisting of several :py:class:`Rectangle` forming an ``I``
    RebarLayer : composed geometry consisting of several :py:class:`Circle`

    Example
    -------
    The following example creates :py:class:`~m_n_kappa.geometry.Rectangle` instances forming an UPE 200 profile

    >>> from m_n_kappa import UPEProfile
    >>> upe200_geometry = UPEProfile(top_edge=10, t_f=5.2, b_f=76, t_w=9.0, h=200)
    >>> upe200_geometry
    UPEProfile(top_edge=10, t_f=5.2, b_f=76, t_w=9.0, h_w=189.6, h=200, centroid_y=0.0, \
geometries=[\
Rectangle(top_edge=10.00, bottom_edge=86.00, width=5.20, left_edge=-100.00, right_edge=-94.80), \
Rectangle(top_edge=10.00, bottom_edge=19.00, width=189.60, left_edge=-94.80, right_edge=94.80), \
Rectangle(top_edge=10.00, bottom_edge=86.00, width=5.20, left_edge=94.80, right_edge=100.00)])

    As :py:class:`~m_n_kappa.geometry.UPEProfile` inherits from :py:class:`~m_n_kappa.geometry.ComposedGeometry`
    it also inherits its functionality tranforming to a :py:class:`m_n_kappa.Crosssection`
    by adding :py:class:`m_n_kappa.Material`.

    >>> from m_n_kappa import Steel
    >>> steel = Steel(f_y = 300.0, f_u = 350.0, failure_strain=0.25)
    >>> cross_section = upe200_geometry + steel
    >>> cross_section
    Crosssection(sections=sections)

    """

    top_edge: float
    t_f: float
    b_f: float
    t_w: float
    h_w: float = None
    h: float = None
    centroid_y: float = 0.0
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

        log.info(f"Created {self.__repr__()}")

    def _left_flange(self) -> Rectangle:
        return Rectangle(
            top_edge=self.top_edge,
            bottom_edge=self.top_edge + self.b_f,
            width=self.t_f,
            left_edge=self.centroid_y - 0.5 * self.h_w - self.t_f,
        )

    def _web(self) -> Rectangle:
        return Rectangle(
            top_edge=self.top_edge,
            bottom_edge=self.top_edge + self.t_w,
            width=self.h_w,
            left_edge=self.centroid_y - 0.5 * self.h_w,
        )

    def _right_flange(self) -> Rectangle:
        return Rectangle(
            top_edge=self.top_edge,
            bottom_edge=self.top_edge + self.b_f,
            width=self.t_f,
            left_edge=self.centroid_y + 0.5 * self.h_w,
        )
