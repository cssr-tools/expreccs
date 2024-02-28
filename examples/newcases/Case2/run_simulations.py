# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "Grid_0_40m",
    "Grid_1_120m",
    "Grid_2_200m",
    "Grid_3_600m",
    "Grid_4_1000m",
    "Grid_5_5000m",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.txt -o {name} -m none -p yes & "
command += "wait"
os.system(command)
os.system("expreccs -c compare")
