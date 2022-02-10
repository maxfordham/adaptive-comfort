"""Main module."""

import functools
import sys
import pathlib
import numpy as np
import pandas as pd

PATH_MODULE = pathlib.Path(__file__).parent
sys.path.append(str(PATH_MODULE / "lib"))

from xlsx_templater import to_excel

from ies_calcs import deltaT, np_calc_op_temp, np_calculate_max_adaptive_temp, calculate_running_mean_temp_hourly
from utils import repeat_every_element_n_times, create_paths, fromfile, np_round_half_up
from constants import DIR_TESTJOB1, arr_air_speed
from criteria_testing import criterion_one, criterion_two, criterion_three

class Tm52CalcWizard:
    def __init__(self, input):
        """[summary]

        Args:
            input (Tm52InputData): Class instace containing the required inputs.
        """
        self.define_vars(input)
        self.op_temp(input)
        self.max_adaptive_temp(input)
        self.deltaT()
        self.run_criteria()
        self.merge_dfs()
        self.to_excel(input)

    def define_vars(self, input):        
        self.arr_sorted_room_names = np.vectorize(input.di_room_id_name_map.get)(input.arr_room_ids_sorted)
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]

    def op_temp(self, input):
        self.arr_op_temp_v = np_calc_op_temp(
            input.arr_air_temp,
            arr_air_speed,
            input.arr_mean_radiant_temp
            )

    def max_adaptive_temp(self, input):
        arr_running_mean_temp = calculate_running_mean_temp_hourly(input.arr_dry_bulb_temp)
        cat_II_temp = 3  # For TM52 calculation use category 2
        self.arr_max_adaptive_temp = np_calculate_max_adaptive_temp(arr_running_mean_temp, cat_II_temp)
        if self.arr_max_adaptive_temp.shape[0] != self.arr_op_temp_v.shape[2]:  # If max adaptive time step axis does not match operative temp time step then modify.
            n = int(self.arr_op_temp_v.shape[2]/self.arr_max_adaptive_temp.shape[0])
            f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
            self.arr_max_adaptive_temp = np.apply_along_axis(f, 0, self.arr_max_adaptive_temp)

    def deltaT(self):
        self.arr_deltaT = deltaT(self.arr_op_temp_v, self.arr_max_adaptive_temp)

    def run_criteria(self, input):
        self.arr_deltaT = np_round_half_up(self.arr_deltaT)  # Round delta T as specified by CIBSE TM52 guide.
        arr_criterion_one_bool, arr_criterion_one_percent = criterion_one(self.arr_deltaT, input.arr_occupancy)
        arr_criterion_two_bool, arr_criterion_two_percent = criterion_two(self.arr_deltaT)
        arr_criterion_three_bool, arr_criterion_three_percent = criterion_three(self.arr_deltaT)

        di_criteria = {
            "Criterion 1": zip(arr_criterion_one_bool, arr_criterion_one_percent),
            "Criterion 2": zip(arr_criterion_two_bool, arr_criterion_two_percent),
            "Criterion 3": zip(arr_criterion_three_bool, arr_criterion_three_percent),
        }

        # Constructing dictionary of data frames for each air speed.
        self.di_data_frame_criterion = {}
        for name, criterion in di_criteria.items():
            li_room_criterion = [{
                "Room Name": self.arr_sorted_room_names, 
                "{0} (Pass/Fail)".format(name): arr_room[0],
                "{0} Percentage (%)".format(name): arr_room[1],
                } for arr_room in criterion]
            di_data_frames_criterion = {
                speed: pd.DataFrame(data, columns=["Room Name", "{0} Percentage (%)".format(name), "{0} (Pass/Fail)".format(name)]) 
                    for speed, data in zip(self.li_air_speeds_str, li_room_criterion)
                }
            self.di_data_frame_criterion[name] = di_data_frames_criterion

    def merge_dfs(self):
        self.li_all_criteria_data_frames = []
        for speed in self.li_air_speeds_str:  # Loop through number of air speeds
            df_criteria_one_and_two = pd.merge(self.di_data_frame_criterion["Criterion 1"][speed], self.di_data_frame_criterion["Criterion 2"][speed], on=["Room Name"])
            df_all_criteria = pd.merge(df_criteria_one_and_two, self.di_data_frame_criterion["Criterion 3"][speed], on=["Room Name"])

            df_all_criteria["TM52 (Pass/Fail)"] = df_all_criteria.sum(axis=1) >= 2

            # Map true and false to fail and pass respectively
            li_columns_to_map = [
                "Criterion 1 (Pass/Fail)",
                "Criterion 2 (Pass/Fail)",
                "Criterion 3 (Pass/Fail)",
                "TM52 (Pass/Fail)"
            ]
            di_bool_map = {True: "Fail", False: "Pass"}
            for column in li_columns_to_map:
                df_all_criteria[column] = df_all_criteria[column].map(di_bool_map) 

            di_all_criteria_data_frame = {
                "sheet_name": speed,
                "df": df_all_criteria,
            }
            self.li_all_criteria_data_frames.append(di_all_criteria_data_frame)
    
    def to_excel(self, input, on_linux=True):
        file_name = "TM52__{0}.xlsx".format(input.di_project_info['project_name'])
        fpth_results = pathlib.PureWindowsPath(input.di_project_info['project_path']) / "mf_results" / "tm52" / file_name
        if on_linux:
            output_path = fpth_results.as_posix().replace("C:/", "/mnt/c/")
        else:
            output_path = str(fpth_results)
        to_excel(data_object=self.li_all_criteria_data_frames, fpth=output_path, open=False)
        print("done")


if __name__ == "__main__":
    paths = create_paths(DIR_TESTJOB1)
    tm52_input_data = fromfile(paths)
    tm52_calc = Tm52CalcWizard(tm52_input_data)