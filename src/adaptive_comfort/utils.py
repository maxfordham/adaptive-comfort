import numpy as np

def round_half_up(value):
    """Rounds 

    Args:
        value ([type]): [description]

    Returns:
        [type]: [description]
    """
    if (value % 1) >= 0.5:
        rounded_value = np.ceil(value)
    else:
        rounded_value = np.floor(value)
    return rounded_value


def round_for_criteria_two(value):
    if value <= 0:
        rounded_value = 0.0
    elif (value % 1) >= 0.5:
        rounded_value = np.ceil(value)
    else:
        rounded_value = np.floor(value)
    return rounded_value


def mean_every_n_elements(arr, n=24, axis=1):
    return np.reshape(arr, (-1, n)).mean(axis)


def sum_every_n_elements(arr, n=24, axis=1):
    return np.reshape(arr, (-1, n)).sum(axis)


def repeat_every_element_n_times(arr, n=24, axis=1):
    return np.repeat(arr, n, axis)
    