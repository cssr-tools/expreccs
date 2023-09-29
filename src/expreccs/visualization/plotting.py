# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to plot the top surface for the reference, regional, and site reservoirs.
"""

from datetime import timedelta
import os
import argparse
import datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from expreccs.visualization.maps2d import (
    final_time_maps,
    final_time_maps_difference,
)

try:
    from opm.io.ecl import ESmry as OpmSmry
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import ERst as OpmRst
    from opm.io.ecl import EGrid as OpmGrid
except ImportError:
    print("The opm Python package was not found, using ecl")
try:
    from ecl.summary import EclSum
    from ecl.eclfile import EclFile
    from ecl.grid import EclGrid
except ImportError:
    print("The ecl Python package was not found, using opm")

font = {"family": "normal", "weight": "normal", "size": 13}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 1.5,
        "legend.fontsize": 12,
        "lines.linewidth": 4,
        "axes.titlesize": 13,
        "axes.grid": True,
        "figure.figsize": (10, 5),
    }
)


def main():
    """Postprocessing"""
    parser = argparse.ArgumentParser(description="Main script to plot the results")
    parser.add_argument(
        "-t",
        "--time",
        default=0.0,
        help="The workflow time.",
    )
    parser.add_argument(
        "-f",
        "--folder",
        default="output",
        help="The folder to the studies.",
    )
    parser.add_argument(
        "-c",
        "--compare",
        default="",
        help="Generate a common plot for the current folders.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="all",
        help="Plot the whole framework ('all'), only the reference ('reference'), or  "
        "only regional and site models ('noreference') ('all' by default).",
    )
    parser.add_argument(
        "-r",
        "--reading",
        default="ecl",
        help="Using the 'ecl' or 'opm' python package (ecl by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"folders": [cmdargs["folder"].strip()]}
    dic["compare"] = cmdargs["compare"]  # No empty, then the create compare folder
    dic["time"] = float(cmdargs["time"])
    dic["exe"] = os.getcwd()  # Path to the folder of the configuration file
    dic["mode"] = cmdargs["mode"]  # Parts of the workflow to plot
    dic["reading"] = cmdargs["reading"]  # Ecl or opm python package
    plot_results(dic)


def plot_results(dic):
    """
    Function to plot the 2D maps/1D projections for the different quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["rhog_ref"] = 1.86843  # CO2 reference density
    dic["sat_thr"] = 1e-3  # Threshold for the gas saturation
    if dic["compare"]:
        dic["where"] = "compare/"
        dic["folders"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )
        if "compare" not in dic["folders"]:
            os.system(f"mkdir {dic['exe']}/compare")
        else:
            os.system(f"rm -rf {dic['exe']}/compare")
            os.system(f"mkdir {dic['exe']}/compare")
            dic["folders"].remove("compare")
    else:
        dic["where"] = f"{dic['exe']}/{dic['folders'][0]}/postprocessing"
    dic["colors"] = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "r",
    ]
    dic["markers"] = [
        "o",
        "v",
        "^",
        "<",
        ">",
        "1",
        "2",
        "3",
        "4",
    ]
    dic["linestyle"] = [
        "--",
        (0, (1, 1)),
        "-.",
        (0, (1, 10)),
        (0, (1, 1)),
        (5, (10, 3)),
        (0, (5, 10)),
        (0, (5, 5)),
        (0, (5, 1)),
        (0, (3, 10, 1, 10)),
        (0, (3, 5, 1, 5)),
        (0, (3, 1, 1, 1)),
        (0, (3, 5, 1, 5, 1, 5)),
        (0, (3, 10, 1, 10, 1, 10)),
        (0, (3, 1, 1, 1, 1, 1)),
        (0, ()),
        "-",
    ]
    if dic["reading"] == "ecl":
        dic = reading_ecl(dic)
    else:
        dic = reading_opm(dic)
    if dic["mode"] in ["reference"]:
        plt.rcParams.update({"axes.grid": False})
        final_time_maps(dic)
        return
    well_well_well(dic)
    over_time_distance(dic)
    dic["fig"], dic["axis"] = [], []
    for nqua, quantity in enumerate(dic["quantity"]):
        over_time_max_difference(dic, nqua, quantity)
    if dic["compare"]:
        return
    plt.rcParams.update({"axes.grid": False})
    final_time_maps(dic)
    final_time_maps_difference(dic)
    if dic["time"] > 0:
        print(f"Execution time: {timedelta(seconds=dic['time'])}")


