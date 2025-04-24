# SPDX-FileCopyrightText: 2025 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302,R0914,R1702,R0912,R0915

"""
Utiliy script for creating a deck with projected pressures from given
regional and site decks.
"""

import os
import csv
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Polygon, Point
from scipy.interpolate import LinearNDInterpolator, interp1d
from resdata.grid import Grid
from resdata.resfile import ResdataFile


def create_deck(dic):
    """
    Create a deck from given reg and site decks with projected pressures

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["zones"]:
        dic["explicit"] = False
    case = f"{dic['freg']}/{dic['reg']}"
    rst = case + ".UNRST"
    grid = case + ".EGRID"
    init = case + ".INIT"
    dic["rrst"], dic["rgrid"] = ResdataFile(rst), Grid(grid)
    dic["rinit"] = ResdataFile(init)
    case = f"{dic['fsit']}/{dic['sit']}"
    rst = case + ".UNRST"
    grid = case + ".EGRID"
    init = case + ".INIT"
    dic["sdata"] = case + ".DATA"
    dic["srst"], dic["sgrid"], dic["sinit"] = (
        ResdataFile(rst),
        Grid(grid),
        ResdataFile(init),
    )
    dic["rfip"] = [1] * (dic["rgrid"].nx * dic["rgrid"].ny * dic["rgrid"].nz)
    dic["sfip"] = [1] * (dic["sgrid"].nx * dic["sgrid"].ny * dic["sgrid"].nz)
    dic["ufip"] = [1]
    if dic["zones"]:
        dic["rfip"] = np.array(dic["rinit"].iget_kw("FIPNUM")[0])
        dic["sfip"] = np.array(dic["sinit"].iget_kw("FIPNUM")[0])
        dic["ufip"] = np.intersect1d(np.unique(dic["rfip"]), np.unique(dic["sfip"]))
    rdates = np.array(dic["rrst"].report_dates)
    rdays = rdates - rdates[0]
    dic["rdays"] = np.array([val.days for val in rdays])
    sdates = np.array(dic["srst"].report_dates)
    sdays = sdates - sdates[0]
    dic["isdays"] = np.array([val.days for val in sdays])
    if len(dic["freq"]) < len(dic["isdays"]) - 2:
        dic["freq"] = np.array([int(dic["freq"][0])] * (len(dic["isdays"]) - 1))
    else:
        dic["freq"] = np.array([int(val) for val in dic["freq"]])
    if len(dic["acoeff"]) < len(dic["isdays"]) - 2:
        dic["acoeff"] = np.array([float(dic["acoeff"][0])] * (len(dic["isdays"]) - 1))
    else:
        dic["acoeff"] = np.array([float(val) for val in dic["acoeff"]])
    if max(dic["freq"]) > 0:
        dic["sdays"] = np.array([val.days for val in sdays])
    else:
        dic["sdays"] = []
    dic["sbound"], dic["sai"], dic["gc"] = [], [], 0
    dic["sxs"], dic["sxe"], dic["sxn"], dic["sxw"] = [], [], [], []
    dic["sys"], dic["sye"], dic["syn"], dic["syw"] = [], [], [], []
    dic["szs"], dic["sze"], dic["szn"], dic["szw"] = [], [], [], []
    dic["sfs"], dic["sfe"], dic["sfn"], dic["sfw"] = [], [], [], []
    dic["sts"], dic["ste"], dic["stn"], dic["stw"] = [], [], [], []
    dic["rbound"], dic["rcoord"], dic["sdel"], dic["snum"], dic["fipn"], dic["oprn"] = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    dic["sopn"] = ["1"] * (dic["sgrid"].nx * dic["sgrid"].ny * dic["sgrid"].nz)
    if not os.path.exists(f"{dic['fol']}"):
        os.system(f"mkdir {dic['fol']}")
    if not os.path.exists(f"{dic['fol']}/bc") and max(dic["freq"]) > 0:
        os.system(f"mkdir {dic['fol']}/bc")
    find_ij_orientation(dic)
    extract_site_borders(dic)
    find_regional_cells(dic)
    dynamic_interpolator(dic)
    temporal_interpolation(dic)
    write_files(dic)
    print(f"\nThe execution of ExpReCCS succeeded, see {dic['fol']}/.")


def handle_grid_coord(dic):
    """
    Process the regional and site grid coordinates

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["sbox"] = dic["sgrid"].get_bounding_box_2d()
    dic["sbox"] += (dic["sbox"][0],)
    c_x, c_y, c_z = [], [], []
    s_x, s_y = [], []
    poly = Polygon(
        [
            (dic["sbox"][0][0], dic["sbox"][0][1]),
            (dic["sbox"][1][0], dic["sbox"][1][1]),
            (dic["sbox"][2][0], dic["sbox"][2][1]),
            (dic["sbox"][3][0], dic["sbox"][3][1]),
        ]
    )
    ijn = dic["sgrid"].nx * dic["sgrid"].ny - 1
    for n, cell in enumerate(dic["sgrid"]):
        if cell.active:
            s_x.append(cell.coordinate[0])
            s_y.append(cell.coordinate[1])
        if n == ijn:
            break
    s_x = np.array(s_x)
    s_y = np.array(s_y)
    for cell in dic["rgrid"]:
        if cell.active:
            c_x.append(cell.coordinate[0])
            c_y.append(cell.coordinate[1])
            c_z.append(cell.coordinate[2])
            point = Point(cell.coordinate[0], cell.coordinate[1])
            if poly.contains(point):
                ind = pd.Series(abs(c_x[-1] - s_x) + abs(c_y[-1] - s_y)).argmin()
                ijk = dic["sgrid"].get_ijk(active_index=ind)
                z_t = dic["sgrid"].get_xyz(ijk=ijk)[2]
                z_b = dic["sgrid"].get_xyz(
                    ijk=(ijk[0], ijk[1], ijk[2] + dic["sgrid"].nz - 1)
                )[2]
                d_z = 0.5 * dic["sgrid"].cell_dz(ijk=ijk)
                dic["fipn"].append(f"{cell.k+2}")
                if (
                    c_z[-1] + 0.5 * cell.dz >= z_t - d_z
                    and c_z[-1] - 0.5 * cell.dz <= z_b + d_z
                ):
                    dic["oprn"].append("1")
                else:
                    dic["oprn"].append("7")
            else:
                dic["oprn"].append("8")
                dic["fipn"].append("1")
        else:
            dic["oprn"].append("8")
            dic["fipn"].append("1")
    dic["c_x"] = np.array(c_x)
    dic["c_y"] = np.array(c_y)
    dic["c_z"] = np.array(c_z)
    dic["rnxy"] = dic["rgrid"].nx * dic["rgrid"].ny
    dic["rnxyz"] = dic["rgrid"].nx * dic["rgrid"].ny * dic["rgrid"].nz


