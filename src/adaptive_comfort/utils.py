import pathlib
import numpy as np

from data_objs import Tm52InputPaths, Tm52InputData

def round_half_up(value):
    """Rounds 

    Args:
        value (float): vValue we would like to round

    Returns:
        float: Rounded value
    """
    if (value % 1) >= 0.5:
        rounded_value = np.ceil(value)
    else:
        rounded_value = np.floor(value)
    return rounded_value


np_round_half_up = np.vectorize(round_half_up)

def round_for_criteria_two(value):
    if value <= 0:
        rounded_value = 0.0
    elif (value % 1) >= 0.5:
        rounded_value = np.ceil(value)
    else:
        rounded_value = np.floor(value)
    return rounded_value

np_round_for_criteria_two = np.vectorize(round_for_criteria_two)

def mean_every_n_elements(arr, n=24, axis=1):
    return np.reshape(arr, (-1, n)).mean(axis)


def sum_every_n_elements(arr, n=24, axis=1):
    return np.reshape(arr, (-1, n)).sum(axis)


def repeat_every_element_n_times(arr, n=24, axis=1):
    return np.repeat(arr, n, axis)


def create_paths(fdir):
    """Create paths for the input data from a given file directory.

    Args:
        fdir (str): [description]

    Returns:
        Tm52InputPaths: Returns a class object containing the required paths.
    """
    paths = Tm52InputPaths()
    paths.fpth_project_info = pathlib.Path(fdir) / 'arr_project_info.npy'
    paths.fpth_aps_info = pathlib.Path(fdir) / 'arr_aps_info.npy'
    paths.fpth_weather_file_info = pathlib.Path(fdir) / 'arr_weather_file_info.npy'
    paths.fpths_room_ids_sorted = pathlib.Path(fdir) / 'arr_room_ids_sorted.npy'
    paths.fpths_room_id_name_map = pathlib.Path(fdir) / 'arr_room_id_name_map.npy'
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
    input_data.arr_room_ids_sorted = di_input_data["arr_room_ids_sorted"]
    input_data.arr_air_temp = di_input_data["arr_air_temp"]
    input_data.arr_mean_radiant_temp = di_input_data["arr_mean_radiant_temp"]
    input_data.arr_occupancy = di_input_data["arr_occupancy"]
    input_data.arr_dry_bulb_temp = di_input_data["arr_dry_bulb_temp"]

    return input_data


if __name__ == "__main__":
    from constants import DIR_TESTJOB1
    paths = create_paths(DIR_TESTJOB1)
    di_input_data = fromfile(paths)
    print("done")