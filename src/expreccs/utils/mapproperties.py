# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0914,R0915

"""Utiliy function for mapping quantities in the different sites"""

import numpy as np


def mapping_properties(dic):
    """Handle the reservoir location settings"""
    dic["site_dims"] = [
        dic["site_location"][j + 3] - dic["site_location"][j] for j in range(3)
    ]

    thickness = np.array(dic["thickness"])
    thickness_cum = np.concatenate(([0.0], np.cumsum(thickness)))

    for res in ["regional", "reference"]:
        res_dims = dic[f"{res}_dims"]

        for i, (name, arr) in enumerate(
            zip(["xmx", "ymy", "zmz"], ["x_n", "y_n", "z_n"])
        ):

            coord = [0.0]
            counts = dic[f"{res}_{arr}"]

            for j, num in enumerate(counts):
                if (
                    i == 2
                    and len(counts) > 1
                    and len(thickness) > 1
                    and len(thickness) == len(counts)
                ):
                    base = thickness_cum[j]
                    for k in range(num):
                        coord.append(((k + 1.0) / num) * thickness[j] + base)
                else:
                    factor = res_dims[i] / len(counts)
                    for k in range(num):
                        coord.append((j + (k + 1.0) / num) * factor)

            coord = np.array(coord)
            dic[f"{res}_{name}"] = coord
            dic[f"{res}_{name}_dsize"] = coord[1:] - coord[:-1]
            dic[f"{res}_{name}_mid"] = 0.5 * (coord[1:] + coord[:-1])
            dic[f"{res}_num_cells"][i] = len(coord) - 1

        zmid = dic[f"{res}_zmz_mid"]
        dic[f"{res}_layers"] = np.zeros(len(zmid), int)
        for t in thickness_cum[1:]:
            dic[f"{res}_layers"] += zmid > t

    res = "site"
    dic[f"{res}_num_cells"] = [0] * 3

    for i, name in enumerate(["xmx", "ymy", "zmz"]):
        ref = dic[f"reference_{name}"]
        mask = (dic["site_location"][i] <= ref) & (ref <= dic["site_location"][3 + i])
        coord = ref[mask]

        dic[f"{res}_{name}"] = coord
        dic[f"{res}_{name}_mid"] = 0.5 * (coord[1:] + coord[:-1])
        dic[f"{res}_num_cells"][i] = len(coord) - 1

    zmid = dic[f"{res}_zmz_mid"]
    dic[f"{res}_layers"] = np.zeros(len(zmid), int)
    for t in thickness_cum[1:]:
        dic[f"{res}_layers"] += zmid > t

    regional_zmid = dic["regional_zmz_mid"]
    site_zmid = dic["site_zmz_mid"]

    dic[f"{res}_zmaps"] = np.array(
        [np.abs(regional_zmid - z).argmin() for z in site_zmid]
    )
    dic[f"{res}ka"] = [
        dic["rock"][int(dic[f"{res}_layers"][i])][2] > 0
        for i in range(dic[f"{res}_num_cells"][2])
    ]

    positions_reference(dic)
    positions_regional(dic)
    rotate_grid(dic)
    if dic["rotate"] > 0:
        positions_rotation(dic)
    else:
        positions_site(dic)


def rotate_grid(dic):
    """Rotate the grid site if requiered"""
    dic["site_xc"], dic["site_yc"] = [], []
    angle = dic["rotate"] * np.pi / 180
    cosang, sinang = np.cos(angle), np.sin(angle)
    for j in range(dic["site_num_cells"][1] + 1):
        for i in range(dic["site_num_cells"][0] + 1):
            dic["site_xc"].append(
                1.5 * dic["site_dims"][0]
                + (dic["site_xmx"][i] - 1.5 * dic["site_dims"][0]) * cosang
                - (dic["site_ymy"][j] - 1.5 * dic["site_dims"][1]) * sinang
            )
            dic["site_yc"].append(
                1.5 * dic["site_dims"][1]
                + (dic["site_ymy"][j] - 1.5 * dic["site_dims"][1]) * cosang
                + (dic["site_xmx"][i] - 1.5 * dic["site_dims"][0]) * sinang
            )
    dic["site_xc"], dic["site_yc"] = np.array(dic["site_xc"]), np.array(dic["site_yc"])


