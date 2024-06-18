# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to plot the 2D top surfaces
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def final_time_maps(dic):
    """
    Function to plot the 2D maps for the different reservoirs and quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    for nfol, fol in enumerate(dic["folders"]):
        for res in dic[f"{fol}_decks"]:
            # es = "regional"
            dic = manage_name(dic, res)
            for j, quantity in enumerate(dic["quantity"][:2]):
                # j = 2
                # quantity = "FLOWATI+"
                dic[f"{fol}/{res}_{quantity}_plot"] = np.zeros(
                    [
                        len(dic[f"{fol}/{dic['name']}_ymy"]) - 1,
                        len(dic[f"{fol}/{dic['name']}_xmx"]) - 1,
                    ]
                )
                fig, axis = plt.subplots()
                if "site" in res:
                    if res[-1].isdigit():
                        rwh = res[:-2]
                    else:
                        rwh = res
                    for i in np.arange(0, len(dic[f"{fol}/{dic['name']}_ymy"]) - 1):
                        dic[f"{fol}/{res}_{quantity}_plot"][i, :] = dic[
                            f"{fol}/{res}_{quantity}_array"
                        ][-1][
                            i
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1) : (i + 1)
                            * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1)
                        ]
                    dic["xcor"] = np.load(
                        dic["exe"] + "/" + fol + f"/output/{rwh}/d2x.npy"
                    ).reshape(
                        len(dic[f"{fol}/{dic['name']}_ymy"]),
                        len(dic[f"{fol}/{dic['name']}_xmx"]),
                    )
                    dic["ycor"] = np.load(
                        dic["exe"] + "/" + fol + f"/output/{rwh}/d2y.npy"
                    ).reshape(
                        len(dic[f"{fol}/{dic['name']}_ymy"]),
                        len(dic[f"{fol}/{dic['name']}_xmx"]),
                    )
                    imag = axis.pcolormesh(
                        dic["xcor"] / 1000.0,
                        dic["ycor"] / 1000.0,
                        dic[f"{fol}/{res}_{quantity}_plot"],
                        shading="flat",
                        cmap=dic["cmaps"][j],
                    )
                    axis.set_xticks(
                        np.linspace(
                            dic["xcor"].min() / 1000.0,
                            dic["xcor"].max() / 1000.0,
                            6,
                        )
                    )
                    axis.set_yticks(
                        np.linspace(
                            dic["ycor"].min() / 1000.0,
                            dic["ycor"].max() / 1000.0,
                            6,
                        )
                    )
                else:
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
    Function to plot the difference between the reference and site simulations
    in the last time step

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    for fol in dic["folders"]:
        for res in dic[f"{fol}_sites"]:
            dic = manage_name(dic, res)
            for j, quantity in enumerate(dic["quantity"]):
                dic[f"{fol}/{res}_difference_{quantity}"] = (
                    dic[f"{fol}/reference_{quantity}_array"][-1][
                        dic[f"{fol}/reference_fipn"] == 1
                    ]
                    - dic[f"{fol}/{res}_{quantity}_array"][-1]
                )
                if quantity in ["FLOWATI+", "FLOGASI+"]:
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}"][
                            (k + 1) * (len(dic[f"{fol}/site_xmx"]) - 1) - 1
                        ] = 0
                if quantity in ["FLOWATJ-", "FLOGASJ-"]:
                    for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}"][k] = 0
                dic[f"{fol}/{res}_difference_{quantity}_plot"] = np.zeros(
                    [len(dic[f"{fol}/site_ymy"]) - 1, len(dic[f"{fol}/site_xmx"]) - 1]
                )
                if quantity in ["FLOWATI-", "FLOGASI-"]:
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}"][
                            k * (len(dic[f"{fol}/site_xmx"]) - 1)
                        ] = 0
                if quantity in ["FLOWATJ+", "FLOGASJ+"]:
                    for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}"][
                            (len(dic[f"{fol}/site_ymy"]) - 2)
                            * (len(dic[f"{fol}/site_xmx"]) - 1)
                            + k
                        ] = 0
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
    Function to plot the 2D maps for the reservoir model

    Args:
        dic (dict): Global dictionary with required parameters

    """
    for nfol, fol in enumerate(dic["folders"]):
        for res in dic[f"{fol}_decks"]:
            dic = manage_name(dic, res)
            dic[f"{fol}/{res}_fipn_plot"] = np.zeros(
                [
                    len(dic[f"{fol}/{dic['name']}_ymy"]) - 1,
                    len(dic[f"{fol}/{dic['name']}_xmx"]) - 1,
                ]
            )
            for i in np.arange(0, len(dic[f"{fol}/{dic['name']}_ymy"]) - 1):
                dic[f"{fol}/{res}_fipn_plot"][-1 - i, :] = dic[f"{fol}/{res}_fipn"][
                    i
                    * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1) : (i + 1)
                    * (len(dic[f"{fol}/{dic['name']}_xmx"]) - 1)
                ]
            fig, axis = plt.subplots()
            axis.pcolormesh(
                dic[f"{fol}/{dic['name']}_xcor"] / 1000.0,
                dic[f"{fol}/{dic['name']}_ycor"] / 1000.0,
                dic[f"{fol}/{res}_fipn_plot"],
                shading="flat",
                cmap="Set1",
            )
            axis.set_title(dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})")
            # axis.set_title("REG/REF (Case 1)")
            # axis.set_title("REGIONAL")
            axis.axis("scaled")
            name = dic["name"]
            axis.set_xlabel(
                f"L={(dic[f'{fol}/{name}_xmx'][-1] - dic[f'{fol}/{name}_xmx'][0])/1000.:.0f}"
                + f" [km], dx={dic[f'{fol}/{name}_xmx'][1]:.0f} [m]"
            )
            axis.set_ylabel(
                f"W={(dic[f'{fol}/{name}_ymy'][-1] - dic[f'{fol}/{name}_ymy'][0])/1000.:.0f}"
                + f" [km], dy={dic[f'{fol}/{name}_ymy'][1]:.0f} [m]"
            )
            # axis.set_xticks(dic[f"{fol}/{dic['name']}_xcor"][0] / 1000.0)
            # axis.set_yticks(dic[f"{fol}/{dic['name']}_ymy"] / 1000.0)
            axis.set_xticks([])
            axis.set_yticks([])
            # axis.grid(True, color="k", lw=1)
            # plt.setp(axis.get_xticklabels(), visible=False)
            # plt.setp(axis.get_yticklabels(), visible=False)
            fig.savefig(
                f"{dic['where']}/{dic['id']}{res}_fipnum.png", bbox_inches="tight"
            )
            plt.close()


def manage_name(dic, res):
    """Figure out the folder name (needs to be fixed)"""
    if "regional" in res:
        dic["name"] = "regional"
    elif "site" in res:
        dic["name"] = "site"
    else:
        dic["name"] = res
    return dic