def wells_site(dic, nquan, nfol, ndeck, nwell):
    """
    Function to plot the injection rates and BHP

    Args:
        dic (dict): Global dictionary with required parameters

    """
    yvalues = []
    fol = dic["folders"][nfol]
    res = dic[f"{fol}_decks"][ndeck]
    opm = ["WBHP", "WGIR", "WOIR"]
    for nrst, _ in enumerate(dic[f"{fol}/{res}_smsp_dates"]):
        if dic["reading"] == "ecl":
            yvalues.append(
                dic[f"{fol}/{res}_smsp"][f"{opm[nquan]}:INJ{nwell}"].values[nrst]
            )
        else:
            yvalues.append(dic[f"{fol}/{res}_smsp"][f"{opm[nquan]}:INJ{nwell}"][nrst])
    fols = f" ({fol})"
    dic["axis"].step(
        dic[f"{fol}/{res}_smsp_dates"],
        yvalues,
        label=f"well{nwell} {res}" + f"{fols if dic['compare'] else ''}",
        color=dic["colors"][nwell % len(dic["colors"])],
        linestyle=dic["linestyle"][(-1 + nfol) % len(dic["linestyle"])],
        marker=dic["markers"][ndeck],
        lw=1,
    )
    return dic


def well_well_well(dic):
    """
    Function to plot the injection rates and BHP

    Args:
        dic (dict): Global dictionary with required parameters

    """
    quantites = ["pressure", "CO2 rate", "H2O rate"]
    units = [
        "BHP [Bar]",
        "Rate [sm3/day]",
        "Rate [sm3/day]",
    ]
    for i, quantity in enumerate(quantites):
        dic["fig"], dic["axis"] = plt.subplots()
        for nfol, fol in enumerate(dic["folders"]):
            for ndeck, res in enumerate(dic[f"{fol}_decks"]):
                if res == "regional":
                    continue
                for nwell in range(dic[f"{fol}/{res}_nowells_site"]):
                    dic = wells_site(dic, i, nfol, ndeck, nwell)
        dic["axis"].set_ylabel(units[i])
        dic["axis"].set_xlabel("Time")
        handles, labels = plt.gca().get_legend_handles_labels()
        order = np.argsort(labels)
        dic["axis"].legend(
            [handles[idx] for idx in order], [labels[idx] for idx in order]
        )
        dic["axis"].set_title("Injectors in the site location")
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(
            f"{dic['where']}/wells_{quantity}_site_reference.png", bbox_inches="tight"
        )
        plt.close()
        dic["fig"], dic["axis"] = plt.subplots()
        for nfol, fol in enumerate(dic["folders"]):
            for ndeck, res in enumerate(dic[f"{fol}_decks"]):
                if "site" in res:
                    continue
                for nwell in range(dic[f"{fol}/{res}_nowells"]):
                    dic = wells_site(dic, i, nfol, ndeck, nwell)
        dic["axis"].set_ylabel(units[i])
        dic["axis"].set_xlabel("Time")
        handles, labels = plt.gca().get_legend_handles_labels()
        order = np.argsort(labels)
        dic["axis"].legend(
            [handles[idx] for idx in order], [labels[idx] for idx in order]
        )
        dic["axis"].set_title("Injectors in the regional location")
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(
            f"{dic['where']}/wells_{quantity}_regional_reference.png",
            bbox_inches="tight",
        )
        plt.close()


