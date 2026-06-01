# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1713

"""Script to run Case 1 in https://doi.org/10.1016/j.geoen.2025.213733"""

import subprocess
from pathlib import Path

whr = Path(__file__).resolve().parent

subprocess.run(
    f"expreccs -i {whr}/basecase_pres.toml -o {whr}/Case_1 -m all -p no & wait",
    shell=True,
    check=True,
)
command = ""
for name in ["flux", "porvproj", "closed", "open"]:
    command += (
        f"expreccs -i {whr}/basecase_{name}.toml -o {whr}/Case_1 -m site -p no & "
    )
command += "wait"
subprocess.run(command, shell=True, check=True)
subprocess.run(
    f"expreccs -i {whr}/basecase_pres.toml -o {whr}/Case_1 -m none -p all",
    shell=True,
    check=True,
)

files = [
    "Case_1_reference_saturation.png",
    "Case_1_reference_pressure.png",
    "Case_1_reference_watfluxi+.png",
    "Case_1_summary_PR_site_reference.png",
    "Case_1_distance_from_border.png",
    "Case_1_difference_site_pres_pressure.png",
    "Case_1_difference_site_pres_saturation.png",
    "Case_1_difference_site_pres_gasfluxi+.png",
    "Case_1_difference_site_flux_pressure.png",
    "Case_1_difference_site_flux_saturation.png",
    "Case_1_difference_site_flux_gasfluxi+.png",
    "Case_1_maximum_gasfluxi+_difference_over_time.png",
    "Case_1_maximum_pressure_difference_over_time.png",
]

for name in files:
    subprocess.run(
        f"cp {whr}/Case_1/postprocessing/{name} {whr}", shell=True, check=True
    )
