# SPDX-FileCopyrightText: 2023-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302, R0912, E1102

"""
Utiliy script for mapping to the site boundaries
"""

import math as mt
import numpy as np
import pandas as pd
from alive_progress import alive_bar
from scipy.interpolate import RegularGridInterpolator, interp1d
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import EclFile as OpmFile


def porv_regional_segmentation(dic):
    """
    Function to locate the different sides for the pv projections

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["regional_opernum"] = []
    for _, z_c in enumerate(dic["regional_zmz_mid"]):
        for _, y_c in enumerate(dic["regional_ymy_mid"]):
            for _, x_c in enumerate(dic["regional_xmx_mid"]):
                if (
                    z_c in pd.Interval(dic["site_location"][2], dic["site_location"][5])
                    and y_c
                    in pd.Interval(dic["site_location"][1], dic["site_location"][4])
                ) and x_c in pd.Interval(
                    dic["site_location"][0], dic["site_location"][3]
                ):
                    dic["regional_opernum"].append("1 ")
                elif Polygon(
                    [
                        (0, 0),
                        (dic["site_location"][0], dic["site_location"][1]),
                        (dic["site_location"][3], dic["site_location"][1]),
                        (dic["reference_dims"][0], 0),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("2 ")
                elif Polygon(
                    [
                        (dic["reference_dims"][0], 0),
                        (dic["site_location"][3], dic["site_location"][1]),
                        (dic["site_location"][3], dic["site_location"][4]),
                        (dic["reference_dims"][0], dic["reference_dims"][1]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("3 ")
                elif Polygon(
                    [
                        (dic["reference_dims"][0], dic["reference_dims"][1]),
                        (dic["site_location"][3], dic["site_location"][4]),
                        (dic["site_location"][0], dic["site_location"][4]),
                        (0, dic["reference_dims"][1]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("4 ")
                elif Polygon(
                    [
                        (0, dic["reference_dims"][1]),
                        (dic["site_location"][0], dic["site_location"][4]),
                        (dic["site_location"][0], dic["site_location"][1]),
                        (0, 0),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("5 ")
                elif Polygon(
                    [
                        (dic["site_location"][3], 0),
                        (dic["site_location"][3], dic["site_location"][1]),
                        (dic["reference_dims"][0], dic["site_location"][1]),
                        (dic["reference_dims"][0], 0),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("6 ")
                elif Polygon(
                    [
                        (dic["site_location"][3], dic["site_location"][4]),
                        (dic["site_location"][3], dic["reference_dims"][1]),
                        (dic["reference_dims"][0], dic["reference_dims"][1]),
                        (dic["reference_dims"][0], dic["site_location"][4]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("7 ")
                elif Polygon(
                    [
                        (0, dic["site_location"][4]),
                        (dic["site_location"][0], dic["site_location"][4]),
                        (dic["site_location"][0], dic["reference_dims"][1]),
                        (0, dic["reference_dims"][1]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_opernum"].append("8 ")
                else:
                    dic["regional_opernum"].append("9 ")


def porv_projections(dic):
    """
    Function to project the pore volumes from the regional to the site.

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    case = f"{dic['fol']}/simulations/regional/REGIONAL"
    ini = OpmFile(case + ".INIT")
    porv = np.array(ini["PORV"])
    opernum = np.array(ini["OPERNUM"])
    mask = porv > 0
    dic["pv_bottom"] = (
        porv[mask][opernum == 2].sum()
        + 0.5 * porv[mask][opernum == 9].sum()
        + 0.5 * porv[mask][opernum == 6].sum()
    )
    dic["pv_right"] = (
        porv[mask][opernum == 3].sum()
        + 0.5 * porv[mask][opernum == 6].sum()
        + 0.5 * porv[mask][opernum == 7].sum()
    )
    dic["pv_top"] = (
        porv[mask][opernum == 4].sum()
        + 0.5 * porv[mask][opernum == 7].sum()
        + 0.5 * porv[mask][opernum == 8].sum()
    )
    dic["pv_left"] = (
        porv[mask][opernum == 5].sum()
        + 0.5 * porv[mask][opernum == 8].sum()
        + 0.5 * porv[mask][opernum == 9].sum()
    )


