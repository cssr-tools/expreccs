# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0914,C0302,E1102,R0912,C0301

"""
Script to plot the top surface for the reference, regional, and site reservoirs.
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from alive_progress import alive_bar
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


def plot_results(dic):
    """
    Plot the 2D maps/1D projections for the different quantities

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    font = {"family": "normal", "weight": "normal", "size": 16}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": dic["latex"],
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
    dic["rhog_ref"] = 1.86843  # CO2 reference density
    dic["sat_thr"] = 0.01  # Threshold for the plume location [-]
    if dic["compare"]:
        dic["where"] = "compare/"
        dic["folders"] = sorted(
            [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name)]
        )
        if f"{os.getcwd()}/compare" not in dic["folders"]:
            os.system("mkdir compare")
        else:
            dic["folders"].remove(f"{os.getcwd()}/compare")
        dic["id"] = "compare" + dic["folders"][0].split("/")[-1] + "_"
    else:
        dic["where"] = f"{dic['folders'][0]}/postprocessing"
        dic["id"] = dic["folders"][0].split("/")[-1] + "_"
    dic["lfolders"] = [name.split("/")[-1].replace("_", " ") for name in dic["folders"]]
    plotting_settings(dic)
    if dic["use"] == "resdata":
        reading_resdata(dic)
    else:
        reading_opm(dic)
    dic["tot"] = 0
    dic["tod"] = 0
    if dic["plot"] in ["reference", "regional", "site"]:
        dic["tot"] = 1
        plt.rcParams.update({"axes.grid": False})
        geological_maps(dic)
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
    over_time_distance(dic)
    for i, quantity in enumerate(quantites):
        summary_plot(dic, i, quantity)
    dic["fig"], dic["axis"], dic["figs"], dic["axiss"] = [], [], [], []
    print("Over time maximum difference and sensor:")
    with alive_bar(len(dic["quantity"])) as bar_animation:
        for nqua, quantity in enumerate(dic["quantity"]):
            bar_animation()
            over_time_max_difference(dic, nqua, quantity)
            over_time_sensor(dic, nqua, quantity)
    if dic["compare"]:
        return
    plt.rcParams.update({"axes.grid": False})
    for fol in dic["folders"]:
        for _ in dic[f"{fol}_decks"]:
            dic["tot"] += 1
        for _ in dic[f"{fol}_sites"]:
            dic["tod"] += 1
    geological_maps(dic)
    final_time_maps(dic)
    final_time_maps_difference(dic)


