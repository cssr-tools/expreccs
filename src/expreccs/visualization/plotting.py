# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0914

""""
Script to plot the top surface for the reference, regional, and site reservoirs.
"""

from datetime import timedelta
import os
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from expreccs.visualization.maps2d import (
    final_time_maps,
    final_time_maps_difference,
    geological_maps,
)
from expreccs.visualization.reading import (
    reading_resdata,
    reading_opm,
)

GAS_DEN_REF = 1.86843  # kg/sm3
WAT_DEN_REF = 998.108  # kg/sm3
KG_TO_KT = 1e-6
KG_TO_MT = 1e-9

font = {"family": "normal", "weight": "normal", "size": 16}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 2.2,
        "legend.fontsize": 14,
        "lines.linewidth": 3,
        "axes.titlesize": 16,
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
        "-p",
        "--plot",
        default="all",
        help="Plot 'all', 'reference', 'regional', 'site', or no ('no' by default).",
    )
    parser.add_argument(
        "-r",
        "--reading",
        default="opm",
        help="Using the 'resdata' or 'opm' python package (opm by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"folders": [cmdargs["folder"].strip()]}
    dic["compare"] = cmdargs["compare"]  # No empty, then the create compare folder
    dic["time"] = float(cmdargs["time"])
    dic["exe"] = os.getcwd()  # Path to the folder of the configuration file
    dic["plot"] = cmdargs["plot"]  # Parts of the workflow to plot
    dic["reading"] = cmdargs["reading"]  # Res or opm python package
    plot_results(dic)


def plot_results(dic):
    """
    Function to plot the 2D maps/1D projections for the different quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["rhog_ref"] = 1.86843  # CO2 reference density
    dic["sat_thr"] = 0.01  # Threshold for the plume location [-]
    if dic["compare"]:
        dic["where"] = "compare/"
        dic["folders"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )
        if "compare" not in dic["folders"]:
            os.system(f"mkdir {dic['exe']}/compare")
        else:
            dic["folders"].remove("compare")
        dic["id"] = "compare" + dic["folders"][0] + "_"
    else:
        dic["where"] = f"{dic['exe']}/{dic['folders'][0]}/postprocessing"
        dic["id"] = dic["folders"][0] + "_"
    dic["lfolders"] = [name.replace("_", " ") for name in dic["folders"]]
    dic = plotting_settings(dic)
    if dic["reading"] == "resdata":
        dic = reading_resdata(dic)
    else:
        dic = reading_opm(dic)
    if dic["plot"] in ["reference", "regional", "site"]:
        plt.rcParams.update({"axes.grid": False})
        final_time_maps(dic)
        return
    quantites = [
        "BHP",
        "WGIR",
        "WWIR",
        "PR",
        "GIP",
        "GIPL",
        "GIPG",
        "BPR",
        "BGIP",
        "BGIPL",
        "BGIPG",
    ]
    # quantites += ["BFLOWI" "BFLOWJ"]
    for i, quantity in enumerate(quantites):
        summary_plot(dic, i, quantity)
    over_time_distance(dic)
    dic["fig"], dic["axis"], dic["figs"], dic["axiss"] = [], [], [], []
    for nqua, quantity in enumerate(dic["quantity"]):
        over_time_max_difference(dic, nqua, quantity)
        over_time_sensor(dic, nqua, quantity)
    if dic["compare"]:
        return
    plt.rcParams.update({"axes.grid": False})
    geological_maps(dic)
    final_time_maps(dic)
    final_time_maps_difference(dic)
    if dic["time"] > 0:
        print(f"Execution time: {timedelta(seconds=dic['time'])}")


def plotting_settings(dic):
    """Set the color/line styles and labels"""
    dic["colors"] = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#17becf",
        "#bcbd22",
        "k",
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
        (0, (3, 5, 1, 5, 1, 5)),
        ":",
        "-.",
        "--",
        (0, (3, 1, 1, 1)),
        (0, (3, 1, 1, 1, 1, 1)),
        "solid",
    ]
    dic["lreference"] = r"REF"
    dic["lregional"] = r"REG"
    dic["lregional_1"] = r"REG_1"
    dic["lregional_2"] = r"REG_2"
    dic["lsite_pres"] = r"SITE$_p$"
    dic["lsite_pres2p"] = r"SITE$_{2p}$"
    dic["lsite_pres_1"] = r"SITE$_{1,p}$"
    dic["lsite_pres_2"] = r"SITE$_{2,p}$"
    dic["lsite_flux"] = r"SITE$_f$"
    dic["lsite_porvproj"] = r"SITE$_{V_p}$"
    dic["lsite_wells"] = r"SITE$_w$"
    dic["lsite_closed"] = r"SITE$_c$"
    dic["lsite_free"] = r"SITE$_o$"
    dic["cmaps"] = [
        "jet",
        "brg",
        "coolwarm",
        "coolwarm",
        "coolwarm",
        "coolwarm",
        "coolwarm",
        "coolwarm",
        "coolwarm",
        "coolwarm",
        "jet",
        "jet",
        "jet",
    ]
    dic["quantity"] = [
        "saturation",
        "pressure",
        "FLOWATI+",
        "FLOWATJ+",
        "FLOWATI-",
        "FLOWATJ-",
        "FLOGASI+",
        "FLOGASJ+",
        "FLOGASI-",
        "FLOGASJ-",
        "mass",
        "diss",
        "gas",
    ]
    dic["names"] = [
        "saturation",
        "pressure",
        "watfluxi+",
        "watfluxj+",
        "watfluxi-",
        "watfluxj-",
        "gasfluxi+",
        "gasfluxj+",
        "gasfluxi-",
        "gasfluxj-",
        "CO$_2$ total",
        "CO$_2$ dissolved",
        "CO$_2$ gas",
    ]
    dic["units"] = [
        "Saturation [-]",
        "Pressure [bar]",
        "H$_2$O velocity x+ direction [m day$^{-1}$]",
        "H$_2$O velocity y+ direction [m day$^{-1}$]",
        "H$_2$O velocity x- direction [m day$^{-1}$]",
        "H$_2$O velocity y- direction [m day$^{-1}$]",
        "CO$_2$ velocity x+ direction [m day$^{-1}$]",
        "CO$_2$ velocity y+ direction [m day$^{-1}$]",
        "CO$_2$ velocity x- direction [m day$^{-1}$]",
        "CO$_2$ velocity y- direction [m day$^{-1}$]",
        "CO$_2$ in-place [kt]",
        "CO$_2$ in-place (liquid phase) [kt]",
        "CO$_2$ in-place (gas phase) [kt]",
    ]
    return dic


def wells_site(dic, nquan, nfol, ndeck, nwell):
    """
    Function to plot the injection rates and BHP

    Args:
        dic (dict): Global dictionary with required parameters

    """
    fol = dic["folders"][nfol]
    res = dic[f"{fol}_decks"][ndeck]
    opm = ["WBHP", "WGIR", f"W{dic[f'{fol}/{res}l']}IR"]
    if dic["reading"] == "resdata":
        yvalues = dic[f"{fol}/{res}_smsp"][f"{opm[nquan]}:INJ{nwell}"].values
    else:
        yvalues = dic[f"{fol}/{res}_smsp"][f"{opm[nquan]}:INJ{nwell}"]
    if opm[nquan] == "WGIR":
        yvalues = [val * GAS_DEN_REF * KG_TO_MT * 365.25 for val in yvalues]
    if opm[nquan] == f"W{dic[f'{fol}/{res}l']}R":
        yvalues = [val * WAT_DEN_REF * KG_TO_MT * 365.25 for val in yvalues]
    # fols = f" ({fol})"
    # if nwell > 0:
    #     marker = dic["markers"][nwell]
    # else:
    #     marker = ""
    # dic["axis"].step(
    #     dic[f"{fol}/{res}_smsp_dates"],
    #     yvalues,
    #     label=f"INJ{nwell} "
    #     + dic[f"l{res}"]
    #     + f" {' ('+dic['lfolders'][nfol]+')' if dic['compare'] else ''}",
    #     color=dic["colors"][-ndeck - 1],
    #     linestyle=dic["linestyle"][-ndeck - 1 - nfol * len(dic[f"{fol}_decks"])],
    #     marker=marker,
    #     lw=2,
    # )
    # if ndeck == 0 and nfol == 1 or nwell > 0:
    #     return dic
    # if ndeck == 0:
    #     dic["axis"].step(
    #         dic[f"{fol}/{res}_smsp_dates"],
    #         yvalues,
    #         label=f"reference",
    #         color=dic["colors"][ - 1],
    #         lw=3,
    #     )
    # else:
    #     dic["axis"].step(
    #         dic[f"{fol}/{res}_smsp_dates"],
    #         yvalues,
    #         label=f"{res}",
    #         color=dic["colors"][ - ndeck],
    #         linestyle=dic["linestyle"][ - ndeck],
    #         lw=3,
    #     )
    # if ndeck > 0:
    #     return dic
    # dic["axis"].step(
    #     dic[f"{fol}/{res}_smsp_dates"],
    #     yvalues,
    #     label=f"INJ{nwell}",
    #     color=dic["colors"][nwell],
    #     linestyle=dic["linestyle"][-1 + nwell],
    #     lw=3,
    # )
    if ndeck != 1 or nfol > 0:  # or nwell > 0:
        return dic
    dic["axis"].step(
        dic[f"{fol}/{res}_smsp_dates"],
        yvalues,
        label=f"INJ{nwell}",
        color=dic["colors"][nwell],
        linestyle=dic["linestyle"][-1 + nwell],
        lw=3,
    )
    return dic


def summary_site(dic, nfol, ndeck, opmn):
    """
    Function to plot summary quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    # if dic["compare"]:
    #     marker = dic["markers"][nfol]
    # else:
    #     marker = ""
    fol = dic["folders"][nfol]
    res = dic[f"{fol}_decks"][ndeck]
    if dic["reading"] == "resdata":
        yvalues = dic[f"{fol}/{res}_smsp"][f"{opmn}"].values
    else:
        yvalues = dic[f"{fol}/{res}_smsp"][f"{opmn}"]
    if opmn[1:4] == "GIP":
        yvalues = [val * GAS_DEN_REF * KG_TO_KT for val in yvalues]
    if opmn[:6] == "BFLOWI":
        dy = dic[f"{fol}/{res}_dy"][dic[f"{fol}/{res}_sensor"]]
        dz = dic[f"{fol}/{res}_dz"][dic[f"{fol}/{res}_sensor"]]
        poro = dic[f"{fol}/{res}_poro"][dic[f"{fol}/{res}_sensor"]]
        yvalues = [val / (poro * dy * dz) for val in yvalues]
    if opmn[:6] == "BFLOWJ":
        dx = dic[f"{fol}/{res}_dx"][dic[f"{fol}/{res}_sensor"]]
        dz = dic[f"{fol}/{res}_dz"][dic[f"{fol}/{res}_sensor"]]
        poro = dic[f"{fol}/{res}_poro"][dic[f"{fol}/{res}_sensor"]]
        yvalues = [val / (poro * dx * dz) for val in yvalues]
    if ndeck == 0 and nfol > 0:
        return dic
    if ndeck == 0:
        dic["axis"].step(
            dic[f"{fol}/{res}_smsp_dates"],
            yvalues,
            label=dic["lreference"],
            color=dic["colors"][-ndeck - 1],
        )
    else:
        dic["axis"].step(
            dic[f"{fol}/{res}_smsp_dates"],
            yvalues,
            label=dic[f"l{res}"]
            + f"{' ('+dic['lfolders'][nfol]+')' if dic['compare'] else ''}",
            color=dic["colors"][-ndeck - 1],
            linestyle=dic["linestyle"][-nfol - 2],
        )
    return dic


def handle_site_summary(dic, i, quantity):
    """Routine for the summary qunatities at the site location"""
    for nfol, fol in enumerate(dic["folders"]):
        for ndeck, res in enumerate(dic[f"{fol}_decks"]):
            if res == "regional":
                continue
            if quantity in ["PR", "GIP", "GIPL", "GIPG"]:
                dic = summary_site(dic, nfol, ndeck, f"R{quantity}:1")
                dic["axis"].set_title(
                    "SITE "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
            elif quantity in ["BPR", "BGIP", "BGIPL", "BGIPG", "BFLOWI", "BFLOWJ"]:
                dic = summary_site(
                    dic,
                    nfol,
                    ndeck,
                    f"{quantity}:{dic[f'{fol}/{res}_sensorijk'][0]+1},"
                    + f"{dic[f'{fol}/{res}_sensorijk'][1]+1},"
                    + f"{dic[f'{fol}/{res}_sensorijk'][2]+1}",
                )
                dic["axis"].set_title(
                    "SITE "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
            else:
                for nwell in range(dic[f"{fol}/{res}_nowells_site"]):
                    dic = wells_site(dic, i, nfol, ndeck, nwell)
                dic["axis"].set_title(
                    "SITE "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
    return dic


def summary_plot(dic, i, quantity):
    """
    Function to plot the summary qunatities

    Args:
        dic (dict): Global dictionary with required parameters
        i (int): Index of the quantity
        quantity (str): Name of the quantity

    """
    units = [
        "W$_{BHP}$ [bar]",
        "Rate [Mtpa]",
        "Rate [Mtpa]",
        "Field average pressure [bar]",
        "CO$_2$ in-place [kt]",
        "CO$_2$ in-place (liquid phase) [kt]",
        "CO$_2$ in-place (gas phase) [kt]",
        "Pressure at the sensor [bar]",
        "CO$_2$ at the sensor [kt]",
        "CO$_2$ at the sensor (liquid phase) [kt]",
        "CO$_2$ at the sensor (gas phase) [kt]",
        "Mass flux in the x+ direction [t m$^{-2}$ day$^{-1}$]",
        "Mass flux in the j+ direction [t m$^{-2}$ day$^{-1}$]",
    ]
    dic["fig"], dic["axis"] = plt.subplots()
    dic = handle_site_summary(dic, i, quantity)
    dic["axis"].set_ylabel(units[i])
    dic["axis"].set_xlabel("Time")
    handles, labels = plt.gca().get_legend_handles_labels()
    order = np.argsort(labels)
    dic["axis"].legend([handles[idx] for idx in order], [labels[idx] for idx in order])
    dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
    dic["fig"].savefig(
        f"{dic['where']}/{dic['id']}summary_{quantity}_site_reference.png",
        bbox_inches="tight",
    )
    plt.close()
    dic["fig"], dic["axis"] = plt.subplots()
    for nfol, fol in enumerate(dic["folders"]):
        for ndeck, res in enumerate(dic[f"{fol}_decks"]):
            if "site" in res:
                continue
            if quantity in ["PR", "GIP", "GIPL", "GIPG"]:
                dic = summary_site(dic, nfol, ndeck, f"F{quantity}")
                dic["axis"].set_title(
                    "REGION "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
            elif quantity in ["BPR", "BGIP", "BGIPL", "BGIPG", "BFLOWI", "BFLOWJ"]:
                dic = summary_site(
                    dic,
                    nfol,
                    ndeck,
                    f"{quantity}:{dic[f'{fol}/{res}_sensorijk'][0]+1},"
                    + f"{dic[f'{fol}/{res}_sensorijk'][1]+1},"
                    + f"{dic[f'{fol}/{res}_sensorijk'][2]+1}",
                )
                dic["axis"].set_title(
                    "REGION "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
            else:
                for nwell in range(dic[f"{fol}/{res}_nowells"]):
                    dic = wells_site(dic, i, nfol, ndeck, nwell)
                dic["axis"].set_title(
                    "REGION "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
    dic["axis"].set_ylabel(units[i])
    dic["axis"].set_xlabel("Time")
    handles, labels = plt.gca().get_legend_handles_labels()
    order = np.argsort(labels)
    dic["axis"].legend([handles[idx] for idx in order], [labels[idx] for idx in order])
    dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
    dic["fig"].savefig(
        f"{dic['where']}/{dic['id']}summary_{quantity}_regional_reference.png",
        bbox_inches="tight",
    )
    plt.close()


def over_time_distance(dic):
    """
    Function to plot the distance from the closest saturation cell to the site border

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["fig"], dic["axis"], dic["nmarker"] = [], [], 0
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
                if dic["reading"] == "resdata":
                    points = positions_resdata(dic, fol, res, nrst)
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
                    dic[f"{fol}/{res}_indicator_plot"].append(
                        closest_distance.min() / 1000.0
                    )
                else:
                    dic[f"{fol}/{res}_indicator_plot"].append(
                        (dic[f"{fol}/site_boxf"][0] - dic[f"{fol}/site_boxi"][0])
                        / (2.0 * 1000.0)
                    )
            dic = handle_labels_distance(dic, nfol, res, fol, j)

        dic["axis"][-1].set_title(
            "Minimum "
            + r"CO$_2$"
            + f' distance to the borders (saturation thr={dic["sat_thr"]} [-])'
        )
        dic["axis"][-1].set_ylabel("Distance [km]")
        dic["axis"][-1].set_xlabel("Time")
        handles, labels = plt.gca().get_legend_handles_labels()
        order = np.argsort(labels)
        dic["axis"][-1].legend(
            [handles[idx] for idx in order], [labels[idx] for idx in order]
        )
        dic["axis"][-1].xaxis.set_tick_params(rotation=45)
        dic["fig"][-1].savefig(
            f"{dic['where']}/{dic['id']}distance_from_border.png", bbox_inches="tight"
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


def positions_resdata(dic, fol, res, nrst):
    """
    Function to extract the point coordinates using resdata

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
            label = dic[f"l{res}"]
            dic["axis"][-1].step(
                dic[f"{fol}/{res}_dates"],
                dic[f"{fol}/{res}_indicator_plot"],
                color=dic["colors"][-1],
                linestyle=dic["linestyle"][-1],
                label=label,
            )
        if res != "reference":
            label = dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})"
            dic["axis"][-1].step(
                dic[f"{fol}/{res}_dates"],
                dic[f"{fol}/{res}_indicator_plot"],
                color=dic["colors"][-j - 1],
                linestyle=dic["linestyle"][-nfol - 1],
                label=label,
            )
            dic["nmarker"] += 1
    else:
        if j == 0:
            j_j = 0
            nfol = 1
        else:
            j_j = j + 1
        label = dic[f"l{res}"]
        dic["axis"][-1].step(
            dic[f"{fol}/{res}_dates"],
            dic[f"{fol}/{res}_indicator_plot"],
            color=dic["colors"][-1 - j_j],
            linestyle=dic["linestyle"][-nfol - 2],
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
                if quantity == f"FLO{dic[f'{fol}/{res}liq']}I+":
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        quant[(k + 1) * (len(dic[f"{fol}/site_xmx"]) - 1) - 1] = 0
                if quantity == f"FLO{dic[f'{fol}/{res}liq']}I-":
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        quant[k * (len(dic[f"{fol}/site_xmx"]) - 1)] = 0
                if quantity == f"FLO{dic[f'{fol}/{res}liq']}J+":
                    for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                        quant[
                            (len(dic[f"{fol}/site_ymy"]) - 2)
                            * (len(dic[f"{fol}/site_xmx"]) - 1)
                            + k
                        ] = 0
                if quantity == f"FLO{dic[f'{fol}/{res}liq']}J-":
                    for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                        quant[k] = 0
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
        r"$\max$(REF-SITE), $\max$(REF)="
        + f"{np.array(dic[f'reference_maximum_{quantity}']).max():.2E}"
    )
    dic["axis"][nqua].set_ylabel(dic["units"][nqua])
    dic["axis"][nqua].set_xlabel("Time")
    dic["axis"][nqua].legend()
    dic["axis"][nqua].xaxis.set_tick_params(rotation=45)
    dic["fig"][nqua].savefig(
        f"{dic['where']}/{dic['id']}maximum_{dic['names'][nqua]}_difference_over_time.png",
        bbox_inches="tight",
    )
    plt.close()


def over_time_sensor(dic, nqua, quantity):
    """
    Function to plot the the quantities on the sensor.

    Args:
        dic (dict): Global dictionary with required parameters

    """
    fig, axis = plt.subplots()
    dic["figs"].append(fig)
    dic["axiss"].append(axis)
    dic["nmarker"] = 0
    for nfol, fol in enumerate(dic["folders"]):
        for j, res in enumerate(["reference"] + dic[f"{fol}_sites"]):
            dic[f"{fol}/{res}_sensor_{quantity}"] = []
            for nrst in range(dic[f"{fol}/{res}_num_rst"]):
                dic[f"{fol}/{res}_sensor_{quantity}"].append(
                    dic[f"{fol}/{res}_{quantity}_array"][nrst][
                        dic[f"{fol}/{res}_sensor"]
                    ]
                )
            if dic["compare"]:
                if nfol == 0 and res == "reference":
                    label = dic[f"l{res}"]
                    dic["axiss"][nqua].step(
                        dic[f"{fol}/{res}_dates"],
                        dic[f"{fol}/{res}_sensor_{quantity}"],
                        color=dic["colors"][-1],
                        linestyle=dic["linestyle"][-1],
                        label=label,  # +" (Grid 0 40m)"
                    )
                    # referror = np.array(dic[f"{fol}/{res}_sensor_{quantity}"])
                if res != "reference":
                    label = dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})"
                    dic["axiss"][nqua].step(
                        dic[f"{fol}/{res}_dates"],
                        dic[f"{fol}/{res}_sensor_{quantity}"],
                        color=dic["colors"][-j - 1],
                        linestyle=dic["linestyle"][-nfol - 2],
                        label=label,
                    )
                    dic["nmarker"] += 1
                    # quanti = np.array(dic[f"{fol}/{res}_sensor_{quantity}"])
                    # #error = np.max(np.abs(referror - quanti))
                    # error = np.linalg.norm(referror - quanti)
                    # #if quantity == "pressure":
                    # print(fol, res, quantity, f"{error:.2f}")
            else:
                dic["axiss"][nqua].step(
                    dic[f"{fol}/{res}_dates"],
                    dic[f"{fol}/{res}_sensor_{quantity}"],
                    color=dic["colors"][-1 - j],
                    linestyle=dic["linestyle"][-1 - j],
                    label=dic[f"l{res}"],
                )
            location = f"({dic[f'{fol}/{res}_sensor_location'][0]/1000.}, "
            location += f"{dic[f'{fol}/{res}_sensor_location'][1]/1000.}, "
            location += f"{dic[f'{fol}/{res}_sensor_location'][2]/1000.})"
    dic["axiss"][nqua].set_title(f"Sensor location {location} [km] (Case 4)")
    dic["axiss"][nqua].set_ylabel(f"{dic['units'][nqua]}")
    dic["axiss"][nqua].set_xlabel("Time")
    # if quantity != "pressure":
    dic["axiss"][nqua].legend()
    dic["axiss"][nqua].xaxis.set_tick_params(rotation=45)
    dic["figs"][nqua].savefig(
        f"{dic['where']}/{dic['id']}sensor_{dic['names'][nqua]}_over_time.png",
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
        label = (
            dic[f"l{res}"]
            + f" ({dic['lfolders'][nfol]})"
            + r", $\max$="
            + f"{np.array(dic[f'{fol}/{res}_maximum_{quantity}']).max():.2E}"
        )
        dic["axis"][nqua].step(
            dic[f"{fol}/{res}_dates"],
            dic[f"{fol}/{res}_difference_{quantity}"],
            color=dic["colors"][nfol % len(dic["colors"])],
            linestyle=dic["linestyle"][j % len(dic["linestyle"])],
            label=label,
        )
    else:
        label = (
            dic[f"l{res}"]
            + r", $\max$="
            + f"{np.array(dic[f'{fol}/{res}_maximum_{quantity}']).max():.2E}"
        )
        dic["axis"][nqua].step(
            dic[f"{fol}/{res}_dates"],
            dic[f"{fol}/{res}_difference_{quantity}"],
            color=dic["colors"][-j - 2],
            linestyle=dic["linestyle"][-j - 2],
            label=label,
        )
    return dic


if __name__ == "__main__":
    main()
