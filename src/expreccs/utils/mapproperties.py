# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0915

"""
Utiliy function for mapping quantities in the different sites.
"""

import numpy as np
import pandas as pd


def mapping_properties(dic):
    """
    Function to handle the reservoir location settings.

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

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
                    if (
                        i == 2
                        and len(dic[f"{res}_{arr}"]) > 1
                        and len(dic["thickness"]) > 1
                        and len(dic["thickness"]) == len(dic[f"{res}_{arr}"])
                    ):
                        dic[f"{res}_{name}"].append(
                            ((k + 1.0) / num) * dic["thickness"][j]
                            + sum(dic["thickness"][:j])
                        )
                    else:
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
            dic[f"{res}_num_cells"][i] = len(dic[f"{res}_{name}"]) - 1
            np.save(
                f"{dic['fol']}/output/{res}/{res}_{name}",
                dic[f"{res}_{name}"],
            )
        dic[f"{res}_layers"] = np.zeros(dic[f"{res}_num_cells"][2], int)
        for i, _ in enumerate(dic["thickness"]):
            dic[f"{res}_layers"] += dic[f"{res}_zmz_mid"] > sum(
                dic["thickness"][: i + 1]
            )
    for res in ["site"]:
        dic[f"{res}_num_cells"] = [0] * 3
        for i, name in enumerate(["xmx", "ymy", "zmz"]):
            dic[f"{res}_{name}"] = dic[f"reference_{name}"][
                (dic["site_location"][i] <= dic[f"reference_{name}"])
                & (dic[f"reference_{name}"] <= dic["site_location"][3 + i])
            ]
            dic[f"{res}_{name}_mid"] = 0.5 * (
                dic[f"{res}_{name}"][1:] + dic[f"{res}_{name}"][:-1]
            )
            dic[f"{res}_num_cells"][i] = len(dic[f"{res}_{name}"]) - 1
            np.save(
                f"{dic['fol']}/output/{res}_{dic['site_bctype'][0]}/{res}_{name}",
                dic[f"{res}_{name}"],
            )
        dic[f"{res}_layers"] = np.zeros(dic[f"{res}_num_cells"][2], int)
        dic[f"{res}_zmaps"] = np.zeros(dic[f"{res}_num_cells"][2], int)
        for i, _ in enumerate(dic["thickness"]):
            dic[f"{res}_layers"] += dic[f"{res}_zmz_mid"] > sum(
                dic["thickness"][: i + 1]
            )
        dic[f"{res}ka"] = [True] * dic[f"{res}_num_cells"][2]
        for i in range(dic[f"{res}_num_cells"][2]):
            dic[f"{res}_zmaps"][i] = pd.Series(
                abs(dic["regional_zmz_mid"] - dic["site_zmz_mid"][i])
            ).argmin()
            dic[f"{res}ka"][i] = dic["rock"][int(dic[f"{res}_layers"][i])][2] > 0
    positions_reference(dic)
    positions_regional(dic)
    rotate_grid(dic)
    if dic["rotate"] > 0:
        positions_rotation(dic)
    else:
        positions_site(dic)


def rotate_grid(dic):
    """
    Rotate the grid site if requiered.

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["site_xc"], dic["site_yc"] = [], []
    for j in range(dic["site_num_cells"][1] + 1):
        for i in range(dic["site_num_cells"][0] + 1):
            dic["site_xc"].append(
                1.5 * dic["site_dims"][0]
                + (dic["site_xmx"][i] - 1.5 * dic["site_dims"][0])
                * np.cos(dic["rotate"] * np.pi / 180)
                - (dic["site_ymy"][j] - 1.5 * dic["site_dims"][1])
                * np.sin(dic["rotate"] * np.pi / 180)
            )
            dic["site_yc"].append(
                1.5 * dic["site_dims"][1]
                + (dic["site_ymy"][j] - 1.5 * dic["site_dims"][1])
                * np.cos(dic["rotate"] * np.pi / 180)
                + (dic["site_xmx"][i] - 1.5 * dic["site_dims"][0])
                * np.sin(dic["rotate"] * np.pi / 180)
            )
    dic["site_xc"] = np.array(dic["site_xc"])
    dic["site_yc"] = np.array(dic["site_yc"])
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/d2x",
        dic["site_xc"],
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/d2y",
        dic["site_yc"],
    )


