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

from constants import arr_air_speed, may_start_hour, sept_end_hour
from ies_calcs import np_deltaT
from utils import mean_every_n_elements, sum_every_n_elements, repeat_every_element_n_times, \
    round_half_up, round_for_criteria_two

arr_air_temp
arr_dry_bulb_temp

arr_occupancy = np.load(str(PATH_TESTJOB1 / "data_rooms_occupancy.npy"))
arr_sorted_room_ids = np.load(str(PATH_TESTJOB1 / "data_sorted_rooms.npy"))
arr_room_id_to_name_map = np.load(str(PATH_TESTJOB1 / "data_room_id_to_name_map.npy"))

di_map = arr_room_id_to_name_map[0]

arr_sorted_room_names = np.vectorize(di_map.get)(arr_sorted_room_ids)


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
            
    return li_running_mean_temp_daily


def calculate_running_mean_temp_hourly(arr_dry_bulb_temp_hourly):
    arr_dry_bulb_temp_daily_avg = get_dry_bulb_temp_daily(arr_dry_bulb_temp_hourly)  # Convert hourly to daily
    running_mean_temp_startoff = get_running_mean_temp_startoff(arr_dry_bulb_temp_daily_avg)  # Get running mean temp start off value
    li_running_mean_temp_daily = running_mean_temp_daily(running_mean_temp_startoff, arr_dry_bulb_temp_daily_avg)  # Get rest of running mean temps
    li_running_mean_temp_hourly = daily_value_list_into_hourly(li_running_mean_temp_daily)  # Convert back to hourly  # TODO: Replace with repeat_every_element_n_times
    return np.array(li_running_mean_temp_hourly)


def criterion_one(arr_deltaT):
    """[summary]

    Args:
        arr_op_temp ([type]): [description]
        arr_max_adaptive_temp ([type]): [description]

    Returns:
        np.ndarray: Whether room has failed or not
    """
    factor = int(arr_deltaT.shape[2]/8760)
    if factor > 1:  # TODO: Check is also int
        f = functools.partial(mean_every_n_elements, n=factor)
        arr_deltaT = np.apply_along_axis(f, 2, arr_deltaT)

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
    return arr_criterion_two_bool

def criterion_three(arr_deltaT):
    arr_bool = arr_deltaT > 4
    arr_criterion_three_bool = arr_bool.sum(axis=2, dtype=bool)
    return arr_criterion_three_bool



if __name__ == "__main__":
    di_bool_map = {True: "Fail", False: "Pass"}

    if arr_max_adaptive_temp.shape[0] != arr_op_temp.shape[2]:
        n = int(arr_op_temp.shape[2]/arr_max_adaptive_temp.shape[0])
        f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
        arr_max_adaptive_temp = np.apply_along_axis(f, 0, arr_max_adaptive_temp)

    arr_deltaT = np_deltaT(arr_op_temp, arr_max_adaptive_temp)

    li_air_speeds = [float(i[0][0]) for i in arr_air_speed]
    li_air_speeds_str = [str(speed) for speed in li_air_speeds]

    # Criterion 1
    arr_criterion_one_bool = criterion_one(arr_deltaT)
    # arr_criterion_one_bool = np.vectorize(di_bool_map.get)(arr_criterion_one_bool)  # Map true and false to fail and pass respectively
    li_room_criterion_one = [{"Room Name": arr_sorted_room_names, "Criterion 1 (Pass/Fail)": arr_room} for arr_room in arr_criterion_one_bool]
    di_data_frames_criterion_one = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 1 (Pass/Fail)"]) for i, j in zip(li_air_speeds_str, li_room_criterion_one)}  # TODO: Replace i with air speed value. 

    # Criterion 2
    arr_criterion_two_bool = criterion_two(arr_deltaT)
    # arr_criterion_two_bool = np.vectorize(di_bool_map.get)(arr_criterion_two_bool)
    li_room_criterion_two = [{"Room Name": arr_sorted_room_names, "Criterion 2 (Pass/Fail)": arr_room} for arr_room in arr_criterion_two_bool]
    di_data_frames_criterion_two = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 2 (Pass/Fail)"]) for i, j in zip(li_air_speeds_str, li_room_criterion_two)}

    # Criterion 3
    arr_criterion_three_bool = criterion_three(arr_deltaT)
    # arr_criterion_three_bool = np.vectorize(di_bool_map.get)(arr_criterion_three_bool)
    li_room_criterion_three = [{"Room Name": arr_sorted_room_names, "Criterion 3 (Pass/Fail)": arr_room} for arr_room in arr_criterion_three_bool]
    di_data_frames_criterion_three = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 3 (Pass/Fail)"]) for i, j in zip(li_air_speeds_str, li_room_criterion_three)}

    # Merging
    li_all_criteria_data_frames = []
    for speed in li_air_speeds_str:  # Loop through number of air speeds
        df_criteria_one_and_two = pd.merge(di_data_frames_criterion_one[speed], di_data_frames_criterion_two[speed], on=["Room Name"])
        df_all_criteria = pd.merge(df_criteria_one_and_two, di_data_frames_criterion_three[speed], on=["Room Name"])

        df_all_criteria["TM52 (Pass/Fail)"] = df_all_criteria.sum(axis=1) >= 2

        # Map true and false to fail and pass respectively
        li_columns_to_map = [
            "Criterion 1 (Pass/Fail)",
            "Criterion 2 (Pass/Fail)",
            "Criterion 3 (Pass/Fail)",
            "TM52 (Pass/Fail)"
        ]
        for column in li_columns_to_map:
            df_all_criteria[column] = df_all_criteria[column].map(di_bool_map) 

        di_all_criteria_data_frame = {
            "sheet_name": speed,
            "df": df_all_criteria,
        }
        li_all_criteria_data_frames.append(di_all_criteria_data_frame)
    
    to_excel(data_object=li_all_criteria_data_frames, fpth="test_output.xlsx", open=False)
    print("done")