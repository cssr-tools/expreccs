# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to back-couple from site to regional model used by expreccs.
"""

import os
import numpy as np

from expreccs.visualization.reading import (
    reading_resdata,
    reading_opm,
)
from expreccs.utils.runs import simulations
from expreccs.utils.writefile import (
    write_files,
)


def backcoupling(dic):
    """
    Function to update regional model based on the
    site model. A multiplier that compensate for the
    difference in fluxes are computed
    MULT[-X, X, -Y , Y] = Flux_site / Flux_regional
    and added to the regional model. This is done
    iterativly for number of iterations given in the input

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for iteration in range(1, int(dic["iterations"])):
        fil = ""
        if iteration > 1:
            fil = f"_{iteration-1}"
        compute_multipliers(dic, fil)
        write_folder_iter(dic, f"regional_{iteration}")
        write_files(dic, f"regional_{iteration}", iteration)
        simulations(dic, f"regional_{iteration}")

        # For now this is commented, first focusing on one way
        # i.e., from site to regional

        # if dic["site_bctype"][0] in ["flux", "pres", "pres2p"]:
        #     if dic["use"] == "resdata":
        #         aquaflux_resdata(dic, f"_{iteration}")
        #     else:
        #         aquaflux_opm(dic, f"_{iteration}")
        #     if dic["site_bctype"][0] == "flux":
        #         temporal_interpolation_flux(dic)
        #     else:
        #         temporal_interpolation_pressure(dic)
        # elif dic["site_bctype"][0] == "porvproj":
        #     porv_projections(dic)

        # write_folder_iter(dic, f"site_{dic['site_bctype'][0]}_{iteration}")
        # write_files(dic, f"site_{dic['site_bctype'][0]}_{iteration}")
        # simulations(dic, f"site_{dic['site_bctype'][0]}_{iteration}")


def write_folder_iter(dic, fil):
    """
    Write folders for the _{iteration} models

    Args:
        dic (dict): Global dictionary\n
        fil (str): Name of the geological model

    Returns:
        None

    """
    if not os.path.exists(f"{dic['fol']}/preprocessing/{fil}"):
        os.system(f"mkdir {dic['fol']}/preprocessing/{fil}")
    if not os.path.exists(f"{dic['fol']}/simulations/{fil}"):
        os.system(f"mkdir {dic['fol']}/simulations/{fil}")


