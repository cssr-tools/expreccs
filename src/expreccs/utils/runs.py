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
    Function to Run Flow

    Args:
        dic (dict): Global dictionary with required parameters

    """
    os.system(
        f"{dic['flow']} --output-dir={dic['exe']}/{dic['fol']}/output/{name} "
        f"{dic['exe']}/{dic['fol']}/preprocessing/{name}/{name.upper()}.DATA  & wait\n"
    )


def plotting(dic, time):
    """
    Function to run the plotting.py file

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["folders"] = [dic["fol"]]
    dic["time"] = time
    os.chdir(f"{dic['exe']}/{dic['fol']}/postprocessing")
    plot_exe = [
        "python",
        f"{dic['pat']}/visualization/plotting.py",
        f"-t {time}",
        f"-f {dic['fol']}",
        f"-m {dic['plot']}",
        f"-r {dic['reading']}",
    ]
    print(" ".join(plot_exe))
    plot_results(dic)


def run_models(dic):
    """Run the reference, regional, and site"""
    dic = set_gridmako(dic, dic["z_xy"])
    if dic["mode"] in ["all", "reference"]:
        write_files(dic, "reference")
        simulations(dic, "reference")
    if dic["mode"] in ["all", "regional", "noreference"]:
        dic = porv_regional_segmentation(dic)
        write_files(dic, "regional")
        simulations(dic, "regional")
    if dic["mode"] in ["all", "site", "noreference"]:
        if dic["site_bctype"] in ["flux", "pres", "pres2p"]:
            if dic["reading"] == "resdata":
                dic = aquaflux_resdata(dic)
            else:
                dic = aquaflux_opm(dic)
            if dic["site_bctype"] in ["pres", "pres2p"]:
                dic = temporal_interpolation_pressure(dic)
            else:
                dic = temporal_interpolation_flux(dic)
        elif dic["site_bctype"] == "porvproj":
            dic = porv_projections(dic)
        write_files(dic, f"site_{dic['site_bctype']}")
        simulations(dic, f"site_{dic['site_bctype']}")
    return dic
