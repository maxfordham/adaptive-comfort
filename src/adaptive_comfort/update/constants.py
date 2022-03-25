di_bool_map = {True: "Fail", False: "Pass"}

li_tm52_columns_to_map = [
    "Criterion 1 (Pass/Fail)",
    "Criterion 2 (Pass/Fail)",
    "Criterion 3 (Pass/Fail)",
    "TM52 (Pass/Fail)"
]
li_tm52_columns_sorted = [
    'Room Name', 
    'Criterion 1 (Pass/Fail)', 
    'Criterion 1 (% Hours Delta T >= 1K)',
    'Criterion 2 (Pass/Fail)',
    'Criterion 2 (Max Daily Weight)', 
    'Criterion 3 (Pass/Fail)',
    'Criterion 3 (Max Delta T)', 
    'TM52 (Pass/Fail)'
]
di_tm52_criterion_defs = {
    "Criterion 1 (% Hours Delta T >= 1K)": "The percentage of occupied hours where delta T equals or exceeds the threshold (1 kelvin) over the total occupied hours.",
    "Criterion 2 (Max Daily Weight)": "The maximum daily weight taken from the year.",
    "Criterion 3 (Max Delta T)": "The maximum delta T taken from the year.",
}