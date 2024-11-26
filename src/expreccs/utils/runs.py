# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to run the studies.
"""
import os
from expreccs.visualization.plotting import plot_results
from expreccs.utils.writefile import set_gridmako, write_files
from expreccs.utils.mapboundaries import (
    aquaflux_resdata,
    aquaflux_opm,
    porv_projections,
    porv_regional_segmentation,
    temporal_interpolation_flux,
    temporal_interpolation_pressure,
)


def simulations(dic, name):
    """
    Run OPM Flow

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the input deck

    Returns:
        None

    """
    os.system(
        f"{dic['flow']} --output-dir={dic['exe']}/{dic['fol']}/output/{name} "
        f"{dic['exe']}/{dic['fol']}/preprocessing/{name}/{name.upper()}.DATA & wait\n"
    )


def plotting(dic, time):
    """
    Generate the figures

    Args:
        dic (dict): Global dictionary\n
        time (float): Execution time to be printed at the end.

    Returns:
        None

    """
    dic["folders"] = [dic["fol"]]
    dic["time"] = time
    os.chdir(f"{dic['exe']}/{dic['fol']}/postprocessing")
    plot_exe = [
        "python3",
        f"{dic['pat']}/visualization/plotting.py",
        f"-t {time}",
        f"-f {dic['fol']}",
        f"-m {dic['plot']}",
        f"-r {dic['reading']}",
        f"-l {dic['latex']}",
    ]
    print(" ".join(plot_exe))
    plot_results(dic)


def run_models(dic):
    """
    Run the reference, regional, and site geological models

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    set_gridmako(dic, dic["z_xy"])
    if dic["mode"] in ["all", "reference"]:
        write_files(dic, "reference")
        simulations(dic, "reference")
    if dic["mode"] in ["all", "regional", "noreference"]:
        porv_regional_segmentation(dic)
        write_files(dic, "regional")
        simulations(dic, "regional")
    if dic["mode"] in ["all", "site", "noreference"]:
        if dic["site_bctype"] in ["flux", "pres", "pres2p"]:
            if dic["reading"] == "resdata":
                aquaflux_resdata(dic)
            else:
                aquaflux_opm(dic)
            if dic["site_bctype"] in ["pres", "pres2p"]:
                temporal_interpolation_pressure(dic)
            else:
                temporal_interpolation_flux(dic)
        elif dic["site_bctype"] == "porvproj":
            porv_projections(dic)
        write_files(dic, f"site_{dic['site_bctype']}")
        simulations(dic, f"site_{dic['site_bctype']}")
