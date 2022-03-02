"""
Miscellaneous functions used to support the calculation of TM52 and TM59 scripts.
"""

import pathlib
import numpy as np
import pandas as pd

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



def filter_bedroom_comfort_one_day(arr):
    return np.concatenate([arr[:7], arr[-2:]])

def filter_bedroom_comfort_many_days(arr, axis=1):
    arr_daily_split = np.reshape(arr, (-1, 24))  # Split yearly arrays into daily arrays
    arr_bedroom_comfort_split = np.apply_along_axis(filter_bedroom_comfort_one_day, axis, arr_daily_split)
    arr_bedroom_comfort = np.concatenate(arr_bedroom_comfort_split).ravel()
    return arr_bedroom_comfort

def filter_bedroom_comfort_time(arr, axis=2):
    return np.apply_along_axis(filter_bedroom_comfort_many_days, axis, arr)


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


def create_df_from_criterion(arr_sorted_room_names, arr_sorted_room_ids, li_air_speeds_str, zip_criterion, str_criterion_name, str_value_col):
    str_criterion_pass_fail_col = "{0} (Pass/Fail)".format(str_criterion_name)
    li_room_criterion = [{
        "Room Name": arr_sorted_room_names,
        "Room ID": arr_sorted_room_ids, 
        str_criterion_pass_fail_col: arr_room[0],
        str_value_col: arr_room[1],
    } for arr_room in zip_criterion]

    di_data_frames_criterion = {
        speed: pd.DataFrame(data, columns=["Room Name", "Room ID", str_value_col, str_criterion_pass_fail_col]) 
            for speed, data in zip(li_air_speeds_str, li_room_criterion)
        }
    return di_data_frames_criterion


if __name__ == "__main__":
    from constants import DIR_TESTJOB1_TM52
    paths = create_paths(DIR_TESTJOB1_TM52)
    di_input_data = fromfile(paths)
    print("done")
