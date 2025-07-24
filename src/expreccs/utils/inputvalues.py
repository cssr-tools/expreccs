# SPDX-FileCopyrightText: 2023-2025 NORCE Research AS
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
    dic["hysteresis"] = False
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
    dic["ntabs"] = dic["satnum"]
    if dic["hysteresis"]:
        dic["ntabs"] *= 2
    process_tuning(dic)


def process_tuning(dic):
    """
    Preprocess tuning

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["tuning"] = False
    for value in dic["flow"].split():
        if "--enable-tuning" in value:
            if value[16:] in ["true", "True", "1"]:
                dic["tuning"] = True
                break
    if len(dic["inj"][0][0]) == 4:
        print(
            "\nAfter the 2025.04 release, column 4 in the first entry for the maximum "
            + "solver time step in the injection has been moved as a new entry, including "
            + "the items for the TUNING keyword, which gives more control when setting "
            + "the simulations. Please see the configuration files in the examples and "
            + "online documentation (Configuration file->Well-related parameters), and "
            + "update your configuration file accordingly.\n"
        )
        sys.exit()
    size = 3 if dic["site_bctype"][0] == "wells" else 2
    for i, inj in enumerate(dic["inj"]):
        if len(inj) > size:
            tmp = inj[-1].split("/")
            dic["inj"][i][-1] = tmp[0].strip()
            if len(tmp) > 1:
                for val in tmp[1:]:
                    dic["inj"][i].append(val.strip())


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
