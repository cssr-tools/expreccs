# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=E1102,R0914

"""
Script to plot the 2D top surfaces
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from alive_progress import alive_bar
from mpl_toolkits.axes_grid1 import make_axes_locatable


def final_time_maps(dic):
    """
    Plot the 2D maps for the different reservoirs and quantities

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    print("Final time 2d maps:")
    with alive_bar(dic["tot"]) as bar_animation:
        for nfol, fol in enumerate(dic["folders"]):
            for res in dic[f"{fol}_decks"]:
                bar_animation()
                # es = "regional"
                manage_name(dic, res)
                for j, quantity in enumerate(dic["quantity"]):
                    # j = 2
                    # quantity = "FLOWATI+"
                    dic[f"{fol}/{res}_{quantity}_plot"] = np.zeros(
                        [
                            len(dic[f"{fol}/{dic['name']}_ymy"]) - 1,
                            len(dic[f"{fol}/{dic['name']}_xmx"]) - 1,
                        ]
                    )
                    fig, axis = plt.subplots()
                    for i in np.arange(0, len(dic[f"{fol}/{dic['name']}_ymy"]) - 1):
                        dic[f"{fol}/{res}_{quantity}_plot"][-1 - i, :] = dic[
                            f"{fol}/{res}_{quantity}_array"
                        ][-1][
                            i
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1) : (i + 1)
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1)
                        ]
                    imag = axis.pcolormesh(
                        dic[f"{fol}/{dic['name']}_xcor"] / 1000.0,
                        dic[f"{fol}/{dic['name']}_ycor"] / 1000.0,
                        dic[f"{fol}/{res}_{quantity}_plot"],
                        shading="flat",
                        cmap=dic["cmaps"][j],
                    )
                    axis.set_xticks(
                        np.linspace(
                            0 * 5 + dic[f"{fol}/{dic['name']}_xcor"].min() / 1000.0,
                            0 * 10 + dic[f"{fol}/{dic['name']}_xcor"].max() / 1000.0,
                            6,
                        )
                    )
                    axis.set_yticks(
                        np.linspace(
                            0 * 5 + dic[f"{fol}/{dic['name']}_ycor"].min() / 1000.0,
                            0 * 10 + dic[f"{fol}/{dic['name']}_ycor"].max() / 1000.0,
                            6,
                        )
                    )
                    axis.set_title(dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})")
                    # axis.set_title(f"REFERENCE (Case 4)")
                    # axis.set_title("REGIONAL (Cases 1, 2, and 3)")
                    # axis.set_title(f"REGIONAL: {dic['lfolders'][nfol]} (Case 2)")
                    maxp = dic[f"{fol}/{res}_{quantity}_plot"].max()
                    minp = dic[f"{fol}/{res}_{quantity}_plot"].min()
                    # minp, maxp = -0.55, 0.43
                    axis.axis("scaled")
                    axis.set_xlabel("Easting [km]")
                    axis.set_ylabel("Northing [km]")
                    # axis.spines['left'].set_color('white')
                    # axis.yaxis.label.set_color('white')
                    # axis.tick_params(axis='y', colors='white')
                    cax = (make_axes_locatable(axis)).append_axes(
                        "right", size="5%", pad=0.05
                    )
                    vect = np.linspace(
                        minp,
                        maxp,
                        5,
                        endpoint=True,
                    )
                    fig.colorbar(
                        imag,
                        cax=cax,
                        orientation="vertical",
                        ticks=vect,
                        label=dic["units"][j],
                        format=lambda x, _: f"{x:.2f}",
                    )
                    # axis.set_xlim([5, 10])
                    # axis.set_ylim([5, 10])
                    imag.set_clim(
                        minp,
                        maxp,
                    )
                    fig.savefig(
                        f"{dic['where']}/{dic['id']}{res}_{dic['names'][j]}.png",
                        bbox_inches="tight",
                    )
                    plt.close()


