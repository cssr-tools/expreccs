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
COMMAND = ""
for i, name in enumerate(NAMES):
    COMMAND += f"expreccs -i {name}.toml -m all -o {name} -p no & "
COMMAND += "wait"
os.system(COMMAND)
os.system("expreccs -c compare")
