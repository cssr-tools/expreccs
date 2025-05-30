# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912

"""
Utiliy functions for necessary files and variables to run OPM Flow.
"""

import os
import csv
import subprocess
from mako.template import Template


def write_files(dic, reservoir, iteration=0):
    """
    Function to write opm-related reference files by running mako templates

    Args:
        dic (dict): Global dictionary\n
        reservoir (str): Name of the geological model

    Returns:
        None

    """
    name = "site" if "site" in reservoir else reservoir
    name = "regional" if "regional" in name else name
    relpath = ""
    if iteration > 0:
        relpath = "../regional/"
    mytemplate = Template(filename=f"{dic['pat']}/templates/decks/{name}.mako")
    var = {"dic": dic, "reservoir": name, "inc": reservoir, "relpath": relpath}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic[f'fpre{reservoir}']}{reservoir.upper()}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    if name == "regional" and dic["iterations"] > 0:
        for mlt in ["X", "Y", "X-", "Y-"]:
            with open(
                f"{dic[f'fpre{reservoir}']}{reservoir.upper()}_MULT{mlt}.INC",
                "w",
                encoding="utf8",
            ) as file:
                file.write(f"MULT{mlt}\n")
                for val in dic[f"{name}_mult{mlt.lower()}"]:
                    file.write(f"{val} ")
                file.write("/\n")
    if iteration > 0:
        return
    if name != "site":
        kwrs = ["fipnum"]
        if name == "regional":
            kwrs += ["opernum"]
        for kwr in kwrs:
            dic[f"{name}_{kwr}"].insert(0, f"{kwr.upper()}\n")
            dic[f"{name}_{kwr}"].append("/")
            with open(
                f"{dic[f'fpre{reservoir}']}{reservoir.upper()}_{kwr.upper()}.INC",
                "w",
                encoding="utf8",
            ) as file:
                file.write("".join(dic[f"{name}_{kwr}"]))
            dic[f"{name}_{kwr}"] = dic[f"{name}_{kwr}"][1:-1]
    mytemplate = Template(
        filename=f"{dic['pat']}/templates/common/saturation_functions.mako"
    )
    var = {"dic": dic, "reservoir": reservoir}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['fol']}/saturation_functions.py",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"chmod u+x {dic['fol']}/saturation_functions.py")
    prosc = subprocess.run(
        [
            "python",
            f"{dic['fol']}/saturation_functions.py",
            "-r",
            f"{reservoir}",
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    os.system(f"rm {dic['fol']}/saturation_functions.py")
    var = {"dic": dic, "reservoir": name}
    filledtemplate = dic["gridtemplate"].render(**var)
    with open(
        f"{dic[f'fpre{reservoir}']}{reservoir.upper()}_GRID.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)


def write_properties(dic):
    """
    Write some numpy files used in the plotting routine

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["schedule_r"] = [0]
    dic["schedule_s"] = [0]
    for nrst in dic["inj"]:
        for _ in range(round(nrst[0][0] / nrst[0][1])):
            dic["schedule_r"].append(dic["schedule_r"][-1] + nrst[0][1] * 86400.0)
        for _ in range(round(nrst[0][0] / nrst[0][2])):
            dic["schedule_s"].append(dic["schedule_s"][-1] + nrst[0][2] * 86400.0)


def set_gridmako(dic, f_xy):
    """
    Set the mainfold function in the grid for the reservoir z profile

    Args:
        dic (dict): Global dictionary\n
        f_xy: The function for the reservoir surface

    Returns:
        dic (dict): Modified global dictionary

    """
    lol = []
    with open(f"{dic['pat']}/templates/common/grid.mako", "r", encoding="utf8") as file:
        for i, row in enumerate(csv.reader(file, delimiter="#")):
            if i == 3:
                lol.append(f"    z = {f_xy}")
            elif len(row) == 0:
                lol.append("")
            else:
                lol.append(row[0])
    dic["gridtemplate"] = Template(text="\n".join(lol))


def write_folders(dic):
    """
    Function to make the output folders

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    if not os.path.exists(f"{dic['fol']}"):
        os.system(f"mkdir {dic['fol']}")
    if not dic["subfolders"]:
        return
    for fil in ["preprocessing", "simulations"]:
        if not os.path.exists(f"{dic['fol']}/{fil}"):
            os.system(f"mkdir {dic['fol']}/{fil}")
    if dic["mode"] in ["all"]:
        for fil in ["reference", "regional", f"site_{dic['site_bctype'][0]}"]:
            if not os.path.exists(f"{dic['fol']}/preprocessing/{fil}"):
                os.system(f"mkdir {dic['fol']}/preprocessing/{fil}")
            if not os.path.exists(f"{dic['fol']}/simulations/{fil}"):
                os.system(f"mkdir {dic['fol']}/simulations/{fil}")
    else:
        names = []
        if dic["mode"] in ["reference", "regional"]:
            names = [dic["mode"]]
        elif dic["mode"] == "regional_site":
            names = ["regional", f"site_{dic['site_bctype'][0]}"]
        elif dic["mode"] == "site":
            names = [f"site_{dic['site_bctype'][0]}"]
        for name in names:
            if not os.path.exists(f"{dic['fol']}/preprocessing/{name}"):
                os.system(f"mkdir {dic['fol']}/preprocessing/{name}")
            if not os.path.exists(f"{dic['fol']}/simulations/{name}"):
                os.system(f"mkdir {dic['fol']}/simulations/{name}")
