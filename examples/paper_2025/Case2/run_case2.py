# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Script to run Case 2 in https://doi.org/10.1016/j.geoen.2025.213733"""

import os
import subprocess
from pathlib import Path

whr = Path(__file__).resolve().parent
cwd = os.getcwd()

NAMES = [
    "grid_0_40m",
    "grid_1_120m",
    "grid_2_200m",
    "grid_3_600m",
    "grid_4_1000m",
    "grid_5_5000m",
]
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {whr}/{name}.toml -o {whr}/{name} -m all -p no & "
command += "wait"
subprocess.run(command, shell=True, check=True)
os.chdir(whr)
subprocess.run("expreccs -c compare", shell=True, check=True)
os.chdir(cwd)

files = [
    "comparegrid_0_40m_sensor_pressure_over_time.png",
    "comparegrid_0_40m_sensor_gasfluxi+_over_time.png",
]

for name in files:
    subprocess.run(f"cp {whr}/compare/{name} {whr}", shell=True, check=True)
