"""
Calculation Procedure:

The calculation is performed using the Tm52CalcWizard class. 

The class takes two inputs:
    inputs:
        This is a Tm52InputData class instance. The data within the class:
            Project information
            Aps information
            Weather data
            Room air temperature ("Air temperature" in IES Vista)
            Room mean radiant temperature ("Mean radiant temperature" in IES Vista)
            Room occupancy ("Number of people" in IES Vista)
            Dry bulb temperature
            Room names and IDs

    on_linux: 
        Boolean value based on whether the output path for the results needs to be given in linux or windows.

Outputs
    An excel spreadsheet containing the results in the project folder.

Process
    1. Calculate The Operative Temperature
        Calculate operative temperature for each room that we want to analyse.
        It'll do this for each air speed. *Reference: See CIBSE Guide A, Equation 1.2, Part 1.2.2*

        .. math::
            T_{op} = \\frac{T_{a}\sqrt{10v} + T_{r}}{1 + \sqrt{10v}}

        where $T_{op}$ is the room operative temperature ($^\circ C$),
        $T_{a}$ is the indoor air temperature ($^\circ C$),
        $T_{r}$ is the mean radiant temperature ($^\circ C$),
        and $v$ is the summer (elevated) air speed ($m/s$)

    2. Calculate The Maximum Acceptable Temperature
        Calculate the maximum acceptable temperature for each room that we want to analyse.
        

        It'll do this for each air speed. *Reference: See CIBSE Guide A, Equation 1.2, Part 1.2.2*

    3. Calculate Delta T
        Calculates changes in temperature for each room between the operative temperature and the maximum
        acceptable temperature. *Reference: See CIBSE TM52: 2013, Page 13, Equation 9, Section 6.1.2*

    4. Run through the TM52 criteria
        Criterion one 
            No room can have delta T equal or excede the threshold (1 kelvin) during occupied hours for more than 3 percent of the 
            total occupied hours. *Reference: See CIBSE TM52: 2013, Page 13, Section 6.1.2a*
        Criterion two
            No room can have a daily weight greater than the threshold (6) where the daily weight is calculated from the reporting intervals
            within occupied hours. *Reference: See CIBSE TM52: 2013, Page 14, Section 6.1.2b*
        Criterion three 
            No room, at any point, can have a reading where delta T excedes the threshold (4 kelvin). *Reference: See CIBSE TM52: 2013, Page 14, Section 6.1.2c*

    5. Merge Data Frames
        Merges the data frames for project information, criterion percentage definitions, and the results for each 
        air speed.

    6. Output To Excel
        Outputs the dataframes to an excel spreadsheet in the project location.
"""

import functools
import pathlib
import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict

import sys
sys.path.append(str(pathlib.Path(__file__).parents[1]))
# # for dev only

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.equations import deltaT, calculate_running_mean_temp_hourly, np_calc_op_temp, np_calculate_max_acceptable_temp
from adaptive_comfort.utils import repeat_every_element_n_times, create_paths, fromfile, mean_every_n_elements, np_round_half_up
from adaptive_comfort.constants import arr_air_speed
from adaptive_comfort.criteria_testing import criterion_one, criterion_two, criterion_three

