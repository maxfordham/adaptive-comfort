import numpy as np

from adaptive_comfort.constants import MAY_START_HOUR, SEPT_END_HOUR
from adaptive_comfort.utils import np_round_half_up, filter_bedroom_comfort_time
from adaptive_comfort.equations import daily_weighted_exceedance


def criterion_hours_of_exceedance(arr_deltaT_hourly, arr_occupancy_hourly):
    """Calculates whether a room has exceeded the threshold for hours of exceedance. 
    Also calculates the percentage of occupied hours exceeded out of total occupied hours for each room.

    *See CIBSE TM52: 2013, Page 13, Section 6.1.2a*
    
    Args:
        arr_deltaT_hourly (numpy.ndarray): Delta T (Operative temperature - Max acceptable temperature)
        arr_occupancy (numpy.ndarray): Occupancy (Number of people)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of exceedance.
    """
    arr_deltaT_may_to_sept_hourly = arr_deltaT_hourly[:, :, MAY_START_HOUR:SEPT_END_HOUR]  # Obtaining deltaT between May and end of September
    arr_occupancy_may_to_sept_hourly = arr_occupancy_hourly[:, MAY_START_HOUR:SEPT_END_HOUR]  # Obtaining occupancy between May and end of September

    arr_deltaT_occupied_may_to_sept_hourly = np.where(arr_occupancy_may_to_sept_hourly==0, 0, arr_deltaT_may_to_sept_hourly)  # Where unoccupied, set delta T to 0 to ignore in criterion test.
    # arr_deltaT_occupied_may_to_sept_hourly = np_round_half_up(arr_deltaT_occupied_may_to_sept_hourly).astype(int)  # Round delta T as specified by CIBSE TM52 guide.
    arr_deltaT_occupied_may_to_sept_hourly = arr_deltaT_occupied_may_to_sept_hourly.round()

    arr_deltaT_bool = arr_deltaT_occupied_may_to_sept_hourly >= 1  # Find where delta T is greater than or equal to 1K.
    arr_room_total_hours_exceedance = arr_deltaT_bool.sum(axis=2)  # Sum along last axis (hours) to get total hours of exceedance per room
    
    arr_occupancy_bool = arr_occupancy_may_to_sept_hourly > 0  # True where hour has occupancy greater than 0
    arr_occupancy_3_percent = arr_occupancy_bool.sum(axis=1)*0.03  # Sum along time-step axis (hours), i.e. sum hours per room where occupied

    arr_bool = arr_room_total_hours_exceedance > arr_occupancy_3_percent
    arr_percent = (arr_room_total_hours_exceedance/arr_occupancy_bool.sum(axis=1))*100  # Percentage of occupied hours exceeded out of total occupied hours
    return arr_bool, arr_percent


def criterion_daily_weighted_exceedance(arr_deltaT, arr_occupancy):
    """Calculates whether a room has exceeded the daily weighted exceedance.
    Also calculates the percentage of days exceeding daily weight out of the total days.

    *See CIBSE TM52: 2013, Page 14, Section 6.1.2b*

    Args:
        arr_deltaT (numpy.ndarray): Delta T (Operative temperature - Max acceptable temperature)
        arr_occupancy (numpy.ndarray): Occupancy (Number of people)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of how often exceedance occurred.
    """
    arr_deltaT_occupied = np.where(arr_occupancy==0, 0, arr_deltaT)  # Sets cells in arr_deltaT to 0 where arr_occupancy is 0. We only want to consider occupied intervals.
    arr_daily_weights = daily_weighted_exceedance(arr_deltaT_occupied)
    arr_daily_weight_bool = arr_daily_weights > 6  # See which days exceed 6
    arr_criterion_two_bool = arr_daily_weight_bool.sum(axis=2, dtype=bool) # sum the days for each room where exceedance occurs
    # arr_criterion_two_percent = (arr_daily_weight_bool.sum(axis=2) / 365) * 100  # Percentage of days exceeding daily weight out of the total days.
    arr_max = arr_daily_weights.max(axis=2)
    return arr_criterion_two_bool, arr_max


def criterion_upper_limit_temperature(arr_deltaT):
    """Checks whether delta T exceeds 4K at any point. K meaning kelvin.
    Also calculates the percentage of the number of readings exceeding 4K over total number of readings

    *See CIBSE TM52: 2013, Page 14, Section 6.1.2c*

    Args:
        arr_deltaT (numpy.ndarray): Delta T (Operative temperature - Max acceptable temperature)

    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of exceedance.
    """
    arr_deltaT_round = np_round_half_up(arr_deltaT).astype(int)
    # arr_deltaT_round = arr_deltaT.round()
    arr_bool = arr_deltaT_round > 4  # Boolean array wherever delta T value exceeds 4K
    arr_criterion_three_bool = arr_bool.sum(axis=2, dtype=bool)  # Sum for each room to see if there is at least one exceedance
    # arr_criterion_three_percent = (arr_bool.sum(axis=2) / arr_deltaT_round.shape[2]) * 100  # Percentage of number of readings exceeding 4K over total number of readings
    arr_max = arr_deltaT_round.max(axis=2)
    return arr_criterion_three_bool, arr_max


def criterion_bedroom_comfort(arr_op_temp_v_hourly):
    if arr_op_temp_v_hourly.shape[2] != 8760:
        raise ValueError("Reporting intervals are not hourly for the operative temperature.")
    arr_op_temp_v_bedroom_comfort = filter_bedroom_comfort_time(arr_op_temp_v_hourly)
    arr_bedroom_comfort_exceed_temp_bool = arr_op_temp_v_bedroom_comfort > 26
    arr_bedroom_comfort_total_hours = arr_bedroom_comfort_exceed_temp_bool.sum(axis=2)
    arr_bool = arr_bedroom_comfort_total_hours > 32  # Can't exceed 32 hours (1 percent of annual hours between 10pm and 7am)
    arr_percent = (arr_bedroom_comfort_total_hours / arr_op_temp_v_bedroom_comfort.shape[2]) * 100  # Percentage of hours exceeding 26 degrees celsius over total annual hours between 10pm and 7am
    return arr_bool, arr_percent


def criterion_tm59_mechvent(arr_op_temp_v, arr_occupancy):
    arr_op_temp_v_occupied = np.where(arr_occupancy==0, 0, arr_op_temp_v)
    arr_op_temp_exceed_bool = arr_op_temp_v_occupied > 26

    arr_occupancy_bool = arr_occupancy > 0  # True where hour has occupancy greater than 0
    arr_occupancy_3_percent = arr_occupancy_bool.sum(axis=1)*0.03  # Sum along time-step axisi.e. sum time per room where occupied
    
    arr_bool = arr_op_temp_exceed_bool.sum(axis=2) > arr_occupancy_3_percent
    arr_percent = (arr_op_temp_exceed_bool.sum(axis=2)/arr_occupancy_bool.sum(axis=1))*100  # Percentage of occupied time exceeded out of total occupied time

    return arr_bool, arr_percent
