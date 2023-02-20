from dataclasses import dataclass, field
from itertools import groupby
from decimal import Decimal

from .log import LoggerMethods

log = LoggerMethods(__name__)


def curvature(
    neutral_axis_value: float, position_value: float, strain_at_position: float
) -> float:
    """
    curvature from strain at a position and neutral-axis

    Parameters
    ----------
    neutral_axis_value : float
        vertical position of the neutral axis :math:`z_\\mathrm{n}`
    position_value : float
        vertical position of the ``strain_at_position`` :math:`z`
    strain_at_position : float
        strain :math:`\\varepsilon` at the ``position_value``

    Returns
    -------
    float
        computed curvature :math:`\\kappa`

    Notes
    -----
    In mathematical notation this method works as follows.

    .. math::

       \\kappa = \\frac{\\varepsilon}{z - z_\\mathrm{n}}

    Where

    - :math:`\\varepsilon` = ``strain_at_position``
    - :math:`z` = ``position_value``
    - :math:`z_\\mathrm{n}` = ``neutral_axis_value``

    See Also
    --------
    curvature_by_points : method to compute curvature by two points

    Raises
    ------
    ZeroDivisionError
        In case ``neutral_axis_value == position_value``
    """
    if neutral_axis_value == position_value:
        raise ZeroDivisionError(
            'Arguments "neutral_axis_value" and "position_value" must have different values'
        )
    else:
        return strain_at_position / (position_value - neutral_axis_value)


def curvature_by_points(
    top_edge: float, bottom_edge: float, top_strain: float, bottom_strain: float
) -> float:
    """
    compute curvature by two given points

    Point 1: (``top_edge``
    Parameters
    ----------
    top_edge : float
        vertical position of the top-edge
    bottom_edge : float
        vertical position of the bottom-edge
    top_strain : float
        strain at the top-edge
    bottom_strain : float
        strain at the bottom-edge

    Returns
    -------
    float
        curvature-value from two strain-position-values

    See Also
    --------
    :py:meth:`~m_n_kappa.general.curvature` : compute curvature from strain, its position and neutral axis
    :py:meth:`~m_n_kappa.general.neutral_axis` : compute curvature from strain, its position and curvature
    :py:meth:`~m_n_kappa.general.position` : compute position of strain from neutral-axis and curvature
    :py:meth:`~m_n_kappa.general.strain` : compute strain from its vertical position, neutral-axis and curvature

    """
    return float(
        (Decimal(top_strain) - Decimal(bottom_strain))
        / (Decimal(top_edge) - Decimal(bottom_edge))
    )


def strain(
    neutral_axis_value: float, curvature_value: float, position_value: float
) -> float:
    """
    compute the strain from its position, the neutral axis and the curvature value

    This method assumes a linear strain distribution over the height.

    Parameters
    ----------
    neutral_axis_value : float
        position where strain is zero
    curvature_value : float
        value of the curvature
    position_value : float
        geometric position of the strain

    Returns
    -------
    float
        strain from its position, neutral axis and curvature value

    Raises
    ------
    ValueError
        if curvature is zero

    See Also
    --------
    :py:meth:`~m_n_kappa.general.curvature` : compute curvature from strain, its position and neutral axis
    :py:meth:`~m_n_kappa.general.neutral_axis` : compute curvature from strain, its position and curvature
    :py:meth:`~m_n_kappa.general.position` : compute position of strain from neutral-axis and curvature

    Examples
    --------

    >>> from m_n_kappa.general import strain
    >>> strain(neutral_axis_value=10, curvature_value=0.0001, position_value=0.0)
    -0.001

    """
    if neutral_axis_value == position:
        return 0.0
    elif curvature_value == 0.0:
        raise ValueError("Curvature must be unequal zero")
    else:
        return float(
            Decimal(curvature_value)
            * (Decimal(position_value) - Decimal(neutral_axis_value))
        )


def position(
    strain_at_position: float, neutral_axis_value: float, curvature_value: float
) -> float:
    """
    compute the vertical position of a given strain using neutral-axis and curvature

    This method assumes a linear strain distribution over the height.

    Parameters
    ----------
    strain_at_position : float
        strain at a geometric position
    neutral_axis_value : float
        position where strain is zero
    curvature_value : float
        value of the curvature

    Returns
    -------
        position of the given strain under given strain-distribution

    See Also
    --------
    :py:meth:`~m_n_kappa.general.curvature` : compute curvature from strain, its position and neutral axis
    :py:meth:`~m_n_kappa.general.neutral_axis` : compute curvature from strain, its position and curvature
    :py:meth:`~m_n_kappa.general.strain` : compute strain from its vertical position, neutral-axis and curvature

    Examples
    --------

    >>> from m_n_kappa.general import position
    >>> position(strain_at_position=-0.1, curvature_value=0.0001, neutral_axis_value=10)
    -990

    """
    return neutral_axis_value + (strain_at_position / curvature_value)


