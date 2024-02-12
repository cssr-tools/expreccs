# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "Grid_0_50m",
    "Grid_1_100m",
    "Grid_2_200m",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.txt -o {name} -m all -p no & "
command += "wait"
os.system(command)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}_flux.txt -o {name} -m site -p yes & "
command += "wait"
os.system(command)
os.system("expreccs -c compare")
