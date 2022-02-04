import pathlib
import numpy as np
import pandas as pd
from datetime import date

PATH_TESTJOB1 = pathlib.Path("/mnt/c/engDev/git_mf/MF_examples/IES_Example_Models/TestJob1/")

arr_op_temp = np.load(str(PATH_TESTJOB1 / "data_rooms_operative_temperature.npy"))
arr_max_adaptive_temp = np.load(str(PATH_TESTJOB1 / "data_rooms_max_adaptive_temperature.npy"))
arr_occupancy = np.load(str(PATH_TESTJOB1 / "data_rooms_occupancy.npy"))

# CONSTANTS
d0 = date(2010, 1, 1)
d1 = date(2010, 5, 1)
d2 = date(2010, 10, 1)
dt_may_start_day = d1 - d0
dt_sept_end_day = d2 - d0
may_start_hour = dt_may_start_day.days * 24
sept_end_hour = dt_sept_end_day.days * 24


def criterion_one(arr_op_temp, arr_max_adaptive_temp):
    """[summary]

    Args:
        arr_op_temp ([type]): [description]
        arr_max_adaptive_temp ([type]): [description]

    Returns:
        [type]: [description]
    """
    #TODO: Review numpy vector multiplication.
    # Delta Ts
    np_deltaT = np.vectorize(deltaT)
    arr_deltaT = np_deltaT(arr_op_temp, arr_max_adaptive_temp)
    arr_deltaT_may_to_sept_incl = arr_deltaT[:, :, may_start_hour:sept_end_hour]  # Obtaining deltaT between May and end of September
    arr_deltaT_bool = arr_deltaT_may_to_sept_incl >= 1  # Find where temperature is greater than 1K.
    arr_room_total_hours_exceedance = arr_deltaT_bool.sum(axis=2)  # Sum along last axis (hours)

    # Occupancy
    arr_occupancy_may_to_sept_incl = arr_occupancy[:, may_start_hour:sept_end_hour]
    arr_occupancy_bool = arr_occupancy_may_to_sept_incl > 0  # Hours where occupied
    arr_occupancy_3_percent = arr_occupancy_bool.sum(axis=1)*0.03 # axis 1 is hours
    print(arr_occupancy_3_percent)

    arr_criterion_one_bool = arr_room_total_hours_exceedance > arr_occupancy_3_percent
    print(arr_criterion_one_bool)

    arr_room_pass = arr_criterion_one_bool.sum(axis=0, dtype=bool)

    return arr_room_pass



# IES CALCS

def deltaT(op_temp, max_adaptive_temp):
    """Returns the difference between the operative temperature and the
    max-adaptive temperature.
    
    See CIBSE TM52: 2013, Page 13, Equation 9, Section 6.1.2

    Args:
        op_temp ([type]): [description]
        max_adaptive_temp ([type]): [description]

    Returns:
        [type]: [description]
    """
    return op_temp - max_adaptive_temp

if __name__ == "__main__":
    criterion_one(arr_op_temp, arr_max_adaptive_temp)

def test_criterion_one(save=True):
    """Obtaining criterion one data between May and September (Inclusive).

    Args:
        save (bool, optional): Whether to save data to csv. Defaults to True.

    Returns:
        np.ndarray: Returns numpy array of operative temperature of rooms.
    """


    
    
    # Getting total hours deltaT is greater than or equal to 1 degrees
    df_criterion_one_bool = df_criterion_one >= 1
    df_total_hours_exceedance = df_criterion_one_bool.sum()
    print(df_total_hours_exceedance)
    
    # Getting total occupied hours between May and September
    di_rooms_occupancy = get_occupancy(
        room_ids=li_room_ids, 
        results_file_reader=self.results_file_reader, 
        start_day=may_start_day,
        end_day=sept_end_day
        )
    df_occupancy_bool = pd.DataFrame.from_dict(di_rooms_occupancy) > 0  # At what hour in which room are there occupants.
    df_total_hours_occupied = df_occupancy_bool.sum()  # Sum occupancy hours for each room.
    df_3_percent_total_hours_occupied = df_total_hours_occupied*0.03
    print(df_3_percent_total_hours_occupied)
    
    df_criterion_pass_bool = df_total_hours_exceedance > df_3_percent_total_hours_occupied  # Compare rooms whether 
    print(df_criterion_pass_bool)  # If any True then that room has failed.
    
    return df_criterion_pass_bool