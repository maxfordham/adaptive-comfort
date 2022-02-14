class Tm52InputData(object):
    di_project_info = None
    di_aps_info = None
    di_weather_file_info = None
    di_room_id_name_map = None
    arr_room_ids_sorted = None
    arr_air_temp = None
    arr_mean_radiant_temp = None
    arr_occupancy = None
    arr_dry_bulb_temp = None

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

class Tm59InputData(Tm52InputData):
    arr_room_ids_vulnerable = None
