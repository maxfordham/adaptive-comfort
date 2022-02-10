import functools
import numpy as np

from constants import may_start_hour, sept_end_hour
from utils import mean_every_n_elements, sum_every_n_elements, np_round_for_criteria_two, np_round_half_up
from ies_calcs import daily_weighted_exceedance


def criterion_one(arr_deltaT_hourly, arr_occupancy):
    """Calculate hours of exceedance.

    See CIBSE TM52: 2013, Page 13, Section 6.1.2a
    
    Args:
        arr_deltaT_hourly (numpy.ndarray): Delta T (Operative temperature - Max adaptive temperature)
        arr_occupancy (numpy.ndarray): Occupancy (Number of people)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of exceedance.
    """
    # TODO: Review Calc
    arr_deltaT_hourly = np_round_half_up(arr_deltaT_hourly)  # Round delta T as specified by CIBSE TM52 guide.
    arr_deltaT_may_to_sept_incl = arr_deltaT_hourly[:, :, may_start_hour:sept_end_hour]  # Obtaining deltaT between May and end of September
    arr_deltaT_bool = arr_deltaT_may_to_sept_incl >= 1  # Find where temperature is greater than 1K.
    arr_room_total_hours_exceedance = arr_deltaT_bool.sum(axis=2)  # Sum along last axis (hours)

    # Occupancy
    arr_occupancy_may_to_sept_incl = arr_occupancy[:, may_start_hour:sept_end_hour]
    arr_occupancy_bool = arr_occupancy_may_to_sept_incl > 0  # Hours where occupied
    arr_occupancy_3_percent = arr_occupancy_bool.sum(axis=1)*0.03 # axis 1 is hours

    arr_criterion_one_bool = arr_room_total_hours_exceedance > arr_occupancy_3_percent
    arr_criterion_one_percent = (arr_room_total_hours_exceedance/arr_occupancy_3_percent)*100
    return arr_criterion_one_bool, arr_criterion_one_percent

def criterion_two(arr_deltaT, arr_occupancy):
    """Calculate daily weighted exceedance.

    See CIBSE TM52: 2013, Page 13, Section 6.1.2b

    Args:
        arr_deltaT_daily (numpy.ndarray): Delta T (Operative temperature - Max adaptive temperature)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of how often exceedance occurred.
    """
    # TODO: Review Calc
    arr_deltaT_occupied = np.where(arr_occupancy==0, 0, arr_deltaT)  # Sets cells in arr_deltaT to 0 where arr_occupancy is 0. We only want to consider occupied intervals.
    n = int(arr_deltaT_occupied.shape[2]/365)  # Factor to take arr_deltaT_occupied time-step to daily
    arr_daily_weight = daily_weighted_exceedance(arr_deltaT_occupied)
    arr_daily_weight_bool = arr_daily_weight > 6  # See which days exceed 6
    arr_criterion_two_bool = arr_daily_weight_bool.sum(axis=2, dtype=bool) # sum the days for each room where exceedance occurs
    arr_criterion_two_percent = (arr_daily_weight_bool.sum(axis=2) / 365) * 100
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
