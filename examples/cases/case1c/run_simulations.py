# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "complexity",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.txt -o Case_1c -m all -p no & "
command += "wait"
os.system(command)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}_flux.txt -o Case_1c -m site -p yes & "
command += "wait"
os.system(command)
