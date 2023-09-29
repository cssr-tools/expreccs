# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions for necessary files and variables to run OPM Flow.
"""

import os
import subprocess
import numpy as np
from mako.template import Template


def write_files(dic, reservoir):
    """
    Function to write opm-related reference files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters
        reservoir (str): Name of the geological model

    """
    name = "site" if "site" in reservoir else reservoir
    mytemplate = Template(filename=f"{dic['pat']}/templates/decks/{name}.mako")
    var = {"dic": dic, "reservoir": name}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/{reservoir}/{reservoir.upper()}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/{reservoir}/FIPNUM_{name.upper()}.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("FIPNUM\n")
        for fipnum in dic[f"{name}_fipnum"]:
            file.write(f"{fipnum} \n")
        file.write("/\n")
    mytemplate = Template(
        filename=f"{dic['pat']}/templates/common/saturation_functions.mako"
    )
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/jobs/saturation_functions.py",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"chmod u+x {dic['exe']}/{dic['fol']}/jobs/saturation_functions.py")
    prosc = subprocess.run(
        [
            "python",
            f"{dic['exe']}/{dic['fol']}/jobs/saturation_functions.py",
            "-r",
            f"{reservoir}",
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    sections = ["geology", "regions", "grid"]
    for section in sections:
        mytemplate = Template(
            filename=os.path.join(dic["pat"], "templates", "common", f"{section}.mako")
        )
        var = {"dic": dic, "reservoir": name}
        filledtemplate = mytemplate.render(**var)
        with open(
            os.path.join(
                dic["exe"],
                dic["fol"],
                "preprocessing",
                reservoir,
                f"{section.upper()}_{name.upper()}.INC",
            ),
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)


def write_properties(dic):
    """
    Function to write some numpy files used in the plotting routine

    Args:
        dic (dict): Global dictionary with required parameters

    """
    schedule = [0]
    for nrst in dic["inj"]:
        for _ in range(round(nrst[0] / nrst[1])):
            schedule.append(schedule[-1] + nrst[1] * 86400.0)
    for fil in ["reference", "regional", f"site_{dic['site_bctype']}"]:
        np.save(f"{dic['exe']}/{dic['fol']}/output/{fil}/schedule", schedule)
        if fil == f"site_{dic['site_bctype']}":
            np.save(
                f"{dic['exe']}/{dic['fol']}/output/{fil}/nowells",
                len(dic["site_wellijk"]),
            )
        else:
            np.save(
                f"{dic['exe']}/{dic['fol']}/output/{fil}/nowells", len(dic["wellCoord"])
            )
        np.save(
            f"{dic['exe']}/{dic['fol']}/output/{fil}/nowells_site",
            len(dic["site_wellijk"]),
        )


def write_folders(dic):
    """
    Function to make the output folders

    Args:
        dic (dict): Global dictionary with required parameters

    """
    if not os.path.exists(f"{dic['exe']}/{dic['fol']}"):
        os.system(f"mkdir {dic['exe']}/{dic['fol']}")
    for fil in ["preprocessing", "jobs", "output", "postprocessing"]:
        if not os.path.exists(f"{dic['exe']}/{dic['fol']}/{fil}"):
            os.system(f"mkdir {dic['exe']}/{dic['fol']}/{fil}")
    for fil in ["reference", "regional", f"site_{dic['site_bctype']}"]:
        if not os.path.exists(f"{dic['exe']}/{dic['fol']}/preprocessing/{fil}"):
            os.system(f"mkdir {dic['exe']}/{dic['fol']}/preprocessing/{fil}")
        if not os.path.exists(f"{dic['exe']}/{dic['fol']}/output/{fil}"):
            os.system(f"mkdir {dic['exe']}/{dic['fol']}/output/{fil}")
    os.chdir(f"{dic['exe']}/{dic['fol']}")
