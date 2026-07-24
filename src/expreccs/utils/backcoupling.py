# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702

"""Utiliy functions to back-couple from site to regional model"""

import os

import numpy as np

from expreccs.utils.runs import simulations
from expreccs.utils.writefile import write_files
from expreccs.visualization.reading import read_fluxes, read_mask


def backcoupling(dic):
    """Function to update regional model based on the
    site model. A multiplier that compensate for the
    difference in fluxes are computed
    MULT[-X, X, -Y , Y] = Flux_site / Flux_regional
    and added to the regional model. This is done
    iterativly for number of iterations given in the input"""
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
        #     aquaflux(dic, f"_{iteration}")
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
    """Write folders for the _{iteration} models"""
    path_pre = f"{dic['fol']}/preprocessing/{fil}"
    path_sim = f"{dic['fol']}/simulations/{fil}"
    if not os.path.exists(path_pre):
        os.makedirs(path_pre, exist_ok=True)
    if not os.path.exists(path_sim):
        os.makedirs(path_sim, exist_ok=True)


def init_multipliers(dic):
    """Initialize input for regional multipliers"""
    numcells = (
        dic["regional_num_cells"][0]
        * dic["regional_num_cells"][1]
        * dic["regional_num_cells"][2]
    )
    for q in ["x", "x-", "y", "y-"]:
        dic["regional_mult" + q] = [1] * numcells


def compute_multipliers(dic, iteration):  # pylint: disable=R1702,R0912,R0914,R0915
    """Compute multiplier that compensate for the difference in fluxes"""
    dic["folders"] = [dic["fol"]]
    dic["rhog_ref"], dic["sat_thr"] = 1.86843, 1e-2
    dic["quantity"] = ["FLOWATI+", "FLOWATJ+", "FLOWATI-", "FLOWATJ-"]

    numx, numy, numz = (
        int(dic["site_num_cells"][0]),
        int(dic["site_num_cells"][1]),
        int(dic["site_num_cells"][2]),
    )
    dx = int(dic["reference_num_cells"][0] / dic["regional_num_cells"][0])
    dy = int(dic["reference_num_cells"][1] / dic["regional_num_cells"][1])
    dz = int(dic["reference_num_cells"][2] / dic["regional_num_cells"][2])
    assert dz == 1
    refine = dx > 1 or dy > 1
    nx_reg, ny_reg, nz_reg = int(numx / dx), int(numy / dy), int(numz / dz)
    stride_xy = numx * numy
    res = "site_" + dic["site_bctype"][0]
    for fol in dic["folders"]:
        if dic["site_bctype"][0] in ["porvproj", "pres"]:
            case = f"{fol}/simulations/regional{iteration}/REGIONAL{iteration}"
            rqs = read_fluxes(case)
            case = f"{fol}/simulations/{res}/{res.upper()}"
            lqs = read_fluxes(case)
            case = f"{fol}/simulations/regional/REGIONAL"
            mask = read_mask(case)
            for quantity, regional_arr, local_arr in zip(dic["quantity"], rqs, lqs):

                regional_fluxes = sum(
                    regional_arr[k][mask] for k in range(len(local_arr))
                )
                local_fluxes = sum(local_arr[k] for k in range(len(local_arr)))

                regional_fluxes, local_fluxes = np.abs(regional_fluxes), np.abs(
                    local_fluxes
                )

                if not refine:
                    sum_local_fluxes = local_fluxes
                else:
                    sum_local_fluxes = np.zeros_like(regional_fluxes)

                    for k_reg in range(nz_reg):
                        base_k = k_reg * stride_xy * dz

                        for j_reg in range(ny_reg):
                            row_base = base_k + j_reg * dy * numx

                            for i_reg in range(nx_reg):
                                ind = i_reg + j_reg * nx_reg + k_reg * nx_reg * ny_reg
                                col_base = row_base + i_reg * dx

                                if quantity == "FLOWATI+":
                                    idxs = col_base + (np.arange(dy) * numx) + (dx - 1)
                                elif quantity == "FLOWATI-":
                                    idxs = col_base + (np.arange(dy) * numx)
                                elif quantity == "FLOWATJ+":
                                    idxs = col_base + (dy - 1) * numx + np.arange(dx)
                                else:
                                    idxs = col_base + np.arange(dx)

                                sum_local_fluxes[ind] = np.sum(local_fluxes[idxs])

                mult = sum_local_fluxes / regional_fluxes
                mult[np.isinf(mult)] = 1
                mult[np.isnan(mult)] = 1

                if quantity == "FLOWATI-":
                    mult.reshape(ny_reg, nx_reg)[:, 1:] = 1
                elif quantity == "FLOWATJ-":
                    mult.reshape(ny_reg, nx_reg)[1:, :] = 1

                direction = "x"
                if quantity == "FLOWATJ+":
                    direction = "y"
                elif quantity == "FLOWATI-":
                    direction = "x-"
                elif quantity == "FLOWATJ-":
                    direction = "y-"

                ll = 0
                for o, inside in enumerate(mask):
                    if inside:
                        dic["regional_mult" + direction][o] = mult[ll]
                        ll += 1
