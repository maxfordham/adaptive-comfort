"""Tests for `adaptive_comfort` package."""

import pytest
import numpy as np
import numpy.ma as ma
import pandas as pd
from collections import OrderedDict

import sys
import pathlib

DIR_MODULE = pathlib.Path(__file__).parents[1] / "src"
sys.path.append(str(DIR_MODULE))
# for dev only

from adaptive_comfort.xlsx_templater import to_excel
from adaptive_comfort.utils import create_paths, fromfile
from adaptive_comfort.tm59_calc import Tm59CalcWizard
from adaptive_comfort.tm59mechvent_calc import Tm59MechVentCalcWizard
from .constants import DIR_TESTJOB1_TM59, DIR_TESTJOB1_TM59MECHVENT, DIR_TESTJOB1_TM59_DATA, DIR_TESTJOB1_TM59MECHVENT_DATA


class TestTm59:
    def test_run_tm59(self):
        """Test to make sure TM59 script runs
        """
        self.tm59_calc = Tm59CalcWizard.from_files(DIR_TESTJOB1_TM59_DATA, fdir_results=DIR_TESTJOB1_TM59)

    def test_run_tm59mechvents(self):
        """Test to make sure TM59 mech vent script runs
        """
        self.tm59mechvent_calc = Tm59MechVentCalcWizard.from_files(DIR_TESTJOB1_TM59MECHVENT_DATA, fdir_results=DIR_TESTJOB1_TM59MECHVENT)
