#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to postprocess everest optimization (differential_evolution) studies.
"""

import argparse
import json
import csv
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

font = {"family": "normal", "weight": "normal", "size": 14}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 3.5,
        "legend.fontsize": 14,
        "lines.linewidth": 4,
        "axes.titlesize": 14,
        "axes.grid": True,
        "figure.figsize": (16, 8),
    }
)


def postprocessing():
    """Main function to postprocess everest results (differential_evolution)"""
    cmdargs = load_parser()
    dic = {"folder": f"{os.getcwd()}/{cmdargs['folder'].strip()}"}
    with open(f"{dic['folder']}/configuration.json", "r", encoding="utf-8") as f:
        dic = {**json.load(f), **dic}

    # Make the figures folder
    if not os.path.exists(f"{dic['folder']}/figures"):
        os.system(f"mkdir {dic['folder']}/figures")

    plot_optimization_results(dic)
    plt.rcParams.update({"axes.grid": False})
    plot_optimization_details(dic)
    find_optimal(dic)


def find_optimal(dic):
    """Find the well locations and folder for the 'optimal' obtained solution"""
    file = f"{dic['folder']}/everest_output/optimization_output/optimizer_output.txt"
    with open(file, "r", encoding="utf8") as file:
        optimal = -np.float16((file.readlines()[-1].strip()).split()[4])
    file = f"{dic['folder']}/everest_output/optimization_output/results.txt"
    dic["ind_batch"] = [0, 0]
    dic["ind_sim"] = [0, 0]
    batch_size = 0
    with open(file, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if len(row) > 0:
                if ((row[0].strip()).split()[0]).isdigit():
                    if int((row[0].strip()).split()[1]) == 0:
                        batch_size += 1
                    if np.float16((row[0].strip()).split()[2]) == optimal:
                        dic["ind_batch"][1] = int(
                            int((row[0].strip()).split()[0]) / batch_size
                        )
                        dic["ind_sim"][1] = (
                            int((row[0].strip()).split()[0])
                            - dic["ind_batch"][1] * batch_size
                        )
                        break
    for i, name in enumerate(["initial_guess", "optimal_solution"]):
        if not os.path.exists(f"{dic['folder']}/figures/{name}"):
            os.system(f"mkdir {dic['folder']}/figures/{name}")
        os.chdir(f"{dic['folder']}/figures/{name}")
        os.system(
            f"cp {dic['folder']}/everest_output/sim_output/"
            + f"batch_{dic['ind_batch'][i]}/geo_realization_0/simulation_"
            + f"{dic['ind_sim'][i]}/point_0.json ."
        )
        os.system(f"python3 {dic['folder']}/jobs/locations.py --mode post")


def read_results(dic):
    """Get the values over the optimization steps"""
    file = f"{dic['folder']}/everest_output/optimization_output/results.txt"
    n, dic["tot_eval"] = 0, 0
    with open(file, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if len(row) > 0:
                if ((row[0].strip()).split()[0]).isdigit():
                    dic["tot_eval"] += 1
                    if n != int((row[0].strip()).split()[1]):
                        for i in range(4):
                            dic[f"s{i}"].append(dic[f"x{i}"])
                            dic[f"x{i}"] = 0
                        n += 1
                    if float((row[0].strip()).split()[2]) == -1e20:
                        dic["x0"] += 1
                    elif float((row[0].strip()).split()[2]) == -1e10:
                        dic["x1"] += 1
                    elif float((row[0].strip()).split()[2]) < 0:
                        dic["x2"] += 1
                    else:
                        dic["x3"] += 1
    for i in range(4):
        dic[f"s{i}"].append(dic[f"x{i}"])


def plot_optimization_details(dic):
    """Plot the number of failed and succeed simulations over steps"""
    for i in range(4):
        dic[f"s{i}"] = []
        dic[f"x{i}"] = 0
    read_results(dic)
    colors = ["k", "m", "r", "g", "b"]
    names = [
        f"Failed (well on inactive region, no={sum(dic['s0'])})",
        f"Failed (stored mass under target, no={sum(dic['s1'])})",
        f"Failed (overpressure, no={sum(dic['s2'])})",
        f"Succeeded (no={sum(dic['s3'])})",
    ]
    fig, ax = plt.subplots()
    allw = 0
    for i in range(4):
        allw += np.array(dic[f"s{i}"])
    allw = np.array(allw)
    indc = np.argsort(allw)
    indc = range(len(allw))
    ax.bar(range(1,len(allw)+1), allw, color=colors[0], label=names[0])
    for i in range(3):
        allw -= np.array([dic[f"s{i}"][r] for r in indc])
        ax.bar(range(1,len(allw)+1), allw, color=colors[i + 1], label=names[i + 1])
    ax.set_title(f"Details on failed and succeed simulations (Total={dic['tot_eval']})")
    ax.set_ylabel(r"Occurence [\#]")
    ax.set_xlabel(r"Step [\#]")
    if len(allw)+1 < 20:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax.set_xticks(np.linspace(
                1,
                len(allw)+1,
                7,
            ))
    ax.legend()
    fig.savefig(f"{dic['folder']}/figures/details.png", bbox_inches="tight", dpi=900)


def plot_optimization_results(dic):
    """Plot the optimization values over steps"""
    optimization = []
    file = f"{dic['folder']}/everest_output/optimization_output/optimizer_output.txt"
    with open(file, "r", encoding="utf8") as file:
        for j, row in enumerate(csv.reader(file)):
            optimization.append(
                [j + 1, -float((row[0].strip()).split()[4])]
            )
    fig, axis = plt.subplots()
    axis.step(
        [step[0] for step in optimization],
        [value[1] for value in optimization],
        lw=5,
        color="b",
    )
    axis.set_title("Optimization results")
    axis.set_ylabel("min[(p$_{lim}$-p)/p$_{lim}$] [-]")
    axis.set_xlabel(r"Step [\#]")
    print(optimization)
    exit()
    if optimization[-1][0] + 1 < 20:
        axis.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        axis.set_xticks(np.linspace(
            0,
            optimization[-1][0] + 1,
            7,
        ))
    fig.savefig(
        f"{dic['folder']}/figures/optimization_results.png", bbox_inches="tight"
    )


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="Postprocess optimization"
        " studies using everest (differential_evolution). The figures"
        " are saved in the figures folder inside the selected folder."
    )
    parser.add_argument(
        "--folder",
        default="coarsened",
        help="The base name of the folder ('coarsened' by default).",
    )
    return vars(parser.parse_known_args()[0])


if __name__ == "__main__":
    postprocessing()