def plotting_settings(dic):
    """
    Set the color/line styles and labels

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["colors"] = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "k",
        "#e377c2",
        "#8c564b",
        "#bcbd22",
        "#17becf",
        "k",
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
        (0, (3, 1, 1, 1)),
        (0, (3, 1, 1, 1, 1, 1)),
        "--",
        "solid",
    ]
    dic["lreference"] = r"REF"
    dic["lregional"] = r"REG"
    for i in range(dic["iterations"]):
        dic[f"lregional_{i+1}"] = f"REG{i+1}"
    dic["lsite_pres"] = r"S$_{pressure}$"
    dic["lsite_pres2p"] = r"S$_{pressure 2p}$"
    dic["lsite_flux"] = r"S$_{flux}$"
    dic["lsite_porvproj"] = r"S$_{pore\;volume}$"
    dic["lsite_wells"] = r"S$_{wells}$"
    dic["lsite_closed"] = r"S$_{closed}$"
    dic["lsite_open"] = r"S$_{open}$"
    dic["cmaps"] = [
        "jet",
        "brg",
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
        "FLOGASI+",
        "FLOGASJ+",
        "mass",
        "diss",
        "gas",
    ]
    dic["names"] = [
        "saturation",
        "pressure",
        "watfluxi+",
        "watfluxj+",
        "gasfluxi+",
        "gasfluxj+",
        "CO$_2$ total",
        "CO$_2$ dissolved",
        "CO$_2$ gas",
    ]
    dic["units"] = [
        "Saturation [-]",
        "Pressure [bar]",
        "H$_2$O velocity x+ direction [m day$^{-1}$]",
        "H$_2$O velocity y+ direction [m day$^{-1}$]",
        "CO$_2$ velocity x+ direction [m day$^{-1}$]",
        "CO$_2$ velocity y+ direction [m day$^{-1}$]",
        "CO$_2$ in-place [kt]",
        "CO$_2$ in-place (liquid phase) [kt]",
        "CO$_2$ in-place (gas phase) [kt]",
    ]


def wells_site(dic, nquan, nfol, ndeck, nwell):
    """
    Plot the injection rates and BHP

    Args:
        dic (dict): Global dictionary\n
        nquan (int): Current number of quantity\n
        nfol (int): Current number of folder\n
        ndeck (int): Current number of deck\n
        nwell (str): Name of well

    Returns:
        dic (dict): Modified global dictionary

    """
    fol = dic["folders"][nfol]
    res = dic[f"{fol}_decks"][ndeck]
    opm = ["WBHP", "WGIR", "WWIR"]
    if dic["use"] == "resdata":
        yvalues = dic[f"{fol}/{res}_smsp"][f"{opm[nquan]}:{nwell}"].values
    else:
        yvalues = dic[f"{fol}/{res}_smsp"][f"{opm[nquan]}:{nwell}"]
    if opm[nquan] == "WGIR":
        yvalues = [val * GAS_DEN_REF * KG_TO_MT * 365.25 for val in yvalues]
    if opm[nquan] == "WWIR":
        yvalues = [val * WAT_DEN_REF * KG_TO_MT * 365.25 for val in yvalues]
    if int(nwell[4:]) > 0:
        marker = dic["markers"][int(nwell[4:])]
    else:
        marker = ""
    dic["axis"].step(
        dic[f"{fol}/{res}_smsp_dates"],
        yvalues,
        label=f"{nwell} "
        + dic[f"l{res}"]
        + f" {' ('+dic['lfolders'][nfol]+')' if dic['compare'] else ''}",
        color=dic["colors"][-ndeck - 1],
        linestyle=dic["linestyle"][-ndeck - 1 - nfol * len(dic[f"{fol}_decks"])],
        marker=marker,
        lw=2,
    )
    # if ndeck == 0 and nfol > 0:
    #     return
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
    #     return
    # dic["axis"].step(
    #     dic[f"{fol}/{res}_smsp_dates"],
    #     yvalues,
    #     label=f"INJ{nwell}",
    #     color=dic["colors"][nwell],
    #     linestyle=dic["linestyle"][-1 + nwell],
    #     lw=3,
    # )
    # if ndeck != 1 or nfol > 0:  # or nwell > 0:
    #     return
    # dic["axis"].step(
    #     dic[f"{fol}/{res}_smsp_dates"],
    #     yvalues,
    #     label=f"INJ{nwell}",
    #     color=dic["colors"][nwell],
    #     linestyle=dic["linestyle"][-1 + nwell],
    #     lw=3,
    # )


def summary_site(dic, nfol, ndeck, opmn):
    """
    Plot summary quantities

    Args:
        dic (dict): Global dictionary\n
        nfol (int): Current number of folder\n
        ndeck (int): Current number of deck\n
        opmn (str): Summary name to plot

    Returns:
        dic (dict): Modified global dictionary

    """
    # if dic["compare"]:
    #     marker = dic["markers"][nfol]
    # else:
    #     marker = ""
    fol = dic["folders"][nfol]
    res = dic[f"{fol}_decks"][ndeck]
    if dic["use"] == "resdata":
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
        return
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


def handle_site_summary(dic, i, quantity):
    """
    Routine for the summary quantities at the site location

    Args:
        dic (dict): Global dictionary\n
        i (int): Index of the quantity\n
        quantity (str): Name of the quantity

    Returns:
        dic (dict): Modified global dictionary

    """
    for nfol, fol in enumerate(dic["folders"]):
        for ndeck, res in enumerate(dic[f"{fol}_decks"]):
            if "regional" in res:
                continue
            if quantity in ["PR", "GIP", "GIPL", "GIPG"]:
                summary_site(dic, nfol, ndeck, f"R{quantity}:1")
                dic["axis"].set_title(
                    "SITE "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
            elif quantity in ["BPR", "BGIP", "BGIPL", "BGIPG", "BFLOWI", "BFLOWJ"]:
                summary_site(
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
                for nwell in dic[f"{fol}/{res}_nowells"]:
                    if nwell[3] == "S":
                        wells_site(dic, i, nfol, ndeck, nwell)
                dic["axis"].set_title(
                    "SITE "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )


def summary_plot(dic, i, quantity):
    """
    Plot the summary quantities

    Args:
        dic (dict): Global dictionary\n
        i (int): Index of the quantity\n
        quantity (str): Name of the quantity

    Returns:
        dic (dict): Modified global dictionary

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
    handle_site_summary(dic, i, quantity)
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
                summary_site(dic, nfol, ndeck, f"F{quantity}")
                dic["axis"].set_title(
                    "REGION "
                    + f"{'' if dic['compare'] else '('+dic['lfolders'][nfol]+')'}"
                )
            elif quantity in ["BPR", "BGIP", "BGIPL", "BGIPG", "BFLOWI", "BFLOWJ"]:
                summary_site(
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
                for nwell in dic[f"{fol}/{res}_nowells"]:
                    wells_site(dic, i, nfol, ndeck, nwell)
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
    Plot the distance from the closest saturation cell to the site border

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["fig"], dic["axis"], dic["nmarker"] = [], [], 0
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    ntot = 0
    for nfol, fol in enumerate(dic["folders"]):
        for j, res in enumerate(["reference"] + dic[f"{fol}_sites"]):
            ntot += 1
    print("Over time distance:")
    with alive_bar(ntot) as bar_animation:
        for nfol, fol in enumerate(dic["folders"]):
            dic["dx_half_size"] = 0.5 * (
                dic[f"{fol}/site_xmx"][1:] - dic[f"{fol}/site_xmx"][:-1]
            )
            dic["dy_half_size"] = 0.5 * (
                dic[f"{fol}/site_ymy"][1:] - dic[f"{fol}/site_ymy"][:-1]
            )
            for j, res in enumerate(["reference"] + dic[f"{fol}_sites"]):
                bar_animation()
                dic[f"{fol}/{res}_indicator_plot"] = []
                for quantity in dic["quantity"]:
                    dic[f"{fol}/{res}_difference_{quantity}"] = []
                for nrst in range(dic[f"{fol}/{res}_num_rst"]):
                    if dic["use"] == "resdata":
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
                handle_labels_distance(dic, nfol, res, fol, j)

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
    Extract the point coordinates using opm

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Name of the reservoir\n
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
    Extract the point coordinates using resdata

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Name of the reservoir\n
        nrst (int): Indice for the schedule

    Returns:
        points (list): x,y,z coordinates

    """
    points = []
    if res == "reference":
        indx = dic[f"{fol}/{res}_phiv"] < 0
        indx[dic[f"{fol}/{res}_mask"]] = [
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
    Manage the labeling for better visualization.

    Args:
        dic (dict): Global dictionary\n
        nfol (int): Indice for the color\n
        res (str): Name of the reservoir\n
        fol (str): Name of the output folder\n
        j (int): Indice for the reservoir

    Returns:
        dic (dict): Modified global dictionary

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
                linestyle=dic["linestyle"][-nfol - 2],
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


def over_time_max_difference(dic, nqua, quantity):
    """
    Plot the max difference between pressure/saturation.

    Args:
        dic (dict): Global dictionary\n
        nqua (int): Index of the quantity\n
        quantity (str): Name of the quantity

    Returns:
        dic (dict): Modified global dictionary

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
                if quantity == "FLOWATI+":
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        quant[(k + 1) * (len(dic[f"{fol}/site_xmx"]) - 1) - 1] = 0
                if quantity == "FLOWATJ+":
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
            handle_labels_difference(dic, res, j, nqua, nfol)
    dic["axis"][nqua].set_title(
        r"$\max|$REF-SITE|, $\max$(REF)="
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
    Plot the quantities on the sensor.

    Args:
        dic (dict): Global dictionary\n
        nqua (int): Index of the quantity\n
        quantity (str): Name of the quantity

    Returns:
        dic (dict): Modified global dictionary

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
                if j == 0:
                    j_j = 0
                else:
                    j_j = j + 1
                dic["axiss"][nqua].step(
                    dic[f"{fol}/{res}_dates"],
                    dic[f"{fol}/{res}_sensor_{quantity}"],
                    color=dic["colors"][-1 - j_j],
                    linestyle=dic["linestyle"][-1 - j],
                    label=dic[f"l{res}"],
                )
    dic["axiss"][nqua].set_title("Sensor")
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
    Manage the labeling to improve the visualization.

    Args:
        dic (dict): Global dictionary\n
        res (str): Name of the reservoir\n
        j (int): Indice for the reservoir\n
        nqua (int): Current number of quantity\n
        nfol (int): Current number of folder

    Returns:
        dic (dict): Modified global dictionary

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
