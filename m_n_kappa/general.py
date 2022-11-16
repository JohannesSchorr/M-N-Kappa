from itertools import groupby


def curvature(neutral_axis: float, position: float, strain_at_position: float):
    if neutral_axis == position:
        raise ZeroDivisionError(
            'Arguments "neutral_axis" and "position" must have different values'
        )
    else:
        return strain_at_position / (position - neutral_axis)


def curvature_by_points(
    top_edge: float, bottom_edge: float, top_strain: float, bottom_strain: float
):
    return (top_strain - bottom_strain) / (top_edge - bottom_edge)


def strain(neutral_axis: float, curvature: float, position: float):
    if neutral_axis == position:
        return 0.0
    elif curvature == 0.0:
        raise ValueError("Curvature must be unequal zero")
    else:
        return curvature * (position - neutral_axis)


def position(strain_at_position: float, neutral_axis: float, curvature: float):
    return neutral_axis + (strain_at_position / curvature)


def neutral_axis(strain_at_position: float, curvature: float, position: float):
    return position - (strain_at_position / curvature)


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
    def wrapper(*args, **kwargs):
        text = [
            "***************************************************",
            "",
            func(*args),
            "",
            "***************************************************",
        ]
        return "\n".join(text)

    return wrapper


def interpolation(position: float, first_pair: list, second_pair: list):
    return first_pair[0] + (position - first_pair[1]) * (
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