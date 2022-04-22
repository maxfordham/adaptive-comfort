"""Miscellaneous functions used to support the calculation of TM52 and TM59 scripts.
"""

import pathlib
import functools
import numpy as np
import pandas as pd
from collections import OrderedDict

from adaptive_comfort.data_objs import Tm52InputPaths, Tm52InputData

def round_half_up(value):
    """If the decimal of value is between 0 and 0.5 then round down.
    Else, round up.

    Args:
        value (float): Value we would like to round

    Returns:
        float: Rounded value
    """
    if (value % 1) >= 0.5:
        rounded_value = np.ceil(value)
    else:
        rounded_value = np.floor(value)
    return rounded_value


np_round_half_up = np.vectorize(round_half_up)

def round_for_daily_weighted_exceedance(value):
    """Used for defining the weighing factor from delta T.
    If value is less than or equal to 0 then the value shall be set to 0.
    Else, round with round_half_up function.

    Args:
        value (float): Value we would like to round

    Returns:
        float: Rounded value
    """
    if value <= 0:
        rounded_value = 0.0
    else:
        rounded_value = round_half_up(value)
    return rounded_value

np_round_for_daily_weighted_exceedance = np.vectorize(round_for_daily_weighted_exceedance)

def mean_every_n_elements(arr, n=24, axis=1):
    """Take the mean every n elements within an array.

    Example::

        # For example, if the array had 4 elements, after running this function, with n=2,
        # the array would consist of 2 elements which would be the means for those
        # 2 element chunks.

        arr = np.array([1, 2, 3, 4])
        n = 2
        axis = 1
        np.reshape(arr, (-1, n)).mean(axis)
        >>> array([1.5, 3.5])


    This function is used to convert the time-step intervals of an array such as going
    from hourly intervals to daily.

    Args:
        arr (numpy.ndarray): Array containing floats or ints.
        n (int, optional): The number of elements we would like to calculate the mean of. Defaults to 24.
        axis (int, optional): Which axis we would like to apply the function to. Defaults to 1.

    Returns:
        numpy.ndarray: The new numpy array where the mean has been taken every n elements.
    """
    return np.reshape(arr, (-1, n)).mean(axis)


def sum_every_n_elements(arr, n=24, axis=1):
    """Take the sum every n elements within an array.

    Example::

        # For example, if the array had 4 elements, after running this function, with n=2,
        # the array would consist of 2 elements which would be the sums for those
        # 2 element chunks.

        arr = np.array([1, 2, 3, 4])
        n = 2
        axis = 1
        np.reshape(arr, (-1, n)).sum(axis)
        >>> array([3, 7])

    This function is used to calculate the daily weighted exceedance.

    Args:
        arr (numpy.ndarray): Array containing floats or ints.
        n (int, optional): The number of elements we would like to calculate the sum of. Defaults to 24.
        axis (int, optional): Which axis we would like to apply the function to. Defaults to 1.

    Returns:
        numpy.ndarray: The new numpy array where the sum has been taken every n elements.
    """
    return np.reshape(arr, (-1, n)).sum(axis)


def repeat_every_element_n_times(arr, n=24, axis=0):
    """Repeat each element within the array n times.

    Example::

        # For example, if the array had 2 elements, after running this function, with n=2,
        # the array would consist of 4 elements which would be the elements repeated twice.
        # The repeated elements are appended next to one another.

        arr = np.array([1, 2])
        n = 2
        axis = 0
        np.repeat(arr, n, axis)
        >>> array([1, 1, 2, 2])

    This function is used to convert the time-step intervals of an array such as going
    from daily intervals to hourly.

    Args:
        arr (numpy.ndarray): Array containing floats or ints.
        n (int, optional): How many times we would like repeat the elements within the array. Defaults to 24.
        axis (int, optional): Which axis we would like to apply the function to. Defaults to 0.

    Returns:
        numpy.ndarray: The new numpy array where each element is now repeated n times.
    """
    return np.repeat(arr, n, axis)

def filter_bedroom_comfort_one_day(arr, factor):
    """Take any time-step array for a day and return the time between 10pm and 7am.

    Args:
        arr (numpy.ndarray): any time-step array for a day

    Returns:
        numpy.ndarray: time-step array between hours 10pm to 7am
    """
    return np.concatenate([arr[:7*factor], arr[-2*factor:]])

def filter_bedroom_comfort_many_days(arr, factor, axis=1):
    """Takes a multiple time-step array for multiple days and returns the time between 10pm and 7am for each one of those days. 

    Args:
        arr (numpy.ndarray): time-step array for many days
        axis (int, optional): Axis to apply function over. Defaults to 1.

    Returns:
        numpy.ndarray: time-step array of time between 10pm to 7am for multiple days
    """
    arr_daily_split = np.reshape(arr, (-1, 24*factor))  # Split yearly arrays into daily arrays
    f = functools.partial(filter_bedroom_comfort_one_day, factor=factor)
    arr_bedroom_comfort_split = np.apply_along_axis(f, axis, arr_daily_split)
    arr_bedroom_comfort = np.concatenate(arr_bedroom_comfort_split).ravel()
    return arr_bedroom_comfort

