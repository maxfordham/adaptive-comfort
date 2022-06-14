import pathlib
import numpy as np

DIR_TESTS = pathlib.Path(__file__).parent
DIR_TESTJOB1 = DIR_TESTS / "testmodels" / "TestJob1"
DIR_TESTJOB1_TM52 = DIR_TESTJOB1 / "mf_results" / "tm52" / "data"
DIR_TESTJOB1_TM59 = DIR_TESTJOB1 / "mf_results" / "tm59" / "data"
DIR_TESTJOB1_TM59MECHVENT = DIR_TESTJOB1 / "mf_results" / "tm59mechvent" / "data"
DIR_TESTOUTPUTS = DIR_TESTS / "testoutputs"
DIR_OP_TEMP_VISTA = DIR_TESTOUTPUTS / "operative_temperature_from_vista.txt"
FPTH_IES_TESTJOB1_V_0_1 = DIR_TESTJOB1 / "vista" / "TestJob1_TM52_0.1.csv"

arr_max_adaptive_temp = np.load(str(DIR_TESTJOB1_TM52 / "arr_max_adaptive_temp.npy"))
arr_running_mean_temp = np.load(str(DIR_TESTJOB1_TM52 / "arr_running_mean_temp.npy"))
