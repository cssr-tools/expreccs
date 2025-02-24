# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Script to run Case 4 in https://doi.org/10.1016/j.geoen.2025.213733
"""

import os

os.system("expreccs -i complexity.toml -o Case_4 -m all -p yes")
