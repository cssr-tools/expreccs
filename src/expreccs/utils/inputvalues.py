# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to set the requiried input values by expreccs.
"""

import sys
import tomllib
import subprocess


def process_input(dic, in_file):
    """
    Function to process the configuration file

    Args:
        dic (dict): Global dictionary\n
        in_file (str): Name of the input toml file

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["hysteresis"] = 0
    dic["salinity"] = 0.0
    dic["rock_comp"] = 0.0
    dic["iterations"] = 0
    dic["z_xy"] = 0.0
    with open(in_file, "rb") as file:
        dic.update(tomllib.load(file))
    check_entries(dic)
    dic["satnum"] = len(dic["thickness"])
    dic["reference_dims"] = dic["regional_dims"]
    for res in ["regional", "reference"]:
        dic[f"{res}_num_cells"] = [
            sum(dic[f"{res}_x_n"]),
            sum(dic[f"{res}_y_n"]),
            sum(dic[f"{res}_z_n"]),
        ]
    if dic["co2store"] == "gasoil":
        dic["liq"] = "OIL"
        dic["lin"] = "OIL"
        dic["l"] = "O"
    else:
        dic["liq"] = "WAT"
        dic["lin"] = "WATER"
        dic["l"] = "W"


def check_entries(dic):
    """
    Check the entries from the toml configuration file

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    if (
        subprocess.call(
            dic["flow"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        != 1
    ):
        print(
            f"\nThe executable 'flow = {dic['flow']}' is not found, "
            f"see the information about installation in the documentation.\n"
        )
        sys.exit()
