import sys
import pathlib
import numpy as np
import pandas as pd

DIR_GITMF = pathlib.Path(__file__).parents[2] / "git_mf"
DIR_IES_MODULE = DIR_GITMF / "IES"
sys.path.append(str(DIR_IES_MODULE))
# ^dev

from ies.IES_eng_calcs import calc_op_temp, additional_cooling

# arr_air_speed = np.array([[[0.1]], [[0.15]], [[0.2]], [[0.3]], [[0.4]], [[0.5]], [[0.6]], [[0.7]], [[0.8]]])

air_speed = np.array([[[0.15]]])
# Now testing with real data saved from test job to obtain operative temperature

# Get data
DIR_TEST_DATA = pathlib.Path("/mnt/c/engDev/git_mf/MF_examples/IES_Example_Models/TestJob1/")
PATH_AIR_TEMP_DATA = DIR_TEST_DATA / "data_rooms_air_temperature.csv"
PATH_MEAN_RADIANT_TEMP_DATA = DIR_TEST_DATA / "data_rooms_mean_radiant_temperature.csv"

arr_air_temp = np.genfromtxt(str(PATH_AIR_TEMP_DATA), delimiter=",", skip_header=1)
arr_mean_radiant_temp = np.genfromtxt(str(PATH_MEAN_RADIANT_TEMP_DATA), delimiter=",", skip_header=1)

# Calculate operative temperature for each room hourly throughout the year

def calculate_operative_temps(arr_air_temp, air_speed, arr_mean_radiant_temp):
    np_calc_op_temp = np.vectorize(calc_op_temp)
    arr_t_op_v = np_calc_op_temp(
        arr_air_temp,
        air_speed,
        arr_mean_radiant_temp
        )
    return arr_t_op_v




if __name__ == "__main__":
    arr_op_temp = calculate_operative_temps(arr_air_temp, air_speed, arr_mean_radiant_temp)
    print(arr_op_temp)


# See where temperature exceeds 26 degrees celsius
# threshold_temp = 26
# arr_threshold_exceedance = arr_t_op_v > threshold_temp

# get_comfort_temp = np.vectorize(additional_cooling)
# arr_comfort_temps = get_comfort_temp(air_speed)
# print(arr_comfort_temps)
