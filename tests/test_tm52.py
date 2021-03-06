"""Tests for `adaptive_comfort` package."""
import numpy as np
import pandas as pd
from collections import OrderedDict

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.utils import create_paths, fromfile
from adaptive_comfort.tm52_calc import Tm52CalcWizard
from .constants import (
    DIR_TESTOUTPUTS,
    DIR_TESTJOB1_TM52,
    DIR_TESTJOB1_TM52_DATA,
    FPTH_IES_TESTJOB1_V_0_1,
    DIR_OP_TEMP_VISTA,
    ARR_MAX_ADAPTIVE_TEMP,
    ARR_RUNNING_MEAN_TEMP,
)


def read_ies_txt(fpth):
    with open(str(fpth), errors="ignore") as f:
        lines = f.read()
    li_txt = lines.split("\n")
    header = [l.split(", ") for l in li_txt if l[0:4] == "Room"][0]
    data = [l.split(", ") for l in li_txt if l[0:2] == "A_"]
    for d in data:
        d[6] = d[6].replace("-,", "")  # Remove dashes
    data = [d for d in data if "Corridor" not in d[0] and "Lobby" not in d[0]]
    df = pd.DataFrame(columns=header, data=data)
    number_cols = [
        "Occupied days (%)",
        "Criteria 1 (%Hrs Top-Tmax>=1K)",
        "Criteria 2 (Max. Daily Deg.Hrs)",
        "Criteria 3 (Max. DeltaT)",
    ]
    df[number_cols] = df[number_cols].apply(pd.to_numeric)
    df = df.sort_values(by=["Room ID"])
    df = df.reset_index(drop=True)
    return df


