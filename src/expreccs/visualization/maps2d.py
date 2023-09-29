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
    for fol in dic["folders"]:
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
                if quantity == "pressure":
                    imag = axis.pcolormesh(
                        dic[f"{fol}/{res}_xcor"],
                        dic[f"{fol}/{res}_ycor"],
                        dic[f"{fol}/{res}_{quantity}_plot"],
                        shading="flat",
                        cmap="jet",
                    )
                    axis.set_title(f"{res} {quantity} [bar]")
                else:
                    imag = axis.pcolormesh(
                        dic[f"{fol}/{res}_xcor"],
                        dic[f"{fol}/{res}_ycor"],
                        dic[f"{fol}/{res}_{quantity}_plot"],
                        shading="flat",
                        cmap="jet",
                    )
                    axis.set_title(f"{res} {dic['names'][j]} [-]")
                axis.axis("scaled")
                axis.set_xlabel("[m]")
                axis.set_ylabel("[m]")
                divider = make_axes_locatable(axis)
                cax = divider.append_axes("right", size="5%", pad=0.05)
                vect = np.linspace(
                    dic[f"{fol}/{res}_{quantity}_plot"].min(),
                    dic[f"{fol}/{res}_{quantity}_plot"].max(),
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
                imag.set_clim(
                    dic[f"{fol}/{res}_{quantity}_plot"].min(),
                    dic[f"{fol}/{res}_{quantity}_plot"].max(),
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
                    dic[f"{fol}/{res}_xcor"],
                    dic[f"{fol}/{res}_ycor"],
                    dic[f"{fol}/{res}_difference_{quantity}_plot"],
                    shading="flat",
                    cmap="jet",
                )
                axis.axis(
                    [
                        dic[f"{fol}/{res}_xcor"].min(),
                        dic[f"{fol}/{res}_xcor"].max(),
                        dic[f"{fol}/{res}_ycor"].min(),
                        dic[f"{fol}/{res}_ycor"].max(),
                    ]
                )
                axis.axis("scaled")
                axis.set_xlabel("[m]")
                axis.set_ylabel("[m]")
                axis.set_title(
                    f"{dic['names'][j]} sum abs(ref-{res})"
                    + f"={abs(dic[f'{fol}/{res}_difference_{quantity}_plot']).sum():.2E}"
                    + f" [{dic['units'][j]}]"
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
                    format=lambda x, _: f"{x:.3f}",
                )
                imag.set_clim(
                    dic[f"{fol}/{res}_difference_{quantity}_plot"].min(),
                    dic[f"{fol}/{res}_difference_{quantity}_plot"].max(),
                )
                fig.savefig(
                    f"{dic['where']}/difference_{res}_{dic['names'][j]}.png",
                    bbox_inches="tight",
                )
                plt.close()