def check_regional_neighbours(dic, gind, p, n, d_z):
    """
    Add to the interpolator neighbouring regional cells

    Args:
        dic (dict): Global dictionary\n
        gind (int): Global cell index\n
        p (str): Cardinal direction\n
        n (int): Side number\n
        d_z (float): Thickness regional cell

    Returns:
        dic (dict): Modified global dictionary

    """
    ijk = dic["rgrid"].get_ijk(global_index=gind)
    if dic["rgrid"].nz > 1:
        noise = -1e-4 * np.random.rand()
    else:
        noise = 0
    if ijk[1] - 1 >= 0:
        if dic["rgrid"].get_active_index(
            global_index=gind - dic["rgrid"].nx
        ) not in dic[f"ri{p}"] and dic["rgrid"].active(
            global_index=gind - dic["rgrid"].nx
        ):
            dic[f"rx{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - dic["rgrid"].nx)[0]
            )
            dic[f"ry{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - dic["rgrid"].nx)[1]
            )
            dic[f"rz{p}"].append(
                noise + dic["rgrid"].get_xyz(global_index=gind - dic["rgrid"].nx)[2]
            )
            dic[f"ri{p}"].append(
                dic["rgrid"].get_active_index(global_index=gind - dic["rgrid"].nx)
            )
            dic[f"rk{p}"].append(ijk[2])
            dic[f"rf{p}"].append(
                dic["rfip"][
                    dic["rgrid"].get_active_index(global_index=gind - dic["rgrid"].nx)
                ]
            )
            dic[f"rt{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - dic["rgrid"].nx)[2]
                - d_z[
                    dic["rgrid"].get_active_index(global_index=gind - dic["rgrid"].nx)
                ]
            )
            dic["oprn"][
                gind - dic["rgrid"].nx
            ] = f"{2+n if int(dic['oprn'][gind-dic['rgrid'].nx])==2+n else 6}"
    if ijk[1] + 1 < dic["rgrid"].ny:
        if dic["rgrid"].get_active_index(
            global_index=gind + dic["rgrid"].nx
        ) not in dic[f"ri{p}"] and dic["rgrid"].active(
            global_index=gind + dic["rgrid"].nx
        ):
            dic[f"rx{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + dic["rgrid"].nx)[0]
            )
            dic[f"ry{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + dic["rgrid"].nx)[1]
            )
            dic[f"rz{p}"].append(
                noise + dic["rgrid"].get_xyz(global_index=gind + dic["rgrid"].nx)[2]
            )
            dic[f"ri{p}"].append(
                dic["rgrid"].get_active_index(global_index=gind + dic["rgrid"].nx)
            )
            dic[f"rk{p}"].append(ijk[2])
            dic[f"rf{p}"].append(
                dic["rfip"][
                    dic["rgrid"].get_active_index(global_index=gind + dic["rgrid"].nx)
                ]
            )
            dic[f"rt{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + dic["rgrid"].nx)[2]
                - d_z[
                    dic["rgrid"].get_active_index(global_index=gind + dic["rgrid"].nx)
                ]
            )
            dic["oprn"][
                gind + dic["rgrid"].nx
            ] = f"{2+n if int(dic['oprn'][gind+dic['rgrid'].nx])==2+n else 6}"
    if ijk[0] - 1 >= 0:
        if dic["rgrid"].get_active_index(global_index=gind - 1) not in dic[
            f"ri{p}"
        ] and dic["rgrid"].active(global_index=gind - 1):
            dic[f"rx{p}"].append(dic["rgrid"].get_xyz(global_index=gind - 1)[0])
            dic[f"ry{p}"].append(dic["rgrid"].get_xyz(global_index=gind - 1)[1])
            dic[f"rz{p}"].append(noise + dic["rgrid"].get_xyz(global_index=gind - 1)[2])
            dic[f"ri{p}"].append(dic["rgrid"].get_active_index(global_index=gind - 1))
            dic[f"rk{p}"].append(ijk[2])
            dic[f"rf{p}"].append(
                dic["rfip"][dic["rgrid"].get_active_index(global_index=gind - 1)]
            )
            dic[f"rt{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - 1)[2]
                - d_z[dic["rgrid"].get_active_index(global_index=gind - 1)]
            )
            dic["oprn"][gind - 1] = f"{2+n if int(dic['oprn'][gind-1])==2+n else 6}"
    if ijk[0] + 1 < dic["rgrid"].nx:
        if dic["rgrid"].get_active_index(global_index=gind + 1) not in dic[
            f"ri{p}"
        ] and dic["rgrid"].active(global_index=gind + 1):
            dic[f"rx{p}"].append(dic["rgrid"].get_xyz(global_index=gind + 1)[0])
            dic[f"ry{p}"].append(dic["rgrid"].get_xyz(global_index=gind + 1)[1])
            dic[f"rz{p}"].append(noise + dic["rgrid"].get_xyz(global_index=gind + 1)[2])
            dic[f"ri{p}"].append(dic["rgrid"].get_active_index(global_index=gind + 1))
            dic[f"rk{p}"].append(ijk[2])
            dic[f"rf{p}"].append(
                dic["rfip"][dic["rgrid"].get_active_index(global_index=gind + 1)]
            )
            dic[f"rt{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + 1)[2]
                - d_z[dic["rgrid"].get_active_index(global_index=gind + 1)]
            )
            dic["oprn"][gind + 1] = f"{2+n if int(dic['oprn'][gind+1])==2+n else 6}"
    if gind - dic["rnxy"] >= 0:
        if dic["rgrid"].get_active_index(global_index=gind - dic["rnxy"]) not in dic[
            f"ri{p}"
        ] and dic["rgrid"].active(global_index=gind - dic["rnxy"]):
            dic[f"rx{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - dic["rnxy"])[0]
            )
            dic[f"ry{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - dic["rnxy"])[1]
            )
            dic[f"rz{p}"].append(
                noise + dic["rgrid"].get_xyz(global_index=gind - dic["rnxy"])[2]
            )
            dic[f"ri{p}"].append(
                dic["rgrid"].get_active_index(global_index=gind - dic["rnxy"])
            )
            dic[f"rk{p}"].append(ijk[2] - 1)
            dic[f"rf{p}"].append(
                dic["rfip"][
                    dic["rgrid"].get_active_index(global_index=gind - dic["rnxy"])
                ]
            )
            dic[f"rt{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind - dic["rnxy"])[2]
                - d_z[dic["rgrid"].get_active_index(global_index=gind - dic["rnxy"])]
            )
            dic["oprn"][
                gind - dic["rnxy"]
            ] = f"{2+n if int(dic['oprn'][gind- dic['rnxy']])==2+n else 6}"
    if gind + dic["rnxy"] < dic["rnxy"] * dic["rgrid"].nz:
        if dic["rgrid"].get_active_index(global_index=gind + dic["rnxy"]) not in dic[
            f"ri{p}"
        ] and dic["rgrid"].active(global_index=gind + dic["rnxy"]):
            dic[f"rx{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + dic["rnxy"])[0]
            )
            dic[f"ry{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + dic["rnxy"])[1]
            )
            dic[f"rz{p}"].append(
                noise + dic["rgrid"].get_xyz(global_index=gind + dic["rnxy"])[2]
            )
            dic[f"ri{p}"].append(
                dic["rgrid"].get_active_index(global_index=gind + dic["rnxy"])
            )
            dic[f"rk{p}"].append(ijk[2] + 1)
            dic[f"rf{p}"].append(
                dic["rfip"][
                    dic["rgrid"].get_active_index(global_index=gind + dic["rnxy"])
                ]
            )
            dic[f"rt{p}"].append(
                dic["rgrid"].get_xyz(global_index=gind + dic["rnxy"])[2]
                - d_z[dic["rgrid"].get_active_index(global_index=gind + dic["rnxy"])]
            )
            dic["oprn"][
                gind + dic["rnxy"]
            ] = f"{2+n if int(dic['oprn'][gind+ dic['rnxy']])==2+n else 6}"


