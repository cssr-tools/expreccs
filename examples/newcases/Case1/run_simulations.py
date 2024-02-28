# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "basecase",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.txt -o Case_1 -m all -p no & "
command += "wait"
os.system(command)
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}_flux.txt -o Case_1 -m site -p no & "
    command += f"expreccs -i {name}_porvproj.txt -o Case_1 -m site -p no & "
    command += f"expreccs -i {name}_closed.txt -o Case_1 -m site -p no & "
    command += f"expreccs -i {name}_open.txt -o Case_1 -m site -p no & "
command += "wait"
os.system(command)
command = f"expreccs -i {name}_open.txt -o Case_1 -m none -p yes"
os.system(command)
