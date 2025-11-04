# SPDX-FileCopyrightText: 2024-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1713

"""
Script to run Case 1 in https://doi.org/10.1016/j.geoen.2025.213733.
"""

import os

os.system("expreccs -i basecase_pres.toml -o Case_1 -m all -p no & wait")
command = ""
for name in ["flux", "porvproj", "closed", "open"]:
    command += f"expreccs -i basecase_{name}.toml -o Case_1 -m site -p no & "
command += "wait"
os.system(command)
os.system("expreccs -i basecase_pres.toml -o Case_1 -m none -p yes")
