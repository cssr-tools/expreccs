# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302,R0912,R0914,R0915,E1102

"""Utiliy script for mapping to the site boundaries"""

import math as mt
import numpy as np
from alive_progress import alive_bar
from scipy.interpolate import RegularGridInterpolator, interp1d
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import EclFile as OpmFile


def porv_regional_segmentation(dic):
    """Locate the different sides for the pv projections"""
    dic["regional_opernum"] = []

    poly2 = Polygon(
        [
            (0, 0),
            (dic["site_location"][0], dic["site_location"][1]),
            (dic["site_location"][3], dic["site_location"][1]),
            (dic["reference_dims"][0], 0),
        ]
    )
    poly3 = Polygon(
        [
            (dic["reference_dims"][0], 0),
            (dic["site_location"][3], dic["site_location"][1]),
            (dic["site_location"][3], dic["site_location"][4]),
            (dic["reference_dims"][0], dic["reference_dims"][1]),
        ]
    )
    poly4 = Polygon(
        [
            (dic["reference_dims"][0], dic["reference_dims"][1]),
            (dic["site_location"][3], dic["site_location"][4]),
            (dic["site_location"][0], dic["site_location"][4]),
            (0, dic["reference_dims"][1]),
        ]
    )
    poly5 = Polygon(
        [
            (0, dic["reference_dims"][1]),
            (dic["site_location"][0], dic["site_location"][4]),
            (dic["site_location"][0], dic["site_location"][1]),
            (0, 0),
        ]
    )
    poly6 = Polygon(
        [
            (dic["site_location"][3], 0),
            (dic["site_location"][3], dic["site_location"][1]),
            (dic["reference_dims"][0], dic["site_location"][1]),
            (dic["reference_dims"][0], 0),
        ]
    )
    poly7 = Polygon(
        [
            (dic["site_location"][3], dic["site_location"][4]),
            (dic["site_location"][3], dic["reference_dims"][1]),
            (dic["reference_dims"][0], dic["reference_dims"][1]),
            (dic["reference_dims"][0], dic["site_location"][4]),
        ]
    )
    poly8 = Polygon(
        [
            (0, dic["site_location"][4]),
            (dic["site_location"][0], dic["site_location"][4]),
            (dic["site_location"][0], dic["reference_dims"][1]),
            (0, dic["reference_dims"][1]),
        ]
    )

    for _, z_c in enumerate(dic["regional_zmz_mid"]):
        for _, y_c in enumerate(dic["regional_ymy_mid"]):
            for _, x_c in enumerate(dic["regional_xmx_mid"]):
                if (
                    dic["site_location"][2] <= z_c <= dic["site_location"][5]
                    and dic["site_location"][1] <= y_c <= dic["site_location"][4]
                ) and dic["site_location"][0] <= x_c <= dic["site_location"][3]:
                    dic["regional_opernum"].append("1 ")
                else:
                    point = Point(x_c, y_c)
                    if poly2.contains(point):
                        dic["regional_opernum"].append("2 ")
                    elif poly3.contains(point):
                        dic["regional_opernum"].append("3 ")
                    elif poly4.contains(point):
                        dic["regional_opernum"].append("4 ")
                    elif poly5.contains(point):
                        dic["regional_opernum"].append("5 ")
                    elif poly6.contains(point):
                        dic["regional_opernum"].append("6 ")
                    elif poly7.contains(point):
                        dic["regional_opernum"].append("7 ")
                    elif poly8.contains(point):
                        dic["regional_opernum"].append("8 ")
                    else:
                        dic["regional_opernum"].append("9 ")


