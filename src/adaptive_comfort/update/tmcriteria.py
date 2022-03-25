import functools
import pathlib
import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.equations import deltaT, calculate_running_mean_temp_hourly, np_calc_op_temp, np_calculate_max_acceptable_temp
from adaptive_comfort.utils import np_round_half_up, repeat_every_element_n_times, create_paths, fromfile, create_df_from_criterion
from adaptive_comfort.constants import arr_air_speed
from adaptive_comfort.criteria_testing import criterion_time_of_exceedance, criterion_daily_weighted_exceedance, criterion_upper_limit_temperature, \
    criterion_bedroom_comfort, criterion_tm59_mechvent

def __init__(self, inputs):
        self.arr_sorted_room_names = np.vectorize(inputs.di_room_id_name_map.get)(inputs.arr_room_ids_sorted)
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]

class Tm52Criteria:
    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]
        self.arr_sorted_room_names = np.vectorize(inputs.di_room_id_name_map.get)(inputs.arr_room_ids_sorted)

        self.analysis_name = "TM52"
        arr_deltaT = np_round_half_up(self.arr_deltaT)
        self.arr_criterion_one_bool, self.arr_criterion_one_percent = criterion_time_of_exceedance(arr_deltaT, inputs.arr_occupancy, self.factor)
        self.arr_criterion_two_bool, self.arr_criterion_two_max = criterion_daily_weighted_exceedance(self.arr_deltaT, inputs.arr_occupancy)
        self.arr_criterion_three_bool, self.arr_criterion_three_max = criterion_upper_limit_temperature(self.arr_deltaT)
  
        self.di_criteria = {
            "Criterion 1": {
                "Criterion 1 (Pass/Fail)": self.arr_criterion_one_bool,
                "Criterion 1 (% Hours Delta T >= 1K)": self.arr_criterion_one_percent.round(2),
                },
            "Criterion 2": {
                "Criterion 2 (Pass/Fail)": self.arr_criterion_two_bool,
                "Criterion 2 (Max Daily Weight)": self.arr_criterion_two_max,
                },
            "Criterion 3": {
                "Criterion 3 (Pass/Fail)": self.arr_criterion_three_bool,
                "Criterion 3 (Max Delta T)": self.arr_criterion_three_max,
            }
        }

        # Constructing dictionary of data frames for each air speed.
        self.di_data_frame_criteria = {}
        for criterion, di_criterion in self.di_criteria.items():
            arr_rooms_sorted = self.arr_sorted_room_names
            arr_room_ids_sorted = inputs.arr_room_ids_sorted
            self.di_data_frame_criteria[criterion] = create_df_from_criterion(
                arr_rooms_sorted, 
                arr_room_ids_sorted,
                self.li_air_speeds_str, 
                di_criterion
            )

class Tm59Criteria:
    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.analysis_name = "TM59"
        arr_deltaT = np_round_half_up(self.arr_deltaT)
        bedrooms_indices = [i for i, bool_ in enumerate(self.arr_occupancy_bedroom_bool) if bool_ == True]  # Obtain indices where rooms are NOT bedrooms
        arr_op_temp_v_bedrooms = np.delete(self.arr_op_temp_v, bedrooms_indices, axis=1)  # Remove arrays in "room" axis which are not bedrooms based on their index           
        
        self.arr_criterion_a_bool, self.arr_criterion_a_percent = criterion_time_of_exceedance(arr_deltaT, inputs.arr_occupancy, self.factor)
        self.arr_criterion_b_bool, self.arr_criterion_b_percent, self.arr_criterion_b_value = criterion_bedroom_comfort(arr_op_temp_v_bedrooms, self.factor)

        self.di_criteria = {
            "Criterion A": {
                "Criterion A (Pass/Fail)": self.arr_criterion_a_bool,
                "Criterion A (% Hours Delta T >= 1K)": self.arr_criterion_a_percent.round(2),
                },
            "Criterion B": {
                "Criterion B (Pass/Fail)": self.arr_criterion_b_bool,
                "Criterion B (Hours Operative T > 26 Deg. C)": self.arr_criterion_b_value,
                "Criterion B (% Hours Operative T > 26 Deg. C)": self.arr_criterion_b_percent.round(2),
                },
        }

        self.arr_sorted_bedroom_names = np.vectorize(inputs.di_room_id_name_map.get)(self.arr_bedroom_ids)
        
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

class Tm59MechVentCriteria:
    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.analysis_name = "TM59MechVent"

        self.arr_criterion_one_bool, self.arr_criterion_one_percent = criterion_tm59_mechvent(self.arr_op_temp_v, inputs.arr_occupancy)

        self.di_criteria = {
            "Fixed Temp Criterion": {
                "Fixed Temp Criterion (Pass/Fail)": self.arr_criterion_one_bool,
                "Fixed Temp Criterion (% Hours Operative Temp > 26 Deg. Celsius)": self.arr_criterion_one_percent.round(2),
                },
        }

        # Constructing dictionary of data frames for each air speed.
        self.di_data_frame_criteria = {}
        for criterion, di_criterion in self.di_criteria.items():
            arr_rooms_sorted = self.arr_sorted_room_names
            arr_room_ids_sorted = inputs.arr_room_ids_sorted
            self.di_data_frame_criteria[criterion] = create_df_from_criterion(
                arr_rooms_sorted, 
                arr_room_ids_sorted,
                self.li_air_speeds_str, 
                di_criterion
            )   

class TmDataFrames:
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
            ("Type of Analysis", 'CIBSE TM52 Assessment of overheating risk'),
            ("Weather File", inputs.di_aps_info['weather_file_path']),
            ("Job Number", job_no),
            ("Reporting Interval", "{0} minutes".format(60/self.factor)),
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

    def create_df_criterion_definitions(self, di_criterion_defs):
        """Creates a data frame describing the meaning of the criterion percentage values.

        Returns:
            pandas.DataFrame: Data frame of the criterion percentage definitions.
        """
        df = pd.DataFrame.from_dict(di_criterion_defs, orient="index")
        df = df.rename(columns={0: "Definition"})
        return df.sort_index()

    def merge_dfs(self, inputs, di_data_frame_criteria, li_columns_to_map, li_columns_sorted):
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
            li_dfs = []
            for di_criterion in di_data_frame_criteria:
                df_criterion = di_criterion[speed]
                li_dfs.append(df_criterion)
            
            df_all_criteria = pd.DataFrame().join(li_dfs, on=["Room ID", "Room Name"], how="outer")
            # If a room fails any 2 of the 3 criteria then it is classed as a fail overall
            df_all_criteria["TM52 (Pass/Fail)"] = df_all_criteria.select_dtypes(include=['bool']).sum(axis=1) >= 2  # Sum only boolean columns (pass/fail columns)

            # Map true and false to fail and pass respectively
            for column in li_columns_to_map:
                df_all_criteria[column] = df_all_criteria[column].map(di_bool_map) 

            df_all_criteria = df_all_criteria.set_index("Room ID")  # Set index to room name
            di_all_criteria_data_frame = {
                "sheet_name": "Results, Air Speed {0}".format(speed),
                "df": df_all_criteria[li_columns_sorted],
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


