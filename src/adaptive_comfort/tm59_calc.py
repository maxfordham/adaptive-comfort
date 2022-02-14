import functools
import pathlib
from re import L
import numpy as np
import numpy.ma as ma
import pandas as pd
import datetime
from collections import OrderedDict

import sys
sys.path.append(str(pathlib.Path(__file__).parents[1]))
# # for dev only

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.equations import deltaT, calculate_running_mean_temp_hourly, np_calc_op_temp, np_calculate_max_adaptive_temp
from adaptive_comfort.utils import repeat_every_element_n_times, create_paths, fromfile, mean_every_n_elements, filter_bedroom_comfort_time, np_round_half_up
from adaptive_comfort.constants import arr_air_speed
from adaptive_comfort.criteria_testing import criterion_hours_of_exceedance, criterion_bedroom_comfort

class Tm59CalcWizard:
    def __init__(self, inputs, on_linux=True):
        """Calculates the operative temperature, maximum adaptive temperature, and delta T for each air speed
        and produces the results in an excel spreadsheet. 

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        self.bedroom_ids(inputs)
        self.op_temp(inputs)
        self.max_adaptive_temp(inputs)
        self.deltaT()
        self.run_criteria(inputs)
        # self.merge_dfs(inputs)
        # self.to_excel(inputs, on_linux)

    def bedroom_ids(self, inputs):
        arr_occupancy_bedroom_filtered = filter_bedroom_comfort_time(inputs.arr_occupancy, axis=1)
        self.arr_occupancy_bedroom_bool = (arr_occupancy_bedroom_filtered == 0).sum(axis=1, dtype=bool)  # If value is True then NOT a bedroom
        ma_arr_bedroom_ids = ma.masked_array(inputs.arr_room_ids_sorted, mask=self.arr_occupancy_bedroom_bool)  # Use arr_occupancy_bedroom_bool as a mask to obtain room IDs which are bedrooms. masked_array sets True values to invalid.
        self.arr_bedroom_ids = ma_arr_bedroom_ids.compressed()

    def op_temp(self, inputs):
        """Calculates the operative temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.arr_op_temp_v = np_calc_op_temp(
            inputs.arr_air_temp,
            arr_air_speed,
            inputs.arr_mean_radiant_temp
            )

    def max_adaptive_temp(self, inputs):
        """Calculates the maximum adaptive temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """

        arr_running_mean_temp = calculate_running_mean_temp_hourly(inputs.arr_dry_bulb_temp)
        cat_II_temp = 3  # For TM52 calculation use category 2
        self.arr_max_adaptive_temp = np_calculate_max_adaptive_temp(arr_running_mean_temp, cat_II_temp, arr_air_speed)
        if self.arr_max_adaptive_temp.shape[2] != self.arr_op_temp_v.shape[2]:  # If max adaptive time step axis does not match operative temp time step then modify.
            n = int(self.arr_op_temp_v.shape[2]/self.arr_max_adaptive_temp.shape[2])
            f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
            self.arr_max_adaptive_temp = np.apply_along_axis(f, 2, self.arr_max_adaptive_temp)

    def deltaT(self):
        """Calculates the temperature difference between the operative temperature and the maximum
        adaptive temperature for each air speed.
        """
        self.arr_deltaT = deltaT(self.arr_op_temp_v, self.arr_max_adaptive_temp)

    def run_criterion_one(self, arr_occupancy):
        """Convert delta T and occupancy array so the reporting interval is hourly, round the values,
        and then run criterion one.

        Args:
            arr_occupancy (numpy.ndarray): The number of people for each room per reporting interval

        Returns:
            tuple: First element contains boolean values where True means exceedance.
                Second element contains the percentage of exceedance.
        """
        factor = int(self.arr_deltaT.shape[2]/8760)  # Find factor to convert to hourly time-step array
        if factor > 1:
            f = functools.partial(mean_every_n_elements, n=factor)
            arr_deltaT_hourly = np.apply_along_axis(f, 2, self.arr_deltaT)
            arr_occupancy_hourly = np.apply_along_axis(f, 1, arr_occupancy)
        else:
            arr_deltaT_hourly = self.arr_deltaT
            arr_occupancy_hourly = arr_occupancy
        
        arr_deltaT_hourly = np_round_half_up(arr_deltaT_hourly)
        return criterion_hours_of_exceedance(arr_deltaT_hourly, arr_occupancy_hourly)

    def run_criterion_two(self):
        # TODO: If op_temp not hourly then convert
        # TODO: Only obtain arr_op_temp_v for bedroom IDs.
        criterion_bedroom_comfort(self.arr_op_temp_v)

    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        arr_criterion_one_bool, arr_criterion_one_percent = self.run_criterion_one(inputs.arr_occupancy)
        arr_criterion_two_bool, arr_criterion_two_percent = self.run_criterion_two()


if __name__ == "__main__":
    from constants import DIR_TESTJOB1
    paths = create_paths(DIR_TESTJOB1)
    tm59_input_data = fromfile(paths)
    tm59_calc = Tm59CalcWizard(tm59_input_data)