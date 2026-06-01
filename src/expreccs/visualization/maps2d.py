# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=E1102,R0913,R0914,R0917

"""Script to plot the 2D top surfaces"""

import sys
from contextlib import nullcontext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from alive_progress import alive_bar
from mpl_toolkits.axes_grid1 import make_axes_locatable


def reshape_to_2d(array_1d, nx, ny):
    """Convert flat array to 2D grid (robust to oversized arrays)."""
    expected = nx * ny

    if array_1d.size > expected:
        array_1d = array_1d[:expected]

    return array_1d.reshape(ny, nx)[::-1, :]


def plot_map(
    x,
    y,
    data,
    title,
    filename,
    cmap,
    units=None,
    xticks=True,
    yticks=True,
    show_colorbar=True,
    difference=False,
):
    """Reusable 2D plotting function."""

    fig, axis = plt.subplots()

    imag = axis.pcolormesh(
        x,
        y,
        data,
        shading="flat",
        cmap=cmap,
    )

    axis.axis("scaled")

    if xticks:
        axis.set_xticks(np.linspace(np.min(x), np.max(x), 6))
    else:
        axis.set_xticks([])

    if yticks:
        axis.set_yticks(np.linspace(np.min(y), np.max(y), 6))
    else:
        axis.set_yticks([])

    axis.set_xlabel("Easting [km]")
    axis.set_ylabel("Northing [km]")
    axis.set_title(title)

    if show_colorbar:
        maxp = np.max(data)
        minp = np.min(data)

        if difference and minp < 0 < maxp:
            bnd = max(abs(maxp), abs(minp))
            maxp = bnd
            minp = -bnd

        cax = make_axes_locatable(axis).append_axes("right", size="5%", pad=0.05)

        ticks = np.linspace(minp, maxp, 5)

        fig.colorbar(
            imag,
            cax=cax,
            orientation="vertical",
            ticks=ticks,
            label=units,
            format=lambda x, _: f"{x:.2f}",
        )

        imag.set_clim(minp, maxp)

    fig.savefig(filename, bbox_inches="tight")
    plt.close()


def manage_name(res):
    """Figure out the folder names"""
    if "regional" in res:
        return "regional"
    if "site" in res:
        return "site"
    return res


def final_time_maps(dic):
    """Plot the 2D maps for the different reservoirs and quantities"""
    print("Final time 2d maps:")

    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(dic["tot"], bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for nfol, fol in enumerate(dic["folders"]):
            for res in dic[fol]["decks"]:
                if show_progress:
                    bar_animation()
                name = manage_name(res)

                nx = len(dic[fol][name]["xmx"]) - 1
                ny = len(dic[fol][name]["ymy"]) - 1

                x = dic[fol][name]["xcor"] / 1000.0
                y = dic[fol][name]["ycor"] / 1000.0

                for j, quantity in enumerate(dic["quantity"]):

                    data = reshape_to_2d(
                        dic[fol][res][f"{quantity}_array"][-1],
                        nx,
                        ny,
                    )

                    title = dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})"

                    filename = f"{dic['where']}/{dic['id']}{res}_{dic['names'][j]}.png"

                    plot_map(
                        x,
                        y,
                        data,
                        title,
                        filename,
                        cmap=dic["cmaps"][j],
                        units=dic["units"][j],
                    )


def final_time_maps_difference(dic):
    """Plot differences between reference and site at final timestep"""
    print("Final time 2d maps difference:")
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(dic["tod"], bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for fol in dic["folders"]:
            for res in dic[fol]["sites"]:
                if show_progress:
                    bar_animation()
                name = manage_name(res)

                nx = len(dic[fol]["site"]["xmx"]) - 1
                ny = len(dic[fol]["site"]["ymy"]) - 1

                x = dic[fol][name]["xcor"] / 1000.0
                y = dic[fol][name]["ycor"] / 1000.0

                for j, quantity in enumerate(dic["quantity"]):

                    diff = (
                        dic[fol]["reference"][f"{quantity}_array"][-1][
                            dic[fol]["reference"]["fipn"] != 2
                        ]
                        - dic[fol][res][f"{quantity}_array"][-1]
                    )

                    if quantity in ["FLOWATI+", "FLOGASI+"]:
                        for k in range(ny):
                            diff[(k + 1) * nx - 1] = 0

                    if quantity in ["FLOWATJ+", "FLOGASJ+"]:
                        for k in range(nx):
                            diff[(ny - 1) * nx + k] = 0

                    data = reshape_to_2d(diff, nx, ny)

                    magnitude = np.abs(np.sum(data))

                    title = (
                        r"SITE $\sum$|REF-" + f"{dic[f'l{res}']}" + f"|={magnitude:.2E}"
                    )

                    filename = f"{dic['where']}/{dic['id']}difference_{res}_{dic['names'][j]}.png"

                    plot_map(
                        x,
                        y,
                        data,
                        title,
                        filename,
                        cmap="seismic",
                        units=dic["units"][j],
                        difference=True,
                    )


def geological_maps(dic):
    """Plot static geological maps"""
    print("Static 2d maps:")
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(dic["tot"], bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for fol in dic["folders"]:
            for res in dic[fol]["decks"]:
                if show_progress:
                    bar_animation()
                name = manage_name(res)

                nx = len(dic[fol][name]["xmx"]) - 1
                ny = len(dic[fol][name]["ymy"]) - 1

                x = dic[fol][name]["xcor"] / 1000.0
                y = dic[fol][name]["ycor"] / 1000.0

                for quan in dic[fol][res]["static"]:

                    if quan == "fipn" and dic[fol][res]["sensorijk"][2] == 0:
                        dic[fol][res][quan][
                            dic[fol][res]["sensorijk"][0]
                            + dic[fol][res]["sensorijk"][1] * nx
                        ] = 3

                    data = reshape_to_2d(
                        dic[fol][res][quan],
                        nx,
                        ny,
                    )

                    if quan == "fipn":
                        cmap = colors.ListedColormap(["red", "gray", "blue"])
                        title = dic[f"l{res}"] + " (site in red, sensor in blue)"
                        show_cb = False
                    else:
                        cmap = "jet"
                        title = dic[f"l{res}"] + f" {quan}"
                        show_cb = True

                    filename = (
                        f"{dic['where']}/{dic['id']}{res}_"
                        + ("fipnum_sensor" if quan == "fipn" else quan)
                        + ".png"
                    )

                    plot_map(
                        x,
                        y,
                        data,
                        title,
                        filename,
                        cmap=cmap,
                        units=None,
                        xticks=False,
                        yticks=False,
                        show_colorbar=show_cb,
                    )
