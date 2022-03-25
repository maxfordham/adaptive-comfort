import functools
import numpy as np

from adaptive_comfort.equations import deltaT, calculate_running_mean_temp_hourly, np_calc_op_temp, np_calculate_max_acceptable_temp
from adaptive_comfort.utils import repeat_every_element_n_times
from adaptive_comfort.constants import arr_air_speed


class TmCalc:
    def __init__(self, inputs, include_vulnerable=False):
        """Calculates the operative temperature, maximum adaptive temperature, and delta T for each air speed
        and produces the results in an excel spreadsheet. 

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
            fdir_results (Path): Used to override project path to save elsewhere.
            on_linux (bool, optional): Whether running script in linux or windows. Defaults to True.
        """
        self.factor = int(inputs.arr_air_temp.shape[1] / 8760)  # Find factor to hourly time-step array 

    def op_temp(self, inputs):
        """Calculates the operative temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        self.arr_op_temp_v = np_calc_op_temp(
            inputs.arr_air_temp,
            arr_air_speed,
            inputs.arr_mean_radiant_temp
            )

    def max_acceptable_temp(self, inputs, include_vulnerable=False):
        """Calculates the maximum adaptive temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """

        arr_running_mean_temp = calculate_running_mean_temp_hourly(inputs.arr_dry_bulb_temp)
        cat_I_temp = 2
        cat_II_temp = 3  

        # For TM59 calculation use category 2, for rooms used by vulnerable occupants use category 1
        self.arr_max_acceptable_temp = np_calculate_max_acceptable_temp(arr_running_mean_temp, cat_II_temp, arr_air_speed)

        if include_vulnerable is True:
            self.arr_max_acceptable_temp_vulnerable = np_calculate_max_acceptable_temp(arr_running_mean_temp, cat_I_temp, arr_air_speed)

        if self.arr_max_acceptable_temp.shape[2] != self.arr_op_temp_v.shape[2]:  # If max adaptive time step axis does not match operative temp time step then modify.
            n = int(self.arr_op_temp_v.shape[2]/self.arr_max_acceptable_temp.shape[2])
            f = functools.partial(repeat_every_element_n_times, n=n, axis=0)
            self.arr_max_acceptable_temp = np.apply_along_axis(f, 2, self.arr_max_acceptable_temp)
            if include_vulnerable is True:
                self.arr_max_acceptable_temp_vulnerable = np.apply_along_axis(f, 2, self.arr_max_acceptable_temp_vulnerable)

    def deltaT(self, inputs, include_vulnerable=False):
        """Calculates the temperature difference between the operative temperature and the maximum
        adaptive temperature for each air speed.

        Args:
            inputs (Tm52InputData): Class instance containing the required inputs.
        """
        if include_vulnerable is True:
            # Find indices where room is vulnerable so we can replace the max acceptable temp with correct values.
            li_vulnerable_idx = []
            for idx, room_id in enumerate(inputs.arr_room_ids_sorted):
                if room_id in inputs.di_room_ids_groups["TM59_VulnerableRooms"]:
                    li_vulnerable_idx.append(idx)

            if li_vulnerable_idx:  # If vulnerable room group assigned to any rooms then edit max_adaptive_temp
                # Repeating arr_max_adaptive_temp so a max adaptive temp exists for each room. This is because the max acceptable temp
                # is now room specific depending on the group the room belongs to.
                arr_max_adaptive_temp = np.repeat(self.arr_max_adaptive_temp, len(inputs.arr_room_ids_sorted), axis=1)
                arr_max_adaptive_temp[:, li_vulnerable_idx, :] = np.repeat(self.arr_max_adaptive_temp_vulnerable, len(inputs.di_room_ids_groups["TM59_VulnerableRooms"]), axis=1)
            else:
                arr_max_adaptive_temp = self.arr_max_adaptive_temp
        else:
            arr_max_adaptive_temp = self.arr_max_adaptive_temp

        self.arr_deltaT = deltaT(self.arr_op_temp_v, arr_max_adaptive_temp)

    def air_speed(self):
        self.li_air_speeds_str = [str(float(i[0][0])) for i in arr_air_speed]
        self.arr_sorted_room_names = np.vectorize(inputs.di_room_id_name_map.get)(inputs.arr_room_ids_sorted)
