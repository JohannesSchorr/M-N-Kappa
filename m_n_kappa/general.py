from itertools import groupby


def curvature(neutral_axis_value: float, position_value: float, strain_at_position: float):
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


def position(strain_at_position: float, neutral_axis_value: float, curvature_value: float):
    return neutral_axis_value + (strain_at_position / curvature_value)


def neutral_axis(strain_at_position: float, curvature_value: float, position_value: float):
    return position_value - (strain_at_position / curvature_value)


def remove_duplicates(list_of_lists: list) -> list:
    # list_of_lists.sort()
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


def interpolation(position_value: float, first_pair: list, second_pair: list):
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