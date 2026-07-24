# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Utiliy functions to set the requiried input values by expreccs"""

import subprocess
import sys
import tomllib

import numpy as np


def process_input(dic, in_file):
    """Process the configuration file"""
    (
        dic["hysteresis"],
        dic["salinity"],
        dic["rock_comp"],
        dic["iterations"],
        dic["z_xy"],
    ) = (False, 0.0, 0.0, 0, 0.0)
    with open(in_file, "rb") as file:
        dic.update(tomllib.load(file))
    check_entries(dic)
    dic["satnum"] = len(dic["thickness"])
    dic["reference_dims"] = dic["regional_dims"]
    for res in ["regional", "reference"]:
        dic[f"{res}_num_cells"] = [
            np.sum(dic[f"{res}_x_n"]),
            np.sum(dic[f"{res}_y_n"]),
            np.sum(dic[f"{res}_z_n"]),
        ]
    dic["ntabs"] = dic["satnum"]
    if dic["hysteresis"]:
        dic["ntabs"] *= 2
    process_tuning(dic)


def process_tuning(dic):
    """Preprocess tuning"""
    dic["tuning"] = False
    for value in dic["flow"].split():
        if "--enable-tuning" in value and value[16:] in ["true", "True", "1"]:
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
    """Check the entries from the toml configuration file"""
    if (
        subprocess.call(
            dic["flow"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        != 1
    ):
        print(
            f"\nThe executable 'flow = {dic['flow']}' is not found, see the information about "
            "installation in the documentation.\n"
        )
        sys.exit()
