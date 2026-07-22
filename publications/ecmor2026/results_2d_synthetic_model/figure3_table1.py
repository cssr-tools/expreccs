# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0103,C0116,R1732

"""Script to generate Figure 3 and Table 1 in ecmor2026_Landa-Marban"""

import csv
import shutil
import subprocess
import itertools
from pathlib import Path
from collections import deque

import numpy as np
from mako.template import Template
from opm.io.ecl import ERst as OpmRestart

parallel_runs = 16
delete_results = True
restart_step = 11
pressure_index = 7
number_plot_extreme_cases = 8
pycopm_base_command = ["pycopm", "-t", "2", "-a", "max", "-z", "1:4"]
plopm_base_command = [
    "plopm",
    "-v",
    "fluxnum - 1",
    "-grid",
    "black,1e-2",
    "-o",
    "all_configurations",
    "-clabel",
    "Net 0, non-net 1",
    "-f",
    "8",
    "-remove",
    "1,1,1,1",
    "-x",
    "[5000,15000]",
    "-z",
    "0",
    "-d",
    "1.3,1.3",
]


def to_grid(line):
    return np.array(line).reshape(4, 4)


def canonical_form(x):
    variants = []
    variants.append(x)
    variants.append(np.flipud(x))
    variants.append(np.fliplr(x))
    variants.append(np.flipud(np.fliplr(x)))
    variants = [tuple(variant.flatten()) for variant in variants]
    return min(variants)


def is_connected_left_right_zero(matrix):
    if matrix is None or matrix.size == 0:
        return False
    rows = len(matrix)
    columns = len(matrix[0])
    queue = deque()
    visited = set()
    for row_index in range(rows):
        if matrix[row_index][0] == 0:
            queue.append((row_index, 0))
            visited.add((row_index, 0))
    while queue:
        row_index, column_index = queue.popleft()
        if column_index == columns - 1:
            return True
        for row_step, column_step in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = row_index + row_step
            new_column = column_index + column_step
            if (
                0 <= new_row < rows
                and 0 <= new_column < columns
                and matrix[new_row][new_column] == 0
                and (new_row, new_column) not in visited
            ):
                visited.add((new_row, new_column))
                queue.append((new_row, new_column))
    return False


def run_commands(commands):
    processes = [subprocess.Popen(command) for command in commands]
    for process in processes:
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code,
                process.args,
            )


def process_results(index):
    fine_restart = OpmRestart(f"configuration_{index}/CONFIGURATION_{index}.UNRST")
    coarse_restart = OpmRestart(f"configuration_{index}/CONFIGURATION_{index}_C.UNRST")
    dual_vertical_tf_restart = OpmRestart(
        f"configuration_{index}/CONFIGURATION_{index}_D.UNRST"
    )
    dual_no_vertical_tf_restart = OpmRestart(
        f"configuration_{index}/CONFIGURATION_{index}_DNOVTF.UNRST"
    )
    fine_delta = (
        fine_restart["PRESSURE", restart_step][pressure_index]
        - fine_restart["PRESSURE", 0][pressure_index]
    )
    coarse_delta = (
        coarse_restart["PRESSURE", restart_step][pressure_index]
        - coarse_restart["PRESSURE", 0][pressure_index]
    )
    dual_vertical_tf_delta = (
        dual_vertical_tf_restart["PRESSURE", restart_step][pressure_index]
        - dual_vertical_tf_restart["PRESSURE", 0][pressure_index]
    )
    dual_no_vertical_tf_delta = (
        dual_no_vertical_tf_restart["PRESSURE", restart_step][pressure_index]
        - dual_no_vertical_tf_restart["PRESSURE", 0][pressure_index]
    )
    standard_errors.append(fine_delta - coarse_delta)
    dual_vertical_tf_errors.append(fine_delta - dual_vertical_tf_delta)
    dual_no_vertical_tf_errors.append(fine_delta - dual_no_vertical_tf_delta)


def configuration_as_text(config):
    return " ".join(str(int(value)) for value in config)


