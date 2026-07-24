# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0103

"""Script to generate Table 3 in ecmor2026_Landa-Marban"""

import subprocess
from pathlib import Path

import numpy as np
from opm.io.ecl import EclFile as OpmFile

text = "model, #active cells, # connections with T > 0, Run time [h], Error (global)\n"

for model in [
    "FILLED",
    "STANDARD_COARSENED",
    "DUAL_VERTICAL_TF_COARSENED",
    "DUAL_NO_VERTICAL_TF_COARSENED",
]:
    grid = OpmFile(f"results/{model}_MODEL.EGRID")
    init = OpmFile(f"results/{model}_MODEL.INIT")

    tranx = np.array(init["TRANX"])
    trany = np.array(init["TRANY"])
    tranz = np.array(init["TRANZ"])

    ntranx = np.count_nonzero(tranx > 0)
    ntrany = np.count_nonzero(trany > 0)
    ntranz = np.count_nonzero(tranz > 0)
    nnnc = len(grid["NNC2"])

    with open(f"results/{model}_MODEL.DBG", "r", encoding="utf8") as f:
        for line in reversed(f.readlines()):
            if line.startswith("Simulation time:"):
                sim_time = float(line.split(":")[1].replace("s", "").strip())
                break
    if model != "FILLED":
        dual = "" if model == "STANDARD_COARSENED" else "-dual 0,1 "
        plopm = (
            f"plopm -i 'results/FILLED_MODEL' "
            "-v 'pressure - 0pressure' -s ',,1:217 ,,1:5' "
            f"-diff results/{model}_MODEL "
            f"-save {model.lower()}_diff -m csv {dual}"
        )
        subprocess.run(plopm, shell=True, check=True)
        with open(f"{model.lower()}_diff.csv", "r", encoding="utf8") as file:
            values = np.array([float(line.strip()) for line in file if line.strip()])
        error = f"{np.sum(np.abs(values)/len(values)):.2f}"
        Path(f"{model.lower()}_diff.csv").unlink()
    else:
        error = "-"
    total = nnnc + ntranx + ntrany + ntranz
    text += f"{model}, {len(tranx)}, {total}, {sim_time/3600:.2f}, {error}\n"

with open(
    "table3.csv",
    "w",
    encoding="utf8",
) as file:
    file.write(text)
