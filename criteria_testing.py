import numpy as np
import pandas as pd
import pathlib

PATH_TESTJOB1 = pathlib.Path("/mnt/c/engDev/git_mf/MF_examples/IES_Example_Models/TestJob1/")

arr_op_temp = np.load(str(PATH_TESTJOB1 / "data_rooms_operative_temperature.npy"))
arr_max_adaptive_temp = np.load(str(PATH_TESTJOB1 / "data_rooms_max_adaptive_temperature.npy"))

def criterion_one(arr_op_temp, arr_max_adaptive_temp):
    np_deltaT = np.vectorize(deltaT)
    arr_deltaT = np_deltaT(arr_op_temp, arr_max_adaptive_temp)
    print(arr_deltaT)

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
    return max_adaptive_temp - op_temp