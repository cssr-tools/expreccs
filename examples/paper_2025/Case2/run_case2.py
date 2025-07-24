# SPDX-FileCopyrightText: 2024-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to run Case 2 in https://doi.org/10.1016/j.geoen.2025.213733
"""

import os

NAMES = [
    "grid_0_40m",
    "grid_1_120m",
    "grid_2_200m",
    "grid_3_600m",
    "grid_4_1000m",
    "grid_5_5000m",
]
COMMAND = ""
for i, name in enumerate(NAMES):
    COMMAND += f"expreccs -i {name}.toml -o {name} -m all -p no & "
COMMAND += "wait"
os.system(COMMAND)
os.system("expreccs -c compare")