def neutral_axis(
    strain_at_position: float, curvature_value: float, position_value: float
) -> float:
    """
    compute the neutral axis from strain, its geometric position and the curvature

    The neutral axis describes the point where no strain is given from a linear
    strain distribution.
    This method assumes a linear strain distribution over the height.

    Parameters
    ----------
    strain_at_position : float
        strain at a geometric position
    curvature_value : float
        value of the curvature
    position_value : float
        geometric position of the strain

    Returns
    -------
    float
        geometric point where strain is zero

    See Also
    --------
    py:meth:`~m_n_kappa.general.position` : compute position of strain from neutral-axis and curvature
    py:meth:`~m_n_kappa.general.curvature` : compute curvature from strain, the strain-position and
        neutral-axis and
    :py:meth:`~m_n_kappa.general.strain` : compute strain from its vertical position, neutral-axis and curvature

    Examples
    --------

    >>> from m_n_kappa.general import neutral_axis
    >>> neutral_axis(strain_at_position=0.1, curvature_value=0.0001, position_value=10)
    -990

    """
    return position_value - (strain_at_position / curvature_value)


def remove_duplicates(list_of_lists: list) -> list:
    return [sublist for sublist, _ in groupby(list_of_lists)]


def positive_sign(list_of_lists: list) -> list:
    return [[abs(sublist[0]), abs(sublist[1])] for sublist in list_of_lists]


def negative_sign(list_of_lists: list) -> list:
    return [
        [(-1) * abs(sublist[0]), (-1) * abs(sublist[1])] for sublist in list_of_lists
    ]


def str_start_end(func):
    def wrapper(*args):
        text = [
            "",
            "***************************************************",
            "",
            func(*args),
            "",
            "***************************************************",
        ]
        return "\n".join(text)

    return wrapper


def interpolation(
    position_value: float, first_pair: list[float], second_pair: list[float]
):
    """
    Linear interpolation between

    Parameters
    ----------
    position_value : float
        value the corresponding other value must be interpolated
    first_pair : list[float]
        first pair.
        1st position applies to the value given by argument 'position_value'.
        2nd position applies to the value that is looked for
    second_pair
        first pair.
        1st position applies to the value given by argument 'position_value'.
        2nd position applies to the value that is looked for
    Returns
    -------
    float
        value corresponding to the position-value by linear interpolation between the given pairs
    """
    return first_pair[0] + (position_value - first_pair[1]) * (
        second_pair[0] - first_pair[0]
    ) / (second_pair[1] - first_pair[1])


def remove_none(sequence: list) -> list:
    return list(filter(None, sequence))


def print_chapter(sections: list, separator="\n\n"):
    return separator.join(sections)


def print_sections(sub_sections: list, separator="\n"):
    return separator.join(sub_sections)


def remove_zeros(values: list) -> list:
    return list(filter(lambda x: x != 0.0, values))


@dataclass(slots=True)
class StrainPosition:

    """
    Container for strains at a position_value within a given material

    Parameters
    ----------
    strain: float
        strain at the given ``position``
    position: float
        position of the given float
    material: str
        material the strain is obtained from
    """

    strain: float = field(compare=True)
    position: float = field(compare=True)
    material: str