class Tm52CalcWizard:
    def __init__(self, inputs, fdir_results=None, on_linux=True):
        """Calculates the operative temperature, maximum acceptable temperature, and delta T for each air speed
        and produces the results in an excel spreadsheet. 

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        self.op_temp(inputs)
        self.max_acceptable_temp(inputs)
        self.deltaT()
        self.run_criteria(inputs)
        self.merge_dfs(inputs)
        self.to_excel(inputs, fdir_results, on_linux)

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

    def max_acceptable_temp(self, inputs):
        """Calculates the maximum acceptable temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.arr_running_mean_temp = calculate_running_mean_temp_hourly(inputs.arr_dry_bulb_temp)
        cat_II_temp = 3  # For TM52 calculation use category 2
        self.arr_max_acceptable_temp = np_calculate_max_acceptable_temp(self.arr_running_mean_temp, cat_II_temp, arr_air_speed)
        if self.arr_max_acceptable_temp.shape[2] != self.arr_op_temp_v.shape[2]:  # If max acceptable time step axis does not match operative temp time step then modify.
            n = int(self.arr_op_temp_v.shape[2]/self.arr_max_acceptable_temp.shape[2])
            f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
            self.arr_max_acceptable_temp = np.apply_along_axis(f, 2, self.arr_max_acceptable_temp)

    def deltaT(self):
        """Calculates the temperature difference between the operative temperature and the maximum
        acceptable temperature for each air speed.
        """
        self.arr_deltaT = deltaT(self.arr_op_temp_v, self.arr_max_acceptable_temp)

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
        
        return criterion_one(arr_deltaT_hourly, arr_occupancy_hourly)

    def run_criterion_two(self, arr_occupancy):
        """Runs criterion two.

        Args:
            arr_occupancy (numpy.ndarray): The number of people for each room per reporting interval

        Returns:
            tuple: First element contains boolean values where True means exceedance.
                Second element contains the percentage of exceedance.
        """
        return criterion_two(self.arr_deltaT, arr_occupancy)

    def run_criterion_three(self):
        """Runs criterion three.

        Returns:
            tuple: First element contains boolean values where True means exceedance.
                Second element contains the percentage of exceedance.
        """
        return criterion_three(self.arr_deltaT)

    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        arr_criterion_one_bool, arr_criterion_one_percent = self.run_criterion_one(inputs.arr_occupancy)
        arr_criterion_two_bool, arr_criterion_two_max = self.run_criterion_two(inputs.arr_occupancy)
        arr_criterion_three_bool, arr_criterion_three_max = self.run_criterion_three()

        di_criteria = {
            "Criterion 1": zip(arr_criterion_one_bool, arr_criterion_one_percent.round(1)),
            "Criterion 2": zip(arr_criterion_two_bool, arr_criterion_two_max),
            "Criterion 3": zip(arr_criterion_three_bool, arr_criterion_three_max),
        }

        # Constructing dictionary of data frames for each air speed.
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]
        self.arr_sorted_room_names = np.vectorize(inputs.di_room_id_name_map.get)(inputs.arr_room_ids_sorted)

        # TODO: Code below can be placed into a loop where parameters can be defined.
        self.di_data_frames_criteria = {}

        name = "Criterion 1"
        criterion_one_value_col_name = "{0} (% Hours Delta T >= 1K)".format(name)
        li_room_criterion_one = [{
            "Room Name": self.arr_sorted_room_names,
            "Room ID": inputs.arr_room_ids_sorted, 
            "{0} (Pass/Fail)".format(name): arr_room[0],
            criterion_one_value_col_name: arr_room[1],
            } for arr_room in di_criteria["Criterion 1"]]
        self.di_data_frames_criteria[name] = {
            speed: pd.DataFrame(data, columns=["Room Name", "Room ID", criterion_one_value_col_name, "{0} (Pass/Fail)".format(name)]) 
                for speed, data in zip(self.li_air_speeds_str, li_room_criterion_one)
            }

        name = "Criterion 2"
        criterion_two_value_col_name = "{0} (Max Daily Deg. Hours)".format(name)
        li_room_criterion_two = [{
            "Room Name": self.arr_sorted_room_names, 
            "Room ID": inputs.arr_room_ids_sorted, 
            "{0} (Pass/Fail)".format(name): arr_room[0],
            criterion_two_value_col_name: arr_room[1],
            } for arr_room in di_criteria["Criterion 2"]]
        self.di_data_frames_criteria[name] = {
            speed: pd.DataFrame(data, columns=["Room Name", "Room ID", criterion_two_value_col_name, "{0} (Pass/Fail)".format(name)]) 
                for speed, data in zip(self.li_air_speeds_str, li_room_criterion_two)
            }

        name = "Criterion 3"
        criterion_three_value_col_name = "{0} (Max Delta T)".format(name)
        li_room_criterion_three = [{
            "Room Name": self.arr_sorted_room_names, 
            "Room ID": inputs.arr_room_ids_sorted, 
            "{0} (Pass/Fail)".format(name): arr_room[0],
            criterion_three_value_col_name: arr_room[1],
            } for arr_room in di_criteria["Criterion 3"]]
        self.di_data_frames_criteria[name] = {
            speed: pd.DataFrame(data, columns=["Room Name", "Room ID", criterion_three_value_col_name, "{0} (Pass/Fail)".format(name)]) 
                for speed, data in zip(self.li_air_speeds_str, li_room_criterion_three)
            }


    def create_df_project_info(self, inputs):
        """Creates a data frame displaying the project information.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.

        Returns:
            pandas.DataFrame: Data frame of the project information from the IES API.
        """
        di_project_info = OrderedDict([
            ("Type of Analysis", 'CIBSE TM52 Assessment of overheating risk'),
            ("Weather File", inputs.di_aps_info['weather_file_path']),
            ("Job Number", inputs.di_project_info['project_folder'][4:8]),  # TODO: Review how job number is obtained.
            ("Analysed Spaces", str(len(inputs.arr_room_ids_sorted))),
            ("Analysed Air Speeds", self.li_air_speeds_str),
            ("Weather File Year", str(inputs.di_weather_file_info["year"])),
            ("Weather File - Time Zone", 'GMT+{:.2f}'.format(inputs.di_weather_file_info["time_zone"])),
            ("Longitude", "{:.2f}".format(inputs.di_weather_file_info['longitude'])),
            ("Latitude", "{:.2f}".format(inputs.di_weather_file_info['latitude'])),
            ("Date of Analysis", str(datetime.datetime.now())),
            ("IES_version", inputs.di_project_info['IES_version'])
        ])

        df = pd.DataFrame.from_dict(di_project_info, orient='index')
        df = df.rename(columns={0: "Information"})
        return df

    def create_df_criterion_definitions(self):
        """Creates a data frame describing the meaning of the criterion percentage values.

        Returns:
            pandas.DataFrame: Data frame of the criterion percentage definitions.
        """
        di_criterion_defs = {
            "Criterion 1 Percentage": ["The number of occupied hours where delta T equals or excedes the threshold (1 kelvin) over the total occupied hours."],
            "Criterion 2 Percentage": ["The number of days exceeding the daily weight of 6 over the total days per year."],
            "Criterion 3 Percentage": ["The number of readings where delta T excedes the threshold (4 kelvin) over the total number of readings."],
        }
        df = pd.DataFrame.from_dict(di_criterion_defs, orient="index")
        df = df.rename(columns={0: "Definition"})
        return df.sort_index()

    def merge_dfs(self, inputs):
        """Merge the project information, criterion percentage definitions, and criteria data frames within a list
        which will then be passed onto the to_excel method.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        # Project info
        di_project_info = {
            "sheet_name": "Project Information",
            "df": self.create_df_project_info(inputs),
        }

        # Obtaining criterion percentage defintions
        di_criterion_defs = {
            "sheet_name": "Criterion % Definitions",
            "df": self.create_df_criterion_definitions(),
        }

        self.li_all_criteria_data_frames = [di_project_info, di_criterion_defs]
        for speed in self.li_air_speeds_str:  # Loop through number of air speeds
            df_criteria_one_and_two = pd.merge(self.di_data_frames_criteria["Criterion 1"][speed], self.di_data_frames_criteria["Criterion 2"][speed], on=["Room Name", "Room ID"])
            df_all_criteria = pd.merge(df_criteria_one_and_two, self.di_data_frames_criteria["Criterion 3"][speed], on=["Room Name", "Room ID"])

            # If a room fails any 2 of the 3 criteria then it is classed as a fail overall
            df_all_criteria["TM52 (Pass/Fail)"] = df_all_criteria.select_dtypes(include=['bool']).sum(axis=1) >= 2  # Sum only boolean columns (pass/fail columns)

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
                "sheet_name": "Results, Air Speed {0}".format(speed),
                "df": df_all_criteria,
            }
            self.li_all_criteria_data_frames.append(di_all_criteria_data_frame)
    
    def to_excel(self, inputs, fdir_results, on_linux=True):
        """Output data frames to excel spreadsheet.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            fdir_results (Path): Override project path.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        if fdir_results is None:
            fdir_tm52 = pathlib.PureWindowsPath(inputs.di_project_info['project_path']) / "mf_results" / "tm52"
        else:
            fdir_tm52 = fdir_results
        file_name = "TM52__{0}.xlsx".format(inputs.di_project_info['project_name'])
        fpth_results = fdir_tm52 / file_name
        if on_linux:
            output_path = fpth_results.as_posix().replace("C:/", "/mnt/c/")
        else:
            output_path = str(fpth_results)
        to_excel(data_object=self.li_all_criteria_data_frames, fpth=output_path, open=False)
        print("TM52 Calculation Complete.")
        print("Results File Path: {0}".format(output_path))


if __name__ == "__main__":
    from constants import DIR_TESTJOB1
    paths = create_paths(DIR_TESTJOB1)
    tm52_input_data = fromfile(paths)
    tm52_calc = Tm52CalcWizard(tm52_input_data)