"""Main module."""
import pathlib
import numpy as np


def create_paths(fdir):
    """Create paths for the input data from a given file directory.

    Args:
        fdir (str): [description]

    Returns:
        Tm52InputPaths: Returns a class object containing the required paths.
    """
    paths = Tm52InputPaths()
    paths.fpth_project_info = pathlib.Path(fdir) / 'di_project_info.npy'
    paths.fpth_aps_info = pathlib.Path(fdir) / 'di_aps_info.npy'
    paths.fpth_weather_file_info = pathlib.Path(fdir) / 'di_weather_file_info.npy'
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
    """
    di = {}
    for k, fpth in paths.__dict__.items():
        di[fpth.stem] = np.load(str(fpth))
    return di


class Tm52InputPaths(object):
    fpth_project_info = None
    fpth_aps_info = None
    fpth_weather_file_info = None
    fpths_room_ids_sorted = None
    fpths_room_id_name_map = None
    fpth_air_temp = None
    fpth_mean_radiant_temp = None
    fpth_occupancy = None
    fpth_dry_bulb_temp = None

if __name__ == "__main__":
    from constants import DIR_TESTJOB1
    paths = create_paths(DIR_TESTJOB1)
    di_input_data = fromfile(paths)
    print("done")