def aquaflux(dic, iteration=""):
    """
    Function to read the fluxes and pressures from the regional

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    case = f"{dic['fol']}/simulations/regional/REGIONAL"
    dic["regza"] = [False] * len(dic["regional_zmz_mid"])
    ini = OpmFile(case + ".INIT")
    dic["porvr"] = np.array(ini["PORV"])
    dic["actindr"] = dic["porvr"] > 0
    for k in range(len(dic["regional_zmz_mid"])):
        for j in range(len(dic["regional_ymy_mid"])):
            for i in range(len(dic["regional_xmx_mid"])):
                ind = (
                    i
                    + j * len(dic["regional_xmx_mid"])
                    + k * len(dic["regional_xmx_mid"]) * len(dic["regional_ymy_mid"])
                )
                if dic["porvr"][ind] > 0:
                    dic["regza"][k] = True
    case = f"{dic['fol']}/simulations/regional{iteration}/REGIONAL{iteration}"
    rst = case + ".UNRST"
    grid = case + ".EGRID"
    dic["rst"], dic["grid"] = OpmFile(rst), OpmGrid(grid)
    dic["cells_bottom"] = list(
        range(
            dic["grid"].active_index(
                dic["site_corners"][0][0],
                dic["site_corners"][0][1],
                dic["site_corners"][0][2],
            )
            - dic["regional_num_cells"][0],
            dic["grid"].active_index(
                dic["site_corners"][0][0],
                dic["site_corners"][0][1],
                dic["site_corners"][0][2],
            )
            - dic["regional_num_cells"][0]
            + (dic["site_corners"][1][0] - dic["site_corners"][0][0])
            + 1,
        )
    )
    dic["cells_top"] = list(
        range(
            dic["grid"].active_index(
                dic["site_corners"][1][0],
                dic["site_corners"][1][1],
                dic["site_corners"][1][2],
            )
            - (dic["site_corners"][1][0] - dic["site_corners"][0][0]),
            dic["grid"].active_index(
                dic["site_corners"][1][0],
                dic["site_corners"][1][1],
                dic["site_corners"][1][2],
            )
            + 1,
        )
    )
    dic["cells_left"] = list(
        range(
            dic["grid"].active_index(
                dic["site_corners"][0][0],
                dic["site_corners"][0][1],
                dic["site_corners"][0][2],
            )
            - 1,
            dic["grid"].active_index(
                dic["site_corners"][1][0],
                dic["site_corners"][1][1],
                dic["site_corners"][1][2],
            ),
            dic["regional_num_cells"][0],
        )
    )
    dic["cells_right"] = list(
        range(
            dic["grid"].active_index(
                dic["site_corners"][0][0],
                dic["site_corners"][0][1],
                dic["site_corners"][0][2],
            )
            + (dic["site_corners"][1][0] - dic["site_corners"][0][0]),
            dic["grid"].active_index(
                dic["site_corners"][1][0],
                dic["site_corners"][1][1],
                dic["site_corners"][1][2],
            )
            + 1,
            dic["regional_num_cells"][0],
        )
    )
    for direction in ["bottom", "top", "left", "right"]:
        dic[f"{direction}_num_cells"] = len(dic[f"cells_{direction}"])
        for k in range(dic["regional_num_cells"][2] - 1):
            for i in range(dic[f"{direction}_num_cells"]):
                dic[f"cells_{direction}"].append(
                    dic[f"cells_{direction}"][i]
                    + (k + 1)
                    * dic["regional_num_cells"][0]
                    * dic["regional_num_cells"][1]
                )
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
    print("Handle boundary conditions:")
    with alive_bar(len(dic["schedule_r"])) as bar_animation:
        for i in range(len(dic["schedule_r"])):
            bar_animation()
            for keyword in [
                "FLOWATI+",
                "FLOWATJ+",
                "PRESSURE",
                "WAT_DEN",
            ]:
                dic[keyword][i] = [dic["porvr"] * 0]
                dic[keyword][i][0][dic["actindr"]] = np.array(dic["rst"][keyword, i])
            if dic["site_bctype"][0] == "flux":
                n_xy = dic["regional_num_cells"][0] * dic["regional_num_cells"][1]
                dic["R_AQUFLUX_bottom"][i].append(
                    [
                        np.array(dic["FLOWATJ+"][i][0][j])
                        / (
                            dic["regional_xmx_dsize"][j % dic["regional_num_cells"][0]]
                            * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                        )
                        for j in dic["cells_bottom"]
                    ]
                )
                dic["R_AQUFLUX_top"][i].append(
                    [
                        -np.array(dic["FLOWATJ+"][i][0][j])
                        / (
                            dic["regional_xmx_dsize"][j % dic["regional_num_cells"][0]]
                            * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                        )
                        for j in dic["cells_top"]
                    ]
                )
                dic["R_AQUFLUX_right"][i].append(
                    [
                        -np.array(dic["FLOWATI+"][i][0][j])
                        / (
                            dic["regional_ymy_dsize"][
                                mt.floor((j % n_xy) / dic["regional_num_cells"][0])
                            ]
                            * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                        )
                        for j in dic["cells_right"]
                    ]
                )
                dic["R_AQUFLUX_left"][i].append(
                    [
                        np.array(dic["FLOWATI+"][i][0][j])
                        / (
                            dic["regional_ymy_dsize"][
                                mt.floor((j % n_xy) / dic["regional_num_cells"][0])
                            ]
                            * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                        )
                        for j in dic["cells_left"]
                    ]
                )
            elif dic["site_bctype"][0] == "pres":
                handle_stencil(dic, i)
            elif dic["site_bctype"][0] == "pres2p":
                handle_stencil_2p(dic, i)
    if dic["site_bctype"][0] == "pres" or dic["site_bctype"][0] == "pres2p":
        handle_pressure_correction(dic)


def handle_pressure_correction(dic):
    """
    Correct for the REG pres to the SITE on the z dir if refinement

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for i in range(len(dic["schedule_r"])):
        for k, z_p in enumerate(dic["site_zmz_mid"]):
            for j in range(dic["site_num_cells"][0]):
                for name in ["bottom", "top"]:
                    if not dic[f"as{name}"]:
                        continue
                    corr = (
                        (z_p - dic["regional_zmz_mid"][dic["site_zmaps"][k]])
                        * dic[f"R_WAT_DEN_{name}"][i][0][
                            j + dic["site_zmaps"][k] * dic["site_num_cells"][0]
                        ]
                        * 9.81
                        / 1e5
                    )
                    dic[f"S_PRESSURE_{name}"][i].append(
                        dic[f"R_PRESSURE_{name}"][i][0][
                            j + dic["site_zmaps"][k] * dic["site_num_cells"][0]
                        ]
                        + corr
                    )
            for j in range(dic["site_num_cells"][1]):
                for name in ["left", "right"]:
                    if not dic[f"as{name}"]:
                        continue
                    corr = (
                        (z_p - dic["regional_zmz_mid"][dic["site_zmaps"][k]])
                        * dic[f"R_WAT_DEN_{name}"][i][0][
                            j + dic["site_zmaps"][k] * dic["site_num_cells"][1]
                        ]
                        * 9.81
                        / 1e5
                    )
                    dic[f"S_PRESSURE_{name}"][i].append(
                        dic[f"R_PRESSURE_{name}"][i][0][
                            j + dic["site_zmaps"][k] * dic["site_num_cells"][1]
                        ]
                        + corr
                    )


