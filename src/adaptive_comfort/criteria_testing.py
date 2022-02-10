import functools
import numpy as np

from constants import may_start_hour, sept_end_hour
from utils import mean_every_n_elements, sum_every_n_elements, np_round_for_criteria_two


def criterion_one(arr_deltaT, arr_occupancy):
    """Calculate hours of exceedance.

    See CIBSE TM52: 2013, Page 13, Section 6.1.2a
    
    Args:
        arr_deltaT (numpy.ndarray): Delta T (Operative temperature - Max adaptive temperature)
        arr_occupancy (numpy.ndarray): Occupancy (Number of people)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of exceedance.
    """
    factor = int(arr_deltaT.shape[2]/8760)  # Find factor to convert to hourly time-step array
    if factor > 1:
        f = functools.partial(mean_every_n_elements, n=factor)
        arr_deltaT = np.apply_along_axis(f, 2, arr_deltaT)
        arr_occupancy = np.apply_along_axis(f, 1, arr_occupancy)

    arr_deltaT_may_to_sept_incl = arr_deltaT[:, :, may_start_hour:sept_end_hour]  # Obtaining deltaT between May and end of September
    arr_deltaT_bool = arr_deltaT_may_to_sept_incl >= 1  # Find where temperature is greater than 1K.
    arr_room_total_hours_exceedance = arr_deltaT_bool.sum(axis=2)  # Sum along last axis (hours)

    # Occupancy
    arr_occupancy_may_to_sept_incl = arr_occupancy[:, may_start_hour:sept_end_hour]
    arr_occupancy_bool = arr_occupancy_may_to_sept_incl > 0  # Hours where occupied
    arr_occupancy_3_percent = arr_occupancy_bool.sum(axis=1)*0.03 # axis 1 is hours

    arr_criterion_one_bool = arr_room_total_hours_exceedance > arr_occupancy_3_percent
    arr_criterion_one_percent = (arr_room_total_hours_exceedance/arr_occupancy_3_percent)*100
    return arr_criterion_one_bool, arr_criterion_one_percent

def criterion_two(arr_deltaT):
    """Calculate daily weighted exceedance.

    See CIBSE TM52: 2013, Page 13, Section 6.1.2b

    Args:
        arr_deltaT (numpy.ndarray): Delta T (Operative temperature - Max adaptive temperature)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of how often exceedance occurred.
    """
    arr_deltaT_round = np_round_for_criteria_two(arr_deltaT)
    n = int(arr_deltaT_round.shape[2]/365)  # Factor to take arr_deltaT to daily
    f = functools.partial(sum_every_n_elements, n=n)
    arr_W_e = np.apply_along_axis(f, 2, arr_deltaT_round)  # sums every n elements along the "time step" axis
    # "time step" axis should now become "days" axis.
    arr_w = arr_W_e > 6
    arr_criterion_two_bool = arr_w.sum(axis=2, dtype=bool)
    arr_criterion_two_percent = (arr_w.sum(axis=2) / 365) * 100
    return arr_criterion_two_bool, arr_criterion_two_percent

def criterion_three(arr_deltaT):
    """Checks whether delta T exceeds 4K at any point. K meaning kelvin

    See CIBSE TM52: 2013, Page 13, Section 6.1.2c

    Args:
        arr_deltaT (numpy.ndarray): Delta T (Operative temperature - Max adaptive temperature)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of exceedance.
    """
    arr_bool = arr_deltaT > 4
    arr_criterion_three_bool = arr_bool.sum(axis=2, dtype=bool)
    arr_criterion_three_percent = (arr_bool.sum(axis=2) / 8760) * 100
    return arr_criterion_three_bool, arr_criterion_three_percent