def positions_regional(dic):
    """Locate well, site, and fault positions"""
    dic["regional_fipnum"] = []
    dic["site_corners"] = [[-1, -1, 0], [-1, -1, 0]]
    dic["asleft"], dic["asright"], dic["asbottom"], dic["astop"] = (
        True,
        True,
        True,
        True,
    )
    indx, indc, lasti, found = 0, 0, 0, False

    for _, z_c in enumerate(dic["regional_zmz_mid"]):
        for j, y_c in enumerate(dic["regional_ymy_mid"]):
            row_has_site = False
            for i, x_c in enumerate(dic["regional_xmx_mid"]):
                inside = (
                    dic["site_location"][0] <= x_c <= dic["site_location"][3]
                    and dic["site_location"][1] <= y_c <= dic["site_location"][4]
                    and dic["site_location"][2] <= z_c <= dic["site_location"][5]
                )
                if inside:
                    dic["regional_fipnum"].append("1 ")
                    lasti = i
                    row_has_site = True
                    if dic["site_corners"][0][0] == -1:
                        dic["site_corners"][0] = [i, j, 0]
                else:
                    dic["regional_fipnum"].append("2 ")
                indx += 1
            if row_has_site:
                indc = j
            elif indc != 0 and not row_has_site:
                dic["site_corners"][1] = [lasti, j - 1, 0]
                indc = 0
                found = True
            if (
                j == len(dic["regional_ymy_mid"]) - 1
                and not found
                and dic["site_corners"][0][0] != -1
            ):
                dic["site_corners"][1] = [lasti, j, 0]

    nx, ny = dic["regional_num_cells"][:2]
    i0, j0, _ = dic["site_corners"][0]
    i1, j1, _ = dic["site_corners"][1]
    if i0 == 0:
        dic["asleft"] = False
    if j0 == 0:
        dic["asbottom"] = False
    if i1 == nx - 1:
        dic["asright"] = False
    if i1 == -1:
        for k in range(nx - 1, -1, -1):
            if dic["regional_fipnum"][-nx + k] == "1 ":
                dic["site_corners"][1][0] = k
                break
        else:
            dic["site_corners"][1][0] = nx - 1
            dic["asright"] = False
    if j1 == ny - 1:
        dic["astop"] = False
    if j1 == -1:
        dic["astop"] = False
        dic["site_corners"][1][1] = ny - 1

    dic["regional_wellijk"] = [[] for _ in range(len(dic["well_coords"]))]
    dic["regional_fault"], dic["regional_sensor"] = [0, 0, 0], [0, 0, 0]
    dic["regional_site_fault"] = [[0, 0, 0], [0, 0, 0]]

    for j, _ in enumerate(dic["well_coords"]):
        for _, (well_coord, cord) in enumerate(
            zip(dic["well_coords"][j], ["xmx", "ymy", "zmz", "zmz"])
        ):
            midpoints = dic[f"regional_{cord}_mid"]
            dic["regional_wellijk"][j].append(
                np.abs(well_coord - midpoints).argmin() + 1
            )

    for i, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"regional_{cord}_mid"]

        if i < 2:
            dic["regional_fault"][i] = np.abs(
                dic["fault_regional"][i] - midpoints
            ).argmin()
            dic["regional_site_fault"][0][i] = np.abs(
                dic["fault_site"][0][i] - midpoints
            ).argmin()
            dic["regional_site_fault"][1][i] = np.abs(
                dic["fault_site"][1][i] - midpoints
            ).argmin()

        dic["regional_sensor"][i] = np.abs(dic["sensor_coords"][i] - midpoints).argmin()


def positions_rotation(dic):
    """Find the locations after the rotation"""
    dic["site_fipnum"] = ["1 "] * (
        dic["site_num_cells"][0] * dic["site_num_cells"][1] * dic["site_num_cells"][2]
    )
    dic["site_wellijk"] = []
    dic["site_sensor"] = [0, 0, 0]
    dic["site_fault"] = [[0, 0, 0], [0, 0, 0]]

    for j, _ in enumerate(dic["well_coords"]):
        xw, yw = dic["well_coords"][j][0], dic["well_coords"][j][1]

        if (
            dic["site_location"][0] <= xw <= dic["site_location"][3]
            and dic["site_location"][1] <= yw <= dic["site_location"][4]
        ):
            dic["site_wellijk"].append([])

            w_ij = np.abs(xw - dic["site_xc"]) + np.abs(yw - dic["site_yc"])
            w_ij = w_ij.argmin()

            w_j = np.floor(w_ij / dic["site_num_cells"][0])
            w_i = 1 + dic["site_num_cells"][0] - w_ij + w_j * dic["site_num_cells"][0]

            dic["site_wellijk"][j].append(int(w_i) + 2)
            dic["site_wellijk"][j].append(int(w_j))

            for well_coord, cord in zip(dic["well_coords"][j], ["zmz", "zmz"]):
                midpoints = dic[f"site_{cord}_mid"]
                dic["site_wellijk"][j].append(
                    np.abs(well_coord - midpoints).argmin() + 1
                )

    for k, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"site_{cord}_mid"]

        if k < 2:
            dic["site_fault"][0][k] = np.abs(
                dic["fault_site"][0][k] - midpoints
            ).argmin()
            dic["site_fault"][1][k] = np.abs(
                dic["fault_site"][1][k] - midpoints
            ).argmin()

        dic["site_sensor"][k] = np.abs(dic["sensor_coords"][k] - midpoints).argmin()


