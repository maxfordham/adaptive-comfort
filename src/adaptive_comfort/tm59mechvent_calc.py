"""
Calculation Procedure:

The calculation is performed using the Tm59MechVentCalcWizard class. 

The Tm59MechVentCalcWizard class takes two inputs:
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

    2. Run through the TM59 Mechanically Ventilated criteria
        Criterion one 
            No room can have the operative temperature exceed 26 degrees celsius during occupied hours for more than 3 percent of the 
            total annual occupied hours.

    3. Merge Data Frames
        Merges the data frames for project information, criterion percentage definitions, and the results for each 
        air speed.

    4. Output To Excel
        Outputs the dataframes to an excel spreadsheet in the project location.
"""


import pathlib
import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.equations import np_calc_op_temp
from adaptive_comfort.utils import create_paths, fromfile, create_df_from_criterion
from adaptive_comfort.constants import arr_air_speed
from adaptive_comfort.criteria_testing import criterion_tm59_mechvent

class Tm59MechVentCalcWizard:
    def __init__(self, inputs, fdir_results=None, on_linux=True):
        """Calculates the operative temperature, maximum adaptive temperature, and delta T for each air speed
        and produces the results in an excel spreadsheet. 

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            fdir_results (Path): Used to override project path to save elsewhere.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        self.factor = int(inputs.arr_air_temp.shape[1] / 8760)  # Find factor to hourly time-step array 
        self.op_temp(inputs)
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

    def run_criterion_one(self, arr_occupancy):
        """All occupied rooms should not exceed an operative temperature of 26 deg celsius

        Args:
            arr_occupancy (numpy.ndarray): The number of people for each room per reporting interval

        Returns:
            tuple: First element contains boolean values where True means exceedance.
                Second element contains the percentage of exceedance.
        """
        return criterion_tm59_mechvent(self.arr_op_temp_v, arr_occupancy)

    def run_criteria(self, inputs):
        """Runs all the criteria and collates them into a dictionary of data frames.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.arr_criterion_one_bool, self.arr_criterion_one_percent = self.run_criterion_one(inputs.arr_occupancy)

        self.di_criteria = {
            "Fixed Temp Criterion": {
                "Fixed Temp Criterion (Pass/Fail)": self.arr_criterion_one_bool,
                "Fixed Temp Criterion (% Hours Operative Temp > 26 Deg. Celsius)": self.arr_criterion_one_percent.round(2),
                },
        }

        self.arr_sorted_room_names = np.vectorize(inputs.di_room_id_name_map.get)(inputs.arr_room_ids_sorted)
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]

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
            ("Type of Analysis", 'CIBSE TM59 Mechanically Ventilated Assessment of overheating risk'),
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

    def create_df_criterion_definitions(self):
        """Creates a data frame describing the meaning of the criterion percentage values.

        Returns:
            pandas.DataFrame: Data frame of the criterion percentage definitions.
        """
        di_criterion_defs = {
            "Fixed Temp Criterion (% Hours Operative Temp > 26 Deg. Celsius)": "The percentage of hours where the operative temperature exceeds the threshold (26 degrees celsius) over the total annual hours.",
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
        li_columns_to_map = ["Fixed Temp Criterion (Pass/Fail)",]
        li_columns_sorted = [
                'Room Name',
                'Fixed Temp Criterion (Pass/Fail)',
                'Fixed Temp Criterion (% Hours Operative Temp > 26 Deg. Celsius)',
            ]
        di_bool_map = {True: "Fail", False: "Pass"}
        for speed in self.li_air_speeds_str:  # Loop through number of air speeds
            df_all_criteria = self.di_data_frame_criteria["Fixed Temp Criterion"][speed]
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
            fdir_tm59 = pathlib.PureWindowsPath(inputs.di_project_info['project_path']) / "mf_results" / "tm59mechvent"
        else:
            fdir_tm59 = fdir_results

        file_name = "TM59MechVent__{0}.xlsx".format(inputs.di_project_info['project_name'])
        fpth_results = fdir_tm59 / file_name
        if on_linux:
            output_dir = pathlib.Path(fdir_tm59.as_posix().replace("C:/", "/mnt/c/"))
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            output_path = fpth_results.as_posix().replace("C:/", "/mnt/c/")
        else:
            output_dir = pathlib.Path(str(fdir_tm59))
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            output_path = str(fpth_results)
        to_excel(data_object=self.li_all_criteria_data_frames, fpth=output_path, open=False)
        print("TM59 Mechanically Ventilated Calculation Complete.")
        print("Results File Path: {0}".format(str(fpth_results)))


if __name__ == "__main__":
    from constants import DIR_TESTJOB1_TM59MECHVENT
    paths = create_paths(DIR_TESTJOB1_TM59MECHVENT)
    tm59_input_data = fromfile(paths)
    tm59_calc = Tm59MechVentCalcWizard(tm59_input_data)