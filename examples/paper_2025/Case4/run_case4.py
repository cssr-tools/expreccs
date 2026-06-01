# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Script to run Case 4 in https://doi.org/10.1016/j.geoen.2025.213733"""

import subprocess
from pathlib import Path

whr = Path(__file__).resolve().parent

subprocess.run(
    f"expreccs -i {whr}/complexity.toml -o {whr}/Case_4 -m all -p all",
    shell=True,
    check=True,
)

files = [
    "Case_4_reference_saturation.png",
    "Case_4_reference_pressure.png",
    "Case_4_regional_saturation.png",
    "Case_4_regional_pressure.png",
    "Case_4_site_pres_pressure.png",
    "Case_4_site_pres_saturation.png",
    "Case_4_difference_site_pres_pressure.png",
    "Case_4_difference_site_pres_saturation.png",
]

for name in files:
    subprocess.run(
        f"cp {whr}/Case_4/postprocessing/{name} {whr}", shell=True, check=True
    )