def positions_regional(dic):
    """
    Function to locate well, site, and fault positions

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["regional_fipnum"] = []
    dic["site_corners"] = [[-1, -1, 0], [-1, -1, 0]]
    dic["asleft"], dic["asright"], dic["asbottom"], dic["astop"] = (
        True,
        True,
        True,
        True,
    )  # active side
    indx = 0
    indc = 0
    lasti = 0
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
                and min(dic["regional_fipnum"][-dic["regional_num_cells"][0] :]) == 2
            ):
                dic["site_corners"][1] = [lasti, j - 1, 0]
                indc = 0
    if dic["site_corners"][0][0] == 0:
        dic["asleft"] = False
    if dic["site_corners"][0][1] == 1:
        dic["asbottom"] = False
    if dic["site_corners"][1][0] == dic["regional_num_cells"][0] - 1:
        dic["asright"] = False
    if dic["site_corners"][1][0] == -1:
        if (
            min(dic["regional_fipnum"][-dic["regional_num_cells"][0] :]) == 1
            and dic["regional_fipnum"][-1] != 1
        ):
            for val in dic["regional_fipnum"][-dic["regional_num_cells"][0] :]:
                if val == 2:
                    continue
                dic["site_corners"][1][0] += 1
        else:
            dic["asright"] = False
            dic["site_corners"][1][0] = dic["regional_num_cells"][0] - 1
    if dic["site_corners"][1][1] == -1:
        dic["astop"] = False
        dic["site_corners"][1][1] = dic["regional_num_cells"][1] - 1
    # print(dic["astop"],dic["asbottom"],dic["asright"],dic["asleft"])
    dic["regional_wellijk"] = [[] for _ in range(len(dic["well_coords"]))]
    dic["regional_fault"] = [0, 0, 0]
    dic["regional_sensor"] = [0, 0, 0]
    dic["regional_site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["well_coords"]):
        for _, (well_coord, cord) in enumerate(
            zip(dic["well_coords"][j], ["xmx", "ymy", "zmz", "zmz"])
        ):
            midpoints = dic[f"regional_{cord}_mid"]
            dic["regional_wellijk"][j].append(
                pd.Series(abs(well_coord - midpoints)).argmin() + 1
            )
    for i, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"regional_{cord}_mid"]
        if i < 2:
            dic["regional_fault"][i] = pd.Series(
                abs(dic["fault_regional"][i] - midpoints)
            ).argmin()
            dic["regional_site_fault"][0][i] = pd.Series(
                abs(dic["fault_site"][0][i] - midpoints)
            ).argmin()
            dic["regional_site_fault"][1][i] = pd.Series(
                abs(dic["fault_site"][1][i] - midpoints)
            ).argmin()
        dic["regional_sensor"][i] = pd.Series(
            abs(dic["sensor_coords"][i] - midpoints)
        ).argmin()
    sensor_ind = (
        dic["regional_sensor"][0]
        + dic["regional_sensor"][1] * dic["regional_num_cells"][0]
        + dic["regional_sensor"][2]
        * dic["regional_num_cells"][0]
        * dic["regional_num_cells"][1]
    )
    np.save(
        f"{dic['fol']}/output/regional/sensor",
        sensor_ind,
    )
    np.save(
        f"{dic['fol']}/output/regional/sensor_coords",
        dic["sensor_coords"],
    )
    np.save(
        f"{dic['fol']}/output/regional/sensorijk",
        dic["regional_sensor"],
    )


def positions_rotation(dic):
    """
    Find the locations after the rotation

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["site_fipnum"] = [1] * (
        dic["site_num_cells"][0] * dic["site_num_cells"][1] * dic["site_num_cells"][2]
    )
    dic["site_wellijk"] = []
    dic["site_sensor"] = [0, 0, 0]
    dic["site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["well_coords"]):
        if dic["well_coords"][j][0] in pd.Interval(
            dic["site_location"][0], dic["site_location"][3]
        ) and dic["well_coords"][j][1] in pd.Interval(
            dic["site_location"][1], dic["site_location"][4]
        ):
            dic["site_wellijk"].append([])
            w_ij = pd.Series(
                abs(dic["well_coords"][j][0] - dic["site_xc"])
                + abs(dic["well_coords"][j][1] - dic["site_yc"])
            ).argmin()
            w_j = np.floor(w_ij / dic["site_num_cells"][0])
            w_i = 1 + dic["site_num_cells"][0] - w_ij + (w_j) * dic["site_num_cells"][0]
            dic["site_wellijk"][j].append(int(w_i) + 2)
            dic["site_wellijk"][j].append(int(w_j))
            for _, (well_coord, cord) in enumerate(
                zip(dic["well_coords"][j], ["zmz", "zmz"])
            ):
                midpoints = dic[f"site_{cord}_mid"]
                dic["site_wellijk"][j].append(
                    pd.Series(abs(well_coord - midpoints)).argmin() + 1
                )
    for k, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"site_{cord}_mid"]
        if k < 2:
            dic["site_fault"][0][k] = pd.Series(
                abs(dic["fault_site"][0][k] - midpoints)
            ).argmin()
            dic["site_fault"][1][k] = pd.Series(
                abs(dic["fault_site"][1][k] - midpoints)
            ).argmin()
        dic["site_sensor"][k] = pd.Series(
            abs(dic["sensor_coords"][k] - midpoints)
        ).argmin()
    sensor_ind = (
        dic["site_sensor"][0]
        + dic["site_sensor"][1] * dic["site_num_cells"][0]
        + dic["site_sensor"][2] * dic["site_num_cells"][0] * dic["site_num_cells"][1]
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/sensor",
        sensor_ind,
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/sensor_coords",
        dic["sensor_coords"],
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/sensorijk",
        dic["site_sensor"],
    )


