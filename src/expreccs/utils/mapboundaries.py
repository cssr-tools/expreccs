# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy script for mapping to the site boundaries
"""

import math as mt
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator, interp1d
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

try:
    from opm.io.ecl import EGrid as OpmGrid
    from opm.io.ecl import EclFile as OpmFile
except ImportError:
    print("The Python package opm was not found, using resdata")
try:
    from resdata.grid import Grid
    from resdata.resfile import ResdataFile
except ImportError:
    print("The resdata Python package was not found, using opm")


def porv_regional_segmentation(dic):
    """
    Function to locate the different sides for the pv projections

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["regional_fipnum"] = []
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
                    dic["regional_fipnum"].append(1)
                elif Polygon(
                    [
                        (0, 0),
                        (dic["site_location"][0], dic["site_location"][1]),
                        (dic["site_location"][3], dic["site_location"][1]),
                        (dic["reference_dims"][0], 0),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(2)
                elif Polygon(
                    [
                        (dic["reference_dims"][0], 0),
                        (dic["site_location"][3], dic["site_location"][1]),
                        (dic["site_location"][3], dic["site_location"][4]),
                        (dic["reference_dims"][0], dic["reference_dims"][1]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(3)
                elif Polygon(
                    [
                        (dic["reference_dims"][0], dic["reference_dims"][1]),
                        (dic["site_location"][3], dic["site_location"][4]),
                        (dic["site_location"][0], dic["site_location"][4]),
                        (0, dic["reference_dims"][1]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(4)
                elif Polygon(
                    [
                        (0, dic["reference_dims"][1]),
                        (dic["site_location"][0], dic["site_location"][4]),
                        (dic["site_location"][0], dic["site_location"][1]),
                        (0, 0),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(5)
                elif Polygon(
                    [
                        (dic["site_location"][3], 0),
                        (dic["site_location"][3], dic["site_location"][1]),
                        (dic["reference_dims"][0], dic["site_location"][1]),
                        (dic["reference_dims"][0], 0),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(6)
                elif Polygon(
                    [
                        (dic["site_location"][3], dic["site_location"][4]),
                        (dic["site_location"][3], dic["reference_dims"][1]),
                        (dic["reference_dims"][0], dic["reference_dims"][1]),
                        (dic["reference_dims"][0], dic["site_location"][4]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(7)
                elif Polygon(
                    [
                        (0, dic["site_location"][4]),
                        (dic["site_location"][0], dic["site_location"][4]),
                        (dic["site_location"][0], dic["reference_dims"][1]),
                        (0, dic["reference_dims"][1]),
                    ]
                ).contains(Point(x_c, y_c)):
                    dic["regional_fipnum"].append(8)
                else:
                    dic["regional_fipnum"].append(9)
    return dic


def porv_projections(dic):
    """
    Function to project the pore volumes from the regional to the site.

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    case = f"{dic['exe']}/{dic['fol']}/output/regional/REGIONAL"
    if dic["reading"] == "resdata":
        ini = ResdataFile(case + ".INIT")
        porv = np.array(ini.iget_kw("PORV")[0])
        fipnum = np.array(ini.iget_kw("FIPNUM")[0])
    else:
        ini = OpmFile(case + ".INIT")
        porv = np.array(ini["PORV"])
        fipnum = np.array(ini["FIPNUM"])
    dic["pv_bottom"] = (
        porv[fipnum == 2].sum()
        + 0.5 * porv[fipnum == 9].sum()
        + 0.5 * porv[fipnum == 6].sum()
    )
    dic["pv_right"] = (
        porv[fipnum == 3].sum()
        + 0.5 * porv[fipnum == 6].sum()
        + 0.5 * porv[fipnum == 7].sum()
    )
    dic["pv_top"] = (
        porv[fipnum == 4].sum()
        + 0.5 * porv[fipnum == 7].sum()
        + 0.5 * porv[fipnum == 8].sum()
    )
    dic["pv_left"] = (
        porv[fipnum == 5].sum()
        + 0.5 * porv[fipnum == 8].sum()
        + 0.5 * porv[fipnum == 9].sum()
    )
    return dic


def aquaflux_resdata(dic):
    """
    Function to read the fluxes and pressures from the regional

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    case = f"{dic['exe']}/{dic['fol']}/output/regional/REGIONAL"
    rst = case + ".UNRST"
    grid = case + ".EGRID"
    dic["rst"], dic["grid"] = ResdataFile(rst), Grid(grid)
    dic["cells_bottom"] = list(
        range(
            dic["grid"].get_active_index(dic["site_corners"][0])
            - dic["regional_noCells"][0],
            dic["grid"].get_active_index(dic["site_corners"][0])
            - dic["regional_noCells"][0]
            + (dic["site_corners"][1][0] - dic["site_corners"][0][0])
            + 1,
        )
    )
    dic["cells_top"] = list(
        range(
            dic["grid"].get_active_index(dic["site_corners"][1])
            - (dic["site_corners"][1][0] - dic["site_corners"][0][0]),
            dic["grid"].get_active_index(dic["site_corners"][1]) + 1,
        )
    )
    dic["cells_left"] = list(
        range(
            dic["grid"].get_active_index(dic["site_corners"][0]) - 1,
            dic["grid"].get_active_index(dic["site_corners"][1]),
            dic["regional_noCells"][0],
        )
    )
    dic["cells_right"] = list(
        range(
            dic["grid"].get_active_index(dic["site_corners"][0])
            + (dic["site_corners"][1][0] - dic["site_corners"][0][0]),
            dic["grid"].get_active_index(dic["site_corners"][1]) + 1,
            dic["regional_noCells"][0],
        )
    )
    for direction in ["bottom", "top", "left", "right"]:
        dic[f"{direction}_noCells"] = len(dic[f"cells_{direction}"])
        for k in range(dic["regional_noCells"][2] - 1):
            for i in range(dic[f"{direction}_noCells"]):
                dic[f"cells_{direction}"].append(
                    dic[f"cells_{direction}"][i]
                    + (k + 1) * dic["regional_noCells"][0] * dic["regional_noCells"][1]
                )
    for keyword in [
        f"FLO{dic['liq']}I+",
        f"FLO{dic['liq']}J+",
        "PRESSURE",
        "R_AQUFLUX_bottom",
        "R_AQUFLUX_top",
        "R_AQUFLUX_right",
        "R_AQUFLUX_left",
        "R_PRESSURE_bottom",
        "R_PRESSURE_top",
        "R_PRESSURE_right",
        "R_PRESSURE_left",
    ]:
        dic[keyword] = [[] for _ in range(dic["rst"].num_report_steps())]
    for i in range(dic["rst"].num_report_steps()):
        for keyword in [f"FLO{dic['liq']}I+", f"FLO{dic['liq']}J+", "PRESSURE"]:
            dic[keyword][i].append(np.array(dic["rst"].iget_kw(keyword)[i]))
        if dic["site_bctype"] == "flux":
            n_xy = dic["regional_noCells"][0] * dic["regional_noCells"][1]
            dic["R_AQUFLUX_bottom"][i].append(
                [
                    np.array(dic[f"FLO{dic['liq']}J+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_bottom"]
                ]
            )
            dic["R_AQUFLUX_top"][i].append(
                [
                    -np.array(dic[f"FLO{dic['liq']}J+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_top"]
                ]
            )
            dic["R_AQUFLUX_right"][i].append(
                [
                    -np.array(dic[f"FLO{dic['liq']}I+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_right"]
                ]
            )
            dic["R_AQUFLUX_left"][i].append(
                [
                    np.array(dic[f"FLO{dic['liq']}I+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_left"]
                ]
            )
        elif dic["site_bctype"] == "pres":
            dic = handle_stencil_resdata(dic, i)
        elif dic["site_bctype"] == "pres2p":
            dic = handle_stencil_2p(dic, i)
    return dic


def aquaflux_opm(dic, iteration=""):
    """
    Function to read the fluxes and pressures from the regional

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    case = f"{dic['exe']}/{dic['fol']}/output/regional{iteration}/REGIONAL{iteration}"
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
            - dic["regional_noCells"][0],
            dic["grid"].active_index(
                dic["site_corners"][0][0],
                dic["site_corners"][0][1],
                dic["site_corners"][0][2],
            )
            - dic["regional_noCells"][0]
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
            dic["regional_noCells"][0],
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
            dic["regional_noCells"][0],
        )
    )
    for direction in ["bottom", "top", "left", "right"]:
        dic[f"{direction}_noCells"] = len(dic[f"cells_{direction}"])
        for k in range(dic["regional_noCells"][2] - 1):
            for i in range(dic[f"{direction}_noCells"]):
                dic[f"cells_{direction}"].append(
                    dic[f"cells_{direction}"][i]
                    + (k + 1) * dic["regional_noCells"][0] * dic["regional_noCells"][1]
                )
    for keyword in [
        f"FLO{dic['liq']}I+",
        f"FLO{dic['liq']}J+",
        "PRESSURE",
        "R_AQUFLUX_bottom",
        "R_AQUFLUX_top",
        "R_AQUFLUX_right",
        "R_AQUFLUX_left",
        "R_PRESSURE_bottom",
        "R_PRESSURE_top",
        "R_PRESSURE_right",
        "R_PRESSURE_left",
    ]:
        dic[keyword] = [[] for _ in range(len(dic["schedule_r"]))]
    for i in range(len(dic["schedule_r"])):
        for keyword in [f"FLO{dic['liq']}I+", f"FLO{dic['liq']}J+", "PRESSURE"]:
            dic[keyword][i].append(np.array(dic["rst"][keyword, i]))
        if dic["site_bctype"] == "flux":
            n_xy = dic["regional_noCells"][0] * dic["regional_noCells"][1]
            dic["R_AQUFLUX_bottom"][i].append(
                [
                    np.array(dic[f"FLO{dic['liq']}J+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_bottom"]
                ]
            )
            dic["R_AQUFLUX_top"][i].append(
                [
                    -np.array(dic[f"FLO{dic['liq']}J+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_top"]
                ]
            )
            dic["R_AQUFLUX_right"][i].append(
                [
                    -np.array(dic[f"FLO{dic['liq']}I+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_right"]
                ]
            )
            dic["R_AQUFLUX_left"][i].append(
                [
                    np.array(dic[f"FLO{dic['liq']}I+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_left"]
                ]
            )
        elif dic["site_bctype"] == "pres":
            dic = handle_stencil_opm(dic, i)
        elif dic["site_bctype"] == "pres2p":
            dic = handle_stencil_2p(dic, i)
    return dic


def handle_stencil_resdata(dic, i):
    """
    Function to project the cell pressures to the cell faces

    Args:
        dic (dict): Global dictionary with required parameters
        i (int): Counter for the time in the schedule

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["ncellsh"] = mt.floor(len(dic["cells_bottom"]) / dic["regional_noCells"][2])
    dic["xc"] = np.linspace(
        dic["site_location"][0], dic["site_location"][3], dic["site_noCells"][0] + 1
    )
    dic["xc"] = 0.5 * (dic["xc"][1:] + dic["xc"][:-1])
    dic["yc"] = np.linspace(
        dic["site_location"][1], dic["site_location"][4], dic["site_noCells"][1] + 1
    )
    dic["yc"] = 0.5 * (dic["yc"][1:] + dic["yc"][:-1])
    for ndir, name in enumerate(["bottom", "top"]):
        temp = np.array([])
        for k in range(dic["regional_noCells"][2]):
            x_a = [
                dic["grid"].get_xyz(
                    active_index=dic[f"cells_{name}"][k * dic["ncellsh"]] - 1 + j
                )[0]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            y_a = [
                dic["grid"].get_xyz(
                    active_index=dic[f"cells_{name}"][k * dic["ncellsh"]]
                )[1],
                dic["grid"].get_xyz(
                    active_index=dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + dic["regional_noCells"][0]
                )[1],
            ]
            z_0 = [
                dic["PRESSURE"][i][0][dic[f"cells_{name}"][k * dic["ncellsh"]] - 1 + j]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_1 = [
                dic["PRESSURE"][i][0][
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    - 1
                    + j
                    + dic["regional_noCells"][0]
                ]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_a = np.stack([np.array(z_0).flatten(), np.array(z_1).flatten()], axis=-1)
            interp = RegularGridInterpolator(
                (x_a, y_a), z_a, bounds_error=False, fill_value=None
            )
            x_p, y_p = np.meshgrid(
                dic["xc"], dic["site_location"][1 + 3 * ndir], indexing="ij"
            )
            temp = np.hstack((temp, interp((x_p, y_p)).flatten()))
        dic[f"R_PRESSURE_{name}"][i].append(temp)
    dic["ncellsh"] = mt.floor(len(dic["cells_left"]) / dic["regional_noCells"][2])
    for ndir, name in enumerate(["left", "right"]):
        temp = np.array([])
        for k in range(dic["regional_noCells"][2]):
            x_a = [
                dic["grid"].get_xyz(
                    active_index=dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + dic["regional_noCells"][0] * (-1 + j)
                )[1]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            y_a = [
                dic["grid"].get_xyz(
                    active_index=dic[f"cells_{name}"][k * dic["ncellsh"]]
                )[0],
                dic["grid"].get_xyz(
                    active_index=dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                )[0],
            ]
            z_0 = [
                dic["PRESSURE"][i][0][
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + dic["regional_noCells"][0] * (-1 + j)
                ]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_1 = [
                dic["PRESSURE"][i][0][
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + 1
                    + dic["regional_noCells"][0] * (-1 + j)
                ]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_a = np.stack([np.array(z_0).flatten(), np.array(z_1).flatten()], axis=-1)
            interp = RegularGridInterpolator(
                (x_a, y_a), z_a, bounds_error=False, fill_value=None
            )
            x_p, y_p = np.meshgrid(
                dic["yc"], dic["site_location"][3 * ndir], indexing="ij"
            )
            temp = np.hstack((temp, interp((x_p, y_p)).flatten()))
        dic[f"R_PRESSURE_{name}"][i].append(temp)
    return dic


def handle_stencil_opm(dic, i):
    """
    Function to project the cell pressures to the cell faces

    Args:
        dic (dict): Global dictionary with required parameters
        i (int): Counter for the time in the schedule

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["ncellsh"] = mt.floor(len(dic["cells_bottom"]) / dic["regional_noCells"][2])
    dic["xc"] = np.linspace(
        dic["site_location"][0], dic["site_location"][3], dic["site_noCells"][0] + 1
    )
    dic["xc"] = 0.5 * (dic["xc"][1:] + dic["xc"][:-1])
    dic["yc"] = np.linspace(
        dic["site_location"][1], dic["site_location"][4], dic["site_noCells"][1] + 1
    )
    dic["yc"] = 0.5 * (dic["yc"][1:] + dic["yc"][:-1])
    for ndir, name in enumerate(["bottom", "top"]):
        temp = np.array([])
        for k in range(dic["regional_noCells"][2]):
            x_a = [
                0.5
                * (
                    dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]] - 1 + j
                    )[0][1]
                    - dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]] - 1 + j
                    )[0][0]
                )
                + dic["grid"].xyz_from_active_index(
                    dic[f"cells_{name}"][k * dic["ncellsh"]] - 1 + j
                )[0][0]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            y_a = [
                0.5
                * (
                    dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                    )[1][-1]
                    - dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                    )[1][0]
                )
                + dic["grid"].xyz_from_active_index(
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                )[1][0],
                0.5
                * (
                    dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        + dic["regional_noCells"][0]
                    )[1][-1]
                    - dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        + dic["regional_noCells"][0]
                    )[1][0]
                )
                + dic["grid"].xyz_from_active_index(
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + dic["regional_noCells"][0]
                )[1][0],
            ]
            z_0 = [
                dic["PRESSURE"][i][0][dic[f"cells_{name}"][k * dic["ncellsh"]] - 1 + j]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_1 = [
                dic["PRESSURE"][i][0][
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    - 1
                    + j
                    + dic["regional_noCells"][0]
                ]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_a = np.stack([np.array(z_0).flatten(), np.array(z_1).flatten()], axis=-1)
            interp = RegularGridInterpolator(
                (x_a, y_a), z_a, bounds_error=False, fill_value=None
            )
            x_p, y_p = np.meshgrid(
                dic["xc"], dic["site_location"][1 + 3 * ndir], indexing="ij"
            )
            temp = np.hstack((temp, interp((x_p, y_p)).flatten()))
        dic[f"R_PRESSURE_{name}"][i].append(temp)
    dic["ncellsh"] = mt.floor(len(dic["cells_left"]) / dic["regional_noCells"][2])
    for ndir, name in enumerate(["left", "right"]):
        temp = np.array([])
        for k in range(dic["regional_noCells"][2]):
            x_a = [
                0.5
                * (
                    dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        + dic["regional_noCells"][0] * (-1 + j)
                    )[1][-1]
                    - dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                        + dic["regional_noCells"][0] * (-1 + j)
                    )[1][0]
                )
                + dic["grid"].xyz_from_active_index(
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + dic["regional_noCells"][0] * (-1 + j)
                )[1][0]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            y_a = [
                0.5
                * (
                    dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                    )[0][-1]
                    - dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]]
                    )[0][0]
                )
                + dic["grid"].xyz_from_active_index(
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                )[0][0],
                0.5
                * (
                    dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                    )[0][-1]
                    - dic["grid"].xyz_from_active_index(
                        dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                    )[0][0]
                )
                + dic["grid"].xyz_from_active_index(
                    dic[f"cells_{name}"][k * dic["ncellsh"]] + 1
                )[0][0],
            ]
            z_0 = [
                dic["PRESSURE"][i][0][
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + dic["regional_noCells"][0] * (-1 + j)
                ]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_1 = [
                dic["PRESSURE"][i][0][
                    dic[f"cells_{name}"][k * dic["ncellsh"]]
                    + 1
                    + dic["regional_noCells"][0] * (-1 + j)
                ]
                for j in range(
                    len(
                        dic[f"cells_{name}"][
                            k * dic["ncellsh"] : (k + 1) * dic["ncellsh"]
                        ]
                    )
                    + 2
                )
            ]
            z_a = np.stack([np.array(z_0).flatten(), np.array(z_1).flatten()], axis=-1)
            interp = RegularGridInterpolator(
                (x_a, y_a), z_a, bounds_error=False, fill_value=None
            )
            x_p, y_p = np.meshgrid(
                dic["yc"], dic["site_location"][3 * ndir], indexing="ij"
            )
            temp = np.hstack((temp, interp((x_p, y_p)).flatten()))
        dic[f"R_PRESSURE_{name}"][i].append(temp)
    return dic


def temporal_interpolation(dic):
    """
    Function to interpolate the BC values in time
    """
    if dic["site_bctype"] == "pres" or dic["site_bctype"] == "pres2p":
        keywords = [
            "PRESSURE_bottom",
            "PRESSURE_top",
            "PRESSURE_right",
            "PRESSURE_left",
        ]
    else:
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
            if dic["time_interp"] == "interp":
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
    return dic


def handle_stencil_2p(dic, i):
    """
    Function to project the cell pressures to the cell faces

    Args:
        dic (dict): Global dictionary with required parameters
        i (int): Counter for the time in the schedule

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["R_PRESSURE_bottom"][i].append(
        [
            0.5
            * (
                dic["PRESSURE"][i][0][j]
                + dic["PRESSURE"][i][0][j + dic["regional_noCells"][0]]
            )
            for j in dic["cells_bottom"]
        ]
    )
    dic["R_PRESSURE_top"][i].append(
        [
            0.5
            * (
                dic["PRESSURE"][i][0][j]
                + dic["PRESSURE"][i][0][j + dic["regional_noCells"][0]]
            )
            for j in dic["cells_top"]
        ]
    )
    dic["R_PRESSURE_left"][i].append(
        [
            0.5 * (dic["PRESSURE"][i][0][j] + dic["PRESSURE"][i][0][j + 1])
            for j in dic["cells_left"]
        ]
    )
    dic["R_PRESSURE_right"][i].append(
        [
            0.5 * (dic["PRESSURE"][i][0][j] + dic["PRESSURE"][i][0][j + 1])
            for j in dic["cells_right"]
        ]
    )
    return dic
