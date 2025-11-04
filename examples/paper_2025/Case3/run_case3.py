# SPDX-FileCopyrightText: 2024-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to run Case 3 in https://doi.org/10.1016/j.geoen.2025.213733
"""

import os

NAMES = [
    "everyday",
    "on_report_steps",
    "interpolation_in_time",
]
command = ""
for i, name in enumerate(NAMES):
    command += f"expreccs -i {name}.toml -m all -o {name} -p no & "
command += "wait"
os.system(command)
os.system("expreccs -c compare")
