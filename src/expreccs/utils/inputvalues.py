# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to set the requiried input values by expreccs.
"""

import csv
from io import StringIO
import numpy as np


def process_input(dic, in_file):
    """
    Function to process the input file

    Args:
        dic (dict): Global dictionary with required parameters
        in_file (str): Name of the input text file

    Returns:
        dic (dict): Global dictionary with new added parameters
    """
    lol = []
    with open(in_file, "r", encoding="utf8") as file:
        for row in csv.reader(file, delimiter="#"):
            lol.append(row)
    dic = readthefirstpart(lol, dic)
    set_xy_grid_function(dic)
    return dic


def set_xy_grid_function(dic):
    """
    Function to set the xy function for the grid z coordinates

    Args:
        dic (dict): Global dictionary with required parameters

    """
    lol = []
    with open(
        f"{dic['pat']}/templates/common/gridmako.mako", "r", encoding="utf8"
    ) as file:
        for i, row in enumerate(csv.reader(file, delimiter="#")):
            if i == 3:
                lol.append(f"    z = {dic['z_xy']}")
            elif len(row) == 0:
                lol.append("")
            else:
                lol.append(row[0])
    with open(
        f"{dic['pat']}/templates/common/grid.mako",
        "w",
        encoding="utf8",
    ) as file:
        file.write("\n".join(lol))


def readthefirstpart(lol, dic):
    """
    Function to process the lines in the configuration file.

    Args:
        lol (list): List of lines read from the input file
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters
        inc (int): Number of line in the input file before the first injection value
    """
    dic["flow"] = str(lol[1])[2:-2]  # Path to the flow executable
    dic["regional_dims"] = [float((lol[4][0].strip()).split()[j]) for j in range(3)]
    dic["reference_dims"] = dic["regional_dims"]
    for i, res in enumerate(["regional", "reference"]):
        dic[f"{res}_x_n"] = np.genfromtxt(
            StringIO(lol[5 + 3 * i][0]), delimiter=",", dtype=int
        )
        dic[f"{res}_y_n"] = np.genfromtxt(
            StringIO(lol[6 + 3 * i][0]), delimiter=",", dtype=int
        )
        dic[f"{res}_z_n"] = np.genfromtxt(
            StringIO(lol[7 + 3 * i][0]), delimiter=",", dtype=int
        )
        for ent in ["x_n", "y_n", "z_n"]:
            if dic[f"{res}_{ent}"].size == 1:
                dic[f"{res}_{ent}"] = [dic[f"{res}_{ent}"]]
        dic[f"{res}_noCells"] = [
            sum(dic[f"{res}_x_n"]),
            sum(dic[f"{res}_y_n"]),
            sum(dic[f"{res}_z_n"]),
        ]
    dic["site_location"] = [float((lol[11][0].strip()).split()[j]) for j in [0, 1]]
    dic["site_location"].append(0)
    dic["site_location"].extend(
        [float((lol[11][0].strip()).split()[j]) for j in [2, 3]]
    )
    dic["site_location"].append(dic["regional_dims"][2])
    dic["regional_bctype"] = (lol[12][0].strip()).split()[0]
    dic["reference_bctype"] = dic["regional_bctype"]
    if dic["regional_bctype"] == "porv":
        dic["regional_porv"] = [
            float((lol[12][0].strip()).split()[j + 1]) for j in range(4)
        ]
        dic["reference_porv"] = dic["regional_porv"]
    dic["site_bctype"] = (lol[13][0].strip()).split()[0]
    if dic["site_bctype"] == "porv":
        dic["site_porv"] = [
            float((lol[13][0].strip()).split()[j + 1]) for j in range(4)
        ]
    dic["fault_location"] = [float((lol[14][0].strip()).split()[j]) for j in [0, 1]]
    dic["fault_location"].append(0)
    dic["fault_mult"] = [float((lol[14][0].strip()).split()[j]) for j in [2, 3]]
    dic["fault_jump"] = float((lol[14][0].strip()).split()[4])
    dic["fault_site"] = []
    dic["fault_site"].append([float((lol[15][0].strip()).split()[j]) for j in [0, 1]])
    dic["fault_site"][-1].append(0)
    dic["fault_site"].append([float((lol[15][0].strip()).split()[j]) for j in [2, 3]])
    dic["fault_site"][-1].append(dic["regional_dims"][2])
    dic["fault_site_mult"] = [float((lol[15][0].strip()).split()[j]) for j in [4, 5]]
    dic["thicknes"] = np.genfromtxt(StringIO(lol[16][0]), delimiter=",", dtype=float)
    dic["satnum"] = dic["thicknes"].size  # No. saturation regions
    if dic["thicknes"].size == 1:
        dic["thicknes"] = [dic["thicknes"]]
    dic["pressure"] = float((lol[17][0].strip()).split()[0]) / 1.0e5  # To bars
    dic["temp_top"] = float((lol[17][0].strip()).split()[1])
    dic["temp_bottom"] = float((lol[17][0].strip()).split()[2])
    dic["rock_comp"] = float((lol[17][0].strip()).split()[3]) * 1.0e5  # To 1/bar
    dic["sensor_location"] = [float((lol[18][0].strip()).split()[j]) for j in range(3)]
    dic["z_xy"] = str(lol[19][0])  # The function for the reservoir surface
    index = 22  # Increase this if more rows are added to the model parameters part
    dic = readthesecondpart(lol, dic, index)
    return dic


def readthesecondpart(lol, dic, index):
    """
    Function to process the remaining lines in the configuration file

    Args:
        lol (list): List of lines read from the input file
        dic (dict): Global dictionary with required parameters
        inc (int): Number of line in the input file

    Returns:
        dic (dict): Global dictionary with new added parameters
    """
    dic["krwf"] = str(lol[index][0])  # Wetting rel perm saturation function [-]
    dic["krnf"] = str(lol[index + 1][0])  # Non-wetting rel perm saturation function [-]
    dic["pcwcf"] = str(lol[index + 2][0])  # Capillary pressure saturation function [Pa]
    index += 6
    for name in ["rock", "safu"]:
        dic[name] = []
    for i in range(dic["satnum"]):  # Saturation function values
        row = list((lol[index + i][0].strip()).split())
        dic["safu"].append(
            [
                float(row[1]),
                float(row[3]),
                float(row[5]),
                float(row[7]),
                float(row[9]) / 1.0e5,
                float(row[11]),
                float(row[13]),
                float(row[15]),
                float(row[17]),
            ]
        )  # Convert the pressure to bars
    index += 3 + dic["satnum"]
    for i in range(dic["satnum"]):  # Rock values
        row = list((lol[index + i][0].strip()).split())
        dic["rock"].append(
            [
                float(row[1]),
                float(row[3]),
                float(row[5]),
            ]
        )
    index += 3 + dic["satnum"]
    column = []
    for i in range(len(lol) - index):
        if not lol[index + i]:
            break
        row = list((lol[index + i][0].strip()).split())
        column.append(
            [
                float(row[0]),
                float(row[1]),
                float(row[2]),
                float(row[3]),
            ]
        )
    dic["wellCoord"] = column
    index += len(dic["wellCoord"]) + 3
    column = []
    if dic["site_bctype"] == "wells":
        dic["bc_wells"] = []
    for i in range(len(lol) - index):
        if not lol[index + i]:
            break
        row = list((lol[index + i][0].strip()).split())
        column.append([float(row[j]) for j in range(3 + 2 * len(dic["wellCoord"]))])
        if dic["site_bctype"] == "wells":
            dic["bc_wells"].append(
                [
                    float(row[j]) / 1e5
                    for j in range(
                        3 + 2 * len(dic["wellCoord"]), 3 + 2 * len(dic["wellCoord"]) + 8
                    )
                ]
            )
    dic["inj"] = column
    return dic
