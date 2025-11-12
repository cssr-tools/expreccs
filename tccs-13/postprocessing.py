#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to postprocess everest optimization (differential_evolution) studies.
"""

import argparse
import json
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
    dic = {"folder": os.path.abspath(cmdargs['folder'].strip())}
    with open(f"{dic['folder']}/configuration.json", "r", encoding="utf-8") as f:
        dic = {**json.load(f), **dic}

    # Make the figures folder
    if not os.path.exists(f"{dic['folder']}/figures"):
        os.system(f"mkdir {dic['folder']}/figures")

    dic["ind_batch"], dic["ind_sim"] = [0, 0], [0, 0]
    for i in range(4):
        dic[f"s{i}"] = []
        dic[f"x{i}"] = 0
    process_optimization_results(dic)
    plot_optimization_results(dic)
    plt.rcParams.update({"axes.grid": False})
    plot_optimization_details(dic)
    find_optimal(dic)


def process_optimization_results(dic):
    """Process the optimization results over steps (batches)"""
    os.chdir(dic["folder"])
    dic["tot_eval"], dic["optimal"], dic["optimization"], where = 0, [], [], []
    improved = -np.inf
    root = "everest_output/sim_output"
    for n in range(len(os.listdir(root))):
        for m in range(len(os.listdir(f"{root}/batch_{n}/realization_0"))):
            file = root + f"/batch_{n}/realization_0/evaluation_{m}/func"
            if os.path.exists(file):
                value = np.genfromtxt(file)
                dic["tot_eval"] += 1
                if value == -1e3:
                    dic["x0"] += 1
                elif value == -1e2:
                    dic["x1"] += 1
                elif value < 0:
                    dic["x2"] += 1
                else:
                    dic["x3"] += 1
                if value > -10:
                    improved = max(improved, value)
                    dic["optimal"].append(value)
                    where.append([n, m])
        for i in range(4):
            dic[f"s{i}"].append(dic[f"x{i}"])
            dic[f"x{i}"] = 0
        dic["optimization"].append(improved)
    ind = int(np.nanargmax(np.array(dic["optimal"])))
    dic["optimal"] = dic["optimal"][ind]
    dic["ind_batch"][1] = where[ind][0]
    dic["ind_sim"][1] = where[ind][1]


def find_optimal(dic):
    """Find the well locations and folder for the 'optimal' obtained solution"""
    
    for i, name in enumerate(["initial_guess", "optimal_solution"]):
        if not os.path.exists(f"{dic['folder']}/figures/{name}"):
            os.system(f"mkdir {dic['folder']}/figures/{name}")
        os.chdir(f"{dic['folder']}/figures/{name}")
        os.system(
            f"cp {dic['folder']}/everest_output/sim_output/"
            + f"batch_{dic['ind_batch'][i]}/realization_0/evaluation_"
            + f"{dic['ind_sim'][i]}/point_0.json ."
        )
        os.system(f"python3 {dic['folder']}/jobs/locations.py --mode post")


def plot_optimization_details(dic):
    """Plot the number of failed and succeed simulations over steps"""
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
    fig, axis = plt.subplots()
    axis.step(
        range(1, len(dic["optimization"]) + 1),
        dic["optimization"],
        lw=5,
        color="b",
    )
    axis.set_title("Optimization results")
    axis.set_ylabel("min[(p$_{lim}$-p)/p$_{lim}$] [-]")
    axis.set_xlabel(r"Step [\#]")
    if len(dic["optimization"]) < 20:
        axis.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        axis.set_xticks(np.linspace(
            0,
            len(dic["optimization"]) + 1,
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