def check_intersection(dic, ind, gind, i, n):
    """
    Check if there are nnc in the regional/site overlapping

    Args:
        dic (dict): Global dictionary\n
        ind (int): Index for the closest cell\n
        gind (int): Global cell index in the regional model\n
        i (int): Position of the x, y, or z coords\n
        n (int): Position for the cardinal direction

    Returns:
        lines (list): Horizontal and vertical lines in the regional model

    """
    if i > [dic["sgrid"].nx, dic["sgrid"].ny, dic["sgrid"].nx, dic["sgrid"].nx][n]:
        lift = -1e-4
    else:
        lift = 1e-4
    dic[f"rkg{['n', 'w', 's', 'e'][n]}"].append(
        (dic["rgrid"].get_xyz(active_index=ind)[2] + lift, ind)
    )
    lines = []
    for shift in [dic["rgrid"].nx, 1]:
        x_l, y_l, x_p, y_p = 0, 0, 0, 0
        l_p = [0, 0]
        x_m = dic["rgrid"].get_xyz(active_index=ind)[0]
        y_m = dic["rgrid"].get_xyz(active_index=ind)[1]
        if gind - shift >= 0:
            if dic["rgrid"].active(global_index=gind - shift):
                x_l = dic["rgrid"].get_xyz(global_index=gind - shift)[0]
                y_l = dic["rgrid"].get_xyz(global_index=gind - shift)[1]
                l_p[0] = 1
        if gind + shift < dic["rnxyz"]:
            if dic["rgrid"].active(global_index=gind + shift):
                x_p = dic["rgrid"].get_xyz(global_index=gind + shift)[0]
                y_p = dic["rgrid"].get_xyz(global_index=gind + shift)[1]
                l_p[1] = 1
        if sum(l_p) == 2:
            xy = [x_l, y_l, x_p, y_p]
            lines.append(LineString([(xy[0], xy[1]), (xy[2], xy[3])]))
        elif l_p[1] == 1:
            xy = [x_m, y_m, x_p, y_p]
            lines.append(LineString([(xy[0], xy[1]), (xy[2], xy[3])]))
        elif l_p[0] == 1:
            xy = [x_l, y_l, x_m, y_m]
            lines.append(LineString([(xy[0], xy[1]), (xy[2], xy[3])]))
        else:
            lines.append(0)
    return lines