def positions_site(dic):
    """Locate well and fault positions in the site reservoir"""
    dic["site_fipnum"] = ["1 "] * (
        dic["site_num_cells"][0] * dic["site_num_cells"][1] * dic["site_num_cells"][2]
    )
    dic["site_wellijk"] = []
    dic["site_sensor"] = [0, 0, 0]
    dic["site_fault"] = [[0, 0, 0], [0, 0, 0]]

    for j, _ in enumerate(dic["well_coords"]):
        xw, yw = dic["well_coords"][j][0], dic["well_coords"][j][1]

        if (
            dic["site_location"][0] <= xw <= dic["site_location"][3]
            and dic["site_location"][1] <= yw <= dic["site_location"][4]
        ):
            dic["site_wellijk"].append([])

            for well_coord, cord in zip(
                dic["well_coords"][j], ["xmx", "ymy", "zmz", "zmz"]
            ):
                midpoints = dic[f"site_{cord}_mid"]
                dic["site_wellijk"][j].append(
                    np.abs(well_coord - midpoints).argmin() + 1
                )

        for k, cord in enumerate(["xmx", "ymy", "zmz"]):
            midpoints = dic[f"site_{cord}_mid"]

            if (
                dic["fault_site"][-1][0] != 1
                and dic["fault_site"][-1][1] != 1
                and k < 2
            ):
                dic["site_fault"][0][k] = np.abs(
                    dic["fault_site"][0][k] - midpoints
                ).argmin()
                dic["site_fault"][1][k] = np.abs(
                    dic["fault_site"][1][k] - midpoints
                ).argmin()

            dic["site_sensor"][k] = np.abs(dic["sensor_coords"][k] - midpoints).argmin()


def positions_reference(dic):
    """Locate well, fault, and site positions in the reference reservoir"""
    dic["reference_fipnum"] = []
    for k in dic["reference_zmz_mid"]:
        for j in dic["reference_ymy_mid"]:
            for i in dic["reference_xmx_mid"]:
                if (
                    dic["site_location"][0] <= i <= dic["site_location"][3]
                    and dic["site_location"][1] <= j <= dic["site_location"][4]
                ) and dic["site_location"][2] <= k <= dic["site_location"][5]:
                    dic["reference_fipnum"].append("1 ")
                else:
                    dic["reference_fipnum"].append("2 ")

    dic["reference_wellijk"] = [[] for _ in range(len(dic["well_coords"]))]
    dic["reference_fault"] = [0, 0, 0]
    dic["reference_site_fault"] = [[0, 0, 0], [0, 0, 0]]
    dic["reference_sensor"] = [0, 0, 0]

    for j, _ in enumerate(dic["well_coords"]):
        for well_coord, cord in zip(
            dic["well_coords"][j], ["xmx", "ymy", "zmz", "zmz"]
        ):
            midpoints = dic[f"reference_{cord}_mid"]
            dic["reference_wellijk"][j].append(
                np.abs(well_coord - midpoints).argmin() + 1
            )

    for i, cord in enumerate(["xmx", "ymy", "zmz"]):
        midpoints = dic[f"reference_{cord}_mid"]
        if i < 2:
            dic["reference_fault"][i] = np.abs(
                dic["fault_regional"][i] - midpoints
            ).argmin()
            dic["reference_site_fault"][0][i] = np.abs(
                dic["fault_site"][0][i] - midpoints
            ).argmin()
            dic["reference_site_fault"][1][i] = np.abs(
                dic["fault_site"][1][i] - midpoints
            ).argmin()
        dic["reference_sensor"][i] = np.abs(
            dic["sensor_coords"][i] - midpoints
        ).argmin()