def final_time_maps_difference(dic):
    """
    Plot the difference between the reference and site simulations
    in the last time step

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    print("Final time 2d maps difference:")
    with alive_bar(dic["tod"]) as bar_animation:
        for fol in dic["folders"]:
            for res in dic[f"{fol}_sites"]:
                bar_animation()
                manage_name(dic, res)
                for j, quantity in enumerate(dic["quantity"]):
                    dic[f"{fol}/{res}_difference_{quantity}"] = (
                        dic[f"{fol}/reference_{quantity}_array"][-1][
                            dic[f"{fol}/reference_fipn"] != 2
                        ]
                        - dic[f"{fol}/{res}_{quantity}_array"][-1]
                    )
                    if quantity in ["FLOWATI+", "FLOGASI+"]:
                        for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                            dic[f"{fol}/{res}_difference_{quantity}"][
                                (k + 1) * (len(dic[f"{fol}/site_xmx"]) - 1) - 1
                            ] = 0
                    if quantity in ["FLOWATJ+", "FLOGASJ+"]:
                        for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                            dic[f"{fol}/{res}_difference_{quantity}"][
                                (len(dic[f"{fol}/site_ymy"]) - 2)
                                * (len(dic[f"{fol}/site_xmx"]) - 1)
                                + k
                            ] = 0
                    dic[f"{fol}/{res}_difference_{quantity}_plot"] = np.zeros(
                        [
                            len(dic[f"{fol}/site_ymy"]) - 1,
                            len(dic[f"{fol}/site_xmx"]) - 1,
                        ]
                    )
                    for i in np.arange(0, len(dic[f"{fol}/site_ymy"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}_plot"][-1 - i, :] = dic[
                            f"{fol}/{res}_difference_{quantity}"
                        ][
                            i
                            * (len(dic[f"{fol}/site_xmx"]) - 1) : (i + 1)
                            * (len(dic[f"{fol}/site_xmx"]) - 1)
                        ]
                    fig, axis = plt.subplots()
                    imag = axis.pcolormesh(
                        dic[f"{fol}/{dic['name']}_xcor"] / 1000.0,
                        dic[f"{fol}/{dic['name']}_ycor"] / 1000.0,
                        dic[f"{fol}/{res}_difference_{quantity}_plot"],
                        shading="flat",
                        cmap="seismic",
                    )
                    axis.axis(
                        [
                            dic[f"{fol}/{dic['name']}_xcor"].min() / 1000.0,
                            dic[f"{fol}/{dic['name']}_xcor"].max() / 1000.0,
                            dic[f"{fol}/{dic['name']}_ycor"].min() / 1000.0,
                            dic[f"{fol}/{dic['name']}_ycor"].max() / 1000.0,
                        ]
                    )
                    axis.axis("scaled")
                    axis.set_xticks(
                        np.linspace(
                            dic[f"{fol}/{dic['name']}_xcor"].min() / 1000.0,
                            dic[f"{fol}/{dic['name']}_xcor"].max() / 1000.0,
                            6,
                        )
                    )
                    axis.set_yticks(
                        np.linspace(
                            dic[f"{fol}/{dic['name']}_ycor"].min() / 1000.0,
                            dic[f"{fol}/{dic['name']}_ycor"].max() / 1000.0,
                            6,
                        )
                    )
                    axis.set_xlabel("Easting [km]")
                    axis.set_ylabel("Northing [km]")
                    axis.set_title(
                        r"SITE $\sum$|REF-"
                        + f"{dic[f'l{res}']}"
                        + f"|={abs(dic[f'{fol}/{res}_difference_{quantity}_plot']).sum():.2E}"
                    )
                    # axis.spines['left'].set_color('white')
                    # axis.yaxis.label.set_color('white')
                    # axis.tick_params(axis='y', colors='white')
                    maxp = dic[f"{fol}/{res}_difference_{quantity}_plot"].max()
                    minp = dic[f"{fol}/{res}_difference_{quantity}_plot"].min()
                    # minp, maxp = -0.27, 0.27
                    divider = make_axes_locatable(axis)
                    cax = divider.append_axes("right", size="5%", pad=1e-3)
                    vect = np.linspace(
                        minp,
                        maxp,
                        5,
                        endpoint=True,
                    )
                    fig.colorbar(
                        imag,
                        cax=cax,
                        orientation="vertical",
                        ticks=vect,
                        label=dic["units"][j],
                        format=lambda x, _: f"{x:.2f}",
                    )
                    imag.set_clim(
                        minp,
                        maxp,
                    )
                    # axis.set_xticks(dic[f"{fol}/{dic['name']}_xmx"][::30])
                    # axis.set_yticks(dic[f"{fol}/{dic['name']}_ymy"][::30])
                    fig.savefig(
                        f"{dic['where']}/{dic['id']}difference_{res}_{dic['names'][j]}.png",
                        bbox_inches="tight",
                    )
                    plt.close()


def geological_maps(dic):
    """
    Plot the 2D maps for the reservoir model

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    print("Static 2d maps:")
    with alive_bar(dic["tot"]) as bar_animation:
        for fol in dic["folders"]:
            for res in dic[f"{fol}_decks"]:
                bar_animation()
                manage_name(dic, res)
                for quan in dic[f"{fol}/{res}_static"]:
                    if quan == "fipn" and dic[f"{fol}/{res}_sensorijk"][2] == 0:
                        dic[f"{fol}/{res}_{quan}"][
                            dic[f"{fol}/{res}_sensorijk"][0]
                            + dic[f"{fol}/{res}_sensorijk"][1]
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1)
                        ] = 3
                    dic[f"{fol}/{res}_{quan}_plot"] = np.zeros(
                        [
                            len(dic[f"{fol}/{dic['name']}_ymy"]) - 1,
                            len(dic[f"{fol}/{dic['name']}_xmx"]) - 1,
                        ]
                    )
                    for i in np.arange(0, len(dic[f"{fol}/{dic['name']}_ymy"]) - 1):
                        dic[f"{fol}/{res}_{quan}_plot"][-1 - i, :] = dic[
                            f"{fol}/{res}_{quan}"
                        ][
                            i
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1) : (i + 1)
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1)
                        ]
                    fig, axis = plt.subplots()
                    if quan == "fipn":
                        axis.pcolormesh(
                            dic[f"{fol}/{dic['name']}_xcor"] / 1000.0,
                            dic[f"{fol}/{dic['name']}_ycor"] / 1000.0,
                            dic[f"{fol}/{res}_{quan}_plot"],
                            shading="flat",
                            cmap=colors.ListedColormap(["red", "gray", "blue"]),
                        )
                        axis.set_title(
                            dic[f"l{res}"] + " (site location in red, sensor in blue)"
                        )
                    else:
                        imag = axis.pcolormesh(
                            dic[f"{fol}/{dic['name']}_xcor"] / 1000.0,
                            dic[f"{fol}/{dic['name']}_ycor"] / 1000.0,
                            dic[f"{fol}/{res}_{quan}_plot"],
                            shading="flat",
                            cmap="jet",
                        )
                        axis.set_title(dic[f"l{res}"] + f" {quan}")
                        maxp = dic[f"{fol}/{res}_{quan}_plot"].max()
                        minp = dic[f"{fol}/{res}_{quan}_plot"].min()
                        # minp, maxp = -0.27, 0.27
                        divider = make_axes_locatable(axis)
                        cax = divider.append_axes("right", size="5%", pad=1e-3)
                        vect = np.linspace(
                            minp,
                            maxp,
                            5,
                            endpoint=True,
                        )
                        fig.colorbar(
                            imag,
                            cax=cax,
                            orientation="vertical",
                            ticks=vect,
                            format=lambda x, _: f"{x:.2f}",
                        )
                    # axis.set_title("REG/REF (Case 1)")
                    # axis.set_title("REGIONAL")
                    axis.axis("scaled")
                    name = dic["name"]
                    axis.set_xlabel(
                        f"L={(dic[f'{fol}/{name}_xmx'][-1]-dic[f'{fol}/{name}_xmx'][0])/1000.:.0f}"
                        + f" [km], dx={dic[f'{fol}/{name}_xmx'][1]:.0f} [m]"
                    )
                    axis.set_ylabel(
                        f"W={(dic[f'{fol}/{name}_ymy'][-1]-dic[f'{fol}/{name}_ymy'][0])/1000.:.0f}"
                        + f" [km], dy={dic[f'{fol}/{name}_ymy'][1]:.0f} [m]"
                    )
                    # axis.set_xticks(dic[f"{fol}/{dic['name']}_xcor"][0] / 1000.0)
                    # axis.set_yticks(dic[f"{fol}/{dic['name']}_ymy"] / 1000.0)
                    axis.set_xticks([])
                    axis.set_yticks([])
                    # axis.grid(True, color="k", lw=1)
                    # plt.setp(axis.get_xticklabels(), visible=False)
                    # plt.setp(axis.get_yticklabels(), visible=False)
                    if quan == "fipn":
                        quan = "fipnum_sensor"
                    fig.savefig(
                        f"{dic['where']}/{dic['id']}{res}_{quan}.png",
                        bbox_inches="tight",
                    )
                    plt.close()


def manage_name(dic, res):
    """
    Figure out the folder names

    Args:
        dic (dict): Global dictionary\n
        res (str): Complete name of the simulated model

    Returns:
        dic (dict): Modified global dictionary

    """
    if "regional" in res:
        dic["name"] = "regional"
    elif "site" in res:
        dic["name"] = "site"
    else:
        dic["name"] = res
