# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy function for finding the well i,j, and k ids.
"""

import math as mt
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

try:
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import EGrid as OpmGrid
except ImportError:
    print("The opm Python package was not found, using ecl")
try:
    from ecl.eclfile import EclFile
    from ecl.grid import EclGrid
except ImportError:
    print("The ecl Python package was not found, using opm")


def mapping_properties(dic):
    """
    Function to handle the reservoir location settings.

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["site_dims"] = [
        dic["site_location"][j + 3] - dic["site_location"][j] for j in range(3)
    ]
    for num, res in enumerate(["regional", "reference"]):
        for i, (name, arr) in enumerate(
            zip(["xmx", "ymy", "zmz"], ["x_n", "y_n", "z_n"])
        ):
            dic[f"{res}_{name}"] = [0.0]
            for j, num in enumerate(dic[f"{res}_{arr}"]):
                for k in range(num):
                    dic[f"{res}_{name}"].append(
                        (j + (k + 1.0) / num)
                        * dic[f"{res}_dims"][i]
                        / len(dic[f"{res}_{arr}"])
                    )
            dic[f"{res}_{name}"] = np.array(dic[f"{res}_{name}"])
            dic[f"{res}_{name}_dsize"] = (
                dic[f"{res}_{name}"][1:] - dic[f"{res}_{name}"][:-1]
            )
            dic[f"{res}_{name}_mid"] = 0.5 * (
                dic[f"{res}_{name}"][1:] + dic[f"{res}_{name}"][:-1]
            )
            dic[f"{res}_noCells"][i] = len(dic[f"{res}_{name}"]) - 1
            np.save(
                f"{dic['exe']}/{dic['fol']}/output/{res}/{res}_{name}",
                dic[f"{res}_{name}"],
            )
        dic[f"{res}_layers"] = np.zeros(dic[f"{res}_noCells"][2])
        for i, _ in enumerate(dic["thicknes"]):
            dic[f"{res}_layers"] += dic[f"{res}_zmz_mid"] > sum(
                dic["thicknes"][: i + 1]
            )
    for res in ["site"]:
        dic[f"{res}_noCells"] = [0] * 3
        for i, name in enumerate(["xmx", "ymy", "zmz"]):
            dic[f"{res}_{name}"] = dic[f"reference_{name}"][
                (dic["site_location"][i] <= dic[f"reference_{name}"])
                & (dic[f"reference_{name}"] <= dic["site_location"][3 + i])
            ]
            dic[f"{res}_{name}_mid"] = 0.5 * (
                dic[f"{res}_{name}"][1:] + dic[f"{res}_{name}"][:-1]
            )
            dic[f"{res}_noCells"][i] = len(dic[f"{res}_{name}"]) - 1
            np.save(
                f"{dic['exe']}/{dic['fol']}/output/{res}_{dic['site_bctype']}/{res}_{name}",
                dic[f"{res}_{name}"],
            )
        dic[f"{res}_layers"] = np.zeros(dic[f"{res}_noCells"][2])
        dic[f"{res}_zmaps"] = np.zeros(dic[f"{res}_noCells"][2])
        for i, _ in enumerate(dic["thicknes"]):
            dic[f"{res}_layers"] += dic[f"{res}_zmz_mid"] > sum(
                dic["thicknes"][: i + 1]
            )
        for i in range(dic[f"{res}_noCells"][2]):
            dic[f"{res}_zmaps"][i] = pd.Series(
                abs(dic["regional_zmz_mid"] - dic["site_zmz_mid"][i])
            ).argmin()
    dic = positions_reference(dic)
    dic = positions_regional(dic)
    dic = positions_site(dic)
    return dic