def find_regional_cells(dic):
    """
    Find the cells to build the interpolator

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    handle_grid_coord(dic)
    count = -1
    d_z = 0.5 * dic["rinit"].iget_kw("DZ")[0]
    whr = [True] * len(dic["c_y"])
    for n, p in enumerate(
        ["n", "w", "s", "e"],
    ):
        (
            dic[f"rx{p}"],
            dic[f"ry{p}"],
            dic[f"rz{p}"],
            dic[f"ri{p}"],
            dic[f"sd{p}"],
            dic[f"rf{p}"],
            dic[f"rt{p}"],
            dic[f"rk{p}"],
            dic[f"rkg{p}"],
        ) = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        fin = 0
        for i, (x_c, y_c, z_c) in enumerate(
            zip(dic[f"sx{p}"], dic[f"sy{p}"], dic[f"sz{p}"])
        ):
            if dic["zones"]:
                if fin != dic[f"sf{p}"][i]:
                    fin = dic[f"sf{p}"][i]
                    whr = dic["rfip"] != fin
                    c_x, c_y, c_z = (
                        dic["c_x"].copy(),
                        dic["c_y"].copy(),
                        dic["c_z"].copy(),
                    )
                    c_x[whr], c_y[whr], c_z[whr] = np.inf, np.inf, np.inf
                ind = pd.Series(
                    (abs(c_x - x_c) + abs(c_y - y_c) + abs(c_z - z_c))
                ).argmin()
            else:
                ind = pd.Series(
                    (
                        abs(dic["c_x"] - x_c)
                        + abs(dic["c_y"] - y_c)
                        + abs(dic["c_z"] - z_c)
                    )
                ).argmin()
            count += 1
            gind = dic["rgrid"].global_index(ind)
            lines = check_intersection(dic, ind, gind, i, n)
            if lines[0] == 0 and lines[1] == 0:
                dic["sdel"].append(count)
                dic[f"sd{p}"].append(i)
                continue
            border = LineString(
                [
                    (dic["sbox"][n][0], dic["sbox"][n][1]),
                    (dic["sbox"][n + 1][0], dic["sbox"][n + 1][1]),
                ]
            )
            if lines[0] == 0:
                lines[0] = lines[1]
            elif lines[1] == 0:
                lines[1] = lines[0]
            if lines[0].intersects(border) or lines[1].intersects(border):
                ijk = dic["rgrid"].get_ijk(global_index=gind)
                dic["snum"].append(dic["sai"][count])
                dic[f"rx{p}"].append(dic["rgrid"].get_xyz(active_index=ind)[0])
                dic[f"ry{p}"].append(dic["rgrid"].get_xyz(active_index=ind)[1])
                dic[f"rz{p}"].append(dic["rgrid"].get_xyz(active_index=ind)[2])
                dic[f"ri{p}"].append(ind)
                dic[f"rf{p}"].append(dic["rfip"][ind])
                dic[f"rt{p}"].append(dic[f"rz{p}"][-1] - d_z[int(ind)])
                dic[f"rk{p}"].append(ijk[2])
                dic["oprn"][gind] = f"{n+2}"
                check_regional_neighbours(dic, gind, p, n, d_z)
            else:
                dic["sdel"].append(count)
                dic[f"sd{p}"].append(i)
        dic[f"sx{p}"], dic[f"sy{p}"], dic[f"sz{p}"], dic[f"sf{p}"], dic[f"st{p}"] = (
            np.array(dic[f"sx{p}"]),
            np.array(dic[f"sy{p}"]),
            np.array(dic[f"sz{p}"]),
            np.array(dic[f"sf{p}"]),
            np.array(dic[f"st{p}"]),
        )
        dic[f"ri{p}"] = np.array(dic[f"ri{p}"])
        dic[f"rx{p}"] = np.array(dic[f"rx{p}"])
        dic[f"ry{p}"] = np.array(dic[f"ry{p}"])
        dic[f"rz{p}"] = np.array(dic[f"rz{p}"])
        dic[f"rf{p}"] = np.array(dic[f"rf{p}"])
        dic[f"rt{p}"] = np.array(dic[f"rt{p}"])
        dic[f"rk{p}"] = np.array(dic[f"rk{p}"])
    for rem in reversed(dic["sdel"]):
        del dic["sbound"][rem]
    git = (
        "-- This file was generated by expreccs https://github.com/cssr-tools/expreccs"
    )
    dic["oprn"].insert(0, "OPERNUM")
    dic["oprn"].insert(0, git)
    dic["oprn"].insert(0, "--Copyright (C) 2025 NORCE")
    dic["oprn"].append("/")
    with open(
        f"{dic['freg']}/OPERNUM_EXPRECCS.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("\n".join(dic["oprn"]))
    dic["fipn"].insert(0, "FIPNUM")
    dic["fipn"].insert(0, git)
    dic["fipn"].insert(0, "--Copyright (C) 2025 NORCE")
    dic["fipn"].append("/")
    with open(
        f"{dic['freg']}/FIPNUM_EXPRECCS.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("\n".join(dic["fipn"]))


def dynamic_interpolator(dic):
    """
    Project the pressures from the regional to the site over time

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["rp"] = [[] for _ in range(dic["rrst"].num_report_steps())]
    for p in ["n", "w", "s", "e"]:
        dic[f"rp{p}"] = [[] for _ in range(dic["rrst"].num_report_steps())]
    for i in range(dic["rrst"].num_report_steps()):
        project_pressures(dic, i)


