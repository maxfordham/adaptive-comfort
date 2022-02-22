"""Tests for `adaptive_comfort` package."""

import pytest
import numpy as np
import pandas as pd

import sys; import pathlib
DIR_MODULE = pathlib.Path(__file__).parents[1] / 'src'
sys.path.append(str(DIR_MODULE))
# for dev only

from adaptive_comfort.utils import create_paths, fromfile
from adaptive_comfort.tm52_calc import Tm52CalcWizard
from constants import DIR_TESTJOB1, FPTH_IES_TESTJOB1_V_0_1, FPTH_IES_TESTJOB1_V_0_5, arr_max_adaptive_temp, \
    arr_running_mean_temp


class TestCheckResults:
    def __init__(self):
        paths = create_paths(DIR_TESTJOB1)
        tm52_input_data = fromfile(paths)
        self.tm52_calc = Tm52CalcWizard(tm52_input_data, fdir_results=DIR_TESTJOB1)

    def test_all_criteria(self):
        df_mf_v_0_1 = self.tm52_calc.li_all_criteria_data_frames[2]["df"]  # df for 0.1 air speed
        df_mf_v_0_5 = self.tm52_calc.li_all_criteria_data_frames[7]["df"]  # df for 0.5 air speed

        # Get IES results
        df_ies_v_0_1 = pd.read_csv(FPTH_IES_TESTJOB1_V_0_1, header=22)
        df_ies_v_0_5 = pd.read_csv(FPTH_IES_TESTJOB1_V_0_5, header=22)
        criterion_one_absolute_change = df_mf_v_0_1["Criterion 1 (% Hours Delta T >= 1K)"] - df_ies_v_0_1[" Criteria 1 (%Hrs Top-Tmax>=1K)"]
        criterion_two_absolute_change = df_mf_v_0_1["Criterion 2 (Max Daily Deg. Hours)"] - df_ies_v_0_1[" Criteria 2 (Max. Daily Deg.Hrs)"]
        criterion_three_absolute_change = df_mf_v_0_1["Criterion 3 (Max Delta T)"] - df_ies_v_0_1[" Criteria 3 (Max. DeltaT)"]

        criterion_one_relative_change = (criterion_one_absolute_change / df_ies_v_0_1[" Criteria 1 (%Hrs Top-Tmax>=1K)"]) * 100
        criterion_two_relative_change = (criterion_two_absolute_change / df_ies_v_0_1[" Criteria 2 (Max. Daily Deg.Hrs)"]) * 100
        criterion_three_relative_change = (criterion_three_absolute_change / df_ies_v_0_1[" Criteria 3 (Max. DeltaT)"]) * 100

        print("test")

    def test_daily_running_mean_temp(self):
        arr_running_mean_temp_bool = self.tm52_calc.arr_running_mean_temp[0].round(3) == arr_running_mean_temp.astype("float64").round(3)  # Checking against IES
        print(arr_running_mean_temp_bool)

    def test_max_adaptive_temp(self):
        arr_max_adaptive_bool = self.tm52_calc.arr_max_acceptable_temp[0].round(3) == arr_max_adaptive_temp.astype("float64").round(3)  # Checking against IES
        print(arr_max_adaptive_bool)

    def test_operative_temp(self):
        pass

    def test_criterion_one(self):
        pass

if __name__ == "__main__":
    # TestCheckResults().test_all_criteria()
    TestCheckResults().test_daily_running_mean_temp()
    TestCheckResults().test_max_adaptive_temp()