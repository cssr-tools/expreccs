# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "trollbase",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.txt -o Case_2a -m all -p yes & "
command += "wait"
os.system(command)