def temporal_interpolation(dic):
    """
    Function to interpolate BC pressure values in time

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if max(dic["freq"]) > 0:
        dic["ddays"] = dic["sdays"][1:] - dic["sdays"][:-1]
        idays = []
        for i, day in enumerate(dic["sdays"][:-1]):
            for n in range(dic["freq"][i]):
                if dic["acoeff"][i] != 0:
                    telsc = np.flip(
                        (
                            np.exp(
                                np.flip(
                                    np.linspace(0, dic["acoeff"][i], dic["freq"][i] + 1)
                                )
                            )
                            - 1
                        )
                        / (np.exp(dic["acoeff"][i]) - 1)
                    )
                    idays += [day + 1.0 * dic["ddays"][i] * telsc[n]]
                else:
                    idays += [day + 1.0 * dic["ddays"][i] * n / dic["freq"][i]]
        idays += [dic["sdays"][-1]]
        dic["sdays"] = np.array(idays)
        dic["ddays"] = dic["sdays"][1:] - dic["sdays"][:-1]
    else:
        dic["ddays"] = []
    print(f"Input report steps regional (days, tot={len(dic['rdays'])}):")
    print(dic["rdays"])
    print(f"Input report steps site (days, tot={len(dic['isdays'])}):")
    print(dic["isdays"])
    print(f"Report steps site to write bc (days, tot={len(dic['sdays'])}):")
    print([float(f"{val:.2f}") for val in dic["sdays"]])
    dic["sbc"] = ["" for _ in range(len(dic["sdays"]))]
    for i in range(len(dic["rp"][0])):
        interp_func = interp1d(
            dic["rdays"],
            [dic["rp"][j][i][1] for j in range(len(dic["rdays"]))],
            fill_value="extrapolate",
        )
        for j, time in enumerate(dic["sdays"]):
            if dic["explicit"]:
                dic["sbc"][
                    j
                ] += f"{dic['rp'][0][i][0]} DIRICHLET WATER 1* {interp_func(time)} /\n"
            else:
                pres = interp_func(time) + dic["spres"][dic["rp"][0][i][0] - 1]
                dic["sbc"][j] += f"{dic['rp'][0][i][0]} DIRICHLET WATER 1* {pres} /\n"


def project_pressures(dic, i):
    """
    Project the pressures at restart number i

    Args:
        dic (dict): Global dictionary\n
        i (int): Index of report step in the site

    Returns:
        dic (dict): Modified global dictionary

    """
    count, c_c, s_s, d_t, whr = 0, 1, 0, 0, 0
    for _, p in enumerate(["n", "w", "s", "e"]):
        n = 0
        if len(dic[f"ri{p}"]) == 0:
            count += len(dic[f"sx{p}"])
            c_c += len(dic[f"sx{p}"]) + s_s
            s_s = 0
            continue
        z_p = np.array(dic["rrst"].iget_kw("PRESSURE")[i])[dic[f"ri{p}"]]
        w_d = np.array(dic["rrst"].iget_kw("WAT_DEN")[i])
        if not dic["explicit"]:
            z_p -= np.array(dic["rrst"].iget_kw("PRESSURE")[0])[dic[f"ri{p}"]]
        if dic["rgrid"].nz > 1:
            if not dic["zones"]:
                interp = LinearNDInterpolator(
                    list(zip(dic[f"rx{p}"], dic[f"ry{p}"], dic[f"rz{p}"])), z_p
                )
            for k, (x, y, z) in enumerate(
                zip(dic[f"sx{p}"], dic[f"sy{p}"], dic[f"sz{p}"])
            ):
                if dic["sai"][count] in dic["snum"]:
                    if dic["zones"]:
                        if dic[f"sf{p}"][k] in dic["ufip"]:
                            if n != dic[f"sf{p}"][k]:
                                n = dic[f"sf{p}"][k]
                                whr = dic[f"rf{p}"] == n
                                if len(np.unique(dic[f"rk{p}"][whr])) == 1:
                                    interp = LinearNDInterpolator(
                                        list(
                                            zip(dic[f"rx{p}"][whr], dic[f"ry{p}"][whr])
                                        ),
                                        z_p[whr],
                                    )
                                else:
                                    whs = dic[f"sf{p}"] == n
                                    d_t = np.round(
                                        min(dic[f"rt{p}"][whr])
                                        - min(dic[f"st{p}"][whs]),
                                        2,
                                    )
                                    interp = LinearNDInterpolator(
                                        list(
                                            zip(
                                                dic[f"rx{p}"][whr],
                                                dic[f"ry{p}"][whr],
                                                dic[f"rz{p}"][whr],
                                            )
                                        ),
                                        z_p[whr],
                                    )
                            if len(np.unique(dic[f"rk{p}"][whr])) == 1:
                                z_b = interp((x, y))
                            else:
                                z_b = interp((x, y, z + d_t))
                                if np.isnan(z_b):
                                    z_b = interp((x, y, dic[f"rkg{p}"][k][0]))
                        else:
                            if i == 0:
                                for j, row in enumerate(dic["sbound"]):
                                    if int(row.split()[0]) == dic["sai"][count] + 1:
                                        dic["sbound"].pop(j)
                                        s_s += 1
                                        continue
                            count += 1
                            continue
                    else:
                        z_b = interp((x, y, z))
                        if np.isnan(z_b):
                            if not dic["explicit"]:
                                z_b = interp((x, y, dic[f"rkg{p}"][k][0]))
                            else:
                                z_b = (
                                    interp((x, y, dic[f"rkg{p}"][k][0]))
                                    + (z - dic[f"rkg{p}"][k][0])
                                    * w_d[dic[f"rkg{p}"][k][1]]
                                    * 9.81
                                    / 1e5
                                )
                    if not np.isnan(z_b):
                        dic["rp"][i].append([dic["sai"][count] + 1, z_b])
                        for j, row in enumerate(dic["sbound"]):
                            edit = row.split()
                            if int(edit[0]) == dic["sai"][count] + 1:
                                if i == 0:
                                    edit[0] = str(dic["sai"][count] + 1)
                                    dic["sbound"][j] = " ".join(edit)
                                    dic["sopn"][
                                        dic["sgrid"].get_global_index(
                                            ijk=(
                                                int(edit[1]) - 1,
                                                int(edit[3]) - 1,
                                                int(edit[5]) - 1,
                                            )
                                        )
                                    ] = "2"
                                c_c += 1
                                continue
                    else:
                        if i == 0:
                            for j, row in enumerate(dic["sbound"]):
                                if int(row.split()[0]) == dic["sai"][count] + 1:
                                    dic["sbound"].pop(j)
                                    s_s += 1
                                    continue
                count += 1
        else:
            interp = LinearNDInterpolator(list(zip(dic[f"rx{p}"], dic[f"ry{p}"])), z_p)
            for x, y in zip(dic[f"sx{p}"], dic[f"sy{p}"]):
                if dic["sai"][count] in dic["snum"]:
                    if not np.isnan(interp((x, y))):
                        dic["rp"][i].append([dic["sai"][count] + 1, interp((x, y))])
                        for j, row in enumerate(dic["sbound"]):
                            edit = row.split()
                            if int(edit[0]) == dic["sai"][count] + 1:
                                if i == 0:
                                    edit[0] = str(c_c + s_s)
                                    dic["sbound"][j] = " ".join(edit)
                                    dic["sopn"][
                                        dic["sgrid"].get_global_index(
                                            ijk=(
                                                int(edit[1]) - 1,
                                                int(edit[3]) - 1,
                                                int(edit[5]) - 1,
                                            )
                                        )
                                    ] = "2"
                                c_c += 1
                                continue
                    else:
                        if i == 0:
                            for j, row in enumerate(dic["sbound"]):
                                if int(row.split()[0]) == dic["sai"][count] + 1:
                                    dic["sbound"].pop(j)
                                    s_s += 1
                                    continue
                count += 1


def write_files(dic):
    """
    Write the files with the projected pressures

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["fsit"] != dic["fol"]:
        dic["files"] = [f for f in os.listdir(f"{dic['fsit']}") if f.endswith(".INC")]
        for file in dic["files"]:
            os.system(f"scp -r {dic['fsit']}/{file} {dic['fol']}")
    lol = []
    with open(dic["sdata"], "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2]
            if 0 < nrwo.find("\\t"):
                nrwo = nrwo.replace("\\t", " ")
            lol.append(nrwo)
            if lol[-1] == "GRID" and max(dic["freq"]) > 0:
                lol.append("INCLUDE")
                lol.append("'BCCON.INC' /")
            if lol[-1] == "REGIONS":
                lol.append("INCLUDE")
                lol.append("'OPERNUM_EXPRECCS.INC' /")
    count = 1
    fre = 0
    tstep = 0
    with open(
        f"{dic['fol']}/{dic['fol'].split('/')[-1].upper()}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        for i, row in enumerate(lol):
            edit = row.split()
            if i < len(lol) - 1:
                if lol[i + 1] == "TSTEP" and max(dic["freq"]) > 0:
                    file.write(row)
                    file.write("\n")
                    for _ in range(dic["freq"][fre]):
                        file.write("INCLUDE\n")
                        file.write(f"'bc/BCPROP{count}.INC' /\n")
                        file.write("TSTEP\n")
                        file.write(f"{dic['ddays'][count-1]} /\n")
                        count += 1
                        tstep = 1
                    fre += 1
                elif tstep == 0:
                    file.write(row)
                    file.write("\n")
                elif edit and tstep == 1:
                    if edit[-1] == "/" or edit[0] == "/":
                        tstep = 0
            else:
                if tstep == 0:
                    file.write(row)
    git = (
        "-- This file was generated by expreccs https://github.com/cssr-tools/expreccs"
    )
    if max(dic["freq"]) > 0:
        dic["sbound"].insert(0, "BCCON")
        dic["sbound"].insert(0, git)
        dic["sbound"].insert(0, "--Copyright (C) 2025 NORCE")
        dic["sbound"].append("/")
        with open(
            f"{dic['fol']}/BCCON.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dic["sbound"]))
        for i in range(len(dic["sdays"])):
            dic["sbc"][i] = [dic["sbc"][i]]
            dic["sbc"][i].insert(0, "BCPROP\n")
            dic["sbc"][i].insert(0, f"--No. days = {dic['sdays'][i]:.2f}\n")
            dic["sbc"][i].insert(0, git + "\n")
            dic["sbc"][i].insert(0, "--Copyright (C) 2025 NORCE\n")
            dic["sbc"][i].append("/")
            with open(
                f"{dic['fol']}/bc/BCPROP{i}.INC",
                "w",
                encoding="utf8",
            ) as file:
                file.write("".join(dic["sbc"][i]))
    dic["sopn"].insert(0, "OPERNUM")
    dic["sopn"].insert(0, git)
    dic["sopn"].insert(0, "--Copyright (C) 2025 NORCE")
    dic["sopn"].append("/")
    with open(
        f"{dic['fol']}/OPERNUM_EXPRECCS.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("\n".join(dic["sopn"]))


def find_ij_orientation(dic):
    """
    Find if the counting is left/right handed

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    y1 = dic["sgrid"].get_xyz(ijk=(0, 0, 0))[1]
    y2 = dic["sgrid"].get_xyz(ijk=(0, 1, 0))[1]
    x1 = dic["sgrid"].get_xyz(ijk=(0, 0, 0))[1]
    x2 = dic["sgrid"].get_xyz(ijk=(1, 0, 0))[1]
    if y2 < y1:
        dic["mly"] = 1
    else:
        dic["mly"] = -1
    if x2 < x1:
        dic["mlx"] = 1
    else:
        dic["mlx"] = -1


def extract_site_borders(dic):
    """
    Get the index/coord from the site border

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["spres"] = []
    d_z = 0.5 * dic["sinit"].iget_kw("DZ")[0]
    if dic["boundaries"][0] > -1:
        for k in range(dic["sgrid"].nz):
            j = dic["boundaries"][0]
            for i in range(dic["sgrid"].nx):
                ind = dic["sgrid"].get_active_index(ijk=(i, j, k))
                if dic["sgrid"].active(ijk=(i, j, k)):
                    dic["sai"].append(dic["gc"])
                    xyz = np.array(dic["sgrid"].get_xyz(ijk=(i, j, k)))
                    d_y = 0.5 * dic["sinit"].iget_kw("DY")[0][ind]
                    dic["sbound"].append(
                        f"{dic['gc'] + 1} {i + 1} {i + 1} {j + 1} {j + 1} {k + 1} {k + 1} 'J-' /"
                    )
                    dic["sxn"].append(xyz[0])
                    dic["syn"].append(xyz[1] + dic["mly"] * d_y)
                    dic["szn"].append(xyz[2])
                    dic["sfn"].append(dic["sfip"][ind])
                    dic["stn"].append(xyz[2] - d_z[ind])
                if not dic["explicit"]:
                    dic["spres"].append(dic["srst"].iget_kw("PRESSURE")[0][ind])
                dic["gc"] += 1
    if dic["boundaries"][1] > -1:
        for k in range(dic["sgrid"].nz):
            i = dic["sgrid"].nx - 1 - dic["boundaries"][1]
            for j in range(dic["sgrid"].ny):
                ind = dic["sgrid"].get_active_index(ijk=(i, j, k))
                if dic["sgrid"].active(ijk=(i, j, k)):
                    dic["sai"].append(dic["gc"])
                    xyz = np.array(dic["sgrid"].get_xyz(ijk=(i, j, k)))
                    d_x = 0.5 * dic["sinit"].iget_kw("DX")[0][ind]
                    dic["sbound"].append(
                        f"{dic['gc'] + 1} {i + 1} {i + 1} {j + 1} {j + 1} {k + 1} {k + 1} 'I' /"
                    )
                    dic["sxw"].append(xyz[0] + dic["mlx"] * d_x * (-1))
                    dic["syw"].append(xyz[1])
                    dic["szw"].append(xyz[2])
                    dic["sfw"].append(dic["sfip"][ind])
                    dic["stw"].append(xyz[2] - d_z[ind])
                if not dic["explicit"]:
                    dic["spres"].append(dic["srst"].iget_kw("PRESSURE")[0][ind])
                dic["gc"] += 1
    if dic["boundaries"][2] > -1:
        for k in range(dic["sgrid"].nz):
            j = dic["sgrid"].ny - 1 - dic["boundaries"][2]
            for i in range(dic["sgrid"].nx):
                ii = dic["sgrid"].nx - i - 1
                ind = dic["sgrid"].get_active_index(ijk=(ii, j, k))
                if dic["sgrid"].active(ijk=(ii, j, k)):
                    dic["sai"].append(dic["gc"])
                    xyz = np.array(dic["sgrid"].get_xyz(ijk=(ii, j, k)))
                    d_y = 0.5 * dic["sinit"].iget_kw("DY")[0][ind]
                    dic["sbound"].append(
                        f"{dic['gc'] + 1} {ii + 1} {ii + 1} {j + 1} {j + 1} {k + 1} {k + 1} 'J' /"
                    )
                    dic["sxs"].append(xyz[0])
                    dic["sys"].append(xyz[1] + dic["mly"] * d_y * (-1))
                    dic["szs"].append(xyz[2])
                    dic["sfs"].append(dic["sfip"][ind])
                    dic["sts"].append(xyz[2] - d_z[ind])
                if not dic["explicit"]:
                    dic["spres"].append(dic["srst"].iget_kw("PRESSURE")[0][ind])
                dic["gc"] += 1
    if dic["boundaries"][3] > -1:
        for k in range(dic["sgrid"].nz):
            i = dic["boundaries"][3]
            for j in range(dic["sgrid"].ny):
                jj = dic["sgrid"].ny - j - 1
                ind = dic["sgrid"].get_active_index(ijk=(i, jj, k))
                if dic["sgrid"].active(ijk=(i, jj, k)):
                    dic["sai"].append(dic["gc"])
                    xyz = np.array(dic["sgrid"].get_xyz(ijk=(i, jj, k)))
                    d_x = 0.5 * dic["sinit"].iget_kw("DX")[0][ind]
                    dic["sbound"].append(
                        f"{dic['gc'] + 1} {i + 1} {i + 1} {jj + 1} {jj + 1} {k + 1} {k + 1} 'I-' /"
                    )
                    dic["sxe"].append(xyz[0] + dic["mlx"] * d_x)
                    dic["sye"].append(xyz[1])
                    dic["sze"].append(xyz[2])
                    dic["sfe"].append(dic["sfip"][ind])
                    dic["ste"].append(xyz[2] - d_z[ind])
                if not dic["explicit"]:
                    dic["spres"].append(dic["srst"].iget_kw("PRESSURE")[0][ind])
                dic["gc"] += 1
