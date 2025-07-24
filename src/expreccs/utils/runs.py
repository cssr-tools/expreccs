# SPDX-FileCopyrightText: 2023-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to run the studies.
"""

import os
from expreccs.visualization.plotting import plot_results
from expreccs.utils.writefile import write_files
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
        f"{dic['flow']} --output-dir={dic[f'fsim{name}']} "
        f"{dic[f'fpre{name}']}{name.upper()}.DATA & wait\n"
    )


def plotting(dic):
    """
    Generate the figures

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    dic["folders"] = [dic["fol"]]
    if not os.path.exists(f"{dic['fol']}/postprocessing"):
        os.system(f"mkdir {dic['fol']}/postprocessing")
    os.chdir(f"{dic['fol']}/postprocessing")
    print("\nPlot: Generation of png figures, please wait.")
    plot_results(dic)


def run_models(dic):
    """
    Run the reference, regional, and site geological models

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["mode"] in ["all", "reference"]:
        write_files(dic, "reference")
        simulations(dic, "reference")
    if dic["mode"] in ["all", "regional", "regional_site"]:
        porv_regional_segmentation(dic)
        write_files(dic, "regional")
        simulations(dic, "regional")
    if dic["mode"] in ["all", "site", "regional_site"]:
        if dic["site_bctype"][0] in ["flux", "pres", "pres2p"]:
            if dic["use"] == "resdata":
                aquaflux_resdata(dic)
            else:
                aquaflux_opm(dic)
            if dic["site_bctype"][0] in ["pres", "pres2p"]:
                temporal_interpolation_pressure(dic)
            else:
                temporal_interpolation_flux(dic)
        elif dic["site_bctype"][0] == "porvproj":
            porv_projections(dic)
        write_files(dic, f"site_{dic['site_bctype'][0]}")
        simulations(dic, f"site_{dic['site_bctype'][0]}")
