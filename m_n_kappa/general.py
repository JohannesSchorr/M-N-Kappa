from dataclasses import dataclass
from itertools import groupby


def curvature(
    neutral_axis_value: float, position_value: float, strain_at_position: float
):
    if neutral_axis_value == position_value:
        raise ZeroDivisionError(
            'Arguments "neutral_axis_value" and "position_value" must have different values'
        )
    else:
        return strain_at_position / (position_value - neutral_axis_value)


def curvature_by_points(
    top_edge: float, bottom_edge: float, top_strain: float, bottom_strain: float
):
    return (top_strain - bottom_strain) / (top_edge - bottom_edge)


def strain(neutral_axis_value: float, curvature_value: float, position_value: float):
    if neutral_axis_value == position:
        return 0.0
    elif curvature_value == 0.0:
        raise ValueError("Curvature must be unequal zero")
    else:
        return curvature_value * (position_value - neutral_axis_value)


def position(
    strain_at_position: float, neutral_axis_value: float, curvature_value: float
):
    return neutral_axis_value + (strain_at_position / curvature_value)


def neutral_axis(
    strain_at_position: float, curvature_value: float, position_value: float
):
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


@dataclass
class StrainPosition:

    """Container for strains at a position_value within a given material"""

    strain: float
    position: float
    material: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, StrainPosition):
            return False
        elif self.strain == other.strain and self.position == self.position:
            return True
        else:
            return False


@dataclass
class EffectiveWidths:
    """
    container holding the effective widths

    Parameters
    ----------
    membran : float
        value of the effective width under axial loading
    bending : float
        value of the effective width under bending (Default: None).
        If None, then membran value is applied.
    for_section_type: str = 'slab'
        section_type the effective widths are defined for (Default: 'slab')
    reinforcement_under_tension_use_membran_width: bool
        width for reinforcement under tensile loading
          - True: membran-width
          - False: bending-width (Default)
    reinforcement_under_compression_use_membran_width: bool
        width for reinforcement under compressive loading
          - True: membran-width (Default)
          - False: bending-width
    concrete_under_tension_use_membran_width: bool
        width for concrete under tensile loading
          - True: membran-width
          - False: bending-width  (Default)
    concrete_under_compression_use_membran_width: bool
        width for reinforcement under compressive loading
          - True: membran-width (Default)
          - False: bending-width
    """

    membran: float
    bending: float = None
    for_section_type: str = "slab"
    reinforcement_under_tension_use_membran_width: bool = False
    reinforcement_under_compression_use_membran_width: bool = False
    concrete_under_tension_use_membran_width: bool = False
    concrete_under_compression_use_membran_width: bool = True

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