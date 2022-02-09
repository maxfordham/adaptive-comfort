# import sys
import functools
import sys
import pathlib
import numpy as np
import pandas as pd
from datetime import date

PATH_MODULE = pathlib.Path(__file__).parent
sys.path.append(str(PATH_MODULE / "lib"))

from xlsx_templater import to_excel

from constants import arr_air_speed, may_start_hour, sept_end_hour, DIR_TESTJOB1
from ies_calcs import deltaT, np_calc_op_temp, np_calculate_max_adaptive_temp, calculate_running_mean_temp_hourly
from utils import mean_every_n_elements, sum_every_n_elements, repeat_every_element_n_times, \
    round_half_up, round_for_criteria_two, create_paths, fromfile


def criterion_one(arr_deltaT, arr_occupancy):
    """[summary]

    Args:
        arr_op_temp ([type]): [description]
        arr_max_adaptive_temp ([type]): [description]

    Returns:
        np.ndarray: Whether room has failed or not
    """
    factor = int(arr_deltaT.shape[2]/8760)  # Find factor to convert to hourly time-step array
    if factor > 1:
        f = functools.partial(mean_every_n_elements, n=factor)
        arr_deltaT = np.apply_along_axis(f, 2, arr_deltaT)
        arr_occupancy = np.apply_along_axis(f, 1, arr_occupancy)

    np_round_half_up = np.vectorize(round_half_up)

    arr_deltaT_may_to_sept_incl = arr_deltaT[:, :, may_start_hour:sept_end_hour]  # Obtaining deltaT between May and end of September
    arr_deltaT_may_to_sept_incl = np_round_half_up(arr_deltaT_may_to_sept_incl)
    arr_deltaT_bool = arr_deltaT_may_to_sept_incl >= 1  # Find where temperature is greater than 1K.
    arr_room_total_hours_exceedance = arr_deltaT_bool.sum(axis=2)  # Sum along last axis (hours)

    # Occupancy
    arr_occupancy_may_to_sept_incl = arr_occupancy[:, may_start_hour:sept_end_hour]
    arr_occupancy_bool = arr_occupancy_may_to_sept_incl > 0  # Hours where occupied
    arr_occupancy_3_percent = arr_occupancy_bool.sum(axis=1)*0.03 # axis 1 is hours

    arr_criterion_one_bool = arr_room_total_hours_exceedance > arr_occupancy_3_percent

    arr_criterion_one_percent = (arr_room_total_hours_exceedance/arr_occupancy_3_percent)*100

    return arr_criterion_one_bool

def criterion_two(arr_deltaT):
    np_round_for_criteria_two = np.vectorize(round_for_criteria_two)
    arr_deltaT_round = np_round_for_criteria_two(arr_deltaT)
    n = int(arr_deltaT_round.shape[2]/365)  # Factor to take arr_deltaT to daily
    f = functools.partial(sum_every_n_elements, n=n)
    arr_W_e = np.apply_along_axis(f, 2, arr_deltaT_round)  # sums every n elements along the "time step" axis
    # "time step" axis should now become "days" axis.
    arr_w = arr_W_e > 6
    arr_criterion_two_bool = arr_w.sum(axis=2, dtype=bool)
    arr_criterion_two_percent = (arr_w.sum(axis=2) / 365) * 100
    return arr_criterion_two_bool

def criterion_three(arr_deltaT):
    arr_bool = arr_deltaT > 4
    arr_criterion_three_bool = arr_bool.sum(axis=2, dtype=bool)
    return arr_criterion_three_bool