def positions_regional(dic):
    """
    Function to locate well, site, and fault positions

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["regional_fipnum"] = []
    dic["site_corners"] = [[0, 0, 0], [0, 0, 0]]
    indx = 0
    indc = 0
    for _, z_c in enumerate(dic["regional_zmz_mid"]):
        for j, y_c in enumerate(dic["regional_ymy_mid"]):
            for i, x_c in enumerate(dic["regional_xmx_mid"]):
                if (
                    x_c in pd.Interval(dic["site_location"][0], dic["site_location"][3])
                    and y_c
                    in pd.Interval(dic["site_location"][1], dic["site_location"][4])
                ) and z_c in pd.Interval(
                    dic["site_location"][2], dic["site_location"][5]
                ):
                    dic["regional_fipnum"].append(1)
                    lasti = i
                    if indc == 0:
                        dic["site_corners"][0] = [i, j, 0]
                        indc = j
                else:
                    dic["regional_fipnum"].append(2)
                indx += 1
            if (
                indc > 0
                and min(dic["regional_fipnum"][-dic["regional_noCells"][0] :]) == 2
            ):
                dic["site_corners"][1] = [lasti, j - 1, 0]
                indc = 0
    dic["regional_wellijk"] = [[] for _ in range(len(dic["wellCoord"]))]
    dic["regional_fault"] = [0, 0, 0]
    dic["regional_site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["wellCoord"]):
        for _, (well_coord, cord) in enumerate(
            zip(dic["wellCoord"][j], ["xmx", "ymy", "zmz", "zmz"])
        ):
            midpoints = dic[f"regional_{cord}_mid"]
            dic["regional_wellijk"][j].append(
                pd.Series(abs(well_coord - midpoints)).argmin() + 1
            )
    for i, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"regional_{cord}_mid"]
        dic["regional_fault"][i] = pd.Series(
            abs(dic["fault_location"][i] - midpoints)
        ).argmin()
        dic["regional_site_fault"][0][i] = pd.Series(
            abs(dic["fault_site"][0][i] - midpoints)
        ).argmin()
        dic["regional_site_fault"][1][i] = pd.Series(
            abs(dic["fault_site"][1][i] - midpoints)
        ).argmin()
    return dic


def positions_site(dic):
    """
    Function to locate well and fault positions in the site reservoir.

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["site_fipnum"] = [1] * (
        dic["site_noCells"][0] * dic["site_noCells"][1] * dic["site_noCells"][2]
    )
    dic["site_wellijk"] = []
    dic["site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["wellCoord"]):
        if dic["wellCoord"][j][0] in pd.Interval(
            dic["site_location"][0], dic["site_location"][3]
        ) and dic["wellCoord"][j][1] in pd.Interval(
            dic["site_location"][1], dic["site_location"][4]
        ):
            dic["site_wellijk"].append([])
            for _, (well_coord, cord) in enumerate(
                zip(dic["wellCoord"][j], ["xmx", "ymy", "zmz", "zmz"])
            ):
                midpoints = dic[f"site_{cord}_mid"]
                dic["site_wellijk"][j].append(
                    pd.Series(abs(well_coord - midpoints)).argmin() + 1
                )
    for k, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"site_{cord}_mid"]
        dic["site_fault"][0][k] = pd.Series(
            abs(dic["fault_site"][0][k] - midpoints)
        ).argmin()
        dic["site_fault"][1][k] = pd.Series(
            abs(dic["fault_site"][1][k] - midpoints)
        ).argmin()
    return dic


