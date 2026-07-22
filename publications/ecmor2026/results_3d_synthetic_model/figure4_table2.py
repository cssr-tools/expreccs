# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0103,C0116

"""Script to generate Figure 4 and Table 2 in ecmor2026_Landa-Marban"""

import shutil
import subprocess
from pathlib import Path

import numpy as np
from mako.template import Template

shortest = [
    [
        [0, 1, 1, 1],
        [0, 1, 1, 1],
        [0, 1, 1, 1],
        [0, 0, 0, 0],
    ],
    [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 0],
    ],
    [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 0],
    ],
    [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 0],
    ],
]

intermediate = [
    [
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 1, 1, 0],
        [0, 0, 1, 1],
    ],
    [
        [1, 0, 1, 0],
        [1, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0],
    ],
    [
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [1, 1, 0, 0],
        [0, 1, 1, 0],
    ],
    [
        [1, 0, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 0, 1],
        [0, 1, 0, 0],
    ],
]

longest = [
    [
        [0, 0, 0, 0],
        [1, 1, 1, 0],
        [1, 1, 1, 0],
        [1, 1, 1, 0],
    ],
    [
        [1, 1, 1, 0],
        [1, 1, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
    ],
    [
        [0, 0, 0, 0],
        [0, 1, 1, 1],
        [0, 1, 1, 1],
        [0, 1, 1, 1],
    ],
    [
        [0, 1, 1, 1],
        [0, 1, 1, 1],
        [0, 1, 1, 1],
        [0, 0, 0, 0],
    ],
]


delete_results = False
parallel_runs = 3
restart_step = 11
pycopm_flags = "pycopm -t 2 -a max -z 1:4 "
cases = ["shortest", "intermediate", "longest"]

configurations = [
    np.array(shortest),
    np.array(intermediate),
    np.array(longest),
]

nsimulations = len(configurations)

standard_diff, standard_glob = [], []
dual_diff, dual_glob = [], []
dualnovtf_diff, dualnovtf_glob = [], []

Path("configurations").mkdir(exist_ok=True)

for configuration_index, configuration in enumerate(configurations):
    variables = {"configuration": configuration.flatten()}
    template = Template(filename="case.mako")
    filled_template = template.render(**variables)

    configuration_directory = Path(f"configuration_{configuration_index}")
    configuration_directory.mkdir(exist_ok=True)

    with open(
        configuration_directory / f"CONFIGURATION_{configuration_index}.DATA",
        "w",
        encoding="utf8",
    ) as f:
        f.write(filled_template)


def run_command(command):
    subprocess.run(command, shell=True, check=True)


def process_results(index, approach):
    """Sensor located at the first entry"""
    with open(f"configuration_{index}/{approach}.csv", "r", encoding="utf8") as file:
        values = np.array([float(line.strip()) for line in file if line.strip()])
    return values[0], np.sum(np.abs(values) / len(values))


for start_index in range(0, nsimulations, parallel_runs):
    flow_command = ""
    pycopm_coarse_command = ""
    pycopm_dualverticalTF_command = ""
    pycopm_dualnoverticalTF_command = ""
    coarse_flow_command = ""
    dual_flow_command = ""
    dualnovtf_flow_command = ""
    plopm_command = ""

    batch_indices = range(
        start_index,
        min(start_index + parallel_runs, nsimulations),
    )

    for case_index, letter in zip(batch_indices, ["a", "b", "c"]):
        flow_command += (
            f"flow configuration_{case_index}/CONFIGURATION_{case_index}.DATA "
            f"--output-dir=configuration_{case_index} "
            "--relaxed-max-pv-fraction=0 --enable-tuning=true & "
        )

        pycopm_coarse_command += (
            f"{pycopm_flags} "
            f"-i 'configuration_{case_index}/CONFIGURATION_{case_index}.DATA' "
            f"-o configuration_{case_index} "
            f"-w CONFIGURATION_{case_index}_C -l C & "
        )

        pycopm_dualverticalTF_command += (
            f"{pycopm_flags} "
            f"-i 'configuration_{case_index}/CONFIGURATION_{case_index}.DATA' "
            f"-o configuration_{case_index} "
            f"-w CONFIGURATION_{case_index}_D -l D "
            "-dual 'poro == 0.1' & "
        )

        pycopm_dualnoverticalTF_command += (
            f"{pycopm_flags} "
            f"-i 'configuration_{case_index}/CONFIGURATION_{case_index}.DATA' "
            f"-o configuration_{case_index} "
            f"-w CONFIGURATION_{case_index}_DNOVTF -l DNOVTF "
            "-dual 'poro == 0.1, vertical TF = 0' & "
        )

        coarse_flow_command += (
            f"flow configuration_{case_index}/CONFIGURATION_{case_index}_C.DATA "
            "--relaxed-max-pv-fraction=0 --enable-tuning=true & "
        )

        dual_flow_command += (
            f"flow configuration_{case_index}/CONFIGURATION_{case_index}_D.DATA "
            "--relaxed-max-pv-fraction=0 --enable-tuning=true & "
        )

        dualnovtf_flow_command += (
            f"flow configuration_{case_index}/CONFIGURATION_{case_index}_DNOVTF.DATA "
            "--relaxed-max-pv-fraction=0 --enable-tuning=true & "
        )
        plopm_command += (
            f"plopm -i configuration_{case_index}/CONFIGURATION_{case_index} "
            f"-m vtk -v fluxnum -save figure4{letter}_{cases[case_index]} & "
        )
        plopm_command += (
            f"plopm -i 'configuration_{case_index}/CONFIGURATION_{case_index}' "
            "-v 'pressure - 0pressure' -s ',,1:4 ,,1:1' "
            f"-diff configuration_{case_index}/CONFIGURATION_{case_index}_C "
            f"-save configuration_{case_index}/standard -m csv & "
        )
        plopm_command += (
            f"plopm -i 'configuration_{case_index}/CONFIGURATION_{case_index}' "
            "-v 'pressure - 0pressure' -s ',,1:4 ,,1:1' "
            f"-dual 0,1 -diff configuration_{case_index}/CONFIGURATION_{case_index}_D "
            f"-save configuration_{case_index}/dual -m csv & "
        )
        plopm_command += (
            f"plopm -i 'configuration_{case_index}/CONFIGURATION_{case_index}' "
            "-v 'pressure - 0pressure' -s ',,1:4 ,,1:1' "
            f"-dual 0,1 -diff configuration_{case_index}/CONFIGURATION_{case_index}_DNOVTF "
            f"-save configuration_{case_index}/dualnovtf -m csv & "
        )

    run_command(flow_command + "wait")
    run_command(pycopm_coarse_command + "wait")
    run_command(pycopm_dualverticalTF_command + "wait")
    run_command(pycopm_dualnoverticalTF_command + "wait")
    run_command(coarse_flow_command + "wait")
    run_command(dual_flow_command + "wait")
    run_command(dualnovtf_flow_command + "wait")
    run_command(plopm_command + "wait")

    for case_index in batch_indices:
        diff, glob = process_results(case_index, "standard")
        standard_diff.append(diff)
        standard_glob.append(glob)
        diff, glob = process_results(case_index, "dual")
        dual_diff.append(diff)
        dual_glob.append(glob)
        diff, glob = process_results(case_index, "dualnovtf")
        dualnovtf_diff.append(diff)
        dualnovtf_glob.append(glob)
        Path(f"CONFIGURATION_{case_index}-GRID.vtu").unlink()

        if delete_results:
            shutil.rmtree(
                f"configuration_{case_index}",
                ignore_errors=True,
            )

text = (
    "case, standard diff, standard global, dual (vertical TF) diff, dual (vertical TF) "
    "global, dual (no vertical TF) diff, dual (no vertical TF) global, configuration\n"
)

for case_index in range(nsimulations):
    standard_diff_value = f"{standard_diff[case_index]:.2e}"
    standard_glob_value = f"{standard_glob[case_index]:.2e}"
    dual_diff_value = f"{dual_diff[case_index]:.2e}"
    dual_glob_value = f"{dual_glob[case_index]:.2e}"
    dualnovtf_diff_value = f"{dualnovtf_diff[case_index]:.2e}"
    dualnovtf_glob_value = f"{dualnovtf_glob[case_index]:.2e}"

    text += (
        f"{case_index}, "
        f"{standard_diff_value}, "
        f"{standard_glob_value}, "
        f"{dual_diff_value}, "
        f"{dual_glob_value}, "
        f"{dualnovtf_diff_value}, "
        f"{dualnovtf_glob_value}, "
        f"{cases[case_index]}\n"
    )

with open(
    "table2.csv",
    "w",
    encoding="utf8",
) as f:
    f.write(text)