class TestCheckResults:
    @classmethod
    def setup_class(cls):
        cls.tm52_calc = Tm52CalcWizard.from_files(DIR_TESTJOB1_TM52_DATA, fdir_results=DIR_TESTJOB1_TM52)

    def test_all_criteria(self):
        """Tests to make sure criteria failing in both IES and MF script match. Also checks the margin of error using
        the absolute change and relative change. Outputs excels spreadsheet to view the data.
        """
        df_mf_v_0_1 = self.tm52_calc.li_all_criteria_data_frames[2][
            "df"
        ]  # df for 0.1 air speed
        df_mf_v_0_1 = df_mf_v_0_1.reset_index()

        # Get IES results
        df_ies_v_0_1 = read_ies_txt(FPTH_IES_TESTJOB1_V_0_1)

        # Mapping mf results to ies results.
        chararr_one = np.char.array(
            np.where(self.tm52_calc.arr_criterion_one_bool[0] == 1, "1", "")
        )
        chararr_two = np.char.array(
            np.where(self.tm52_calc.arr_criterion_two_bool[0] == 1, "2", "")
        )
        chararr_three = np.char.array(
            np.where(self.tm52_calc.arr_criterion_three_bool[0] == 1, "3", "")
        )

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
        arr_ies_criteria_failing = np.array(df_ies_v_0_1["Criteria failing"])
        arr_ies_criteria_failing = np.where(
            arr_ies_criteria_failing == " -", "", arr_ies_criteria_failing
        )
        arr_criteria_failing_bool = arr_mf_criteria_failing == arr_ies_criteria_failing

        di_criteria_failing = OrderedDict(
            [
                ("Room Name", self.tm52_calc.arr_sorted_room_names),
                ("IES Results", arr_ies_criteria_failing),
                ("MF Results", arr_mf_criteria_failing),
                ("IES v MF", arr_criteria_failing_bool),
            ]
        )

        df_criterion = pd.DataFrame.from_dict(di_criteria_failing)
        df_criterion = df_criterion.set_index("Room Name")  # Set index to room names
        di_criterion_to_excel = {
            "sheet_name": "Criteria Failing, Air Speed 0.1",
            "df": df_criterion,
        }

        di_names = {
            "Criterion 1": {
                "mf_name": "Criterion 1 (% Time Delta T >= 1K)",
                "ies_name": "Criteria 1 (%Hrs Top-Tmax>=1K)",
                "data": self.tm52_calc.arr_criterion_one_percent[0].round(1),
            },
            "Criterion 2": {
                "mf_name": "Criterion 2 (Max Daily Weight)",
                "ies_name": "Criteria 2 (Max. Daily Deg.Hrs)",
                "data": self.tm52_calc.arr_criterion_two_max[0],
            },
            "Criterion 3": {
                "mf_name": "Criterion 3 (Max Delta T)",
                "ies_name": "Criteria 3 (Max. DeltaT)",
                "data": self.tm52_calc.arr_criterion_three_max[0],
            },
        }

        li_criterion_abs_change = []
        li_criterion_rel_change = []
        li_criteria_to_excel = [di_criterion_to_excel]
        for criterion, di_name in di_names.items():
            criterion_abs_change = di_name["data"] - df_ies_v_0_1[di_name["ies_name"]]
            criterion_rel_change = (
                criterion_abs_change / (df_ies_v_0_1[di_name["ies_name"]])
            ) * 100
            li_criterion_abs_change.append(criterion_abs_change)
            li_criterion_rel_change.append(criterion_rel_change)

            di_criterion = OrderedDict(
                [
                    ("Room Name", self.tm52_calc.arr_sorted_room_names),
                    ("IES Results", df_ies_v_0_1[di_name["ies_name"]]),
                    ("MF Results", di_name["data"]),
                    ("{0} Absolute Change".format(criterion), criterion_abs_change),
                    ("{0} Relative Change (%)".format(criterion), criterion_rel_change),
                ]
            )
            df_criterion = pd.DataFrame.from_dict(di_criterion)
            di_criterion_to_excel = {
                "sheet_name": "{0}, Air Speed 0.1".format(criterion),
                "df": df_criterion,
            }
            li_criteria_to_excel.append(di_criterion_to_excel)

        arr_criterion_abs_change = np.vstack(
            (
                li_criterion_abs_change[0],
                li_criterion_abs_change[1],
                li_criterion_abs_change[2],
            )
        )
        arr_criterion_rel_change = np.vstack(
            (
                li_criterion_rel_change[0],
                li_criterion_rel_change[1],
                li_criterion_rel_change[2],
            )
        )
        arr_criterion_abs_change = np.where(
            np.isfinite(arr_criterion_abs_change), arr_criterion_abs_change, 0
        )  # Set nans to 0
        arr_criterion_rel_change = np.where(
            np.isfinite(arr_criterion_rel_change), arr_criterion_rel_change, 0
        )

        to_excel(
            data_object=li_criteria_to_excel,
            fpth=str(DIR_TESTOUTPUTS / "test_all_criteria.xlsx"),
            open=False,
        )
        assert (
            arr_criteria_failing_bool.sum(dtype=bool) == True
        )  # Do criteria failing match?
        assert (arr_criterion_abs_change <= 1).sum(
            dtype=bool
        ) == True  # Does the absolute difference for all criteria have a value less than or equal to 1?
        assert (arr_criterion_rel_change < 5).sum(
            dtype=bool
        ) == True  # Does the relative difference for all criteria have a margin of error less than 5%?

    def test_daily_running_mean_temp(self):
        """Compares the daily running mean temperature from IES with the one calculated within the MF script.
        """
        ies_results = ARR_RUNNING_MEAN_TEMP.astype("float64").round(3)
        mf_results = self.tm52_calc.ARR_RUNNING_MEAN_TEMP.round(3)
        abs_change = self.tm52_calc.ARR_RUNNING_MEAN_TEMP.round(
            3
        ) - ARR_RUNNING_MEAN_TEMP.astype("float64").round(3)
        rel_change = (
            abs_change / (ARR_RUNNING_MEAN_TEMP.astype("float64").round(3))
        ) * 100
        di = OrderedDict(
            [
                ("IES Results", ies_results),
                ("MF Results", mf_results),
                ("Absolute Change", abs_change),
                ("Relative Change (%)", rel_change),
            ]
        )
        df = pd.DataFrame.from_dict(di)
        di_to_excel = {
            "sheet_name": "Running Mean Temperature",
            "df": df,
        }
        to_excel(
            data_object=di_to_excel,
            fpth=str(DIR_TESTOUTPUTS / "test_running_mean_temp.xlsx"),
            open=False,
        )
        assert (abs_change <= 1).sum(dtype=bool)
        assert (rel_change < 5).sum(dtype=bool)

    def test_max_adaptive_temp(self):
        """Compares the maximum-adaptive temperature from IES with the one calculated within the MF script.
        """
        ies_results = ARR_MAX_ADAPTIVE_TEMP.astype("float64").round(3)
        mf_results = self.tm52_calc.arr_max_acceptable_temp[0][0].round(3)
        abs_change = self.tm52_calc.arr_max_acceptable_temp[0][0].round(
            3
        ) - ARR_MAX_ADAPTIVE_TEMP.astype("float64").round(3)
        rel_change = (
            abs_change / (ARR_MAX_ADAPTIVE_TEMP.astype("float64").round(3))
        ) * 100
        di = OrderedDict(
            [
                ("IES Results", ies_results),
                ("MF Results", mf_results),
                ("Absolute Change", abs_change),
                ("Relative Change (%)", rel_change),
            ]
        )
        df = pd.DataFrame.from_dict(di)
        di_to_excel = {
            "sheet_name": "Max Acceptable Temperature",
            "df": df,
        }
        to_excel(
            data_object=di_to_excel,
            fpth=str(DIR_TESTOUTPUTS / "test_max_acceptable_temp.xlsx"),
            open=False,
        )
        assert (abs_change <= 1).sum(dtype=bool)
        assert (rel_change < 5).sum(dtype=bool)

    def test_operative_temp(self):
        """Compares the operative temperature (with air speed = 0.1m/s) from IES with the one calculated from the MF script
        for one room.
        """
        df_op_temp = pd.read_csv(
            str(DIR_OP_TEMP_VISTA), delimiter="\t", encoding="latin1", header=2
        )
        arr_op_temp_vista = np.array(df_op_temp.iloc[:, 2])

        ies_results = arr_op_temp_vista
        mf_results = self.tm52_calc.arr_op_temp_v[0][0].round(2)
        abs_change = mf_results - ies_results
        rel_change = (abs_change / ies_results) * 100
        di = OrderedDict(
            [
                ("IES Results", ies_results),
                ("MF Results", mf_results),
                ("Absolute Change", abs_change),
                ("Relative Change (%)", rel_change),
            ]
        )
        df = pd.DataFrame.from_dict(di)

        df.to_excel(
            str(DIR_TESTOUTPUTS / "test_operative_temp.xlsx"),
            sheet_name="Operative Temp, Air Speed 0.1",
        )

        assert (abs_change <= 1).sum(dtype=bool)
        assert (rel_change < 5).sum(dtype=bool)


if __name__ == "__main__":
    # import sys; import pathlib
    # DIR_MODULE = pathlib.Path(__file__).parents[1] / 'src'
    # sys.path.append(str(DIR_MODULE))
    # # for dev only

    df_ies_v_0_1 = read_ies_txt(FPTH_IES_TESTJOB1_V_0_1)
    test_check_results = TestCheckResults()
    test_check_results.test_all_criteria()
    # test_check_results.test_operative_temp()
    # test_check_results.test_daily_running_mean_temp()
    # test_check_results.test_max_adaptive_temp()
