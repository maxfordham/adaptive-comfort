"""IES calculations referenced from CIBSE guidance."""
import functools
import numpy as np

from utils import mean_every_n_elements, repeat_every_element_n_times, sum_every_n_elements, np_round_for_criteria_two

def calc_op_temp(air_temp, air_speed, mean_radiant_temp):
    """
    Calculates Operative Temperature for Given Conditions

    See CIBSE Guide A, Equation 1.2, Part 1.2.2
    
    Arguments:
        air_temp (`float`): Indoor Air Temp (C)
        air_speed (`float`): Air Speed in room (m.s^-1)
        mean_radiant_temp (`float`): Mean Radiant Temp (C)
        
    Returns:
        op_temp (`float`): Operative Temp (C)
    """
    return ((air_temp*((10*air_speed)**(1/2))) + mean_radiant_temp) \
                /(1+((10*air_speed)**(1/2)))


def get_running_mean_temp_startoff(dry_bulb_temp_daily_avg):
    """
    Returns Running Mean Temperature Startoff Value

    See CIBSE TM52: 2013, Equation 2.3, Box 2, Page 7, Section 3.3
    
    Arguments:
        dry_bulb_temperature_daily_avg (`list of 365 items`): 
            list of daily average values for the dry bulb temperature over a year
    
    Returns:
        temp_startoff (`int`): returns the running mean temperature startoff value (C)
    """
    temp_startoff = round(((dry_bulb_temp_daily_avg[-1] 
        + dry_bulb_temp_daily_avg[-2]*0.8 
        + dry_bulb_temp_daily_avg[-3]*0.6 
        + dry_bulb_temp_daily_avg[-4]*0.5 
        + dry_bulb_temp_daily_avg[-5]*0.4 
        + dry_bulb_temp_daily_avg[-6]*0.3 
        + dry_bulb_temp_daily_avg[-7]*0.2)/3.8),200)
    return temp_startoff


def running_mean_temp(dry_bulb_temp_yest_avg, running_mean_yest, a=0.8):
    """
    Returns Running Mean Temperature Startoff Value

    See CIBSE TM52: 2013, Equation 2.2, Box 2, Page 7, Section 3.3
    
    Arguments:
        dry_bulb_temp_yest_avg (`float`): Daily mean temperature for previous day (C)
        running_mean_yest (`float`): Running mean temp for previous day (C)
        a (`float, default=0.8`): Correlation constant
    
    Returns: 
        value (`float`):  Running Mean temp for current day (C)
    """
    return ((1-a)*dry_bulb_temp_yest_avg + a*running_mean_yest)


def running_mean_temp_daily(temp_startoff, arr_dry_bulb_temp_daily_avg):
    li_running_mean_temp_daily = [temp_startoff]

    for i, j in enumerate(arr_dry_bulb_temp_daily_avg):
        if i == 0:
            pass
        elif i == 1:
            running_mean_temp_result = running_mean_temp(arr_dry_bulb_temp_daily_avg[i-1], temp_startoff)
            li_running_mean_temp_daily.append(running_mean_temp_result)
        else: 
            running_mean_temp_result = running_mean_temp(arr_dry_bulb_temp_daily_avg[i-1], li_running_mean_temp_daily[i-1])
            li_running_mean_temp_daily.append(running_mean_temp_result)
            
    return np.array(li_running_mean_temp_daily)


def calculate_running_mean_temp_hourly(arr_dry_bulb_temp_hourly):
    f = functools.partial(mean_every_n_elements, n=24, axis=1)
    arr_dry_bulb_temp_daily = np.apply_along_axis(f, 0, arr_dry_bulb_temp_hourly)  # Convert hourly to daily
    
    running_mean_temp_startoff = get_running_mean_temp_startoff(arr_dry_bulb_temp_daily)  # Get running mean temp start off value
    arr_running_mean_temp_daily = running_mean_temp_daily(running_mean_temp_startoff, arr_dry_bulb_temp_daily)  # Get rest of running mean temps

    f = functools.partial(repeat_every_element_n_times, n=24, axis=0)
    arr_running_mean_temp_hourly = np.apply_along_axis(f, 0, arr_running_mean_temp_daily) # Convert back to hourly
    return arr_running_mean_temp_hourly


def calculate_max_adaptive_temp(running_mean_temp, category_temp):
    """[summary]

    Args:
        running_mean_daily_temp ([type]): exponentially weighted running mean of the daily mean outdoor air temperature

    Returns:
        [type]: [description]
    """
    return 0.33*running_mean_temp + 18.8 + category_temp


def deltaT(op_temp, max_adaptive_temp):
    """Returns the difference between the operative temperature and the
    max-adaptive temperature.
    
    See CIBSE TM52: 2013, Page 13, Equation 9, Section 6.1.2

    Args:
        op_temp ([type]): [description]
        max_adaptive_temp ([type]): [description]

    Returns:
        [type]: [description]
    """
    return op_temp - max_adaptive_temp

def daily_weighted_exceedance(arr_deltaT_occupied):
    arr_deltaT_occupied = np_round_for_criteria_two(arr_deltaT_occupied)
    n = int(arr_deltaT_occupied.shape[2]/365)  # Factor to take arr_deltaT time-step to daily
    f = functools.partial(sum_every_n_elements, n=n)  # We want to sum the intervals so the array represents daily intervals
    time_step = 8760/arr_deltaT_occupied.shape[2]  # If half hour steps then time_step = 1/2
    return time_step * np.apply_along_axis(f, 2, arr_deltaT_occupied)

# Vectorised Functions

np_calc_op_temp = np.vectorize(calc_op_temp)

np_calculate_max_adaptive_temp = np.vectorize(calculate_max_adaptive_temp)
