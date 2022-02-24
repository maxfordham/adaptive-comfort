import pathlib
import numpy as np

DIR_TESTS = pathlib.Path(__file__).parent / "testdata"
DIR_TESTJOB1 = DIR_TESTS / "tm52"
FPTH_IES_TESTJOB1_V_0_1 = DIR_TESTJOB1 / "ies_TestJob1_TM52_0.1.csv"
FPTH_IES_TESTJOB1_V_0_5 = DIR_TESTJOB1 / "ies_TestJob1_TM52_0.5.csv"

arr_max_adaptive_temp = np.load(str(DIR_TESTJOB1 / "arr_max_adaptive_temp.npy"))
arr_running_mean_temp = np.load(str(DIR_TESTJOB1 / "arr_running_mean_temp.npy"))
arr_operative_temp = np.load(str(DIR_TESTJOB1 / "arr_operative_temp.npy"))