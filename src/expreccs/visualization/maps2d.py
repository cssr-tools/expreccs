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
            name = "site" if "site" in res else res
            for j, quantity in enumerate(dic["quantity"]):
                dic[f"{fol}/{res}_{quantity}_plot"] = np.zeros(
                    [
                        len(dic[f"{fol}/{name}_ymy"]) - 1,
                        len(dic[f"{fol}/{name}_xmx"]) - 1,
                    ]
                )
                for i in np.arange(0, len(dic[f"{fol}/{name}_ymy"]) - 1):
                    dic[f"{fol}/{res}_{quantity}_plot"][-1 - i, :] = dic[
                        f"{fol}/{res}_{quantity}_array"
                    ][-1][
                        i
                        * (len(dic[f"{fol}/{name}_xmx"]) - 1) : (i + 1)
                        * (len(dic[f"{fol}/{name}_xmx"]) - 1)
                    ]
                fig, axis = plt.subplots()
                maxp = dic[f"{fol}/{res}_{quantity}_plot"].max()
                minp = dic[f"{fol}/{res}_{quantity}_plot"].min()
                if quantity == "pressure":
                    imag = axis.pcolormesh(
                        dic[f"{fol}/{res}_xcor"] / 1000.0,
                        dic[f"{fol}/{res}_ycor"] / 1000.0,
                        dic[f"{fol}/{res}_{quantity}_plot"],
                        shading="flat",
                        cmap=dic["cmaps"][j],
                    )
                else:
                    imag = axis.pcolormesh(
                        dic[f"{fol}/{res}_xcor"] / 1000.0,
                        dic[f"{fol}/{res}_ycor"] / 1000.0,
                        dic[f"{fol}/{res}_{quantity}_plot"],
                        shading="flat",
                        cmap=dic["cmaps"][j],
                    )
                axis.set_title(dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})")
                axis.axis("scaled")
                axis.set_xlabel("Easting [km]")
                axis.set_ylabel("Northing [km]")
                axis.set_xticks(
                    np.linspace(
                        dic[f"{fol}/{res}_xcor"].min() / 1000.0,
                        dic[f"{fol}/{res}_xcor"].max() / 1000.0,
                        6,
                    )
                )
                axis.set_yticks(
                    np.linspace(
                        dic[f"{fol}/{res}_ycor"].min() / 1000.0,
                        dic[f"{fol}/{res}_ycor"].max() / 1000.0,
                        6,
                    )
                )
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
                imag.set_clim(
                    minp,
                    maxp,
                )
                fig.savefig(
                    f"{dic['where']}/{res}_{dic['names'][j]}.png", bbox_inches="tight"
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
            # name = "site" if "site" in res else res
            for j, quantity in enumerate(dic["quantity"]):
                dic[f"{fol}/{res}_difference_{quantity}"] = (
                    dic[f"{fol}/reference_{quantity}_array"][-1][
                        dic[f"{fol}/reference_fipn"] == 1
                    ]
                    - dic[f"{fol}/{res}_{quantity}_array"][-1]
                )
                if quantity == "flooili+":
                    for k in range(len(dic[f"{fol}/site_ymy"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}"][
                            (k + 1) * (len(dic[f"{fol}/site_xmx"]) - 1) - 1
                        ] = 0
                if quantity == "flooilj+":
                    for k in range(len(dic[f"{fol}/site_xmx"]) - 1):
                        dic[f"{fol}/{res}_difference_{quantity}"][
                            (len(dic[f"{fol}/site_ymy"]) - 2)
                            * (len(dic[f"{fol}/site_xmx"]) - 1)
                            + k
                        ] = 0
                dic[f"{fol}/{res}_difference_{quantity}_plot"] = np.zeros(
                    [len(dic[f"{fol}/site_ymy"]) - 1, len(dic[f"{fol}/site_xmx"]) - 1]
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
                    dic[f"{fol}/{res}_xcor"] / 1000.0,
                    dic[f"{fol}/{res}_ycor"] / 1000.0,
                    dic[f"{fol}/{res}_difference_{quantity}_plot"],
                    shading="flat",
                    cmap=dic["cmaps"][j],
                )
                axis.axis(
                    [
                        dic[f"{fol}/{res}_xcor"].min() / 1000.0,
                        dic[f"{fol}/{res}_xcor"].max() / 1000.0,
                        dic[f"{fol}/{res}_ycor"].min() / 1000.0,
                        dic[f"{fol}/{res}_ycor"].max() / 1000.0,
                    ]
                )
                axis.axis("scaled")
                axis.set_xticks(
                    np.linspace(
                        dic[f"{fol}/{res}_xcor"].min() / 1000.0,
                        dic[f"{fol}/{res}_xcor"].max() / 1000.0,
                        6,
                    )
                )
                axis.set_yticks(
                    np.linspace(
                        dic[f"{fol}/{res}_ycor"].min() / 1000.0,
                        dic[f"{fol}/{res}_ycor"].max() / 1000.0,
                        6,
                    )
                )
                axis.set_xlabel("Easting [km]")
                axis.set_ylabel("Northing [km]")
                axis.set_title(
                    r"$\sum$|REF-"
                    + f"{dic[f'l{res}']}"
                    + f"|={abs(dic[f'{fol}/{res}_difference_{quantity}_plot']).sum():.2E}"
                )
                divider = make_axes_locatable(axis)
                cax = divider.append_axes("right", size="5%", pad=1e-3)
                vect = np.linspace(
                    dic[f"{fol}/{res}_difference_{quantity}_plot"].min(),
                    dic[f"{fol}/{res}_difference_{quantity}_plot"].max(),
                    5,
                    endpoint=True,
                )
                fig.colorbar(
                    imag,
                    cax=cax,
                    orientation="vertical",
                    ticks=vect,
                    label=dic["units"][j],
                    format=lambda x, _: f"{x:.3f}",
                )
                imag.set_clim(
                    dic[f"{fol}/{res}_difference_{quantity}_plot"].min(),
                    dic[f"{fol}/{res}_difference_{quantity}_plot"].max(),
                )
                # axis.set_xticks(dic[f"{fol}/{name}_xmx"][::30])
                # axis.set_yticks(dic[f"{fol}/{name}_ymy"][::30])
                fig.savefig(
                    f"{dic['where']}/difference_{res}_{dic['names'][j]}.png",
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
            j = 0
            name = "site" if "site" in res else res
            dic[f"{fol}/{res}_fipn_plot"] = np.zeros(
                [
                    len(dic[f"{fol}/{name}_ymy"]) - 1,
                    len(dic[f"{fol}/{name}_xmx"]) - 1,
                ]
            )
            for i in np.arange(0, len(dic[f"{fol}/{name}_ymy"]) - 1):
                dic[f"{fol}/{res}_fipn_plot"][-1 - i, :] = dic[f"{fol}/{res}_fipn"][
                    i
                    * (len(dic[f"{fol}/{name}_xmx"]) - 1) : (i + 1)
                    * (len(dic[f"{fol}/{name}_xmx"]) - 1)
                ]
            fig, axis = plt.subplots()
            axis.pcolormesh(
                dic[f"{fol}/{res}_xcor"] / 1000.0,
                dic[f"{fol}/{res}_ycor"] / 1000.0,
                dic[f"{fol}/{res}_fipn_plot"],
                shading="flat",
                cmap=dic["cmaps"][j],
            )
            axis.set_title(dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})")
            axis.axis("scaled")
            axis.set_xlabel(
                f"L = {dic[f'{fol}/{name}_xmx'][-1]/1000. - dic[f'{fol}/{name}_xmx'][0]/1000.} [km]"
            )
            axis.set_ylabel(
                f"W = {dic[f'{fol}/{name}_ymy'][-1]/1000. - dic[f'{fol}/{name}_ymy'][0]/1000.} [km]"
            )
            axis.set_xticks(dic[f"{fol}/{res}_xcor"][0] / 1000.0)
            axis.set_yticks(dic[f"{fol}/{name}_ymy"] / 1000.0)
            axis.grid(True, color="k", lw=1)
            plt.setp(axis.get_xticklabels(), visible=False)
            plt.setp(axis.get_yticklabels(), visible=False)
            fig.savefig(f"{dic['where']}/{res}_fipnum.png", bbox_inches="tight")
            plt.close()