def positions_reference(dic):
    """
    Function to locate well, fault, and site positions in the reference reservoir.

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["reference_fipnum"] = []
    for k in dic["reference_zmz_mid"]:
        for j in dic["reference_ymy_mid"]:
            for i in dic["reference_xmx_mid"]:
                if (
                    i in pd.Interval(dic["site_location"][0], dic["site_location"][3])
                    and j
                    in pd.Interval(dic["site_location"][1], dic["site_location"][4])
                ) and k in pd.Interval(
                    dic["site_location"][2], dic["site_location"][5]
                ):
                    dic["reference_fipnum"].append(1)
                else:
                    dic["reference_fipnum"].append(2)
    dic["reference_wellijk"] = [[] for _ in range(len(dic["wellCoord"]))]
    dic["reference_fault"] = [0, 0, 0]
    dic["reference_site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["wellCoord"]):
        for i, (well_coord, cord) in enumerate(
            zip(dic["wellCoord"][j], ["xmx", "ymy", "zmz", "zmz"])
        ):
            midpoints = dic[f"reference_{cord}_mid"]
            dic["reference_wellijk"][j].append(
                pd.Series(abs(well_coord - midpoints)).argmin() + 1
            )
    for i, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"reference_{cord}_mid"]
        dic["reference_fault"][i] = pd.Series(
            abs(dic["fault_location"][i] - midpoints)
        ).argmin()
        dic["reference_site_fault"][0][i] = pd.Series(
            abs(dic["fault_site"][0][i] - midpoints)
        ).argmin()
        dic["reference_site_fault"][1][i] = pd.Series(
            abs(dic["fault_site"][1][i] - midpoints)
        ).argmin()
    return dic


def aquaflux_ecl(dic):
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
    dic["rst"], dic["grid"] = EclFile(rst), EclGrid(grid)
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
        "FLOOILI+",
        "FLOOILJ+",
        "PRESSURE",
        "AQUFLUX_bottom",
        "AQUFLUX_top",
        "AQUFLUX_right",
        "AQUFLUX_left",
        "PRESSURE_bottom",
        "PRESSURE_top",
        "PRESSURE_right",
        "PRESSURE_left",
    ]:
        dic[keyword] = [[] for _ in range(dic["rst"].num_report_steps())]
    for i in range(dic["rst"].num_report_steps()):
        for keyword in ["FLOOILI+", "FLOOILJ+", "PRESSURE"]:
            dic[keyword][i].append(np.array(dic["rst"].iget_kw(keyword)[i]))
        if dic["site_bctype"] == "flux":
            n_xy = dic["regional_noCells"][0] * dic["regional_noCells"][1]
            dic["AQUFLUX_bottom"][i].append(
                [
                    np.array(dic["FLOOILJ+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_bottom"]
                ]
            )
            dic["AQUFLUX_top"][i].append(
                [
                    -np.array(dic["FLOOILJ+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_top"]
                ]
            )
            dic["AQUFLUX_right"][i].append(
                [
                    -np.array(dic["FLOOILI+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_right"]
                ]
            )
            dic["AQUFLUX_left"][i].append(
                [
                    np.array(dic["FLOOILI+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_left"]
                ]
            )
            dic["PRESSURE_bottom"][i].append(
                [
                    0.5
                    * (
                        dic["PRESSURE"][i][0][j]
                        + dic["PRESSURE"][i][0][j + dic["regional_noCells"][0]]
                    )
                    for j in dic["cells_bottom"]
                ]
            )
        else:
            dic = handle_stencil_ecl(dic, i)
    return dic


def aquaflux_opm(dic):
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
        "FLOOILI+",
        "FLOOILJ+",
        "PRESSURE",
        "AQUFLUX_bottom",
        "AQUFLUX_top",
        "AQUFLUX_right",
        "AQUFLUX_left",
        "PRESSURE_bottom",
        "PRESSURE_top",
        "PRESSURE_right",
        "PRESSURE_left",
    ]:
        dic[keyword] = [[] for _ in range(len(dic["inj"]) + 1)]
    for i in range(len(dic["inj"]) + 1):
        for keyword in ["FLOOILI+", "FLOOILJ+", "PRESSURE"]:
            dic[keyword][i].append(np.array(dic["rst"][keyword, i]))
        if dic["site_bctype"] == "flux":
            n_xy = dic["regional_noCells"][0] * dic["regional_noCells"][1]
            dic["AQUFLUX_bottom"][i].append(
                [
                    np.array(dic["FLOOILJ+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_bottom"]
                ]
            )
            dic["AQUFLUX_top"][i].append(
                [
                    -np.array(dic["FLOOILJ+"][i][0][j])
                    / (
                        dic["regional_xmx_dsize"][j % dic["regional_noCells"][0]]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_top"]
                ]
            )
            dic["AQUFLUX_right"][i].append(
                [
                    -np.array(dic["FLOOILI+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_right"]
                ]
            )
            dic["AQUFLUX_left"][i].append(
                [
                    np.array(dic["FLOOILI+"][i][0][j])
                    / (
                        dic["regional_ymy_dsize"][
                            mt.floor((j % n_xy) / dic["regional_noCells"][0])
                        ]
                        * dic["regional_zmz_dsize"][mt.floor(j / n_xy)]
                    )
                    for j in dic["cells_left"]
                ]
            )
            dic["PRESSURE_bottom"][i].append(
                [
                    0.5
                    * (
                        dic["PRESSURE"][i][0][j]
                        + dic["PRESSURE"][i][0][j + dic["regional_noCells"][0]]
                    )
                    for j in dic["cells_bottom"]
                ]
            )
        else:
            dic = handle_stencil_opm(dic, i)
    return dic


def handle_stencil_ecl(dic, i):
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
        dic[f"PRESSURE_{name}"][i].append(temp)
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
        dic[f"PRESSURE_{name}"][i].append(temp)
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
        dic[f"PRESSURE_{name}"][i].append(temp)
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
        dic[f"PRESSURE_{name}"][i].append(temp)
    return dic
