"""Contains functions that perform all the different criteria that will be used for TM52 and TM59.
"""
import numpy as np

from adaptive_comfort.constants import MAY_START_HOUR, SEPT_END_HOUR
from adaptive_comfort.utils import np_round_half_up, filter_bedroom_comfort_time
from adaptive_comfort.equations import daily_weighted_exceedance


def criterion_time_of_exceedance(arr_deltaT, arr_occupancy, factor):
    """Calculates whether a room has exceeded the threshold for time of exceedance. 
    Also calculates the percentage of occupied time exceeded out of total occupied time for each room.
    *See CIBSE TM52: 2013, Page 13, Section 6.1.2a*
    
    Args:
        arr_deltaT (numpy.ndarray): Delta T (Operative temperature - Max acceptable temperature)
        arr_occupancy (numpy.ndarray): Occupancy (Number of people)
    Returns:
        tuple: First element contains boolean values where True means exceedance.
            Second element contains the percentage of exceedance.
    """
    MAY_START = factor * MAY_START_HOUR  # Adjusting index to given time-step intervals
    SEPT_END = factor * SEPT_END_HOUR

    arr_deltaT_may_to_sept = arr_deltaT[
        :, :, MAY_START:SEPT_END
    ]  # Obtaining deltaT between May and end of September
    arr_occupancy_may_to_sept = arr_occupancy[
        :, MAY_START:SEPT_END
    ]  # Obtaining occupancy between May and end of September

    arr_deltaT_occupied_may_to_sept = np.where(
        arr_occupancy_may_to_sept == 0, 0, arr_deltaT_may_to_sept
    )  # Where unoccupied, set delta T to 0 to ignore in criterion test.
    arr_deltaT_occupied_may_to_sept = np_round_half_up(
        arr_deltaT_occupied_may_to_sept
    ).astype(
        int
    )  # Round delta T as specified by CIBSE TM52 guide.

    arr_deltaT_bool = (
        arr_deltaT_occupied_may_to_sept >= 1
    )  # Find where delta T is greater than or equal to 1K.
    arr_room_total_time_exceedance = arr_deltaT_bool.sum(
        axis=2
    )  # Sum along last axis (time) to get total time of exceedance per room

    arr_occupancy_bool = (
        arr_occupancy_may_to_sept > 0
    )  # True where period has occupancy greater than 0
    arr_occupancy_3_percent = (
        arr_occupancy_bool.sum(axis=1) * 0.03
    )  # Sum along time-step axis (time), i.e. sum time per room where occupied

    arr_bool = arr_room_total_time_exceedance > arr_occupancy_3_percent
    arr_percent = (
        arr_room_total_time_exceedance / arr_occupancy_bool.sum(axis=1)
    ) * 100  # Percentage of occupied time exceeded out of total occupied time
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
    arr_deltaT_occupied = np.where(
        arr_occupancy == 0, 0, arr_deltaT
    )  # Sets cells in arr_deltaT to 0 where arr_occupancy is 0. We only want to consider occupied intervals.
    arr_daily_weights = daily_weighted_exceedance(arr_deltaT_occupied)
    arr_daily_weight_bool = arr_daily_weights > 6  # See which days exceed 6
    arr_criterion_two_bool = arr_daily_weight_bool.sum(
        axis=2, dtype=bool
    )  # sum the days for each room where exceedance occurs
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
    arr_bool = arr_deltaT_round > 4  # Boolean array wherever delta T value exceeds 4K
    arr_criterion_three_bool = arr_bool.sum(
        axis=2, dtype=bool
    )  # Sum for each room to see if there is at least one exceedance
    arr_max = arr_deltaT_round.max(axis=2)
    return arr_criterion_three_bool, arr_max


def criterion_bedroom_comfort(arr_op_temp_v, factor):
    """Guarantee comfort during the sleeping hours. The operative temperature in the bedroom from 10pm to 7am must not exceed 26 degrees celsius
    for more than 1% of the annual time.

    Args:
        arr_op_temp_v (numpy.ndarray): Operative temperatue for each air speed at every time-step interval

    Returns:
        tuple: Returns room that failed and passed
            Percentage where 26 degrees celsius was exceeded
    """
    arr_op_temp_v_bedroom_comfort = filter_bedroom_comfort_time(arr_op_temp_v, factor)
    arr_bedroom_comfort_exceed_temp_bool = arr_op_temp_v_bedroom_comfort > 26
    arr_bedroom_comfort_total_time = arr_bedroom_comfort_exceed_temp_bool.sum(axis=2)
    arr_bool = (
        arr_bedroom_comfort_total_time > 32 * factor
    )  # Can't exceed 1 percent of annual time between 10pm and 7am
    arr_percent = (
        arr_bedroom_comfort_total_time / arr_op_temp_v_bedroom_comfort.shape[2]
    ) * 100  # Percentage of time exceeding 26 degrees celsius over total annual time between 10pm and 7am
    arr_hour_value = arr_bedroom_comfort_total_time / factor
    return arr_bool, arr_percent, arr_hour_value


def criterion_tm59_mechvent(arr_op_temp_v, arr_occupancy):
    """For homes with restricted window openings, we must follow this CIBSE criterion.
    All occupied rooms should not exceed an operative temperature of more than 26 degrees celsius for more than
    3 percent of the annual occupied time.

    Args:
        arr_op_temp_v (numpy.ndarray): Operative temperatue for each air speed
        arr_occupancy (numpy.ndarray): Number of people in each room

    Returns:
        tuple: Returns which rooms failed and passed
            Also returns the percentage of time where rooms exceeded the threshold
    """
    arr_op_temp_v_occupied = np.where(
        arr_occupancy == 0, 0, arr_op_temp_v
    )  # Want to ignore any temperatures where rooms are unoccupied
    arr_op_temp_exceed_bool = arr_op_temp_v_occupied > 26

    arr_occupancy_bool = (
        arr_occupancy > 0
    )  # True where time-step has occupancy greater than 0
    arr_occupancy_3_percent = (
        arr_occupancy_bool.sum(axis=1) * 0.03
    )  # Sum along time-step axis i.e. sum time per room where occupied

    arr_bool = arr_op_temp_exceed_bool.sum(axis=2) > arr_occupancy_3_percent
    arr_percent = (
        arr_op_temp_exceed_bool.sum(axis=2) / arr_occupancy_bool.sum(axis=1)
    ) * 100  # Percentage of occupied time exceeded out of total occupied time

    return arr_bool, arr_percent