def positions_site(dic):
    """
    Function to locate well and fault positions in the site reservoir.

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["site_fipnum"] = [1] * (
        dic["site_num_cells"][0] * dic["site_num_cells"][1] * dic["site_num_cells"][2]
    )
    dic["site_wellijk"] = []
    dic["site_sensor"] = [0, 0, 0]
    dic["site_fault"] = [[0, 0, 0], [0, 0, 0]]
    for j, _ in enumerate(dic["well_coords"]):
        if dic["well_coords"][j][0] in pd.Interval(
            dic["site_location"][0], dic["site_location"][3]
        ) and dic["well_coords"][j][1] in pd.Interval(
            dic["site_location"][1], dic["site_location"][4]
        ):
            dic["site_wellijk"].append([])
            for _, (well_coord, cord) in enumerate(
                zip(dic["well_coords"][j], ["xmx", "ymy", "zmz", "zmz"])
            ):
                midpoints = dic[f"site_{cord}_mid"]
                dic["site_wellijk"][j].append(
                    pd.Series(abs(well_coord - midpoints)).argmin() + 1
                )
    for k, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"site_{cord}_mid"]
        if k < 2:
            dic["site_fault"][0][k] = pd.Series(
                abs(dic["fault_site"][0][k] - midpoints)
            ).argmin()
            dic["site_fault"][1][k] = pd.Series(
                abs(dic["fault_site"][1][k] - midpoints)
            ).argmin()
        dic["site_sensor"][k] = pd.Series(
            abs(dic["sensor_coords"][k] - midpoints)
        ).argmin()
    sensor_ind = (
        dic["site_sensor"][0]
        + dic["site_sensor"][1] * dic["site_num_cells"][0]
        + dic["site_sensor"][2] * dic["site_num_cells"][0] * dic["site_num_cells"][1]
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/sensor",
        sensor_ind,
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/sensor_coords",
        dic["sensor_coords"],
    )
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/sensorijk",
        dic["site_sensor"],
    )


def positions_reference(dic):
    """
    Function to locate well, fault, and site positions in the reference reservoir.

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

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
    dic["reference_wellijk"] = [[] for _ in range(len(dic["well_coords"]))]
    dic["reference_fault"] = [0, 0, 0]
    dic["reference_site_fault"] = [[0, 0, 0], [0, 0, 0]]
    dic["reference_sensor"] = [0, 0, 0]
    for j, _ in enumerate(dic["well_coords"]):
        for i, (well_coord, cord) in enumerate(
            zip(dic["well_coords"][j], ["xmx", "ymy", "zmz", "zmz"])
        ):
            midpoints = dic[f"reference_{cord}_mid"]
            dic["reference_wellijk"][j].append(
                pd.Series(abs(well_coord - midpoints)).argmin() + 1
            )
    for i, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"reference_{cord}_mid"]
        if i < 2:
            dic["reference_fault"][i] = pd.Series(
                abs(dic["fault_regional"][i] - midpoints)
            ).argmin()
            dic["reference_site_fault"][0][i] = pd.Series(
                abs(dic["fault_site"][0][i] - midpoints)
            ).argmin()
            dic["reference_site_fault"][1][i] = pd.Series(
                abs(dic["fault_site"][1][i] - midpoints)
            ).argmin()
        dic["reference_sensor"][i] = pd.Series(
            abs(dic["sensor_coords"][i] - midpoints)
        ).argmin()
    sensor_ind = (
        dic["reference_sensor"][0]
        + dic["reference_sensor"][1] * dic["reference_num_cells"][0]
        + dic["reference_sensor"][2]
        * dic["reference_num_cells"][0]
        * dic["reference_num_cells"][1]
    )
    np.save(
        f"{dic['fol']}/output/reference/sensor",
        sensor_ind,
    )
    np.save(
        f"{dic['fol']}/output/reference/sensor_coords",
        dic["sensor_coords"],
    )
    np.save(
        f"{dic['fol']}/output/reference/sensorijk",
        dic["reference_sensor"],
    )