def reading_ecl(dic):
    """
    Function to read the deck quantities using ecl

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["quantity"] = ["saturation", "pressure", "flooili+", "flooilj+"]
    dic["names"] = ["saturation", "pressure", "watfluxi+", "watfluxj+"]
    dic["units"] = ["-", "bar", "sm$^3$/day", "sm$^3$/day"]
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{dic['exe']}/{fol}/output")
        dic[f"{fol}_sites"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )[2:]
        os.chdir(cwd)
        if dic["mode"] in ["reference"]:
            dic[f"{fol}_decks"] = ["reference"]
        elif dic["compare"]:
            dic[f"{fol}_decks"] = ["reference"] + dic[f"{fol}_sites"]
        else:
            dic[f"{fol}_decks"] = ["reference", "regional"] + dic[f"{fol}_sites"]
        for res in dic[f"{fol}_decks"]:
            case = dic["exe"] + "/" + fol + f"/output/{res}/{res.upper()}"
            dic[f"{fol}/{res}_nowells"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells.npy"
            )
            dic[f"{fol}/{res}_nowells_site"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells_site.npy"
            )
            dic[f"{fol}/{res}_rst"] = EclFile(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = EclFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = EclGrid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = EclSum(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = dic[f"{fol}/{res}_rst"].num_report_steps()
            dic[f"{fol}/{res}_dates"] = dic[f"{fol}/{res}_rst"].dates
            dic[f"{fol}/{res}_smsp_dates"] = dic[f"{fol}/{res}_smsp"].dates
            dic[f"{fol}/{res}_saturation"] = dic[f"{fol}/{res}_rst"].iget_kw("SGAS")
            dic[f"{fol}/{res}_pressure"] = dic[f"{fol}/{res}_rst"].iget_kw("PRESSURE")
            dic[f"{fol}/{res}_flooili+"] = dic[f"{fol}/{res}_rst"].iget_kw("FLOOILI+")
            dic[f"{fol}/{res}_flooilj+"] = dic[f"{fol}/{res}_rst"].iget_kw("FLOOILJ+")
            dic[f"{fol}/{res}_phiv"] = dic[f"{fol}/{res}_ini"].iget_kw("PORV")[0]
            dic[f"{fol}/{res}_density"] = dic[f"{fol}/{res}_rst"].iget_kw("GAS_DEN")
            dic[f"{fol}/{res}_fipn"] = np.array(
                dic[f"{fol}/{res}_ini"].iget_kw("FIPNUM")
            )[0]
            dic = handle_smsp_time(dic, fol, res)
            dic[f"{fol}/{res}_indicator_array"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
                for i in range(dic[f"{fol}/{res}_num_rst"]):
                    if quantity == "saturation":
                        dic[f"{fol}/{res}_indicator_array"].append(
                            np.array(dic[f"{fol}/{res}_saturation"][i]) > dic["sat_thr"]
                        )
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_saturation"][i])
                        )
                    else:
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_{quantity}"][i])
                        )
            name = "site" if "site" in res else res
            dic[f"{fol}/{name}_boxi"] = dic[f"{fol}/{res}_grid"].getNodePos(0, 0, 0)
            dic[f"{fol}/{name}_boxf"] = dic[f"{fol}/{res}_grid"].getNodePos(
                dic[f"{fol}/{res}_grid"].getNX(),
                dic[f"{fol}/{res}_grid"].getNY(),
                dic[f"{fol}/{res}_grid"].getNZ(),
            )
            dic[f"{fol}/{name}_xmx"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_xmx.npy"
            )
            dic[f"{fol}/{name}_ymy"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_ymy.npy"
            )
            dic[f"{fol}/{res}_xcor"], dic[f"{fol}/{res}_ycor"] = np.meshgrid(
                dic[f"{fol}/{name}_xmx"], dic[f"{fol}/{name}_ymy"][::-1]
            )
    return dic


def handle_smsp_time(dic, fol, res):
    """
    Function to chandle the times in the summary files

    Args:
        dic (dict): Global dictionary with required parameters
        str (study): Name of the folder containing the results

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic[f"{fol}/{res}_rst_seconds"] = np.load(
        dic["exe"] + "/" + fol + f"/output/{res}/schedule.npy"
    )
    dic[f"{fol}/{res}_smsp_report_step"] = dic[f"{fol}/{res}_smsp"][
        "WBHP:INJ0"
    ].report_step
    dic[f"{fol}/{res}_report_time"] = dic[f"{fol}/{res}_rst"].dates
    dic[f"{fol}/{res}_smsp_seconds"] = [
        (
            dic[f"{fol}/{res}_smsp"].numpy_dates[i + 1]
            - dic[f"{fol}/{res}_smsp"].numpy_dates[i]
        )
        / np.timedelta64(1, "s")
        for i in range(len(dic[f"{fol}/{res}_smsp"].numpy_dates) - 1)
    ]
    dic[f"{fol}/{res}_smsp_seconds"].insert(
        0,
        (
            dic[f"{fol}/{res}_smsp"].numpy_dates[0]
            - np.datetime64(dic[f"{fol}/{res}_smsp"].get_start_time())
        )
        / np.timedelta64(1, "s"),
    )
    for i in range(len(dic[f"{fol}/{res}_smsp"].numpy_dates) - 1):
        dic[f"{fol}/{res}_smsp_seconds"][i + 1] += dic[f"{fol}/{res}_smsp_seconds"][i]
    dic[f"{fol}/{res}_smsp_rst"] = [
        pd.Series(abs(dic[f"{fol}/{res}_smsp_seconds"] - time)).argmin()
        for time in dic[f"{fol}/{res}_rst_seconds"]
    ]
    dic[f"{fol}/{res}_smsp_seconds"] = np.insert(
        dic[f"{fol}/{res}_smsp_seconds"], 0, 0.0
    )
    return dic


