# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302,E1102,R0912,R0914,R0915,C0301

"""Plot top surface for the reference, regional, and site reservoirs"""

import os
import shutil
import sys
from contextlib import nullcontext
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from alive_progress import alive_bar
from expreccs.visualization.reading import reading_simulations
from expreccs.visualization.maps2d import (
    final_time_maps,
    final_time_maps_difference,
    geological_maps,
)

GAS_DEN_REF = 1.86843  # kg/sm3
WAT_DEN_REF = 998.108  # kg/sm3
KG_TO_KT = 1e-6
KG_TO_MT = 1e-9


def plot_results(dic):
    """Plot the 2D maps/1D projections for the different quantities"""
    font = {"family": "normal", "weight": "normal", "size": 16}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") != "None",
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
    dic["rhog_ref"] = 1.86843
    dic["sat_thr"] = 0.01
    if dic["compare"]:
        dic["where"] = "compare/"
        dic["folders"] = sorted(
            [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name)]
        )
        compare_path = f"{os.getcwd()}/compare"
        if compare_path not in dic["folders"]:
            os.system("mkdir compare")
        else:
            dic["folders"].remove(compare_path)
        dic["id"] = "compare" + dic["folders"][0].split("/")[-1] + "_"
    else:
        folder0 = dic["folders"][0]
        dic["where"] = f"{folder0}/postprocessing"
        dic["id"] = folder0.split("/")[-1] + "_"
    dic["lfolders"] = [name.split("/")[-1].replace("_", " ") for name in dic["folders"]]
    plotting_settings(dic)
    reading_simulations(dic)
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
    over_time_distance(dic)
    for i, quantity in enumerate(quantites):
        summary_plot(dic, i, quantity)
    dic["fig"], dic["axis"], dic["figs"], dic["axiss"] = [], [], [], []
    print("Over time maximum difference and sensor:")
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(len(dic["quantity"]), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for nqua, quantity in enumerate(dic["quantity"]):
            if show_progress:
                bar_animation()
            over_time_max_difference(dic, nqua, quantity)
            over_time_sensor(dic, nqua, quantity)
    if dic["compare"]:
        return
    plt.rcParams.update({"axes.grid": False})
    for fol in dic["folders"]:
        decks = dic[fol]["decks"]
        sites = dic[fol]["sites"]
        dic["tot"] += len(decks)
        dic["tod"] += len(sites)
    geological_maps(dic)
    final_time_maps(dic)
    final_time_maps_difference(dic)


def plotting_settings(dic):
    """Set the color/line styles and labels"""
    dic["colors"] = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "k",
        "#e377c2",
        "#8c564b",
        "#17becf",
        "#bcbd22",
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
    """Plot the injection rates and BHP"""
    fol = dic["folders"][nfol]
    res = dic[fol]["decks"][ndeck]
    smsp = dic[fol][res]["smsp"]
    dates = dic[fol][res]["smsp_dates"]
    opm = ["WBHP", "WGIR", "WWIR"]
    key = f"{opm[nquan]}:{nwell}"
    yvalues = smsp[key]
    if opm[nquan] == "WGIR":
        yvalues = [val * GAS_DEN_REF * KG_TO_MT * 365.25 for val in yvalues]
    if opm[nquan] == "WWIR":
        yvalues = [val * WAT_DEN_REF * KG_TO_MT * 365.25 for val in yvalues]
    marker = dic["markers"][int(nwell[4:])] if int(nwell[4:]) > 0 else ""
    dic["axis"].step(
        dates,
        yvalues,
        label=f"{nwell} "
        + dic[f"l{res}"]
        + f" {' ('+dic['lfolders'][nfol]+')' if dic['compare'] else ''}",
        color=dic["colors"][-ndeck - 1],
        linestyle=dic["linestyle"][-ndeck - 1 - nfol * len(dic[fol]["decks"])],
        marker=marker,
        lw=2,
    )


def summary_site(dic, nfol, ndeck, opmn):
    """Plot summary quantities"""
    fol = dic["folders"][nfol]
    res = dic[fol]["decks"][ndeck]
    smsp = dic[fol][res]["smsp"]
    dates = dic[fol][res]["smsp_dates"]
    sensor = dic[fol][res]["sensor"]
    yvalues = smsp[f"{opmn}"]
    if opmn[1:4] == "GIP":
        yvalues = [val * GAS_DEN_REF * KG_TO_KT for val in yvalues]
    if opmn[:6] == "BFLOWI":
        dy = dic[fol][res]["dy"][sensor]
        dz = dic[fol][res]["dz"][sensor]
        poro = dic[fol][res]["poro"][sensor]
        yvalues = [val / (poro * dy * dz) for val in yvalues]
    if opmn[:6] == "BFLOWJ":
        dx = dic[fol][res]["dx"][sensor]
        dz = dic[fol][res]["dz"][sensor]
        poro = dic[fol][res]["poro"][sensor]
        yvalues = [val / (poro * dx * dz) for val in yvalues]
    if ndeck == 0 and nfol > 0:
        return
    if ndeck == 0:
        dic["axis"].step(
            dates, yvalues, label=dic["lreference"], color=dic["colors"][-ndeck - 1]
        )
    else:
        dic["axis"].step(
            dates,
            yvalues,
            label=dic[f"l{res}"]
            + f"{' ('+dic['lfolders'][nfol]+')' if dic['compare'] else ''}",
            color=dic["colors"][-ndeck - 1],
            linestyle=dic["linestyle"][-nfol - 2],
        )


def handle_site_summary(dic, i, quantity):
    """Routine for the summary quantities at the site location"""
    for nfol, fol in enumerate(dic["folders"]):
        decks = dic[fol]["decks"]
        lfolder = dic["lfolders"][nfol]
        for ndeck, res in enumerate(decks):
            if "regional" in res:
                continue
            title = "SITE " + f"{'' if dic['compare'] else '('+lfolder+')'}"
            if quantity in ["PR", "GIP", "GIPL", "GIPG"]:
                summary_site(dic, nfol, ndeck, f"R{quantity}:1")
                dic["axis"].set_title(title)
            elif quantity in ["BPR", "BGIP", "BGIPL", "BGIPG", "BFLOWI", "BFLOWJ"]:
                sensorijk = dic[fol][res]["sensorijk"]
                summary_site(
                    dic,
                    nfol,
                    ndeck,
                    f"{quantity}:{sensorijk[0]+1},{sensorijk[1]+1},{sensorijk[2]+1}",
                )
                dic["axis"].set_title(title)
            else:
                for nwell in dic[fol][res]["nowells"]:
                    if nwell[3] == "S":
                        wells_site(dic, i, nfol, ndeck, nwell)
                dic["axis"].set_title(title)


def summary_plot(dic, i, quantity):
    """Plot the summary quantities"""
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
        decks = dic[fol]["decks"]
        lfolder = dic["lfolders"][nfol]
        for ndeck, res in enumerate(decks):
            if "site" in res:
                continue
            title = "REGION " + f"{'' if dic['compare'] else '('+lfolder+')'}"
            if quantity in ["PR", "GIP", "GIPL", "GIPG"]:
                summary_site(dic, nfol, ndeck, f"F{quantity}")
                dic["axis"].set_title(title)
            elif quantity in ["BPR", "BGIP", "BGIPL", "BGIPG", "BFLOWI", "BFLOWJ"]:
                sensorijk = dic[fol][res]["sensorijk"]
                summary_site(
                    dic,
                    nfol,
                    ndeck,
                    f"{quantity}:{sensorijk[0]+1},{sensorijk[1]+1},{sensorijk[2]+1}",
                )
                dic["axis"].set_title(title)
            else:
                for nwell in dic[fol][res]["nowells"]:
                    wells_site(dic, i, nfol, ndeck, nwell)
                dic["axis"].set_title(title)
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
    """Plot the distance from the closest saturation cell to the site border"""
    dic["fig"], dic["axis"], dic["nmarker"] = [], [], 0
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    ntot = 0
    for nfol, fol in enumerate(dic["folders"]):
        ntot += len(["reference"] + dic[fol]["sites"])
    print("Over time distance:")
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(ntot, bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for nfol, fol in enumerate(dic["folders"]):
            xmx = dic[fol]["site"]["xmx"]
            ymy = dic[fol]["site"]["ymy"]
            boxi = dic[fol]["site_boxi"]
            boxf = dic[fol]["site_boxf"]
            dic["dx_half_size"] = 0.5 * (xmx[1:] - xmx[:-1])
            dic["dy_half_size"] = 0.5 * (ymy[1:] - ymy[:-1])
            bx0 = boxi[0] + dic["dx_half_size"][0]
            bx1 = boxf[0] - dic["dx_half_size"][-1]
            by0 = boxi[1] + dic["dy_half_size"][0]
            by1 = boxf[1] - dic["dy_half_size"][-1]
            for j, res in enumerate(["reference"] + dic[fol]["sites"]):
                if show_progress:
                    bar_animation()
                dic[fol][res]["indicator_plot"] = []
                for quantity in dic["quantity"]:
                    dic[fol][res][f"difference_{quantity}"] = []
                num_rst = dic[fol][res]["num_rst"]
                for nrst in range(num_rst):
                    points = positions(dic, fol, res, nrst)
                    if points.size > 0:
                        xs = points[:, 0]
                        ys = points[:, 1]
                        d0 = np.min(np.abs(xs - bx0))
                        d1 = np.min(np.abs(xs - bx1))
                        d2 = np.min(np.abs(ys - by0))
                        d3 = np.min(np.abs(ys - by1))
                        dic[fol][res]["indicator_plot"].append(
                            min(d0, d1, d2, d3) / 1000.0
                        )
                    else:
                        dic[fol][res]["indicator_plot"].append(
                            (boxf[0] - boxi[0]) / (2.0 * 1000.0)
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


def positions(dic, fol, res, nrst):
    """Get the cell centers"""
    grid = dic[fol][res]["grid"]
    indicator = dic[fol][res]["indicator_array"]
    if res == "reference":
        fipn = dic[fol]["reference"]["fipn"]
        indx = indicator[nrst] & (fipn == 1)
        indices = np.nonzero(indx)[0]
    else:
        indices = np.nonzero(indicator[nrst])[0]
    if indices.size == 0:
        return np.empty((0, 3))
    x_a = []
    y_a = []
    z_a = []
    for index in indices:
        coords = grid.xyz_from_active_index(index)
        x_coords = coords[0]
        y_coords = coords[1]
        z_coords = coords[2]
        x_center = 0.5 * (x_coords[-1] - x_coords[0]) + x_coords[0]
        y_center = 0.5 * (y_coords[-1] - y_coords[0]) + y_coords[0]
        z_center = 0.5 * (z_coords[-1] - z_coords[0]) + z_coords[0]
        x_a.append(x_center)
        y_a.append(y_center)
        z_a.append(z_center)
    points = np.stack([np.array(x_a), np.array(y_a), np.array(z_a)], axis=-1)
    return points


def handle_labels_distance(dic, nfol, res, fol, j):
    """Manage the labeling for better visualization"""
    dates = dic[fol][res]["dates"]
    values = dic[fol][res]["indicator_plot"]
    if dic["compare"]:
        if nfol == 0 and res == "reference":
            label = dic[f"l{res}"]
            dic["axis"][-1].step(
                dates,
                values,
                color=dic["colors"][-1],
                linestyle=dic["linestyle"][-1],
                label=label,
            )
        if res != "reference":
            label = dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})"
            dic["axis"][-1].step(
                dates,
                values,
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
            dates,
            values,
            color=dic["colors"][-1 - j_j],
            linestyle=dic["linestyle"][-nfol - 2],
            label=label,
        )


def over_time_max_difference(dic, nqua, quantity):
    """Plot the max difference between pressure/saturation"""
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    dic[f"reference_maximum_{quantity}"] = []
    for nfol, fol in enumerate(dic["folders"]):
        ref_array = dic[fol]["reference"][f"{quantity}_array"]
        ref_fipn = dic[fol]["reference"]["fipn"]
        site_xmx = dic[fol]["site"]["xmx"]
        site_ymy = dic[fol]["site"]["ymy"]
        nx = len(site_xmx) - 1
        ny = len(site_ymy) - 1

        mask_ref = ref_fipn == 1

        if quantity == "FLOWATI+":
            boundary_mask_site = np.ones(np.sum(mask_ref), dtype=bool)
            boundary_mask_site[np.arange(nx - 1, nx * ny, nx)] = False
        elif quantity == "FLOWATJ+":
            boundary_mask_site = np.ones(np.sum(mask_ref), dtype=bool)
            boundary_mask_site[(ny - 1) * nx : ny * nx] = False
        else:
            boundary_mask_site = None

        for j, res in enumerate(dic[fol]["sites"]):
            dic[fol][res][f"difference_{quantity}"] = []
            dic[fol][res][f"maximum_{quantity}"] = []
            res_array = dic[fol][res][f"{quantity}_array"]
            num_rst = dic[fol][res]["num_rst"]

            for nrst in range(num_rst):
                ref_values_full = np.asarray(ref_array[nrst])
                res_values = np.asarray(res_array[nrst])

                ref_masked = ref_values_full[mask_ref]

                if boundary_mask_site is not None:
                    ref_masked = ref_masked[boundary_mask_site]
                    res_effective = res_values[boundary_mask_site]
                else:
                    res_effective = res_values

                quant = np.abs(ref_masked - res_effective)

                max_diff = np.max(quant)
                max_res = np.max(res_values)

                dic[fol][res][f"difference_{quantity}"].append(max_diff)
                dic[fol][res][f"maximum_{quantity}"].append(max_res)

                if j == 0:
                    dic[f"reference_maximum_{quantity}"].append(np.max(ref_masked))

            handle_labels_difference(dic, res, j, nqua, nfol)

    dic["axis"][nqua].set_title(
        r"$\max|$REF-SITE|, $\max$(REF)="
        + f"{np.max(dic[f'reference_maximum_{quantity}']):.2E}"
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
    """Plot the quantities on the sensor"""
    fig, axis = plt.subplots()
    dic["figs"].append(fig)
    dic["axiss"].append(axis)
    dic["nmarker"] = 0
    for nfol, fol in enumerate(dic["folders"]):
        for j, res in enumerate(["reference"] + dic[fol]["sites"]):
            sensor = dic[fol][res]["sensor"]
            dates = dic[fol][res]["dates"]
            array = dic[fol][res][f"{quantity}_array"]
            num_rst = dic[fol][res]["num_rst"]
            dic[fol][res][f"sensor_{quantity}"] = []
            for nrst in range(num_rst):
                dic[fol][res][f"sensor_{quantity}"].append(array[nrst][sensor])
            values = dic[fol][res][f"sensor_{quantity}"]
            if dic["compare"]:
                if nfol == 0 and res == "reference":
                    label = dic[f"l{res}"]
                    dic["axiss"][nqua].step(
                        dates,
                        values,
                        color=dic["colors"][-1],
                        linestyle=dic["linestyle"][-1],
                        label=label,
                    )
                if res != "reference":
                    label = dic[f"l{res}"] + f" ({dic['lfolders'][nfol]})"
                    dic["axiss"][nqua].step(
                        dates,
                        values,
                        color=dic["colors"][-j - 1],
                        linestyle=dic["linestyle"][-nfol - 2],
                        label=label,
                    )
                    dic["nmarker"] += 1
            else:
                if j == 0:
                    j_j = 0
                else:
                    j_j = j + 1
                dic["axiss"][nqua].step(
                    dates,
                    values,
                    color=dic["colors"][-1 - j_j],
                    linestyle=dic["linestyle"][-1 - j],
                    label=dic[f"l{res}"],
                )
    dic["axiss"][nqua].set_title("Sensor")
    dic["axiss"][nqua].set_ylabel(f"{dic['units'][nqua]}")
    dic["axiss"][nqua].set_xlabel("Time")
    dic["axiss"][nqua].legend()
    dic["axiss"][nqua].xaxis.set_tick_params(rotation=45)
    dic["figs"][nqua].savefig(
        f"{dic['where']}/{dic['id']}sensor_{dic['names'][nqua]}_over_time.png",
        bbox_inches="tight",
    )
    plt.close()


def handle_labels_difference(dic, res, j, nqua, nfol):
    """Manage the labeling to improve the visualization"""
    quantity = dic["quantity"][nqua]
    fol = dic["folders"][nfol]
    dates = dic[fol][res]["dates"]
    diff = dic[fol][res][f"difference_{quantity}"]
    maxv = np.max(dic[fol][res][f"maximum_{quantity}"])
    if dic["compare"]:
        label = (
            dic[f"l{res}"]
            + f" ({dic['lfolders'][nfol]})"
            + r", $\max$="
            + f"{maxv:.2E}"
        )
        dic["axis"][nqua].step(
            dates,
            diff,
            color=dic["colors"][nfol % len(dic["colors"])],
            linestyle=dic["linestyle"][j % len(dic["linestyle"])],
            label=label,
        )
    else:
        label = dic[f"l{res}"] + r", $\max$=" + f"{maxv:.2E}"
        dic["axis"][nqua].step(
            dates,
            diff,
            color=dic["colors"][-j - 2],
            linestyle=dic["linestyle"][-j - 2],
            label=label,
        )
