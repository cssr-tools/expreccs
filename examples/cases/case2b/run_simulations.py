# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "On_report_steps",
    "Interpolation_in_time",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.txt -o {name} -m all -p yes & "
command += "wait"
os.system(command)
os.system("expreccs -c compare")