def reading_opm(dic):
    """
    Function to read the deck quantities using opm

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["quantity"] = ["saturation", "pressure", "flooili+", "flooilj+"]
    dic["names"] = ["saturation", "pressure", "watfluxi+", "watfluxj+"]
    dic["units"] = ["-", "bar", "sm$^3$/day", "sm$^3$/day"]
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{dic['exe']}/{fol}/output")
        dic[f"{fol}_sites"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )[2:]
        os.chdir(cwd)
        if dic["mode"] in ["reference"]:
            dic[f"{fol}_decks"] = ["reference"]
        elif dic["compare"]:
            dic[f"{fol}_decks"] = ["reference"] + dic[f"{fol}_sites"]
        else:
            dic[f"{fol}_decks"] = ["reference", "regional"] + dic[f"{fol}_sites"]
        for res in dic[f"{fol}_decks"]:
            dic[f"{fol}/{res}_rst_seconds"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/schedule.npy"
            )
            dic[f"{fol}/{res}_nowells"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells.npy"
            )
            dic[f"{fol}/{res}_nowells_site"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells_site.npy"
            )
            case = dic["exe"] + "/" + fol + f"/output/{res}/{res.upper()}"
            dic[f"{fol}/{res}_rst"] = OpmRst(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = OpmFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = OpmGrid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = OpmSmry(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = len(dic[f"{fol}/{res}_rst"].report_steps)
            dic[f"{fol}/{res}_dates"] = [
                dic[f"{fol}/{res}_smsp"].start_date
                + datetime.timedelta(seconds=seconds)
                for seconds in dic[f"{fol}/{res}_rst_seconds"]
            ]
            dic[f"{fol}/{res}_smsp_seconds"] = 86400 * dic[f"{fol}/{res}_smsp"]["TIME"]
            dic[f"{fol}/{res}_smsp_dates"] = 86400 * dic[f"{fol}/{res}_smsp"]["TIME"]
            dic[f"{fol}/{res}_smsp_dates"] = [
                dic[f"{fol}/{res}_smsp"].start_date
                + datetime.timedelta(seconds=seconds)
                for seconds in dic[f"{fol}/{res}_smsp_dates"]
            ]
            dic[f"{fol}/{res}_smsp_rst"] = [
                pd.Series(abs(dic[f"{fol}/{res}_smsp_seconds"] - time)).argmin()
                for time in dic[f"{fol}/{res}_rst_seconds"]
            ]
            dic[f"{fol}/{res}_phiv"] = np.array(dic[f"{fol}/{res}_ini"]["PORV"])
            dic[f"{fol}/{res}_fipn"] = np.array(dic[f"{fol}/{res}_ini"]["FIPNUM"])
            dic[f"{fol}/{res}_indicator_array"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
                for i in range(dic[f"{fol}/{res}_num_rst"]):
                    if quantity == "saturation":
                        dic[f"{fol}/{res}_indicator_array"].append(
                            np.array(dic[f"{fol}/{res}_rst"]["SGAS", i])
                            > dic["sat_thr"]
                        )
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_rst"]["SGAS", i])
                        )
                    else:
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_rst"][f"{quantity.upper()}", i])
                        )
            name = "site" if "site" in res else res
            dic[f"{fol}/{name}_boxi"] = [
                dic[f"{fol}/{res}_grid"].xyz_from_ijk(0, 0, 0)[i][0] for i in range(3)
            ]
            dic[f"{fol}/{name}_boxf"] = [
                dic[f"{fol}/{res}_grid"].xyz_from_ijk(
                    dic[f"{fol}/{res}_grid"].dimension[0] - 1,
                    dic[f"{fol}/{res}_grid"].dimension[1] - 1,
                    dic[f"{fol}/{res}_grid"].dimension[2] - 1,
                )[i][-1]
                for i in range(3)
            ]
            dic[f"{fol}/{name}_xmx"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_xmx.npy"
            )
            dic[f"{fol}/{name}_ymy"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_ymy.npy"
            )
            dic[f"{fol}/{res}_xcor"], dic[f"{fol}/{res}_ycor"] = np.meshgrid(
                dic[f"{fol}/{name}_xmx"], dic[f"{fol}/{name}_ymy"][::-1]
            )
    return dic


def over_time_distance(dic):
    """
    Function to plot the distance from the closest saturation cell to the site border

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["fig"], dic["axis"] = [], []
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    for nfol, fol in enumerate(dic["folders"]):
        dic["dx_half_size"] = 0.5 * (
            dic[f"{fol}/site_xmx"][1:] - dic[f"{fol}/site_xmx"][:-1]
        )
        dic["dy_half_size"] = 0.5 * (
            dic[f"{fol}/site_ymy"][1:] - dic[f"{fol}/site_ymy"][:-1]
        )
        for j, res in enumerate(["reference"] + dic[f"{fol}_sites"]):
            dic[f"{fol}/{res}_indicator_plot"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_difference_{quantity}"] = []
            for nrst in range(dic[f"{fol}/{res}_num_rst"]):
                if dic["reading"] == "ecl":
                    points = positions_ecl(dic, fol, res, nrst)
                else:
                    points = positions_opm(dic, fol, res, nrst)
                if points.size > 0:
                    closest_distance = np.zeros(4)
                    for i, border in enumerate(
                        [
                            dic[f"{fol}/site_boxi"][0] + dic["dx_half_size"][0],
                            dic[f"{fol}/site_boxf"][0] - dic["dx_half_size"][-1],
                        ]
                    ):
                        closest_distance[i] = min(
                            np.array([abs(row[0] - border) for row in points])
                        )
                    for i, border in enumerate(
                        [
                            (dic[f"{fol}/site_boxi"][1] + dic["dy_half_size"][0]),
                            (dic[f"{fol}/site_boxf"][1] - dic["dy_half_size"][-1]),
                        ]
                    ):
                        closest_distance[i + 2] = min(
                            np.array([abs(row[1] - border) for row in points])
                        )
                    dic[f"{fol}/{res}_indicator_plot"].append(closest_distance.min())
                else:
                    dic[f"{fol}/{res}_indicator_plot"].append(
                        (dic[f"{fol}/site_boxf"][0] - dic[f"{fol}/site_boxi"][0]) / 2.0
                    )
            dic = handle_labels_distance(dic, nfol, res, fol, j)

        dic["axis"][-1].set_title(
            "Minimum "
            + r"CO$_2$"
            + f' distance to the borders (sat thr={dic["sat_thr"]})'
        )
        dic["axis"][-1].set_ylabel("Distance [m]")
        dic["axis"][-1].set_xlabel("Time")
        dic["axis"][-1].legend()
        dic["axis"][-1].xaxis.set_tick_params(rotation=45)
        dic["fig"][-1].savefig(
            f"{dic['where']}/distance_from_border.png", bbox_inches="tight"
        )
        plt.close()


def positions_opm(dic, fol, res, nrst):
    """
    Function to extract the point coordinates using opm

    Args:
        dic (dict): Global dictionary with required parameters
        fol (str): Name of the output folder
        res (str): Name of the reservoir
        nrst (int): Indice for the schedule

    Returns:
        points (list): x,y,z coordinates

    """
    x_a = [
        0.5
        * (
            dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][-1]
            - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][0]
        )
        + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][0]
        for i in np.nonzero(dic[f"{fol}/{res}_indicator_array"][1])[0]
    ]
    y_a = [
        0.5
        * (
            dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][-1]
            - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][0]
        )
        + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][0]
        for i in np.nonzero(dic[f"{fol}/{res}_indicator_array"][1])[0]
    ]
    z_a = [
        0.5
        * (
            dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][-1]
            - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][0]
        )
        + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][0]
        for i in np.nonzero(dic[f"{fol}/{res}_indicator_array"][1])[0]
    ]
    points = np.stack(
        [np.array(x_a).flatten(), np.array(y_a).flatten(), np.array(z_a).flatten()],
        axis=-1,
    )
    if res == "reference":
        indx = [
            dic[f"{fol}/{res}_indicator_array"][nrst][k]
            and dic[f"{fol}/reference_fipn"][k] == 1
            for k in range(len(dic[f"{fol}/reference_fipn"]))
        ]
        x_a = [
            0.5
            * (
                dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][-1]
                - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][0]
            )
            + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][0]
            for i in np.nonzero(indx)[0]
        ]
        y_a = [
            0.5
            * (
                dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][-1]
                - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][0]
            )
            + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][0]
            for i in np.nonzero(indx)[0]
        ]
        z_a = [
            0.5
            * (
                dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][-1]
                - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][0]
            )
            + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][0]
            for i in np.nonzero(indx)[0]
        ]
    else:
        x_a = [
            0.5
            * (
                dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][-1]
                - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][0]
            )
            + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[0][0]
            for i in np.nonzero(dic[f"{fol}/{res}_indicator_array"][nrst])[0]
        ]
        y_a = [
            0.5
            * (
                dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][-1]
                - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][0]
            )
            + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[1][0]
            for i in np.nonzero(dic[f"{fol}/{res}_indicator_array"][nrst])[0]
        ]
        z_a = [
            0.5
            * (
                dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][-1]
                - dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][0]
            )
            + dic[f"{fol}/{res}_grid"].xyz_from_active_index(i)[2][0]
            for i in np.nonzero(dic[f"{fol}/{res}_indicator_array"][nrst])[0]
        ]
    points = np.stack(
        [np.array(x_a).flatten(), np.array(y_a).flatten(), np.array(z_a).flatten()],
        axis=-1,
    )
    return points


