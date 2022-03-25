import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parents[2]))

from adaptive_comfort.utils import create_paths, fromfile
from adaptive_comfort.update.tmcalc import TmCalc
from adaptive_comfort.update.tmcriteria import Tm52Criteria, TmDataFrames
from adaptive_comfort.update.constants import di_tm52_criterion_defs, li_tm52_columns_to_map, li_tm52_columns_sorted


class Tm52CalcWizard(TmCalc, Tm52Criteria, TmDataFrames):
    def __init__(self, inputs, di_criterion_defs, li_columns_to_map, li_columns_sorted, fdir_results=None, on_linux=True):
        """Calculates the operative temperature, maximum acceptable temperature, and delta T for each air speed
        and produces the results in an excel spreadsheet. 

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            fdir_results (Path): Used to override project path to save elsewhere.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        self.factor = int(inputs.arr_air_temp.shape[1] / 8760)  # Find factor to hourly time-step array 
        self.op_temp(inputs)
        self.max_acceptable_temp(inputs)
        self.deltaT(inputs)
        self.run_criteria(inputs)
        self.merge_dfs(inputs, self.di_data_frame_criteria, di_criterion_defs, li_columns_to_map, li_columns_sorted)
        self.to_excel(inputs, fdir_results, on_linux)


if __name__ == "__main__":
    from adaptive_comfort.constants import DIR_TESTJOB1_TM52
    paths = create_paths(DIR_TESTJOB1_TM52)  # Uses project information stored in numpy files saved
    tm52_input_data = fromfile(paths)
    Tm52CalcWizard(
        inputs=tm52_input_data, 
        di_criterion_defs=di_tm52_criterion_defs,
        li_columns_to_map=li_tm52_columns_to_map,
        li_columns_sorted=li_tm52_columns_sorted
        )