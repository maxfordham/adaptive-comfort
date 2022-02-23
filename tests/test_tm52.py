"""Tests for `adaptive_comfort` package."""

import pytest
import numpy as np
import numpy.ma as ma
import pandas as pd
from collections import OrderedDict

import sys; import pathlib
DIR_MODULE = pathlib.Path(__file__).parents[1] / 'src'
sys.path.append(str(DIR_MODULE))
# for dev only

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.utils import create_paths, fromfile
from adaptive_comfort.tm52_calc import Tm52CalcWizard
from constants import DIR_TESTJOB1, FPTH_IES_TESTJOB1_V_0_1, FPTH_IES_TESTJOB1_V_0_5, arr_max_adaptive_temp, \
    arr_running_mean_temp, arr_operative_temp


class TestCheckResults:
    def __init__(self):
        paths = create_paths(DIR_TESTJOB1)
        tm52_input_data = fromfile(paths)
        self.tm52_calc = Tm52CalcWizard(tm52_input_data, fdir_results=DIR_TESTJOB1)

    def test_all_criteria(self):
        df_mf_v_0_1 = self.tm52_calc.li_all_criteria_data_frames[2]["df"]  # df for 0.1 air speed
        # df_mf_v_0_5 = self.tm52_calc.li_all_criteria_data_frames[7]["df"]  # df for 0.5 air speed

        # Get IES results
        df_ies_v_0_1 = pd.read_csv(FPTH_IES_TESTJOB1_V_0_1, header=22)
        # df_ies_v_0_5 = pd.read_csv(FPTH_IES_TESTJOB1_V_0_5, header=22)

        # Mapping mf results to ies results.
        chararr_one = np.char.array(np.where(df_mf_v_0_1["Criterion 1 (Pass/Fail)"]=="Fail", " 1", ""))
        chararr_two = np.char.array(np.where(df_mf_v_0_1["Criterion 2 (Pass/Fail)"]=="Fail", "2", ""))
        chararr_three = np.char.array(np.where(df_mf_v_0_1["Criterion 3 (Pass/Fail)"]=="Fail", "3", ""))

        li_criteria_failing = []
        for i, j, k in zip(chararr_one, chararr_two, chararr_three):
            final_str = ""
            if i:
                final_str += i            

            if i and j:
                final_str += " & " + j
            else:
                final_str += j
            
            if (j and k) or (i and k):
                final_str += " & " + k
            else:
                final_str += k

            li_criteria_failing.append(final_str)

        arr_mf_criteria_failing = np.array(li_criteria_failing)
        arr_ies_criteria_failing = np.array(df_ies_v_0_1[" Criteria failing"])
        arr_ies_criteria_failing = np.where(arr_ies_criteria_failing==" -", "", arr_ies_criteria_failing)
        arr_criteria_failing_bool = arr_mf_criteria_failing == arr_ies_criteria_failing

        di_criteria_failing = OrderedDict([
                ("Room Name", self.tm52_calc.arr_sorted_room_names),
                ("IES Results", arr_ies_criteria_failing),
                ("MF Results", arr_mf_criteria_failing),
                ("IES v MF", arr_criteria_failing_bool)
            ])

        df_criterion = pd.DataFrame.from_dict(di_criteria_failing)
        di_criterion_to_excel = {
                "sheet_name": "Criteria Failing, Air Speed 0.1",
                "df": df_criterion,
            }
        
        di_names = {
            "Criterion 1": {
                "mf_name": "Criterion 1 (% Hours Delta T >= 1K)",
                "ies_name": " Criteria 1 (%Hrs Top-Tmax>=1K)",
            },
            "Criterion 2": {
                "mf_name": "Criterion 2 (Max Daily Deg. Hours)",
                "ies_name": " Criteria 2 (Max. Daily Deg.Hrs)",
            },
            "Criterion 3": {
                "mf_name": "Criterion 3 (Max Delta T)",
                "ies_name": " Criteria 3 (Max. DeltaT)",
            },
        }

        li_criteria_to_excel = [di_criterion_to_excel]
        for criterion, di_name in di_names.items():
            criterion_abs_change = df_mf_v_0_1[di_name["mf_name"]] - df_ies_v_0_1[di_name["ies_name"]]
            criterion_rel_change = (criterion_abs_change / df_ies_v_0_1[di_name["ies_name"]]) * 100
            di_criterion = OrderedDict([
                ("Room Name", self.tm52_calc.arr_sorted_room_names),
                ("IES Results", df_ies_v_0_1[di_name["ies_name"]]),
                ("MF Results", df_mf_v_0_1[di_name["mf_name"]]),
                ("{0} Absolute Change".format(criterion), criterion_abs_change),
                ("{0} Relative Change (%)".format(criterion), criterion_rel_change)
            ])
            df_criterion = pd.DataFrame.from_dict(di_criterion)
            di_criterion_to_excel = {
                "sheet_name": "{0}, Air Speed 0.1".format(criterion),
                "df": df_criterion,
            }
            li_criteria_to_excel.append(di_criterion_to_excel)
        
        to_excel(data_object=li_criteria_to_excel, fpth="test_all_criteria.xlsx", open=False)

    def test_daily_running_mean_temp(self):
        ies_results = arr_running_mean_temp.astype("float64").round(3)
        mf_results = self.tm52_calc.arr_running_mean_temp.round(3)
        abs_change = abs(self.tm52_calc.arr_running_mean_temp.round(3) - arr_running_mean_temp.astype("float64").round(3))
        rel_change = (abs_change / abs(arr_running_mean_temp.astype("float64").round(3))) * 100
        di = OrderedDict([
            ("IES Results", ies_results),
            ("MF Results", mf_results),
            ("Absolute Change", abs_change),
            ("Relative Change (%)", rel_change)
        ])
        df = pd.DataFrame.from_dict(di)
        di_to_excel = {
            "sheet_name": "Running Mean Temperature",
            "df": df,
        }
        to_excel(data_object=di_to_excel, fpth="test_running_mean_temp.xlsx", open=False)


    def test_max_adaptive_temp(self):
        ies_results = arr_max_adaptive_temp.astype("float64").round(3) 
        mf_results = self.tm52_calc.arr_max_acceptable_temp[0][0].round(3)
        abs_change = abs(self.tm52_calc.arr_max_acceptable_temp[0][0].round(3) - arr_max_adaptive_temp.astype("float64").round(3))
        rel_change = (abs_change / abs(arr_max_adaptive_temp.astype("float64").round(3))) * 100
        di = OrderedDict([
            ("IES Results", ies_results),
            ("MF Results", mf_results),
            ("Absolute Change", abs_change),
            ("Relative Change (%)", rel_change)
        ])
        df = pd.DataFrame.from_dict(di)
        di_to_excel = {
            "sheet_name": "Max Acceptable Temperature",
            "df": df,
        }
        to_excel(data_object=di_to_excel, fpth="test_max_acceptable_temp.xlsx", open=False)


    def test_operative_temp(self):
        di_op_temp = arr_operative_temp.tolist()
        li_df_concat = []
        for i, j in enumerate(sorted(di_op_temp.items())):
            arr_op_temp = j[1]
            ies_results = arr_op_temp.astype("float64").round(3) 
            mf_results = self.tm52_calc.arr_op_temp_v[0][i].round(3)
            abs_change = abs(self.tm52_calc.arr_op_temp_v[0][i].round(3) - arr_op_temp.astype("float64").round(3))
            rel_change = (abs_change / abs(arr_op_temp.astype("float64").round(3))) * 100
            di = OrderedDict([
                ("IES Results", ies_results),
                ("MF Results", mf_results),
                ("Absolute Change", abs_change),
                ("Relative Change (%)", rel_change),
            ])
            df = pd.DataFrame.from_dict(di)
            df.columns = pd.MultiIndex.from_product([str(j[0]), df.columns[df.columns != '']])
            df[("-", "-")] = np.nan  # Add empty column to split between rooms
            li_df_concat.append(df)

        df_concat = pd.concat(li_df_concat, axis=1)  # Concatenate all data frames
        df_concat.to_excel(
            "test_operative_temp.xlsx", 
            sheet_name="Operative Temp, Air Speed 0.1"
        )


if __name__ == "__main__":
    test_check_results = TestCheckResults()
    # test_check_results.test_all_criteria()
    test_check_results.test_operative_temp()
    # test_check_results.test_daily_running_mean_temp()
    # test_check_results.test_max_adaptive_temp()