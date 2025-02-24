# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions for necessary files and variables to run OPM Flow.
"""

import os
import csv
import subprocess
import numpy as np
from mako.template import Template


def write_files(dic, reservoir):
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
    mytemplate = Template(filename=f"{dic['pat']}/templates/decks/{name}.mako")
    var = {"dic": dic, "reservoir": name}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['fol']}/preprocessing/{reservoir}/{reservoir.upper()}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    with open(
        f"{dic['fol']}/preprocessing/{reservoir}/FIPNUM_{name.upper()}.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("FIPNUM\n")
        for fipnum in dic[f"{name}_fipnum"]:
            file.write(f"{fipnum} \n")
        file.write("/\n")
    if name == "regional":
        with open(
            f"{dic['fol']}/preprocessing/{reservoir}/MULTX_{name.upper()}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("MULTX\n")
            for multx in dic[f"{name}_multx"]:
                file.write(f"{multx} \n")
            file.write("/\n")
        with open(
            f"{dic['fol']}/preprocessing/{reservoir}/MULTY_{name.upper()}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("MULTY\n")
            for multy in dic[f"{name}_multy"]:
                file.write(f"{multy} \n")
            file.write("/\n")
        with open(
            f"{dic['fol']}/preprocessing/{reservoir}/MULTX-_{name.upper()}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("MULTX-\n")
            for multx in dic[f"{name}_multx-"]:
                file.write(f"{multx} \n")
            file.write("/\n")
        with open(
            f"{dic['fol']}/preprocessing/{reservoir}/MULTY-_{name.upper()}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("MULTY-\n")
            for multy in dic[f"{name}_multy-"]:
                file.write(f"{multy} \n")
            file.write("/\n")

    mytemplate = Template(
        filename=f"{dic['pat']}/templates/common/saturation_functions.mako"
    )
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['fol']}/jobs/saturation_functions.py",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"chmod u+x {dic['fol']}/jobs/saturation_functions.py")
    prosc = subprocess.run(
        [
            "python",
            f"{dic['fol']}/jobs/saturation_functions.py",
            "-r",
            f"{reservoir}",
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    sections = ["geology", "regions"]
    var = {"dic": dic, "reservoir": name}
    for section in sections:
        mytemplate = Template(
            filename=os.path.join(dic["pat"], "templates", "common", f"{section}.mako")
        )
        filledtemplate = mytemplate.render(**var)
        with open(
            os.path.join(
                dic["fol"],
                "preprocessing",
                reservoir,
                f"{section.upper()}_{name.upper()}.INC",
            ),
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
    filledtemplate = dic["gridtemplate"].render(**var)
    with open(
        os.path.join(
            dic["fol"],
            "preprocessing",
            reservoir,
            f"GRID_{name.upper()}.INC",
        ),
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
    np.save(f"{dic['fol']}/output/regional/schedule", dic["schedule_r"])
    np.save(f"{dic['fol']}/output/reference/schedule", dic["schedule_s"])
    np.save(
        f"{dic['fol']}/output/site_{dic['site_bctype'][0]}/schedule",
        dic["schedule_s"],
    )
    for fil in ["reference", "regional", f"site_{dic['site_bctype'][0]}"]:
        if fil == f"site_{dic['site_bctype'][0]}":
            np.save(
                f"{dic['fol']}/output/{fil}/nowells",
                len(dic["site_wellijk"]),
            )
        else:
            np.save(
                f"{dic['fol']}/output/{fil}/nowells",
                len(dic["well_coords"]),
            )
        np.save(
            f"{dic['fol']}/output/{fil}/nowells_site",
            len(dic["site_wellijk"]),
        )


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
    for fil in ["preprocessing", "jobs", "output", "postprocessing"]:
        if not os.path.exists(f"{dic['fol']}/{fil}"):
            os.system(f"mkdir {dic['fol']}/{fil}")
    for fil in ["reference", "regional", f"site_{dic['site_bctype'][0]}"]:
        if not os.path.exists(f"{dic['fol']}/preprocessing/{fil}"):
            os.system(f"mkdir {dic['fol']}/preprocessing/{fil}")
        if not os.path.exists(f"{dic['fol']}/output/{fil}"):
            os.system(f"mkdir {dic['fol']}/output/{fil}")
    os.chdir(f"{dic['fol']}")