def porv_projections(dic):
    """Project the pore volumes from the regional to the site"""
    case = f"{dic['fol']}/simulations/regional/REGIONAL"
    ini = OpmFile(case + ".INIT")
    porv = np.array(ini["PORV"])
    opernum = np.array(ini["OPERNUM"])
    mask = porv > 0
    porv_masked, opernum_masked = porv[mask], opernum[mask]

    dic["pv_bottom"] = (
        np.sum(porv_masked[opernum_masked == 2])
        + 0.5 * np.sum(porv_masked[opernum_masked == 9])
        + 0.5 * np.sum(porv_masked[opernum_masked == 6])
    )
    dic["pv_right"] = (
        np.sum(porv_masked[opernum_masked == 3])
        + 0.5 * np.sum(porv_masked[opernum_masked == 6])
        + 0.5 * np.sum(porv_masked[opernum_masked == 7])
    )
    dic["pv_top"] = (
        np.sum(porv_masked[opernum_masked == 4])
        + 0.5 * np.sum(porv_masked[opernum_masked == 7])
        + 0.5 * np.sum(porv_masked[opernum_masked == 8])
    )
    dic["pv_left"] = (
        np.sum(porv_masked[opernum_masked == 5])
        + 0.5 * np.sum(porv_masked[opernum_masked == 8])
        + 0.5 * np.sum(porv_masked[opernum_masked == 9])
    )