def write_case_error_csv(filename, ordered_indices):
    with open(filename, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "case",
                "standard_error",
                "standard_absolute_error",
                "dual_vertical_tf_error",
                "dual_vertical_tf_absolute_error",
                "dual_no_vertical_tf_error",
                "dual_no_vertical_tf_absolute_error",
                "configuration",
            ]
        )
        for index in ordered_indices:
            writer.writerow(
                [
                    index,
                    f"{standard_errors[index]:.2e}",
                    f"{standard_absolute_errors[index]:.2e}",
                    f"{dual_vertical_tf_errors[index]:.2e}",
                    f"{dual_vertical_tf_absolute_errors[index]:.2e}",
                    f"{dual_no_vertical_tf_errors[index]:.2e}",
                    f"{dual_no_vertical_tf_absolute_errors[index]:.2e}",
                    configuration_as_text(configurations[index]),
                ]
            )


def write_error_summary_csv(
    filename,
    dual_vertical_tf_better_case,
    dual_vertical_tf_better_fractions,
    dual_no_vertical_tf_better_case,
    dual_no_vertical_tf_better_fractions,
):
    standard_max_index = int(np.argmax(standard_absolute_errors))
    dual_vertical_tf_max_index = int(np.argmax(dual_vertical_tf_absolute_errors))
    dual_no_vertical_tf_max_index = int(np.argmax(dual_no_vertical_tf_absolute_errors))
    with open(filename, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "method",
                "max_signed_error",
                "max_absolute_error",
                "case_with_max_absolute_error",
                "sum_absolute_error",
                "mean_absolute_error",
                "better_cases",
                "better_fraction",
            ]
        )
        writer.writerow(
            [
                "standard",
                f"{standard_errors[standard_max_index]:.2e}",
                f"{np.max(standard_absolute_errors):.2e}",
                standard_max_index,
                f"{np.sum(standard_absolute_errors):.2e}",
                f"{np.mean(standard_absolute_errors):.2e}",
                "nan",
                "nan",
            ]
        )
        writer.writerow(
            [
                "dual_vertical_tf",
                f"{dual_vertical_tf_errors[dual_vertical_tf_max_index]:.2e}",
                f"{np.max(dual_vertical_tf_absolute_errors):.2e}",
                dual_vertical_tf_max_index,
                f"{np.sum(dual_vertical_tf_absolute_errors):.2e}",
                f"{np.mean(dual_vertical_tf_absolute_errors):.2e}",
                dual_vertical_tf_better_case,
                f"{dual_vertical_tf_better_fractions:.2f}",
            ]
        )
        writer.writerow(
            [
                "dual_no_vertical_tf",
                f"{dual_no_vertical_tf_errors[dual_no_vertical_tf_max_index]:.2e}",
                f"{np.max(dual_no_vertical_tf_absolute_errors):.2e}",
                dual_no_vertical_tf_max_index,
                f"{np.sum(dual_no_vertical_tf_absolute_errors):.2e}",
                f"{np.mean(dual_no_vertical_tf_absolute_errors):.2e}",
                dual_no_vertical_tf_better_case,
                f"{dual_no_vertical_tf_better_fractions:.2f}",
            ]
        )


configurations = []
seen = set()

for row in itertools.product([0, 1], repeat=16):
    if sum(row) < 4:
        continue
    grid = np.array(row).reshape(4, 4)
    if not is_connected_left_right_zero(grid):
        continue
    canonical_configuration = canonical_form(grid)
    if canonical_configuration not in seen:
        seen.add(canonical_configuration)
        configurations.append(row)

# configurations = configurations[:16]
nsimulations = len(configurations)

if nsimulations == 0:
    raise ValueError("No configurations were generated.")

template = Template(filename="case.mako")
standard_errors: list[float] = []
dual_vertical_tf_errors: list[float] = []
dual_no_vertical_tf_errors: list[float] = []