def handle_stencil(dic, i):
    """
    Function to project the cell pressures to the cell faces

    Args:
        dic (dict): Global dictionary\n
        i (int): Counter for the time in the schedule

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["ncellsh"] = mt.floor(len(dic["cells_bottom"]) / dic["regional_num_cells"][2])
    dic["xc"] = np.linspace(
        dic["site_location"][0], dic["site_location"][3], dic["site_num_cells"][0] + 1
    )
    dic["xc"] = 0.5 * (dic["xc"][1:] + dic["xc"][:-1])
    dic["yc"] = np.linspace(
        dic["site_location"][1], dic["site_location"][4], dic["site_num_cells"][1] + 1
    )
    dic["yc"] = 0.5 * (dic["yc"][1:] + dic["yc"][:-1])
    for quan in ["PRESSURE", "WAT_DEN"]:
        for ndir, name in enumerate(["bottom", "top"]):
            if not dic[f"as{name}"]:
                continue
            temp = np.array([])
            for k in range(dic["regional_num_cells"][2]):
                if not dic["regza"][k]:
                    temp = np.hstack((temp, np.zeros(len(dic["xc"]))))
                    continue
                x_a = [
                    0.5
                    * (
                        dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                - dic["asleft"]
                                + j
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                - dic["asleft"]
                                + j
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                - dic["asleft"]
                                + j
                            )[2],
                        )[0][1]
                        - dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                - dic["asleft"]
                                + j
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                - dic["asleft"]
                                + j
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                - dic["asleft"]
                                + j
                            )[2],
                        )[0][0]
                    )
                    + dic["grid"].xyz_from_ijk(
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]] - dic["asleft"] + j
                        )[0],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]] - dic["asleft"] + j
                        )[1],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]] - dic["asleft"] + j
                        )[2],
                    )[0][0]
                    for j in range(
                        len(
                            dic[f"cells_{name}"][
                                k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                            ]
                        )
                        + dic["asleft"]
                        + dic["asright"]
                    )
                ]
                y_a = [
                    0.5
                    * (
                        dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[2],
                        )[1][-1]
                        - dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[2],
                        )[1][0]
                    )
                    + dic["grid"].xyz_from_ijk(
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                        )[0],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                        )[1],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                        )[2],
                    )[1][0],
                    0.5
                    * (
                        dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0]
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0]
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0]
                            )[2],
                        )[1][-1]
                        - dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0]
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0]
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0]
                            )[2],
                        )[1][0]
                    )
                    + dic["grid"].xyz_from_ijk(
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                            + dic["regional_num_cells"][0]
                        )[0],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                            + dic["regional_num_cells"][0]
                        )[1],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                            + dic["regional_num_cells"][0]
                        )[2],
                    )[1][0],
                ]
                z_0 = [
                    dic[f"{quan}"][i][0][
                        dic[f"cells_{name}"][k * dic["ncellsh"]] - dic["asleft"] + j
                    ]
                    for j in range(
                        len(
                            dic[f"cells_{name}"][
                                k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                            ]
                        )
                        + dic["asleft"]
                        + dic["asright"]
                    )
                ]
                z_1 = [
                    dic[f"{quan}"][i][0][
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        - dic["asleft"]
                        + j
                        + dic["regional_num_cells"][0]
                    ]
                    for j in range(
                        len(
                            dic[f"cells_{name}"][
                                k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                            ]
                        )
                        + dic["asleft"]
                        + dic["asright"]
                    )
                ]
                z_a = np.stack(
                    [np.array(z_0).flatten(), np.array(z_1).flatten()], axis=-1
                )
                interp = RegularGridInterpolator(
                    (x_a, y_a), z_a, bounds_error=False, fill_value=None
                )
                x_p, y_p = np.meshgrid(
                    dic["xc"], dic["site_location"][1 + 3 * ndir], indexing="ij"
                )
                temp = np.hstack((temp, interp((x_p, y_p)).flatten()))
            dic[f"R_{quan}_{name}"][i].append(temp)
        dic["ncellsh"] = mt.floor(len(dic["cells_left"]) / dic["regional_num_cells"][2])
        for ndir, name in enumerate(["left", "right"]):
            if not dic[f"as{name}"]:
                continue
            temp = np.array([])
            for k in range(dic["regional_num_cells"][2]):
                if not dic["regza"][k]:
                    temp = np.hstack((temp, np.zeros(len(dic["yc"]))))
                    continue
                x_a = [
                    0.5
                    * (
                        dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                            )[2],
                        )[1][-1]
                        - dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                                + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                            )[2],
                        )[1][0]
                    )
                    + dic["grid"].xyz_from_ijk(
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                            + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                        )[0],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                            + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                        )[1],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                            + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                        )[2],
                    )[1][0]
                    for j in range(
                        len(
                            dic[f"cells_{name}"][
                                k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                            ]
                        )
                        + int(dic["astop"])
                        + int(dic["asbottom"])
                    )
                ]
                y_a = [
                    0.5
                    * (
                        dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[2],
                        )[0][-1]
                        - dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]]
                            )[2],
                        )[0][0]
                    )
                    + dic["grid"].xyz_from_ijk(
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                        )[0],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                        )[1],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]]
                        )[2],
                    )[0][0],
                    0.5
                    * (
                        dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                            )[2],
                        )[0][-1]
                        - dic["grid"].xyz_from_ijk(
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                            )[0],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                            )[1],
                            dic["grid"].ijk_from_global_index(
                                dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                            )[2],
                        )[0][0]
                    )
                    + dic["grid"].xyz_from_ijk(
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                        )[0],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                        )[1],
                        dic["grid"].ijk_from_global_index(
                            dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                        )[2],
                    )[0][0],
                ]
                z_0 = [
                    dic[f"{quan}"][i][0][
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                    ]
                    for j in range(
                        len(
                            dic[f"cells_{name}"][
                                k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                            ]
                        )
                        + int(dic["astop"])
                        + int(dic["asbottom"])
                    )
                ]
                z_1 = [
                    dic[f"{quan}"][i][0][
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        + 1
                        + dic["regional_num_cells"][0] * (-dic["asbottom"] + j)
                    ]
                    for j in range(
                        len(
                            dic[f"cells_{name}"][
                                k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                            ]
                        )
                        + int(dic["astop"])
                        + int(dic["asbottom"])
                    )
                ]
                z_a = np.stack(
                    [np.array(z_0).flatten(), np.array(z_1).flatten()], axis=-1
                )
                interp = RegularGridInterpolator(
                    (x_a, y_a), z_a, bounds_error=False, fill_value=None
                )
                x_p, y_p = np.meshgrid(
                    dic["yc"], dic["site_location"][3 * ndir], indexing="ij"
                )
                temp = np.hstack((temp, interp((x_p, y_p)).flatten()))
            dic[f"R_{quan}_{name}"][i].append(temp)


def temporal_interpolation_pressure(dic):
    """
    Function to interpolate the BC pressure values in time

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """

    keywords = [
        "PRESSURE_bottom",
        "PRESSURE_top",
        "PRESSURE_right",
        "PRESSURE_left",
    ]
    for keyword in keywords:
        dic[f"{keyword}"] = [
            [np.array([0.0 for _ in range(len(dic[f"S_{keyword}"][0]))])]
            for _ in range(len(dic["schedule_s"]))
        ]
        for i in range(len(dic[f"S_{keyword}"][0])):
            if dic["site_bctype"][-1] == "interp":
                interp_func = interp1d(
                    dic["schedule_r"],
                    [dic[f"S_{keyword}"][j][i] for j in range(len(dic["schedule_r"]))],
                    fill_value="extrapolate",
                )
                for j, time in enumerate(dic["schedule_s"]):
                    dic[f"{keyword}"][j][0][i] = interp_func(time)
            else:
                for j, time in enumerate(dic["schedule_s"]):
                    dic[f"{keyword}"][j][0][i] = dic[f"S_{keyword}"][
                        np.searchsorted(dic["schedule_r"], time)
                    ][i]


def temporal_interpolation_flux(dic):
    """
    Function to interpolate the BC fluxes values in time

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    keywords = [
        "AQUFLUX_bottom",
        "AQUFLUX_top",
        "AQUFLUX_right",
        "AQUFLUX_left",
    ]
    for keyword in keywords:
        dic[f"{keyword}"] = [
            [np.array([0.0 for _ in range(len(dic[f"R_{keyword}"][0][0]))])]
            for _ in range(len(dic["schedule_s"]))
        ]
        for i in range(len(dic[f"R_{keyword}"][0][0])):
            if dic["site_bctype"][-1] == "interp":
                interp_func = interp1d(
                    dic["schedule_r"],
                    [
                        dic[f"R_{keyword}"][j][0][i]
                        for j in range(len(dic["schedule_r"]))
                    ],
                    fill_value="extrapolate",
                )
                for j, time in enumerate(dic["schedule_s"]):
                    dic[f"{keyword}"][j][0][i] = interp_func(time)
            else:
                for j, time in enumerate(dic["schedule_s"]):
                    dic[f"{keyword}"][j][0][i] = dic[f"R_{keyword}"][
                        np.searchsorted(dic["schedule_r"], time)
                    ][0][i]


def handle_stencil_2p(dic, i):
    """
    Function to project the cell pressures to the cell faces

    Args:
        dic (dict): Global dictionary\n
        i (int): Counter for the time in the schedule

    Returns:
        dic (dict): Modified global dictionary

    """
    for quan in ["PRESSURE", "WAT_DEN"]:
        dic[f"R_{quan}_bottom"][i].append(
            [
                0.5
                * (
                    dic[quan][i][0][j]
                    + dic[quan][i][0][j + dic["regional_num_cells"][0]]
                )
                for j in dic["cells_bottom"]
            ]
        )
        dic[f"R_{quan}_top"][i].append(
            [
                0.5
                * (
                    dic[quan][i][0][j]
                    + dic[quan][i][0][j + dic["regional_num_cells"][0]]
                )
                for j in dic["cells_top"]
            ]
        )
        dic[f"R_{quan}_left"][i].append(
            [
                0.5 * (dic[quan][i][0][j] + dic[quan][i][0][j + 1])
                for j in dic["cells_left"]
            ]
        )
        dic[f"R_{quan}_right"][i].append(
            [
                0.5 * (dic[quan][i][0][j] + dic[quan][i][0][j + 1])
                for j in dic["cells_right"]
            ]
        )
