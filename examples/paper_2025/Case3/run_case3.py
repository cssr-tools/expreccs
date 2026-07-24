# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Script to run Case 3 in https://doi.org/10.1016/j.geoen.2025.213733"""

import os
import subprocess
from pathlib import Path

whr = Path(__file__).resolve().parent
cwd = os.getcwd()

NAMES = [
    "everyday",
    "on_report_steps",
    "interpolation_in_time",
]
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {whr}/{name}.toml -m all -o {whr}/{name} -p no & "
command += "wait"
subprocess.run(command, shell=True, check=True)
os.chdir(whr)
subprocess.run("expreccs -c compare", shell=True, check=True)
os.chdir(cwd)

files = ["compareeveryday_sensor_pressure_over_time.png"]

for name in files:
    subprocess.run(f"cp {whr}/compare/{name} {whr}", shell=True, check=True)
