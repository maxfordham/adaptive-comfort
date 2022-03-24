"""
Calculation Procedure:

The calculation is performed using the Tm59CalcWizard class. 

The Tm59CalcWizard class takes two inputs:
    inputs:
        Tm52InputData class instance. Attributes within the class:
            - Project information
            - Aps information
            - Weather data
            - Room air temperature ("Air temperature" in IES Vista)
            - Room mean radiant temperature ("Mean radiant temperature" in IES Vista)
            - Room occupancy ("Number of people" in IES Vista)
            - Dry bulb temperature
            - Room names, IDs, and groups

        on_linux: 
            Boolean value based on whether the output path for the results needs to be given in linux or windows.

Outputs
    An excel spreadsheet containing the results in the project folder.

Process
    1. Calculate The Operative Temperature
        Calculate operative temperature for each room that we want to analyse.
        It'll do this for each air speed.

    2. Calculate The Maximum Acceptable Temperature
        Calculate the maximum acceptable temperature for each room that we want to analyse.
        It'll do this for each air speed. 

    3. Calculate Delta T
        Calculates changes in temperature for each room between the operative temperature and the maximum
        acceptable temperature.

    4. Run through the TM59 criteria
        Criterion one 
            For living rooms, kitchens, and bedrooms: No room can have delta T equal or exceed the threshold (1 kelvin) during occupied hours between May and September inclusive
            for more than 3 percent of the total occupied hours.
        Criterion two
            For bedrooms only: The operative temperature between 10pm and 7am must not exceed 26 degrees celsius for more than 1% of annual hours.

    5. Merge Data Frames
        Merges the data frames for project information, criterion percentage definitions, and the results for each 
        air speed.

    6. Output To Excel
        Outputs the dataframes to an excel spreadsheet in the project location.
"""

import functools
import pathlib
import numpy as np
import numpy.ma as ma
import pandas as pd
import datetime
from collections import OrderedDict

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.equations import deltaT, calculate_running_mean_temp_hourly, np_calc_op_temp, np_calculate_max_acceptable_temp
from adaptive_comfort.utils import repeat_every_element_n_times, create_paths, fromfile, mean_every_n_elements, filter_bedroom_comfort_time, np_round_half_up, \
    create_df_from_criterion
from adaptive_comfort.constants import arr_air_speed
from adaptive_comfort.criteria_testing import criterion_hours_of_exceedance, criterion_bedroom_comfort

