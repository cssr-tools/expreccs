# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions for necessary files and variables to run OPM Flow.
"""

import os
import subprocess
from mako.template import Template


def reference_files(dic):
    """
    Function to write opm-related reference files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    mytemplate = Template(
        filename=f"{dic['pat']}/templates/{dic['tom']}/reference.mako"
    )
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/REFERENCE.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/FIPNUM_REFERENCE.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("FIPNUM\n")
        for fipnum in dic["reference_fipnum"]:
            file.write(f"{fipnum} \n")
        file.write("/\n")


def regional_files(dic):
    """
    Function to write opm-related regional files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    for name in ["regional"]:
        mytemplate = Template(
            filename=f"{dic['pat']}/templates/{dic['tom']}/{name}.mako"
        )
        var = {"dic": dic}
        filledtemplate = mytemplate.render(**var)
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/{name.upper()}.DATA",
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/FIPNUM_{name.upper()}.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("FIPNUM\n")
            for fipnum in dic[f"{name}_fipnum"]:
                file.write(f"{fipnum} \n")
            file.write("/\n")
    mytemplate = Template(filename=f"{dic['pat']}/templates/common/safu_eval.mako")
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/jobs/safu_eval.py",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"chmod u+x {dic['exe']}/{dic['fol']}/jobs/safu_eval.py")
    prosc = subprocess.run(
        ["python", f"{dic['exe']}/{dic['fol']}/jobs/safu_eval.py"],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")


def site_files(dic):
    """
    Function to write opm-related site files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    mytemplate = Template(filename=f"{dic['pat']}/templates/{dic['tom']}/site.mako")
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/SITE.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    mytemplate = Template(
        filename=f"{dic['pat']}/templates/{dic['tom']}/site_openboundaries.mako"
    )
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/SITE_OPENBOUNDARIES.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    mytemplate = Template(filename=f"{dic['pat']}/templates/common/grid.mako")
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/SITE.GRDECL",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
