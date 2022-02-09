import pathlib
import numpy as np
from datetime import date

arr_air_speed = np.array([[[0.1]], [[0.15]], [[0.2]], [[0.3]], [[0.4]], [[0.5]], [[0.6]], [[0.7]], [[0.8]]])

# CONSTANTS
d0 = date(2010, 1, 1)
d1 = date(2010, 5, 1)
d2 = date(2010, 10, 1)
dt_may_start_day = d1 - d0
dt_sept_end_day = d2 - d0
may_start_hour = dt_may_start_day.days * 24
sept_end_hour = dt_sept_end_day.days * 24

# Test job 1
DIR_TESTJOB1 = pathlib.Path("/mnt/c/engDev/git_mf/MF_examples/IES_Example_Models/TestJob1/mf_results/tm52")