def filter_bedroom_comfort_time(arr, factor, axis=2):
    """Takes a multiple time-step array for multiple days for multiple rooms and returns the time between 10pm and 7am 
    for each one of those days for each room. 

    Args:
        arr (numpy.ndarray): time-step array for many days for multiple rooms
        axis (int, optional): Axis to apply function over. Defaults to 2.

    Returns:
        numpy.ndarray: time-step array of time 10pm to 7am for multiple days for each room
    """
    f = functools.partial(filter_bedroom_comfort_many_days, factor=factor)
    return np.apply_along_axis(f, axis, arr)


def create_paths(fdir):
    """Create file paths for the input data from a given file directory.

    Args:
        fdir (str): File directory containing the npy files.

    Returns:
        Tm52InputPaths: Returns a class object containing the required paths.
    """
    paths = Tm52InputPaths()
    paths.fpth_project_info = pathlib.Path(fdir) / 'arr_project_info.npy'
    paths.fpth_aps_info = pathlib.Path(fdir) / 'arr_aps_info.npy'
    paths.fpth_weather_file_info = pathlib.Path(fdir) / 'arr_weather_file_info.npy'
    paths.fpth_room_ids_sorted = pathlib.Path(fdir) / 'arr_room_ids_sorted.npy'
    paths.fpth_room_ids_groups = pathlib.Path(fdir) / 'arr_room_ids_groups.npy'
    paths.fpth_room_id_name_map = pathlib.Path(fdir) / 'arr_room_id_name_map.npy'
    paths.fpth_air_temp = pathlib.Path(fdir) / 'arr_air_temp.npy'
    paths.fpth_mean_radiant_temp = pathlib.Path(fdir) / 'arr_mean_radiant_temp.npy'
    paths.fpth_occupancy = pathlib.Path(fdir) / 'arr_occupancy.npy'
    paths.fpth_dry_bulb_temp = pathlib.Path(fdir) / 'arr_dry_bulb_temp.npy'
    return paths


def fromfile(paths):
    """Obtain input data which is dumped by IES API.

    Args:
        paths (Tm52InputPaths): Created from create_paths function.

    Returns:
        dict: Contains key value pairs of the dumped data from IES.
            keys: arr_project_info, arr_aps_info, arr_weather_file_info, 
                arr_room_ids_sorted, arr_room_id_name_map, arr_air_temp, 
                arr_mean_radiant_temp, arr_occupancy, arr_dry_bulb_temp
    """
    di_input_data = {}
    for k, fpth in paths.__dict__.items():
        di_input_data[fpth.stem] = np.load(str(fpth))

    input_data = Tm52InputData()
    input_data.di_project_info = di_input_data["arr_project_info"].item()
    input_data.di_aps_info = di_input_data["arr_aps_info"].item()
    input_data.di_weather_file_info = di_input_data["arr_weather_file_info"].item()
    input_data.di_room_id_name_map = di_input_data["arr_room_id_name_map"].item()
    input_data.di_room_ids_groups = di_input_data["arr_room_ids_groups"].item()
    input_data.arr_room_ids_sorted = di_input_data["arr_room_ids_sorted"]
    input_data.arr_air_temp = di_input_data["arr_air_temp"]
    input_data.arr_mean_radiant_temp = di_input_data["arr_mean_radiant_temp"]
    input_data.arr_occupancy = di_input_data["arr_occupancy"]
    input_data.arr_dry_bulb_temp = di_input_data["arr_dry_bulb_temp"]

    return input_data


def create_df_from_criterion(arr_sorted_room_names, arr_sorted_room_ids, li_air_speeds_str, di_criterion):
    """Creates pandas data frame for a criterion.

    Args:
        arr_sorted_room_names (numpy.ndarray): Sorted room names
        arr_sorted_room_ids (numpy.ndarray): Sorted room IDs
        li_air_speeds_str (list): list of air speeds       
        di_criterion (dict): criterion data with column names
            Example:
                di_criterion = {
                    "Criterion A": {
                        "Criterion A (Pass/Fail)": arr_criterion_a_bool,
                        "Criterion A (% Hours Delta T >= 1K)": arr_criterion_a_percent.round(2),
                        }

    Returns:
        dict: dict of data frames for each air speed.
    """
    li_room_criterion = []
    for i, speed in enumerate(li_air_speeds_str):  # Loop through air speeds and add specified columns with data from di_criterion
        di = OrderedDict([
            ("Room Name", arr_sorted_room_names),
            ("Room ID", arr_sorted_room_ids), 
        ])
        for k, v in di_criterion.items():
            di[k] = v[i]
            
        li_room_criterion.append(di)

    columns = [name for name in li_room_criterion[0].keys()]  # Obtaining columns for data frame
    di_data_frames_criterion = {
        speed: pd.DataFrame(data, columns=columns) 
            for speed, data in zip(li_air_speeds_str, li_room_criterion)
        }  # Creating dictionary of data frames for each air speed
    return di_data_frames_criterion


def jobno_fromdir(dir):
    '''
    returns the job number from a given file directory

    Name: 

    Args: 
        dir (filepath): file-directory
    Returns: 
        job associated to file-directory
    '''
    string = dir
    string = string[4:]
    job_no=string[:4]
    return job_no


if __name__ == "__main__":
    from constants import DIR_TESTJOB1_TM52
    paths = create_paths(DIR_TESTJOB1_TM52)
    di_input_data = fromfile(paths)
    print("done")