def init_multipliers(dic):
    """
    Function initialize input for regional multipliers

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    numcells = (
        dic["regional_num_cells"][0]
        * dic["regional_num_cells"][1]
        * dic["regional_num_cells"][2]
    )
    for q in ["x", "x-", "y", "y-"]:
        dic["regional_mult" + q] = [1] * numcells


def compute_multipliers(dic, iteration):  # pylint: disable=R1702,R0912,R0914,R0915
    """
    Function to compute multiplier that compensate for the
    difference in fluxes
    MULT[-X, X, -Y , Y] = Flux_site / Flux_regional
    and added to the regional model

    Args:
        dic (dict): Global dictionary\n
        iteration (int): Current iteration number

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["folders"] = [dic["fol"]]
    dic["rhog_ref"] = 1.86843  # CO2 reference density
    dic["sat_thr"] = 1e-2  # Threshold for the gas saturation

    dic["quantity"] = [
        "FLOWATI+",
        "FLOWATJ+",
        "FLOWATI-",
        "FLOWATJ-",
    ]

    if dic["use"] == "resdata":
        reading_resdata(dic, False)
    else:
        reading_opm(dic, False)

    # Check for refinement
    numx = (int)(dic["site_num_cells"][0])
    numy = (int)(dic["site_num_cells"][1])
    numz = (int)(dic["site_num_cells"][2])
    dx = (int)(dic["reference_num_cells"][0] / dic["regional_num_cells"][0])
    dy = (int)(dic["reference_num_cells"][1] / dic["regional_num_cells"][1])
    dz = (int)(dic["reference_num_cells"][2] / dic["regional_num_cells"][2])
    # We dont support refinement in z
    assert dz == 1
    refine = dx > 1 or dy > 1
    nx_reg = (int)(numx / dx)
    ny_reg = (int)(numy / dy)
    nz_reg = (int)(numz / dz)

    # pylint: disable=R1702
    for fol in dic["folders"]:
        for res in dic[f"{fol}_sites"]:
            if "site_porvproj" in res or "site_pres" in res:
                for j, quantity in enumerate(dic["quantity"]):
                    if "FLOWAT" in quantity:
                        regional_fluxes = 0.0
                        local_fluxes = 0.0
                        for k, b in enumerate(dic[f"{fol}/{res}_{quantity}_array"]):
                            a = dic[f"{fol}/regional{iteration}_{quantity}_array"][k][
                                dic[f"{fol}/regional_fipn"] == 1
                            ]
                            regional_fluxes += a
                            local_fluxes += b

                        regional_fluxes = np.abs(regional_fluxes)
                        local_fluxes = np.abs(local_fluxes)

                        if not refine:
                            sum_local_fluxes = local_fluxes
                        else:
                            sum_local_fluxes = 0 * regional_fluxes
                            for k_reg in range(nz_reg):
                                for j_reg in range(ny_reg):
                                    for i_reg in range(nx_reg):
                                        ind = (
                                            i_reg
                                            + j_reg * nx_reg
                                            + k_reg * nx_reg * ny_reg
                                        )
                                        if quantity == "FLOWATI+":
                                            for j in range(dy):
                                                # for k in range(dz):
                                                ind_loc = (
                                                    i_reg * dx
                                                    + (j_reg * dy + j) * numx
                                                    + k_reg * dz * numx * numy
                                                    + dx
                                                    - 1
                                                )
                                                sum_local_fluxes[ind] += local_fluxes[
                                                    ind_loc
                                                ]
                                        elif quantity == "FLOWATI-":
                                            for j in range(dy):
                                                # for k in range(dz):
                                                ind_loc = (
                                                    i_reg * dx
                                                    + (j_reg * dy + j) * numx
                                                    + k_reg * dz * numx * numy
                                                )
                                                sum_local_fluxes[ind] += local_fluxes[
                                                    ind_loc
                                                ]
                                        elif quantity == "FLOWATJ+":
                                            for i in range(dx):
                                                # for k in range(dz):
                                                ind_loc = (
                                                    i_reg * dx
                                                    + j_reg * dy * numx
                                                    + k_reg * dz * numx * numy
                                                    + (dy - 1) * numx
                                                    + i
                                                )
                                                sum_local_fluxes[ind] += local_fluxes[
                                                    ind_loc
                                                ]
                                        elif quantity == "FLOWATJ-":
                                            for i in range(dx):
                                                # for k in range(dz):
                                                ind_loc = (
                                                    i_reg * dx
                                                    + j_reg * dy * numx
                                                    + k_reg * dz * numx * numy
                                                    + i
                                                )
                                                sum_local_fluxes[ind] += local_fluxes[
                                                    ind_loc
                                                ]

                        # compute multipliers
                        mult = sum_local_fluxes / regional_fluxes
                        mult[np.isinf(mult)] = 1
                        mult[np.isnan(mult)] = 1

                        # use 1 on the boundary
                        if quantity == "FLOWATI-":
                            for i in range(1, nx_reg):
                                for j in range(0, ny_reg):
                                    mult[i + j * nx_reg] = 1
                        elif quantity == "FLOWATJ-":
                            for i in range(0, nx_reg):
                                for j in range(1, ny_reg):
                                    mult[i + j * nx_reg] = 1
                        ll = 0

                        direction = "x"
                        if quantity == "FLOWATJ+":
                            direction = "y"
                        elif quantity == "FLOWATI-":
                            direction = "x-"
                        elif quantity == "FLOWATJ-":
                            direction = "y-"

                        for l, inside in enumerate(dic[f"{fol}/regional_fipn"] == 1):
                            if inside:
                                dic["regional_mult" + direction][l] = mult[ll]
                                ll += 1
