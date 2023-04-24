"""
Utiliy functions to set the requiried input values by expreccs.
"""

import csv


def process_input(dic, in_file):
    """
    Function to process the input file

    Args:
        dic (dict): Global dictionary with required parameters
        in_file (str): Name of the input text file

    Returns:
        dic (dict): Global dictionary with new added parameters
    """
    dic["tom"] = "co2"  # Physical model
    lol = []
    with open(in_file, "r", encoding="utf8") as file:
        for row in csv.reader(file, delimiter="#"):
            lol.append(row)
    dic = readthefirstpart(lol, dic)
    return dic


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
    dic["regional_noCells"] = [int((lol[5][0].strip()).split()[j]) for j in range(3)]
    dic["site_location"] = [float((lol[6][0].strip()).split()[j]) for j in range(6)]
    dic["site_noCells"] = [int((lol[7][0].strip()).split()[j]) for j in range(3)]
    dic["fault_location"] = [float((lol[8][0].strip()).split()[j]) for j in range(3)]
    dic["fault_mult"] = [float((lol[8][0].strip()).split()[j + 3]) for j in range(2)]
    dic["fault_site"] = []
    dic["fault_site"].append([float((lol[9][0].strip()).split()[j]) for j in range(3)])
    dic["fault_site"].append(
        [float((lol[9][0].strip()).split()[j + 3]) for j in range(3)]
    )
    dic["fault_site_mult"] = [
        float((lol[9][0].strip()).split()[j + 6]) for j in range(2)
    ]
    dic["satnum"] = int(lol[10][0])  # No. saturation regions
    dic["zfact"] = round(dic["site_noCells"][2] / dic["regional_noCells"][2])
    dic["regional_satnum"] = round(dic["satnum"] / dic["zfact"])
    dic["site_dims"] = [
        dic["site_location"][j + 3] - dic["site_location"][j] for j in range(3)
    ]
    for name in ["regional", "site"]:
        dic[f"{name}_dsize"] = [
            round(dic[f"{name}_dims"][i] / dic[f"{name}_noCells"][i]) for i in range(3)
        ]
    dic["reference_noCells"] = [
        round(dic["regional_dims"][j] / dic["site_dsize"][j]) for j in range(3)
    ]
    dic["reference_dims"] = dic["regional_dims"]
    index = 13  # Increase this if more rows are added to the model parameters part
    dic["krwf"] = str(lol[index][0])  # Wetting rel perm saturation function [-]
    dic["krcf"] = str(lol[index + 1][0])  # Non-wetting rel perm saturation function [-]
    dic["pcwcf"] = str(lol[index + 2][0])  # Capillary pressure saturation function [Pa]
    index += 6
    for name in ["rock", "safu"]:
        dic[name] = []
    for i in range(dic["satnum"]):  # Saturation function values
        row = list((lol[index + i][0].strip()).split())
        dic["safu"].append(
            [
                float(row[1]),
                1.0 - float(row[3]),
                float(row[5]),
                float(row[7]),
                float(row[9]) / 1.0e5,
            ]
        )  # Convert the pressure to bars
    index += 3 + dic["satnum"]
    for i in range(dic["satnum"]):  # Rock values
        row = list((lol[index + i][0].strip()).split())
        dic["rock"].append(
            [
                float(row[1]),
                float(row[3]),
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
            ]
        )
    dic["wellCoord"] = column
    index += len(dic["wellCoord"]) + 3
    column = []
    for i in range(len(lol) - index):
        if not lol[index + i]:
            break
        row = list((lol[index + i][0].strip()).split())
        column.append([float(row[j]) for j in range(2 + 2 * len(dic["wellCoord"]))])
    dic["inj"] = column
    return dic
