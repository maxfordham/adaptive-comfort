"""Class objects used to store the data in a structured manner so the data can be easily accessed in the class wizards.
"""


class Tm52InputData(object):
    di_project_info = None
    di_aps_info = None
    di_weather_file_info = None
    di_room_id_name_map = None
    di_room_ids_groups = None
    arr_room_ids_sorted = None
    arr_air_temp = None
    arr_mean_radiant_temp = None
    arr_occupancy = None
    arr_dry_bulb_temp = None


class Tm52InputPaths(object):
    fpth_project_info = None
    fpth_aps_info = None
    fpth_weather_file_info = None
    fpth_room_id_name_map = None
    fpth_room_ids_groups = None
    fpth_room_ids_sorted = None
    fpth_air_temp = None
    fpth_mean_radiant_temp = None
    fpth_occupancy = None
    fpth_dry_bulb_temp = None


class Tm52ExtraData(object):
    ARR_RUNNING_MEAN_TEMP = None
    ARR_MAX_ADAPTIVE_TEMP = None
    arr_operative_temp = None