def positions_ecl(dic, fol, res, nrst):
    """
    Function to extract the point coordinates using ecl

    Args:
        dic (dict): Global dictionary with required parameters
        fol (str): Name of the output folder
        res (str): Name of the reservoir
        nrst (int): Indice for the schedule

    Returns:
        points (list): x,y,z coordinates

    """
    points = dic[f"{fol}/{res}_grid"].export_position(
        dic[f"{fol}/{res}_grid"].export_index()[dic[f"{fol}/{res}_indicator_array"][1]]
    )
    if res == "reference":
        indx = [
            dic[f"{fol}/{res}_indicator_array"][nrst][k]
            and dic[f"{fol}/reference_fipn"][k] == 1
            for k in range(len(dic[f"{fol}/reference_fipn"]))
        ]
        points = dic[f"{fol}/{res}_grid"].export_position(
            dic[f"{fol}/{res}_grid"].export_index()[indx]
        )
    else:
        points = dic[f"{fol}/{res}_grid"].export_position(
            dic[f"{fol}/{res}_grid"].export_index()[
                dic[f"{fol}/{res}_indicator_array"][nrst]
            ]
        )
    return points


def handle_labels_distance(dic, nfol, res, fol, j):
    """
    Function to handle the labeling for better visualization.

    Args:
        dic (dict): Global dictionary with required parameters
        nfol (int): Indice for the color
        res (str): Name of the reservoir
        fol (str): Name of the output folder
        j (int): Indice for the reservoir

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    if dic["compare"]:
        if nfol == 0 and res == "reference":
            label = f"{res}"
            dic["axis"][-1].plot(
                dic[f"{fol}/{res}_dates"],
                dic[f"{fol}/{res}_indicator_plot"],
                color=dic["colors"][-1],
                linestyle=dic["linestyle"][-1],
                label=label,
            )
        if res != "reference":
            label = f"{res} ({fol})"
            dic["axis"][-1].plot(
                dic[f"{fol}/{res}_dates"],
                dic[f"{fol}/{res}_indicator_plot"],
                color=dic["colors"][(nfol + 1) % len(dic["colors"])],
                linestyle=dic["linestyle"][j % len(dic["linestyle"])],
                label=label,
            )
    else:
        label = f"{res}"
        dic["axis"][-1].plot(
            dic[f"{fol}/{res}_dates"],
            dic[f"{fol}/{res}_indicator_plot"],
            color=dic["colors"][-1 - j],
            linestyle=dic["linestyle"][-1 - j],
            label=label,
        )
    return dic


def over_time_max_difference(dic, nqua, quantity):
    """
    Function to plot the the max difference between pressure/saturation.

    Args:
        dic (dict): Global dictionary with required parameters

    """
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    dic[f"reference_maximum_{quantity}"] = []
    for nfol, fol in enumerate(dic["folders"]):
        for j, res in enumerate(dic[f"{fol}_sites"]):
            dic[f"{fol}/{res}_difference_{quantity}"] = []
            dic[f"{fol}/{res}_maximum_{quantity}"] = []
            for nrst in range(dic[f"{fol}/{res}_num_rst"]):
                quant = abs(
                    np.array(dic[f"{fol}/reference_{quantity}_array"][nrst])[
                        dic[f"{fol}/reference_fipn"] == 1
                    ]
                    - dic[f"{fol}/{res}_{quantity}_array"][nrst]
                )
                if quantity == "flooili+":
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        quant[(k + 1) * (len(dic[f"{fol}/site_xmx"]) - 1) - 1] = 0
                if quantity == "flooilj+":
                    for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                        quant[
                            (len(dic[f"{fol}/site_ymy"]) - 2)
                            * (len(dic[f"{fol}/site_xmx"]) - 1)
                            + k
                        ] = 0
                dic[f"{fol}/{res}_difference_{quantity}"].append(max(quant))
                dic[f"{fol}/{res}_maximum_{quantity}"].append(
                    max(dic[f"{fol}/{res}_{quantity}_array"][nrst])
                )
                if j == 0:
                    dic[f"reference_maximum_{quantity}"].append(
                        max(
                            dic[f"{fol}/reference_{quantity}_array"][nrst][
                                dic[f"{fol}/reference_fipn"] == 1
                            ]
                        )
                    )
            dic = handle_labels_difference(dic, res, j, nqua, nfol)
    dic["axis"][nqua].set_title(
        f"Maximum {dic['names'][nqua]} difference "
        + f"(w.r.t. reference, max {dic['names'][nqua]} of "
        + f"{np.array(dic[f'reference_maximum_{quantity}']).max():.2E} "
        + f"[{dic['units'][nqua]}]))"
    )
    dic["axis"][nqua].set_ylabel(f"Difference [{dic['units'][nqua]}]")
    dic["axis"][nqua].set_xlabel("Time")
    dic["axis"][nqua].legend()
    dic["axis"][nqua].xaxis.set_tick_params(rotation=45)
    dic["fig"][nqua].savefig(
        f"{dic['where']}/maximum_{dic['names'][nqua]}_difference_over_time.png",
        bbox_inches="tight",
    )
    plt.close()


def handle_labels_difference(dic, res, j, nqua, nfol):
    """
    Function to handle the labeling for improve visualization.

    Args:
        dic (dict): Global dictionary with required parameters
        res (str): Name of the reservoir
        j (int): Indice for the reservoir

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    quantity = dic["quantity"][nqua]
    fol = dic["folders"][nfol]
    if dic["compare"]:
        label = f"{res} ({fol})"
        dic["axis"][nqua].plot(
            dic[f"{fol}/{res}_dates"],
            dic[f"{fol}/{res}_difference_{quantity}"],
            color=dic["colors"][nfol % len(dic["colors"])],
            linestyle=dic["linestyle"][j % len(dic["linestyle"])],
            label=label,
        )
    else:
        label = (
            f"{res} (max {dic['names'][nqua]} of "
            + f"{np.array(dic[f'{fol}/{res}_maximum_{quantity}']).max():.2E}"
            + f"[{dic['units'][nqua]}])"
        )
        dic["axis"][nqua].plot(
            dic[f"{fol}/{res}_dates"],
            dic[f"{fol}/{res}_difference_{quantity}"],
            color=dic["colors"][j % len(dic["colors"])],
            linestyle=dic["linestyle"][j % len(dic["linestyle"])],
            label=label,
        )
    return dic


if __name__ == "__main__":
    main()
