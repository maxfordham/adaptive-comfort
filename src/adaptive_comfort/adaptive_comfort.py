"""Main module."""

import functools
import numpy as np
import pandas as pd

from ies_calcs import deltaT, np_calc_op_temp, np_calculate_max_adaptive_temp, calculate_running_mean_temp_hourly
from utils import mean_every_n_elements, sum_every_n_elements, repeat_every_element_n_times, \
    round_half_up, round_for_criteria_two, create_paths, fromfile
from constants import DIR_TESTJOB1, arr_air_speed
from criteria_testing import criterion_one, criterion_two, criterion_three

class Tm52CalcWizard:
    def __init__(self):
        self.define_vars()

    def define_vars(self):
        paths = create_paths(DIR_TESTJOB1)
        di_input_data = fromfile(paths)

        self.di_project_info = di_input_data["arr_project_info"].item()
        self.di_aps_info = di_input_data["arr_aps_info"].item()
        self.di_weather_file_info = di_input_data["arr_weather_file_info"].item()
        self.di_room_id_name_map = di_input_data["arr_room_id_name_map"].item()
        self.arr_room_ids_sorted = di_input_data["arr_room_ids_sorted"]
        self.arr_air_temp = di_input_data["arr_air_temp"]
        self.arr_mean_radiant_temp = di_input_data["arr_mean_radiant_temp"]
        self.arr_occupancy = di_input_data["arr_occupancy"]
        self.arr_dry_bulb_temp = di_input_data["arr_dry_bulb_temp"]
        self.arr_sorted_room_names = np.vectorize(self.di_room_id_name_map.get)(self.arr_room_ids_sorted)
        self.di_bool_map = {True: "Fail", False: "Pass"}
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]

    def op_temp(self):
        self.arr_op_temp_v = np_calc_op_temp(
            self.arr_air_temp,
            arr_air_speed,
            self.arr_mean_radiant_temp
            )

    def max_adaptive_temp(self):
        arr_running_mean_temp = calculate_running_mean_temp_hourly(self.arr_dry_bulb_temp)
        cat_II_temp = 3  # For TM52 calculation use category 2
        self.arr_max_adaptive_temp = np_calculate_max_adaptive_temp(arr_running_mean_temp, cat_II_temp)
        if self.arr_max_adaptive_temp.shape[0] != self.arr_op_temp_v.shape[2]:  # If max adaptive time step axis does not match operative temp time step then modify.
            n = int(self.arr_op_temp_v.shape[2]/self.arr_max_adaptive_temp.shape[0])
            f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
            self.arr_max_adaptive_temp = np.apply_along_axis(f, 0, self.arr_max_adaptive_temp)

    def deltaT(self):
        self.arr_deltaT = deltaT(self.arr_op_temp_v, self.arr_max_adaptive_temp)

    def criterion_one(self):
        arr_criterion_one_bool = criterion_one(self.arr_deltaT)
        li_room_criterion_one = [{"Room Name": self.arr_sorted_room_names, "Criterion 1 (Pass/Fail)": arr_room} for arr_room in arr_criterion_one_bool]
        self.di_data_frames_criterion_one = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 1 (Pass/Fail)"]) for i, j in zip(self.li_air_speeds_str, li_room_criterion_one)} 

    def criterion_two(self):
        arr_criterion_two_bool = criterion_two(self.arr_deltaT)
        li_room_criterion_two = [{"Room Name": self.arr_sorted_room_names, "Criterion 2 (Pass/Fail)": arr_room} for arr_room in arr_criterion_two_bool]
        di_data_frames_criterion_two = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 2 (Pass/Fail)"]) for i, j in zip(self.li_air_speeds_str, li_room_criterion_two)}

    def criterion_three(self):
        arr_criterion_three_bool = criterion_three(self.arr_deltaT)
        li_room_criterion_three = [{"Room Name": self.arr_sorted_room_names, "Criterion 3 (Pass/Fail)": arr_room} for arr_room in arr_criterion_three_bool]
        di_data_frames_criterion_three = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 3 (Pass/Fail)"]) for i, j in zip(self.li_air_speeds_str, li_room_criterion_three)}

    def run_criteria(self):
        di_criteria = {
            "arr_criterion_one_bool": criterion_one(self.arr_deltaT),
            "arr_criterion_two_bool": criterion_two(self.arr_deltaT),
            "arr_criterion_three_bool": criterion_three(self.arr_deltaT),
        }
        for criterion in di_criteria:
            li_room_criterion = [{"Room Name": self.arr_sorted_room_names, "Criterion 3 (Pass/Fail)": arr_room} for arr_room in criterion]
            di_data_frames_criterion = {i: pd.DataFrame(j, columns=["Room Name", "Criterion 3 (Pass/Fail)"]) for i, j in zip(self.li_air_speeds_str, li_room_criterion)}


    