for case_index, configuration in enumerate(configurations):
    variables = {"configuration": configuration}
    filled_template = template.render(**variables)
    configuration_directory = Path(f"configuration_{case_index}")
    configuration_directory.mkdir(exist_ok=True)
    with open(
        configuration_directory / f"CONFIGURATION_{case_index}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filled_template)

for batch_start in range(0, nsimulations, parallel_runs):
    flow_commands = []
    pycopm_coarse_commands = []
    pycopm_dual_vertical_tf_commands = []
    pycopm_dual_no_vertical_tf_commands = []
    coarse_flow_commands = []
    dual_vertical_tf_flow_commands = []
    dual_no_vertical_tf_flow_commands = []
    plopm_commands = []

    batch_indices = range(
        batch_start,
        min(batch_start + parallel_runs, nsimulations),
    )

    for case_index in batch_indices:
        flow_commands.append(
            [
                "flow",
                f"configuration_{case_index}/CONFIGURATION_{case_index}.DATA",
                f"--output-dir=configuration_{case_index}",
                "--relaxed-max-pv-fraction=0",
                "--enable-tuning=true",
            ]
        )

        pycopm_coarse_commands.append(
            pycopm_base_command
            + [
                "-i",
                f"configuration_{case_index}/CONFIGURATION_{case_index}.DATA",
                "-o",
                f"configuration_{case_index}",
                "-w",
                f"CONFIGURATION_{case_index}_C",
                "-l",
                "C",
            ]
        )

        pycopm_dual_vertical_tf_commands.append(
            pycopm_base_command
            + [
                "-i",
                f"configuration_{case_index}/CONFIGURATION_{case_index}.DATA",
                "-o",
                f"configuration_{case_index}",
                "-w",
                f"CONFIGURATION_{case_index}_D",
                "-l",
                "D",
                "-dual",
                "poro == 0.1",
            ]
        )

        pycopm_dual_no_vertical_tf_commands.append(
            pycopm_base_command
            + [
                "-i",
                f"configuration_{case_index}/CONFIGURATION_{case_index}.DATA",
                "-o",
                f"configuration_{case_index}",
                "-w",
                f"CONFIGURATION_{case_index}_DNOVTF",
                "-l",
                "DNOVTF",
                "-dual",
                "poro == 0.1, vertical TF = 0",
            ]
        )

        coarse_flow_commands.append(
            [
                "flow",
                f"configuration_{case_index}/CONFIGURATION_{case_index}_C.DATA",
                "--relaxed-max-pv-fraction=0",
                "--enable-tuning=true",
            ]
        )

        dual_vertical_tf_flow_commands.append(
            [
                "flow",
                f"configuration_{case_index}/CONFIGURATION_{case_index}_D.DATA",
                "--relaxed-max-pv-fraction=0",
                "--enable-tuning=true",
            ]
        )

        dual_no_vertical_tf_flow_commands.append(
            [
                "flow",
                f"configuration_{case_index}/CONFIGURATION_{case_index}_DNOVTF.DATA",
                "--relaxed-max-pv-fraction=0",
                "--enable-tuning=true",
            ]
        )

        plopm_commands.append(
            plopm_base_command
            + [
                "-i",
                f"configuration_{case_index}/CONFIGURATION_{case_index}",
                "-save",
                str(case_index),
            ]
        )

    run_commands(flow_commands)
    run_commands(pycopm_coarse_commands)
    run_commands(pycopm_dual_vertical_tf_commands)
    run_commands(pycopm_dual_no_vertical_tf_commands)
    run_commands(coarse_flow_commands)
    run_commands(dual_vertical_tf_flow_commands)
    run_commands(dual_no_vertical_tf_flow_commands)
    run_commands(plopm_commands)

    for case_index in batch_indices:
        process_results(case_index)

        if delete_results:
            shutil.rmtree(f"configuration_{case_index}", ignore_errors=True)


standard_absolute_errors = np.abs(np.array(standard_errors))
dual_vertical_tf_absolute_errors = np.abs(np.array(dual_vertical_tf_errors))
dual_no_vertical_tf_absolute_errors = np.abs(np.array(dual_no_vertical_tf_errors))
standard_order = np.argsort(standard_absolute_errors)
dual_vertical_tf_order = np.argsort(dual_vertical_tf_absolute_errors)
dual_no_vertical_tf_order = np.argsort(dual_no_vertical_tf_absolute_errors)
dual_vertical_tf_better_cases = int(
    np.sum(dual_vertical_tf_absolute_errors < standard_absolute_errors)
)
dual_no_vertical_tf_better_cases = int(
    np.sum(dual_no_vertical_tf_absolute_errors < standard_absolute_errors)
)
dual_vertical_tf_better_fraction = (
    dual_vertical_tf_better_cases / nsimulations if nsimulations else float("nan")
)
dual_no_vertical_tf_better_fraction = (
    dual_no_vertical_tf_better_cases / nsimulations if nsimulations else float("nan")
)

write_case_error_csv(
    "standard_absolute_errors.csv",
    standard_order,
)

write_case_error_csv(
    "dual_vertical_tf_absolute_errors.csv",
    dual_vertical_tf_order,
)

write_case_error_csv(
    "dual_no_vertical_tf_absolute_errors.csv",
    dual_no_vertical_tf_order,
)

write_error_summary_csv(
    "table1_error_summary.csv",
    dual_vertical_tf_better_cases,
    dual_vertical_tf_better_fraction,
    dual_no_vertical_tf_better_cases,
    dual_no_vertical_tf_better_fraction,
)


def write_plot_case(index, model_folder):
    filled = template.render(**{"configuration": configurations[index]})
    confi_directory = Path(f"{model_folder}/configuration_{index}")
    confi_directory.mkdir(exist_ok=True)
    with open(
        confi_directory / f"CONFIGURATION_{index}.DATA",
        "w",
        encoding="utf8",
    ) as f:
        f.write(filled)


def run_plot_cases(case_indices, model_folder):
    commands = []
    for index in case_indices:
        write_plot_case(index, model_folder)
        commands.append(
            [
                "flow",
                f"{model_folder}/configuration_{index}/CONFIGURATION_{index}.DATA",
                f"--output-dir={model_folder}/configuration_{index}",
                "--relaxed-max-pv-fraction=0",
                "--enable-tuning=true",
            ]
        )
    run_commands(commands)


def format_exponential(value, precision=2):
    mantissa, exponent = f"{value:.{precision}e}".split("e")
    exponent = int(exponent)
    return f"{mantissa}e{exponent}"


def plot_title(index):
    return (
        f"{format_exponential(standard_absolute_errors[index], 1)}|"
        f"{format_exponential(dual_vertical_tf_absolute_errors[index], 1)}|"
        f"{format_exponential(dual_no_vertical_tf_absolute_errors[index], 1)}"
    )


def plot_error_extremes(model, case, order):
    model_folder = Path(f"{model}_extremes")
    model_folder.mkdir(exist_ok=True)
    if number_plot_extreme_cases < 1:
        raise ValueError("number_plot_extreme_cases must be at least 1.")
    if 2 * number_plot_extreme_cases > nsimulations:
        raise ValueError(
            "2 * number_plot_extreme_cases must be less than or equal to nsimulations "
            "to avoid duplicated cases."
        )
    lowest_error_cases = list(order[:number_plot_extreme_cases])
    highest_error_cases = list(order[-number_plot_extreme_cases:])
    plot_case_indices = lowest_error_cases + highest_error_cases
    run_plot_cases(plot_case_indices, str(model_folder))
    plopm_inputs = " ".join(
        f"{str(model_folder)}/configuration_{case_index}/CONFIGURATION_{case_index}"
        for case_index in plot_case_indices
    )
    low_titles = "  ".join(plot_title(case_index) for case_index in lowest_error_cases)
    high_titles = "  ".join(
        plot_title(case_index) for case_index in highest_error_cases
    )
    plot_titles = f"{low_titles}  {high_titles}"
    plot_width = 4 * number_plot_extreme_cases
    plot_height = 8
    plopm_command = [
        "plopm",
        "-i",
        plopm_inputs,
        "-t",
        plot_titles,
        "-subfigs",
        f"2,{number_plot_extreme_cases}",
        "-suptitle",
        "0",
        "-v",
        "fluxnum - 1",
        "-x",
        "[5000,15000]",
        "-z",
        "0",
        "-grid",
        "black,1e-2",
        "-cbsfax",
        "-1,0.0,0.0,0.0",
        "-remove",
        "1,1,0,0",
        "-d",
        f"{plot_width},{plot_height}",
        "-save",
        f"figure{case}_{model}_absolute_error_extremes_{number_plot_extreme_cases}",
    ]

    run_commands([plopm_command])
    if delete_results:
        shutil.rmtree(str(model_folder), ignore_errors=True)


plot_error_extremes("standard", "a", standard_order)
plot_error_extremes("dual_vertical_tf", "b", dual_vertical_tf_order)
plot_error_extremes("dual_no_vertical_tf", "a", dual_no_vertical_tf_order)