@dataclass(slots=True)
class EffectiveWidths:
    """
    container holding the effective widths

    Parameters
    ----------
    membran : float
        value of the effective width under axial loading
    bending : float
        value of the effective width under bending (Default: ``None``).
        If None, then membran value is applied.
    for_section_type: str
        section_type the effective widths are defined for (Default: ``slab``)
    reinforcement_under_tension_use_membran_width: bool
        width for reinforcement under tensile loading
          - ``True``: membran-width
          - ``False``: bending-width (Default)
    reinforcement_under_compression_use_membran_width: bool
        width for reinforcement under compressive loading
          - ``True``: membran-width (Default)
          - ``False``: bending-width
    concrete_under_tension_use_membran_width: bool
        width for concrete under tensile loading
          - ``True``: membran-width
          - ``False``: bending-width  (Default)
    concrete_under_compression_use_membran_width: bool
        width for reinforcement under compressive loading
          - ``True``: membran-width (Default)
          - ``False``: bending-width
    """

    membran: float = field(compare=True)
    bending: float = field(compare=True, default=None)
    for_section_type: str = field(compare=True, default="slab")
    reinforcement_under_tension_use_membran_width: bool = field(
        compare=True, default=False
    )
    reinforcement_under_compression_use_membran_width: bool = field(
        compare=True, default=False
    )
    concrete_under_tension_use_membran_width: bool = field(compare=True, default=False)
    concrete_under_compression_use_membran_width: bool = field(
        compare=True, default=True
    )

    def __post_init__(self) -> None:
        if self.bending is None:
            self.bending = self.membran

    def width(self, material: str, strain_value: float) -> float:
        """width considering the material and the loading"""
        if material == "Reinforcement":
            return self._reinforcement_width(strain_value)
        elif material == "Concrete":
            return self._concrete_width(strain_value)

    def _concrete_width(self, strain_value: float) -> float:
        """width for concrete considering the loading"""
        if strain_value > 0.0:
            return self._get_width(self.concrete_under_tension_use_membran_width)
        else:
            return self._get_width(self.concrete_under_compression_use_membran_width)

    def _reinforcement_width(self, strain_value: float) -> float:
        """width for reinforcement considering the loading"""
        if strain_value > 0.0:
            return self._get_width(self.reinforcement_under_tension_use_membran_width)
        else:
            return self._get_width(
                self.reinforcement_under_compression_use_membran_width
            )

    def _get_width(self, membran_width: bool) -> float:
        """
        if True: membran-width, False: bending-width
        """
        if membran_width:
            return self.membran
        else:
            return self.bending


@dataclass(slots=True)
class EdgeStrains:
    """
    store strains at edges and compute curvature from these points

    .. versionadded:: 0.1.0

    Parameters
    ----------
    bottom_edge_strain : :py:class:`~m_n_kappa.StrainPosition`
        strain and position at the bottom-edge
    top_edge_strain : :py:class:`~m_n_kappa.StrainPosition`
        strain and position at the top-edge
    """

    bottom_edge_strain: StrainPosition
    top_edge_strain: StrainPosition

    def __post_init_(self):
        if self.top_edge_strain.position > self.bottom_edge_strain.position:
            self.top_edge_strain, self.bottom_edge_strain = (
                self.bottom_edge_strain,
                self.top_edge_strain,
            )
            log.info("EdgeStrains: changed bottom-edge and top-edge")

    @property
    def curvature(self) -> float:
        """
        curvature by comparison of the strains at the edges

        See Also
        --------
        curvature_by_points : method to compute curvature from two stress-position points
        """
        return curvature_by_points(
            top_edge=self.top_edge_strain.position,
            bottom_edge=self.bottom_edge_strain.position,
            top_strain=self.top_edge_strain.strain,
            bottom_strain=self.bottom_edge_strain.strain,
        )


@dataclass(slots=True)
class NotSuccessfulReason:

    """
    Container for reasons why computation has not been successful

    .. versionadded:: 0.2.0

    Parameters
    ----------
    keyword : str
        keyword is the shortcut to describe the reason why a computation was not successful
        (Default: None)
    reason : str
        custom reason
    strain_position : StrainPosition
        strain, its position and the material that led to the not successful computation
    """

    keyword: str = None
    variable: str = None
    reason: str = None
    strain_position: StrainPosition = None

    def __repr__(self) -> str:
        if self.strain_position is None:
            return self.reason
        else:
            return f"{self.reason} ({self.strain_position})"

    def __str__(self) -> str:
        return self.__repr__()

    def __post_init__(self):
        if self.reason is None:
            if self.keyword is not None:
                if self.keyword in self.keywords.keys():
                    self.reason = self.keywords[self.keyword]
            elif self.variable is not None:
                self.same_sign(self.variable)

    def __eq__(self, other) -> bool:
        if isinstance(other, NotSuccessfulReason):
            if self.reason == other.reason:
                if self.strain_position == other.strain_position:
                    return True

    def same_sign(self, variable: str):
        key = f"same sign {variable}"
        if key in list(self.keywords.keys()):
            self.reason = self.keywords[key]

    @property
    def keywords(self) -> dict:
        """shortcut to describe reasons why computation was not successful"""
        return {
            "iteration": "maximum number of iterations reached, without finding equilibrium of axial-forces",
            "converge": "Iteration not converging",
            "same sign": "difference of axial forces at the boundary values have same sign",
            "same sign strain": "difference of axial forces at minimum and maximum strain have same sign",
            "same sign neutral-axis": "difference of axial forces at minimum and maximum neutral axis have same sign",
            "same sign curvature": "difference of axial forces at minimum and maximum curvature have same sign",
        }