def aquaflux(dic, iteration=""):
    """Read the fluxes and pressures from the regional"""
    case = f"{dic['fol']}/simulations/regional/REGIONAL"
    ini = OpmFile(case + ".INIT")
    dic["porvr"] = np.array(ini["PORV"])
    dic["actindr"] = dic["porvr"] > 0

    nx, ny = len(dic["regional_xmx_mid"]), len(dic["regional_ymy_mid"])
    nxy = nx * ny
    nz = len(dic["regional_zmz_mid"])

    porv_rsh = dic["porvr"].reshape(nz, ny, nx)
    dic["regza"] = np.any(porv_rsh > 0, axis=(1, 2)).tolist()

    case = f"{dic['fol']}/simulations/regional{iteration}/REGIONAL{iteration}"
    dic["rst"], dic["grid"] = OpmFile(case + ".UNRST"), OpmGrid(case + ".EGRID")

    idx0 = dic["grid"].active_index(
        dic["site_corners"][0][0], dic["site_corners"][0][1], dic["site_corners"][0][2]
    )
    idx1 = dic["grid"].active_index(
        dic["site_corners"][1][0], dic["site_corners"][1][1], dic["site_corners"][1][2]
    )

    dic["cells_bottom"] = list(
        range(
            idx0 - dic["regional_num_cells"][0],
            idx0
            - dic["regional_num_cells"][0]
            + (dic["site_corners"][1][0] - dic["site_corners"][0][0])
            + 1,
        )
    )
    dic["cells_top"] = list(
        range(idx1 - (dic["site_corners"][1][0] - dic["site_corners"][0][0]), idx1 + 1)
    )
    dic["cells_left"] = list(range(idx0 - 1, idx1, dic["regional_num_cells"][0]))
    dic["cells_right"] = list(
        range(
            idx0 + (dic["site_corners"][1][0] - dic["site_corners"][0][0]),
            idx1 + 1,
            dic["regional_num_cells"][0],
        )
    )

    for direction in ["bottom", "top", "left", "right"]:
        base_cells = dic[f"cells_{direction}"]
        numcells = len(base_cells)
        dic[f"{direction}_num_cells"] = numcells
        for k in range(1, dic["regional_num_cells"][2]):
            offset = k * nxy
            base_cells.extend([base_cells[i] + offset for i in range(numcells)])

    for keyword in [
        "FLOWATI+",
        "FLOWATJ+",
        "PRESSURE",
        "WAT_DEN",
        "R_AQUFLUX_bottom",
        "R_AQUFLUX_top",
        "R_AQUFLUX_right",
        "R_AQUFLUX_left",
        "R_PRESSURE_bottom",
        "R_PRESSURE_top",
        "R_PRESSURE_right",
        "R_PRESSURE_left",
        "R_WAT_DEN_bottom",
        "R_WAT_DEN_top",
        "R_WAT_DEN_right",
        "R_WAT_DEN_left",
        "S_PRESSURE_bottom",
        "S_PRESSURE_top",
        "S_PRESSURE_right",
        "S_PRESSURE_left",
    ]:
        dic[keyword] = [[] for _ in range(len(dic["schedule_r"]))]

    cache_grid_coordinates(dic)

    xsize = dic["regional_xmx_dsize"]
    ysize = dic["regional_ymy_dsize"]
    zsize = dic["regional_zmz_dsize"]
    nx_reg = dic["regional_num_cells"][0]

    print("Handle boundary conditions:")
    with alive_bar(len(dic["schedule_r"])) as bar_animation:
        for i in range(len(dic["schedule_r"])):
            bar_animation()

            for keyword in ["FLOWATI+", "FLOWATJ+", "PRESSURE", "WAT_DEN"]:
                arr = np.zeros_like(dic["porvr"])
                arr[dic["actindr"]] = np.array(dic["rst"][keyword, i])
                dic[keyword][i] = [arr]

            if dic["site_bctype"][0] == "flux":

                flowi = dic["FLOWATI+"][i][0]
                flowj = dic["FLOWATJ+"][i][0]

                for jset, sign, isx in [
                    ("cells_bottom", 1, True),
                    ("cells_top", -1, True),
                    ("cells_right", -1, False),
                    ("cells_left", 1, False),
                ]:
                    result = []
                    for j in dic[jset]:
                        if isx:
                            dim = xsize[(j % nxy) % nx_reg]
                            flux = flowj[j]
                        else:
                            dim = ysize[(j % nxy) // nx_reg]
                            flux = flowi[j]
                        zval = zsize[j // nxy]
                        result.append(sign * flux / (dim * zval))
                    dic[f"R_AQUFLUX_{jset.split('_')[1]}"][i].append(result)

            elif dic["site_bctype"][0] == "pres":
                handle_stencil(dic, i)

            elif dic["site_bctype"][0] == "pres2p":
                handle_stencil_2p(dic, i)

    if dic["site_bctype"][0] in ["pres", "pres2p"]:
        handle_pressure_correction(dic)


def handle_pressure_correction(dic):
    """Correct for the REG pres to the SITE on the z dir if refinement"""
    for i in range(len(dic["schedule_r"])):
        for k, z_p in enumerate(dic["site_zmz_mid"]):
            zmap = dic["site_zmaps"][k]
            zreg = dic["regional_zmz_mid"][zmap]
            dz = (z_p - zreg) * 9.81 / 1e5

            for j in range(dic["site_num_cells"][0]):
                idx = j + zmap * dic["site_num_cells"][0]
                for name in ["bottom", "top"]:
                    if not dic[f"as{name}"]:
                        continue
                    corr = dz * dic[f"R_WAT_DEN_{name}"][i][0][idx]
                    dic[f"S_PRESSURE_{name}"][i].append(
                        dic[f"R_PRESSURE_{name}"][i][0][idx] + corr
                    )

            for j in range(dic["site_num_cells"][1]):
                idx = j + zmap * dic["site_num_cells"][1]
                for name in ["left", "right"]:
                    if not dic[f"as{name}"]:
                        continue
                    corr = dz * dic[f"R_WAT_DEN_{name}"][i][0][idx]
                    dic[f"S_PRESSURE_{name}"][i].append(
                        dic[f"R_PRESSURE_{name}"][i][0][idx] + corr
                    )


def cache_grid_coordinates(dic):
    """Precompute xyz centers only for needed indices"""
    grid = dic["grid"]
    ijkfun = grid.ijk_from_global_index
    xyzfun = grid.xyz_from_ijk

    all_cells = set()
    for name in ["bottom", "top", "left", "right"]:
        all_cells.update(dic[f"cells_{name}"])

    max_index = max(all_cells) + dic["regional_num_cells"][0] + 2
    dic["grid_xmid"], dic["grid_ymid"] = np.zeros(max_index), np.zeros(max_index)
    dic["grid_mask"] = np.zeros(max_index, dtype=bool)

    for idx in all_cells:
        ijk = ijkfun(idx)
        xyz = xyzfun(ijk[0], ijk[1], ijk[2])
        dic["grid_xmid"][idx] = 0.5 * (xyz[0][1] - xyz[0][0]) + xyz[0][0]
        dic["grid_ymid"][idx] = 0.5 * (xyz[1][-1] - xyz[1][0]) + xyz[1][0]
        dic["grid_mask"][idx] = True


def handle_stencil(dic, i):
    """Project the cell pressures to the cell faces"""
    dic["ncellsh"] = mt.floor(len(dic["cells_bottom"]) / dic["regional_num_cells"][2])
    dic["xc"] = np.linspace(
        dic["site_location"][0], dic["site_location"][3], dic["site_num_cells"][0] + 1
    )
    dic["xc"] = 0.5 * (dic["xc"][1:] + dic["xc"][:-1])
    dic["yc"] = np.linspace(
        dic["site_location"][1], dic["site_location"][4], dic["site_num_cells"][1] + 1
    )
    dic["yc"] = 0.5 * (dic["yc"][1:] + dic["yc"][:-1])
    nx = dic["regional_num_cells"][0]
    xmid = dic["grid_xmid"]
    ymid = dic["grid_ymid"]

    for quan in ["PRESSURE", "WAT_DEN"]:
        arr = dic[quan][i][0]

        for ndir, name in enumerate(["bottom", "top"]):
            if not dic[f"as{name}"]:
                continue
            temp_list = []
            cells_all = dic[f"cells_{name}"]
            for k in range(dic["regional_num_cells"][2]):
                if not dic["regza"][k]:
                    temp_list.append(np.zeros(len(dic["xc"])))
                    continue
                base = k * dic["ncellsh"]
                shift0 = cells_all[base]
                length = (
                    len(cells_all[base : (k + 1) * dic["ncellsh"]])
                    + dic["asleft"]
                    + dic["asright"]
                )
                idx_array = shift0 - dic["asleft"] + np.arange(length)
                x_a = xmid[idx_array]
                y_a = np.array([ymid[shift0], ymid[shift0 + nx]])
                z_0 = arr[idx_array]
                z_1 = arr[idx_array + nx]

                order = np.argsort(x_a)
                x_a = x_a[order]
                z_0 = z_0[order]
                z_1 = z_1[order]
                x_a, unique_idx = np.unique(x_a, return_index=True)
                z_0 = z_0[unique_idx]
                z_1 = z_1[unique_idx]

                if len(x_a) < 2:
                    temp_list.append(np.zeros(len(dic["xc"])))
                    continue

                z_a = np.stack([z_0, z_1], axis=-1)
                interp = RegularGridInterpolator(
                    (x_a, y_a), z_a, bounds_error=False, fill_value=None
                )
                x_p, y_p = np.meshgrid(
                    dic["xc"], dic["site_location"][1 + 3 * ndir], indexing="ij"
                )
                temp_list.append(interp((x_p, y_p)).flatten())

            dic[f"R_{quan}_{name}"][i].append(np.concatenate(temp_list))

        dic["ncellsh"] = mt.floor(len(dic["cells_left"]) / dic["regional_num_cells"][2])
        for ndir, name in enumerate(["left", "right"]):
            if not dic[f"as{name}"]:
                continue
            temp_list = []
            cells_all = dic[f"cells_{name}"]
            for k in range(dic["regional_num_cells"][2]):
                if not dic["regza"][k]:
                    temp_list.append(np.zeros(len(dic["yc"])))
                    continue
                base = k * dic["ncellsh"]
                shift0 = cells_all[base]
                length = (
                    len(cells_all[base : (k + 1) * dic["ncellsh"]])
                    + int(dic["astop"])
                    + int(dic["asbottom"])
                )
                idx_array = shift0 + nx * (np.arange(length) - dic["asbottom"])

                x_a = ymid[idx_array]
                y_a = np.array([xmid[shift0], xmid[shift0 + 1]])
                z_0 = arr[idx_array]
                z_1 = arr[idx_array + 1]

                order = np.argsort(x_a)
                x_a = x_a[order]
                z_0 = z_0[order]
                z_1 = z_1[order]
                x_a, unique_idx = np.unique(x_a, return_index=True)
                z_0 = z_0[unique_idx]
                z_1 = z_1[unique_idx]

                if len(x_a) < 2:
                    temp_list.append(np.zeros(len(dic["yc"])))
                    continue

                z_a = np.stack([z_0, z_1], axis=-1)
                interp = RegularGridInterpolator(
                    (x_a, y_a), z_a, bounds_error=False, fill_value=None
                )
                x_p, y_p = np.meshgrid(
                    dic["yc"], dic["site_location"][3 * ndir], indexing="ij"
                )
                temp_list.append(interp((x_p, y_p)).flatten())

            dic[f"R_{quan}_{name}"][i].append(np.concatenate(temp_list))


def temporal_interpolation_pressure(dic):
    """Interpolate the BC pressure values in time"""
    keywords = ["PRESSURE_bottom", "PRESSURE_top", "PRESSURE_right", "PRESSURE_left"]
    schedule_r, schedule_s = dic["schedule_r"], dic["schedule_s"]

    for keyword in keywords:
        base = dic[f"S_{keyword}"]
        nvals = len(base[0])
        dic[keyword] = [[np.zeros(nvals)] for _ in range(len(schedule_s))]

        if dic["site_bctype"][-1] == "interp":
            for i in range(nvals):
                interp_func = interp1d(
                    schedule_r,
                    [base[j][i] for j in range(len(schedule_r))],
                    fill_value="extrapolate",
                )
                for j, time in enumerate(schedule_s):
                    dic[keyword][j][0][i] = interp_func(time)
        else:
            indices = np.searchsorted(schedule_r, schedule_s)
            for j, idx in enumerate(indices):
                dic[keyword][j][0][:] = base[idx]


def temporal_interpolation_flux(dic):
    """Interpolate the BC fluxes values in time"""
    keywords = ["AQUFLUX_bottom", "AQUFLUX_top", "AQUFLUX_right", "AQUFLUX_left"]
    schedule_r, schedule_s = dic["schedule_r"], dic["schedule_s"]

    for keyword in keywords:
        base = dic[f"R_{keyword}"]
        nvals = len(base[0][0])
        dic[keyword] = [[np.zeros(nvals)] for _ in range(len(schedule_s))]

        if dic["site_bctype"][-1] == "interp":
            for i in range(nvals):
                interp_func = interp1d(
                    schedule_r,
                    [base[j][0][i] for j in range(len(schedule_r))],
                    fill_value="extrapolate",
                )
                for j, time in enumerate(schedule_s):
                    dic[keyword][j][0][i] = interp_func(time)
        else:
            indices = np.searchsorted(schedule_r, schedule_s)
            for j, idx in enumerate(indices):
                dic[keyword][j][0][:] = base[idx][0]


def handle_stencil_2p(dic, i):
    """Project the cell pressures to the cell faces"""
    nx = dic["regional_num_cells"][0]
    for quan in ["PRESSURE", "WAT_DEN"]:
        arr = dic[quan][i][0]
        dic[f"R_{quan}_bottom"][i].append(
            [0.5 * (arr[j] + arr[j + nx]) for j in dic["cells_bottom"]]
        )
        dic[f"R_{quan}_top"][i].append(
            [0.5 * (arr[j] + arr[j + nx]) for j in dic["cells_top"]]
        )
        dic[f"R_{quan}_left"][i].append(
            [0.5 * (arr[j] + arr[j + 1]) for j in dic["cells_left"]]
        )
        dic[f"R_{quan}_right"][i].append(
            [0.5 * (arr[j] + arr[j + 1]) for j in dic["cells_right"]]
        )
