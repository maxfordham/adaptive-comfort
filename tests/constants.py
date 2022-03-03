import pathlib
import numpy as np

DIR_TESTS = pathlib.Path(__file__).parent
DIR_TESTJOB1_TM52 = DIR_TESTS / "testmodels" / "TestJob1" / "mf_results" / "tm52" / "data"
DIR_TESTDATA = DIR_TESTS / "testdata"
FPTH_IES_TESTJOB1_V_0_1 = DIR_TESTDATA / "tm52_vista_pro" / "ies_TestJob1_TM52_0_1.csv" 
FPTH_IES_TESTJOB1_V_0_5 = DIR_TESTDATA / "tm52_vista_pro" / "ies_TestJob1_TM52_0_5.csv"

arr_max_adaptive_temp = np.load(str(DIR_TESTJOB1_TM52 / "arr_max_adaptive_temp.npy"))
arr_running_mean_temp = np.load(str(DIR_TESTJOB1_TM52 / "arr_running_mean_temp.npy"))
# arr_operative_temp = np.load(str(DIR_TESTJOB1_TM52 / "arr_operative_temp.npy"))