"""
Utiliy function for finding the well i,j, and k ids.
"""

import numpy as np
import pandas as pd
from ecl.eclfile import EclFile
from ecl.grid import EclGrid


def positions_regional(dic):
    """
    Function to locate well positions

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["regional_fipnum"] = []
    dic["site_corners"] = [[0, 0, 0], [0, 0, 0]]
    indx = 0
    indc = 0
    for k in range(dic["regional_noCells"][2]):
        for j in range(dic["regional_noCells"][1]):
            for i in range(dic["regional_noCells"][0]):
                if (
                    (i + 0.5)
                    * round(dic["regional_dims"][0] / dic["regional_noCells"][0])
                    in pd.Interval(dic["site_location"][0], dic["site_location"][3])
                    and (j + 0.5)
                    * round(dic["regional_dims"][1] / dic["regional_noCells"][1])
                    in pd.Interval(dic["site_location"][1], dic["site_location"][4])
                ) and (k + 0.5) * round(
                    dic["regional_dims"][2] / dic["regional_noCells"][2]
                ) in pd.Interval(
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
    for j, _ in enumerate(dic["wellCoord"]):
        for i, well_coord in enumerate(dic["wellCoord"][j]):
            corners = np.linspace(
                0, dic["regional_dims"][i], dic["regional_noCells"][i] + 1
            )
            midpoints = (corners[1:] + corners[:-1]) / 2.0
            dic["regional_wellijk"][j].append(
                pd.Series(abs(well_coord - midpoints)).argmin() + 1
            )
            dic["regional_fault"][i] = (
                pd.Series(abs(dic["fault_location"][i] - midpoints)).argmin() + 1
            )
    return dic


def positions_site(dic):
    """
    Function to locate well positions

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["site_wellijk"] = []
    dic["site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["wellCoord"]):
        if dic["wellCoord"][j][0] in pd.Interval(
            dic["site_location"][0], dic["site_location"][3]
        ) and dic["wellCoord"][j][1] in pd.Interval(
            dic["site_location"][1], dic["site_location"][4]
        ):
            dic["site_wellijk"].append([])
            for k, well_coord in enumerate(dic["wellCoord"][j]):
                corners = np.linspace(
                    dic["site_location"][k],
                    dic["site_location"][k + 3],
                    dic["site_noCells"][k] + 1,
                )
                midpoints = (corners[1:] + corners[:-1]) / 2.0
                dic["site_wellijk"][-1].append(
                    pd.Series(abs(well_coord - midpoints)).argmin() + 1
                )
    for k in range(3):
        corners = np.linspace(
            dic["site_location"][k],
            dic["site_location"][k + 3],
            dic["site_noCells"][k] + 1,
        )
        midpoints = (corners[1:] + corners[:-1]) / 2.0
        dic["site_fault"][0][k] = (
            pd.Series(abs(dic["fault_site"][0][k] - midpoints)).argmin() + 1
        )
        dic["site_fault"][1][k] = (
            pd.Series(abs(dic["fault_site"][1][k] - midpoints)).argmin() + 1
        )
    return dic


def positions_reference(dic):
    """
    Function to locate well positions

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["reference_fipnum"] = []
    for k in range(dic["reference_noCells"][2]):
        for j in range(dic["reference_noCells"][1]):
            for i in range(dic["reference_noCells"][0]):
                if (
                    (i + 0.5)
                    * round(dic["reference_dims"][0] / dic["reference_noCells"][0])
                    in pd.Interval(dic["site_location"][0], dic["site_location"][3])
                    and (j + 0.5)
                    * round(dic["reference_dims"][1] / dic["reference_noCells"][1])
                    in pd.Interval(dic["site_location"][1], dic["site_location"][4])
                ) and (k + 0.5) * round(
                    dic["reference_dims"][2] / dic["reference_noCells"][2]
                ) in pd.Interval(
                    dic["site_location"][2], dic["site_location"][5]
                ):
                    dic["reference_fipnum"].append(1)
                else:
                    dic["reference_fipnum"].append(2)
    dic["reference_wellijk"] = [[] for _ in range(len(dic["wellCoord"]))]
    dic["reference_fault"] = [0, 0, 0]
    for j, _ in enumerate(dic["wellCoord"]):
        for i, well_coord in enumerate(dic["wellCoord"][j]):
            corners = np.linspace(
                0, dic["reference_dims"][i], dic["reference_noCells"][i] + 1
            )
            midpoints = (corners[1:] + corners[:-1]) / 2.0
            dic["reference_wellijk"][j].append(
                pd.Series(abs(well_coord - midpoints)).argmin() + 1
            )
            dic["reference_fault"][i] = (
                pd.Series(abs(dic["fault_location"][i] - midpoints)).argmin() + 1
            )
    dic["reference_site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for i in range(3):
        corners = np.linspace(
            0, dic["reference_dims"][i], dic["reference_noCells"][i] + 1
        )
        midpoints = (corners[1:] + corners[:-1]) / 2.0
        dic["reference_site_fault"][0][i] = (
            pd.Series(abs(dic["fault_site"][0][i] - midpoints)).argmin() + 1
        )
        dic["reference_site_fault"][1][i] = (
            pd.Series(abs(dic["fault_site"][1][i] - midpoints)).argmin() + 1
        )
    return dic


def aquaflux(dic):
    """
    Function to read the fluxes from the regional

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    case = f"{dic['exe']}/{dic['fol']}/output/REGIONAL"
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
        "AQUFLUX_bottom",
        "AQUFLUX_top",
        "AQUFLUX_right",
        "AQUFLUX_left",
    ]:
        dic[keyword] = [[] for _ in range(dic["rst"].num_report_steps())]
    for i in range(dic["rst"].num_report_steps()):
        for keyword in ["FLOOILI+", "FLOOILJ+"]:
            dic[keyword][i].append(np.array(dic["rst"].iget_kw(keyword)[i]))
        dic["AQUFLUX_bottom"][i].append(
            [
                np.array(dic["FLOOILJ+"][i][0][j])
                / (dic["regional_dsize"][0] * dic["regional_dsize"][2])
                for j in dic["cells_bottom"]
            ]
        )
        dic["AQUFLUX_top"][i].append(
            [
                -np.array(dic["FLOOILJ+"][i][0][j])
                / (dic["regional_dsize"][0] * dic["regional_dsize"][2])
                for j in dic["cells_top"]
            ]
        )
        dic["AQUFLUX_right"][i].append(
            [
                -np.array(dic["FLOOILI+"][i][0][j])
                / (dic["regional_dsize"][1] * dic["regional_dsize"][2])
                for j in dic["cells_right"]
            ]
        )
        dic["AQUFLUX_left"][i].append(
            [
                np.array(dic["FLOOILI+"][i][0][j])
                / (dic["regional_dsize"][1] * dic["regional_dsize"][2])
                for j in dic["cells_left"]
            ]
        )
    return dic
