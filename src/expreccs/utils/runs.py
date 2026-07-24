# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Utiliy functions to run the studies"""

import os
import subprocess

from expreccs.utils.mapboundaries import (
    aquaflux,
    porv_projections,
    porv_regional_segmentation,
    temporal_interpolation_flux,
    temporal_interpolation_pressure,
)
from expreccs.utils.writefile import write_files
from expreccs.visualization.plotting import plot_results


def simulations(dic, name):
    """Run OPM Flow"""
    command = (
        f"{dic['flow']} --output-dir={dic[f'fsim{name}']} "
        f"{dic[f'fpre{name}']}{name.upper()}.DATA"
    )
    subprocess.run(command, shell=True, check=True)


def plotting(dic):
    """Generate the figures"""
    dic["folders"] = [dic["fol"]]
    post_dir = f"{dic['fol']}/postprocessing"
    if not os.path.exists(post_dir):
        os.makedirs(post_dir, exist_ok=True)
    os.chdir(post_dir)
    print("\nPlot: Generation of png figures, please wait.")
    plot_results(dic)


def run_models(dic):
    """Run the reference, regional, and site geological models"""
    if dic["mode"] in ["all", "reference"]:
        write_files(dic, "reference")
        simulations(dic, "reference")
    if dic["mode"] in ["all", "regional", "regional_site"]:
        porv_regional_segmentation(dic)
        write_files(dic, "regional")
        simulations(dic, "regional")
    if dic["mode"] in ["all", "site", "regional_site"]:
        if dic["site_bctype"][0] in ["flux", "pres", "pres2p"]:
            aquaflux(dic)
            if dic["site_bctype"][0] in ["pres", "pres2p"]:
                temporal_interpolation_pressure(dic)
            else:
                temporal_interpolation_flux(dic)
        elif dic["site_bctype"][0] == "porvproj":
            porv_projections(dic)
        write_files(dic, f"site_{dic['site_bctype'][0]}")
        simulations(dic, f"site_{dic['site_bctype'][0]}")