class Tm59CalcWizard:
    def __init__(self, inputs, fdir_results=None, on_linux=True):
        """Calculates the operative temperature, maximum adaptive temperature, and delta T for each air speed
        and produces the results in an excel spreadsheet. 

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            fdir_results (Path): Used to override project path to save elsewhere.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        self.factor = int(inputs.arr_dry_bulb_temp / 8760)  # Find factor to hourly time-step array 
        self.bedroom_ids(inputs)
        self.op_temp(inputs)
        self.max_adaptive_temp(inputs)
        self.deltaT(inputs)
        self.run_criteria(inputs)
        self.merge_dfs(inputs)
        self.to_excel(inputs, fdir_results, on_linux)

    def bedroom_ids(self, inputs):
        """Obtains the room IDs for the bedrooms by seeing which rooms are occupied between the hours of 10pm and 7am.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        arr_occupancy_bedroom_filtered = filter_bedroom_comfort_time(inputs.arr_occupancy, self.factor, axis=1)
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
        cat_I_temp = 2
        cat_II_temp = 3  

        # For TM59 calculation use category 2, for rooms used by vulnerable occupants use category 1
        self.arr_max_adaptive_temp = np_calculate_max_acceptable_temp(arr_running_mean_temp, cat_II_temp, arr_air_speed)
        self.arr_max_adaptive_temp_vulnerable = np_calculate_max_acceptable_temp(arr_running_mean_temp, cat_I_temp, arr_air_speed)

        if self.arr_max_adaptive_temp.shape[2] != self.arr_op_temp_v.shape[2]:  # If max adaptive time step axis does not match operative temp time step then modify.
            n = int(self.arr_op_temp_v.shape[2]/self.arr_max_adaptive_temp.shape[2])
            f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
            self.arr_max_adaptive_temp = np.apply_along_axis(f, 2, self.arr_max_adaptive_temp)

    def deltaT(self, inputs):
        """Calculates the temperature difference between the operative temperature and the maximum
        adaptive temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        # Find indices where room is vulnerable so we can replace the max acceptable temp with correct values.
        li_vulnerable_idx = []
        for idx, room_id in enumerate(inputs.arr_room_ids_sorted):
            if room_id in inputs.di_room_ids_groups["TM59_VulnerableRooms"]:
                li_vulnerable_idx.append(idx)

        if li_vulnerable_idx:  # If vulnerable room group assigned to any rooms then edit max_adaptive_temp
            # Repeating arr_max_adaptive_temp so a max adaptive temp exists for each room. This is because the max acceptable temp
            # is now room specific depending on the group the room belongs to.
            arr_max_adaptive_temp = np.repeat(self.arr_max_adaptive_temp, len(inputs.arr_room_ids_sorted), axis=1)
            arr_max_adaptive_temp[:, li_vulnerable_idx, :] = np.repeat(self.arr_max_adaptive_temp_vulnerable, len(inputs.di_room_ids_groups["TM59_VulnerableRooms"]), axis=1)
        else:
            arr_max_adaptive_temp = self.arr_max_adaptive_temp

        self.arr_deltaT = deltaT(self.arr_op_temp_v, arr_max_adaptive_temp)

    def run_criterion_a(self, arr_occupancy):
        """Convert delta T and occupancy array so the reporting interval is hourly, round the values,
        and then run criterion one.

        Args:
            arr_occupancy (numpy.ndarray): The number of people for each room per reporting interval

        Returns:
            tuple: First element contains boolean values where True means exceedance.
                Second element contains the percentage of exceedance.
        """
        arr_deltaT = np_round_half_up(self.arr_deltaT)
        return criterion_hours_of_exceedance(arr_deltaT, arr_occupancy)

    def run_criterion_b(self):
        """Run CIBSE TM59 criterion two associated with bedroom comfort. 

        Returns:
            tuple: First element contains boolean values where True means exceedance.
                Second element contains the percentage of exceedance.
        """
        bedrooms_indices = [i for i, bool_ in enumerate(self.arr_occupancy_bedroom_bool) if bool_ == True]  # Obtain indices where rooms are NOT bedrooms
        arr_op_temp_v_bedrooms = np.delete(self.arr_op_temp_v, bedrooms_indices, axis=1)  # Remove arrays in "room" axis which are not bedrooms based on their index           
        return criterion_bedroom_comfort(arr_op_temp_v_bedrooms, self.factor)

    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        arr_criterion_a_bool, arr_criterion_a_percent = self.run_criterion_a(inputs.arr_occupancy)
        arr_criterion_b_bool, arr_criterion_b_percent, arr_criterion_b_value = self.run_criterion_b()

        self.di_criteria = {
            "Criterion A": {
                "Criterion A (Pass/Fail)": arr_criterion_a_bool,
                "Criterion A (% Hours Delta T >= 1K)": arr_criterion_a_percent.round(2),
                },
            "Criterion B": {
                "Criterion B (Pass/Fail)": arr_criterion_b_bool,
                "Criterion B (Hours Operative T > 26 Deg. C)": arr_criterion_b_value,
                "Criterion B (% Hours Operative T > 26 Deg. C)": arr_criterion_b_percent.round(2),
                },
        }

        self.arr_sorted_room_names = np.vectorize(inputs.di_room_id_name_map.get)(inputs.arr_room_ids_sorted)
        self.arr_sorted_bedroom_names = np.vectorize(inputs.di_room_id_name_map.get)(self.arr_bedroom_ids)
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]

        # Constructing dictionary of data frames for each air speed.
        self.di_data_frame_criteria = {}
        for criterion, di_criterion in self.di_criteria.items():
            if criterion == "Criterion A":
                arr_rooms_sorted = self.arr_sorted_room_names
                arr_room_ids_sorted = inputs.arr_room_ids_sorted
            else:
                arr_rooms_sorted = self.arr_sorted_bedroom_names
                arr_room_ids_sorted = self.arr_bedroom_ids

            self.di_data_frame_criteria[criterion] = create_df_from_criterion(
                arr_rooms_sorted, 
                arr_room_ids_sorted,
                self.li_air_speeds_str, 
                di_criterion
            )
    
    def create_df_project_info(self, inputs):
        """Creates a data frame displaying the project information.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.

        Returns:
            pandas.DataFrame: Data frame of the project information from the IES API.
        """
        if inputs.di_project_info['project_folder'].find("J:") != -1: # Get job number if J drive is a parent directory
            job_no = inputs.di_project_info['project_folder'][4:8]  # TODO: Won't work for linux
        else:
            job_no = ''

        di_project_info = OrderedDict([
            ("Type of Analysis", 'CIBSE TM59 Assessment of overheating risk'),
            ("Weather File", inputs.di_aps_info['weather_file_path']),
            ("Job Number", job_no),
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
            "Criterion A (% Hours Delta T >= 1K)": "The percentage of occupied hours where delta T equals or exceeds the threshold (1 kelvin) over the total occupied hours.",
            "Criterion B (% Hours Operative T > 26 Deg. C)": "The percentage of occupied hours in a bedroom where the operative temperature exceeds the threshold (26 degrees celsius) between 10pm and 7am over the total annual occupied hours between 10pm and 7am.",
            "Criterion B (Hours Operative T > 26 Deg. C)": "Number of hours where the operative temperature is strictly greater than 26 Deg. C." 
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
            "sheet_name": "Criterion Definitions",
            "df": self.create_df_criterion_definitions(),
        }

        self.li_all_criteria_data_frames = [di_project_info, di_criterion_defs]
        for speed in self.li_air_speeds_str:  # Loop through number of air speeds
            df_all_criteria = pd.merge(self.di_data_frame_criteria["Criterion A"][speed], self.di_data_frame_criteria["Criterion B"][speed], on=["Room ID", "Room Name"], how="left")

            # If a room fails both criteria then it has failed to pass TM59. Note that if room is not a bedroom then it won't be run through Criterion B, so we assume that the room passes.
            df_all_criteria["TM59 (Pass/Fail)"] = df_all_criteria.loc[:, ["Criterion A (Pass/Fail)", "Criterion B (Pass/Fail)"]].fillna(False).sum(axis=1) >= 1  # Sum only boolean columns (pass/fail columns) 
            
            # Map true and false to fail and pass respectively
            li_columns_to_map = [
                "Criterion A (Pass/Fail)",
                "Criterion B (Pass/Fail)",
                "TM59 (Pass/Fail)"
            ]
            di_bool_map = {True: "Fail", False: "Pass"}
            for column in li_columns_to_map:
                df_all_criteria[column] = df_all_criteria[column].map(di_bool_map) 

            # Add ForVulnerableOccupants column showing which rooms are in group TM59_VulnerableRooms
            df_all_criteria.insert(loc=2, column="Vulnerable Occupancy", value=df_all_criteria["Room ID"].isin(inputs.di_room_ids_groups["TM59_VulnerableRooms"]))

            df_all_criteria = df_all_criteria.set_index("Room ID")  # Set index to room name

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
            fdir_tm59 = pathlib.PureWindowsPath(inputs.di_project_info['project_path']) / "mf_results" / "tm59"
        else:
            fdir_tm59 = fdir_results

        file_name = "TM59__{0}.xlsx".format(inputs.di_project_info['project_name'])
        fpth_results = fdir_tm59 / file_name
        if on_linux:
            output_dir = pathlib.Path(fdir_tm59.as_posix().replace("C:/", "/mnt/c/"))
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            output_path = fpth_results.as_posix().replace("C:/", "/mnt/c/")
        else:
            output_dir = pathlib.Path(str(fdir_tm59))  # TODO: Test this
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            output_path = str(fpth_results)
        to_excel(data_object=self.li_all_criteria_data_frames, fpth=output_path, open=False)
        print("TM59 Calculation Complete.")
        print("Results File Path: {0}".format(str(fpth_results)))


if __name__ == "__main__":
    # import sys
    # sys.path.append(str(pathlib.Path(__file__).parents[1]))
    # ^dev import - copy to top when debugging

    from constants import DIR_TESTJOB1_TM59
    paths = create_paths(DIR_TESTJOB1_TM59)
    tm59_input_data = fromfile(paths)
    tm59_calc = Tm59CalcWizard(tm59_input_data)