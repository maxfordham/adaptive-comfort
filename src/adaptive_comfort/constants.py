import pathlib
import numpy as np
from datetime import date

arr_air_speed = np.array([[[0.1]], [[0.15]], [[0.2]], [[0.3]], [[0.4]], [[0.5]], [[0.6]], [[0.7]], [[0.8]]])

# CONSTANTS
DT_MAY_START_DAY = date(2010, 5, 1) - date(2010, 1, 1)
DT_SEPT_END_DAY = date(2010, 10, 1) - date(2010, 1, 1)
MAY_START_HOUR = DT_MAY_START_DAY.days * 24
SEPT_END_HOUR = DT_SEPT_END_DAY.days * 24

# Test job 1
DIR_TESTJOB1_TM52 = pathlib.Path(__file__).parents[2] / "tests" / "testmodels" / "TestJob1" / "mf_results" / "tm52"
DIR_TESTJOB1_TM59 = pathlib.Path(__file__).parents[2] / "tests" / "testmodels" / "TestJob1" / "mf_results" / "tm59"
DIR_TESTJOB1_TM59MECHVENT = pathlib.Path(__file__).parents[2] / "tests" / "testmodels" / "TestJob1" / "mf_results" / "tm59mechvent"