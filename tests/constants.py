import pathlib
import numpy as np

DIR_TESTS = pathlib.Path(__file__).parent
DIR_TESTJOB1 = DIR_TESTS / "testmodels" / "TestJob1"
DIR_TESTJOB1_TM52 = DIR_TESTJOB1 / "mf_results" / "tm52"
DIR_TESTJOB1_TM59 = DIR_TESTJOB1 / "mf_results" / "tm59"
DIR_TESTJOB1_TM59MECHVENT = DIR_TESTJOB1 / "mf_results" / "tm59mechvent"
DIR_TESTJOB1_TM52_DATA = DIR_TESTJOB1_TM52 / "data"
DIR_TESTJOB1_TM59_DATA = DIR_TESTJOB1_TM59 / "data"
DIR_TESTJOB1_TM59MECHVENT_DATA = DIR_TESTJOB1_TM59MECHVENT / "data"

DIR_TESTOUTPUTS = DIR_TESTS / "testoutputs"
DIR_OP_TEMP_VISTA = DIR_TESTOUTPUTS / "operative_temperature_from_vista.txt"
FPTH_IES_TESTJOB1_V_0_1 = DIR_TESTJOB1 / "vista" / "TestJob1_TM52_0.1.csv"

ARR_MAX_ADAPTIVE_TEMP = np.load(str(DIR_TESTJOB1_TM52_DATA / "arr_max_adaptive_temp.npy"))
ARR_RUNNING_MEAN_TEMP = np.load(str(DIR_TESTJOB1_TM52_DATA / "arr_running_mean_temp.npy"))
