# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy script for creating a deck with projected pressures from given
regional and site decks.
"""

import os
import csv
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Polygon, Point
from scipy.interpolate import LinearNDInterpolator
from resdata.grid import Grid
from resdata.resfile import ResdataFile


def create_deck(dic):
    """Create a deck from given reg and site decks with projected pressures"""
    case = f"{dic['exe']}/{dic['reg']}/{dic['reg'].upper()}"
    rst = case + ".UNRST"
    grid = case + ".EGRID"
    init = case + ".INIT"
    dic["rrst"], dic["rgrid"] = ResdataFile(rst), Grid(grid)
    case = f"{dic['exe']}/{dic['sit']}/{dic['sit'].upper()}"
    rst = case + ".UNRST"
    grid = case + ".EGRID"
    init = case + ".INIT"
    dic["sdata"] = case + ".DATA"
    dic["srst"], dic["sgrid"], dic["sinit"] = (
        ResdataFile(rst),
        Grid(grid),
        ResdataFile(init),
    )
    dic["sbound"], dic["sai"], dic["gc"] = [], [], 0
    dic["sxs"], dic["sxe"], dic["sxn"], dic["sxw"] = [], [], [], []
    dic["sys"], dic["sye"], dic["syn"], dic["syw"] = [], [], [], []
    dic["szs"], dic["sze"], dic["szn"], dic["szw"] = [], [], [], []
    dic["rbound"], dic["rcoord"], dic["sdel"], dic["snum"], dic["fipn"] = (
        [],
        [],
        [],
        [],
        [],
    )
    find_ij_orientation(dic)
    extract_site_borders(dic)
    find_regional_cells(dic)
    dynamic_mapping(dic)
    write_files(dic)


def handle_grid_coord(dic):
    """Process the regional and site grid coordinates"""
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
                if c_z[-1] >= z_t and c_z[-1] <= z_b:
                    dic["fipn"].append("1")
                else:
                    dic["fipn"].append("4")
            else:
                dic["fipn"].append("4")
        else:
            dic["fipn"].append("4")
    dic["c_x"] = np.array(c_x)
    dic["c_y"] = np.array(c_y)
    dic["c_z"] = np.array(c_z)
    dic["rnxy"] = dic["rgrid"].nx * dic["rgrid"].ny


def check_regional_neighbours(dic, gind, p):
    """Add to the interpolator neighbouring regional cells"""
    if dic["rgrid"].nz > 1:
        noise = -1e-4 * np.random.rand()
    else:
        noise = 0
    if dic["rgrid"].get_active_index(global_index=gind - dic["rgrid"].nx) not in dic[
        f"ri{p}"
    ] and dic["rgrid"].active(global_index=gind - dic["rgrid"].nx):
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
        dic["fipn"][
            gind - dic["rgrid"].nx
        ] = f"{2 if int(dic['fipn'][gind-dic['rgrid'].nx])==2 else 3}"
    if dic["rgrid"].get_active_index(global_index=gind + dic["rgrid"].nx) not in dic[
        f"ri{p}"
    ] and dic["rgrid"].active(global_index=gind + dic["rgrid"].nx):
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
        dic["fipn"][
            gind + dic["rgrid"].nx
        ] = f"{2 if int(dic['fipn'][gind+dic['rgrid'].nx])==2 else 3}"
    if dic["rgrid"].get_active_index(global_index=gind - 1) not in dic[
        f"ri{p}"
    ] and dic["rgrid"].active(global_index=gind - 1):
        dic[f"rx{p}"].append(dic["rgrid"].get_xyz(global_index=gind - 1)[0])
        dic[f"ry{p}"].append(dic["rgrid"].get_xyz(global_index=gind - 1)[1])
        dic[f"rz{p}"].append(noise + dic["rgrid"].get_xyz(global_index=gind - 1)[2])
        dic[f"ri{p}"].append(dic["rgrid"].get_active_index(global_index=gind - 1))
        dic["fipn"][gind - 1] = f"{2 if int(dic['fipn'][gind-1])==2 else 3}"
    if dic["rgrid"].get_active_index(global_index=gind + 1) not in dic[
        f"ri{p}"
    ] and dic["rgrid"].active(global_index=gind + 1):
        dic[f"rx{p}"].append(dic["rgrid"].get_xyz(global_index=gind + 1)[0])
        dic[f"ry{p}"].append(dic["rgrid"].get_xyz(global_index=gind + 1)[1])
        dic[f"rz{p}"].append(noise + dic["rgrid"].get_xyz(global_index=gind + 1)[2])
        dic[f"ri{p}"].append(dic["rgrid"].get_active_index(global_index=gind + 1))
        dic["fipn"][gind + 1] = f"{2 if int(dic['fipn'][gind+1])==2 else 3}"
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
            dic["fipn"][
                gind - dic["rnxy"]
            ] = f"{2 if int(dic['fipn'][gind- dic['rnxy']])==2 else 3}"
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
            dic["fipn"][
                gind + dic["rnxy"]
            ] = f"{2 if int(dic['fipn'][gind+ dic['rnxy']])==2 else 3}"


def check_intersection(dic, ind, gind, i, n):
    """Check if there are nnc in the regional/site overlapping"""
    shift = [dic["rgrid"].nx, 1, dic["rgrid"].nx, 1][n]
    x_l, y_l, x_p, y_p = 0, 0, 0, 0
    l_p = [0, 0]
    x_m = dic["rgrid"].get_xyz(active_index=ind)[0]
    y_m = dic["rgrid"].get_xyz(active_index=ind)[1]
    if dic["rgrid"].active(global_index=gind - shift):
        x_l = dic["rgrid"].get_xyz(global_index=gind - shift)[0]
        y_l = dic["rgrid"].get_xyz(global_index=gind - shift)[1]
        l_p[0] = 1
    if dic["rgrid"].active(global_index=gind + shift):
        x_p = dic["rgrid"].get_xyz(global_index=gind + shift)[0]
        y_p = dic["rgrid"].get_xyz(global_index=gind + shift)[1]
        l_p[1] = 1
    if i > [dic["sgrid"].nx, dic["sgrid"].ny, dic["sgrid"].nx, dic["sgrid"].nx][n]:
        lift = -1e-4
    else:
        lift = 1e-4
    dic[f"rkg{['n', 'w', 's', 'e'][n]}"].append(
        (dic["rgrid"].get_xyz(active_index=ind)[2] + lift, ind)
    )
    if sum(l_p) == 2:
        xy = [x_l, y_l, x_p, y_p]
    elif l_p[1] == 1:
        xy = [x_m, y_m, x_p, y_p]
    elif l_p[0] == 1:
        xy = [x_l, y_l, x_m, y_m]
    else:
        return 0
    return LineString([(xy[0], xy[1]), (xy[2], xy[3])])


def find_regional_cells(dic):
    """Find the cells to build the interpolator"""
    handle_grid_coord(dic)
    count = -1
    for n, p in enumerate(
        ["n", "w", "s", "e"],
    ):
        dic[f"rx{p}"], dic[f"ry{p}"], dic[f"rz{p}"], dic[f"ri{p}"], dic[f"sd{p}"] = (
            [],
            [],
            [],
            [],
            [],
        )
        dic[f"rkg{p}"] = []
        for i, (x_c, y_c, z_c) in enumerate(
            zip(dic[f"sx{p}"], dic[f"sy{p}"], dic[f"sz{p}"])
        ):
            count += 1
            ind = pd.Series(
                (abs(dic["c_x"] - x_c) + abs(dic["c_y"] - y_c) + abs(dic["c_z"] - z_c))
            ).argmin()
            gind = dic["rgrid"].global_index(ind)
            line = check_intersection(dic, ind, gind, i, n)
            if line == 0:
                dic["sdel"].append(count)
                dic[f"sd{p}"].append(i)
                continue
            border = LineString(
                [
                    (dic["sbox"][n][0], dic["sbox"][n][1]),
                    (dic["sbox"][n + 1][0], dic["sbox"][n + 1][1]),
                ]
            )
            if line.intersects(border):
                dic["snum"].append(dic["sai"][count])
                dic[f"rx{p}"].append(dic["rgrid"].get_xyz(active_index=ind)[0])
                dic[f"ry{p}"].append(dic["rgrid"].get_xyz(active_index=ind)[1])
                dic[f"rz{p}"].append(dic["rgrid"].get_xyz(active_index=ind)[2])
                dic[f"ri{p}"].append(ind)
                dic["fipn"][gind] = "2"
                check_regional_neighbours(dic, gind, p)
            else:
                dic["sdel"].append(count)
                dic[f"sd{p}"].append(i)
        dic[f"sx{p}"], dic[f"sy{p}"], dic[f"sz{p}"] = (
            np.array(dic[f"sx{p}"]),
            np.array(dic[f"sy{p}"]),
            np.array(dic[f"sz{p}"]),
        )
        dic[f"ri{p}"] = np.array(dic[f"ri{p}"])
        dic[f"rx{p}"] = np.array(dic[f"rx{p}"])
        dic[f"ry{p}"] = np.array(dic[f"ry{p}"])
        dic[f"rz{p}"] = np.array(dic[f"rz{p}"])
    for rem in reversed(dic["sdel"]):
        del dic["sbound"][rem]
    git = (
        "-- This file was generated by expreccs https://github.com/cssr-tools/expreccs"
    )
    dic["fipn"].insert(0, "FIPNUM")
    dic["fipn"].insert(0, git)
    dic["fipn"].insert(0, "--Copyright (C) 2024 NORCE")
    dic["fipn"].append("/")
    with open(
        f"{dic['exe']}/{dic['reg']}/FIPNUM.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("\n".join(dic["fipn"]))


def dynamic_mapping(dic):
    """Project the pressures from the regional to the site over time"""
    dic["rp"] = ["" for _ in range(dic["rrst"].num_report_steps())]
    for p in ["n", "w", "s", "e"]:
        dic[f"rp{p}"] = [[] for _ in range(dic["rrst"].num_report_steps())]
    for i in range(dic["rrst"].num_report_steps()):
        project_pressures(dic, i)


def project_pressures(dic, i):
    """Project the pressures at restart number i"""
    count, c_c = 0, 0
    for p in ["n", "w", "s", "e"]:
        z_p = np.array(dic["rrst"].iget_kw("PRESSURE")[i])[dic[f"ri{p}"]]
        w_d = np.array(dic["rrst"].iget_kw("WAT_DEN")[i])
        if dic["rgrid"].nz > 1:
            interp = LinearNDInterpolator(
                list(zip(dic[f"rx{p}"], dic[f"ry{p}"], dic[f"rz{p}"])), z_p
            )
            for k, (x, y, z) in enumerate(
                zip(dic[f"sx{p}"], dic[f"sy{p}"], dic[f"sz{p}"])
            ):
                if dic["sai"][count] in dic["snum"]:
                    z_b = interp((x, y, z))
                    if np.isnan(z_b):
                        z_b = (
                            interp((x, y, dic[f"rkg{p}"][k][0]))
                            + (z - dic[f"rkg{p}"][k][0])
                            * w_d[dic[f"rkg{p}"][k][1]]
                            * 9.81
                            / 1e5
                        )
                    dic[f"rp{p}"][
                        i
                    ] = f"{dic['sai'][count]+1} DIRICHLET WATER 1* {z_b} /\n"
                    dic["rp"][i] += dic[f"rp{p}"][i]
                c_c += 1
                count += 1
        else:
            interp = LinearNDInterpolator(list(zip(dic[f"rx{p}"], dic[f"ry{p}"])), z_p)
            for x, y in zip(dic[f"sx{p}"], dic[f"sy{p}"]):
                if dic["sai"][count] in dic["snum"]:
                    dic[f"rp{p}"][
                        i
                    ] = f"{dic['sai'][count]+1} DIRICHLET WATER 1* {interp((x, y))} /\n"
                    dic["rp"][i] += dic[f"rp{p}"][i]
                count += 1
                c_c += 1


def write_files(dic):
    """Write the files"""
    dic["files"] = [
        f for f in os.listdir(f"{dic['exe']}/{dic['sit']}") if f.endswith(".INC")
    ]
    for file in dic["files"]:
        os.system(f"scp -r {dic['exe']}/{dic['sit']}/{file} {dic['exe']}/{dic['fol']}")
    lol = []
    with open(dic["sdata"], "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2]
            if 0 < nrwo.find("\\t"):
                nrwo = nrwo.replace("\\t", " ")
            lol.append(nrwo)
            if lol[-1] == "GRID":
                lol.append("INCLUDE")
                lol.append("'BCCON.INC' /")
    count = 1
    with open(
        f"{dic['exe']}/{dic['fol']}/EXPRECCS.DATA",
        "w",
        encoding="utf8",
    ) as file:
        for i, row in enumerate(lol):
            if i < len(lol) - 1:
                if lol[i + 1] == "TSTEP":
                    file.write(row)
                    file.write("\n")
                    file.write("INCLUDE\n")
                    file.write(f"'bc/BCPROP{count}.INC' /\n")
                    count += 1
                else:
                    file.write(row)
                    file.write("\n")
            else:
                file.write(row)
    git = (
        "-- This file was generated by expreccs https://github.com/cssr-tools/expreccs"
    )
    dic["sbound"].insert(0, "BCCON")
    dic["sbound"].insert(0, git)
    dic["sbound"].insert(0, "--Copyright (C) 2024 NORCE")
    dic["sbound"].append("/")
    with open(
        f"{dic['exe']}/{dic['fol']}/BCCON.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("\n".join(dic["sbound"]))
    for i in range(dic["rrst"].num_report_steps()):
        dic["rp"][i] = [dic["rp"][i]]
        dic["rp"][i].insert(0, "BCPROP\n")
        dic["rp"][i].insert(0, git + "\n")
        dic["rp"][i].insert(0, "--Copyright (C) 2024 NORCE\n")
        dic["rp"][i].append("/")
        with open(
            f"{dic['exe']}/{dic['fol']}/bc/BCPROP{i}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("".join(dic["rp"][i]))


def find_ij_orientation(dic):
    """Find if the counting is left/right handed"""
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
    """Get the index/coord from the site border"""
    for k in range(dic["sgrid"].nz):
        j = 0
        for i in range(dic["sgrid"].nx):
            if dic["sgrid"].active(ijk=(i, j, k)):
                dic["sai"].append(dic["gc"])
                ind = dic["sgrid"].get_active_index(ijk=(i, j, k))
                xyz = np.array(dic["sgrid"].get_xyz(ijk=(i, j, k)))
                d_y = 0.5 * dic["sinit"].iget_kw("DY")[0][ind]
                dic["sbound"].append(
                    f"{dic['gc'] + 1} {i + 1} {i + 1} {j + 1} {j + 1} {k + 1} {k + 1} 'J-' /"
                )
                dic["sxn"].append(xyz[0])
                dic["syn"].append(xyz[1] + dic["mly"] * d_y)
                dic["szn"].append(xyz[2])
            dic["gc"] += 1
    for k in range(dic["sgrid"].nz):
        i = dic["sgrid"].nx - 1
        for j in range(dic["sgrid"].ny):
            if dic["sgrid"].active(ijk=(i, j, k)):
                dic["sai"].append(dic["gc"])
                ind = dic["sgrid"].get_active_index(ijk=(i, j, k))
                xyz = np.array(dic["sgrid"].get_xyz(ijk=(i, j, k)))
                d_x = 0.5 * dic["sinit"].iget_kw("DX")[0][ind]
                dic["sbound"].append(
                    f"{dic['gc'] + 1} {i + 1} {i + 1} {j + 1} {j + 1} {k + 1} {k + 1} 'I' /"
                )
                dic["sxw"].append(xyz[0] + dic["mlx"] * d_x * (-1))
                dic["syw"].append(xyz[1])
                dic["szw"].append(xyz[2])
            dic["gc"] += 1
    for k in range(dic["sgrid"].nz):
        j = dic["sgrid"].ny - 1
        for i in range(dic["sgrid"].nx):
            ii = dic["sgrid"].nx - i - 1
            if dic["sgrid"].active(ijk=(ii, j, k)):
                dic["sai"].append(dic["gc"])
                ind = dic["sgrid"].get_active_index(ijk=(ii, j, k))
                xyz = np.array(dic["sgrid"].get_xyz(ijk=(ii, j, k)))
                d_y = 0.5 * dic["sinit"].iget_kw("DY")[0][ind]
                dic["sbound"].append(
                    f"{dic['gc'] + 1} {ii + 1} {ii + 1} {j + 1} {j + 1} {k + 1} {k + 1} 'J' /"
                )
                dic["sxs"].append(xyz[0])
                dic["sys"].append(xyz[1] + dic["mly"] * d_y * (-1))
                dic["szs"].append(xyz[2])
            dic["gc"] += 1
    for k in range(dic["sgrid"].nz):
        i = 0
        for j in range(dic["sgrid"].ny):
            jj = dic["sgrid"].ny - j - 1
            if dic["sgrid"].active(ijk=(i, jj, k)):
                dic["sai"].append(dic["gc"])
                ind = dic["sgrid"].get_active_index(ijk=(i, jj, k))
                xyz = np.array(dic["sgrid"].get_xyz(ijk=(i, jj, k)))
                d_x = 0.5 * dic["sinit"].iget_kw("DX")[0][ind]
                dic["sbound"].append(
                    f"{dic['gc'] + 1} {i + 1} {i + 1} {jj + 1} {jj + 1} {k + 1} {k + 1} 'I-' /"
                )
                dic["sxe"].append(xyz[0] + dic["mlx"] * d_x)
                dic["sye"].append(xyz[1])
                dic["sze"].append(xyz[2])
            dic["gc"] += 1
