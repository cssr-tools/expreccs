#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to preprocess, evaluate, and postprocess the well locations.
"""

import argparse
import json
import sys
import os
import numpy as np
from resdata.resfile import ResdataFile
from resdata.summary import Summary
from resdata.grid import Grid
from mako.template import Template

KG_TO_MT = 1e-9
RDEN = 1.868433  # kg/sm3
STRESSC = 0.134


def delete():
    """Remove the files with the following extensions"""
    for ext in [
        "DATA",
        "DBG",
        "EGRID",
        "PRT",
        "SMSPEC",
        "UNRST",
        "UNSMRY",
        "INC",
        "INIT",
        "stderr.0",
        "stderr.1",
        "stdout.0",
        "stdout.1",
    ]:
        os.system(f"rm *.{ext}")
    os.system("rm -rf logs")


def input_constraints(options):
    """Check the input constraints"""
    if options.mode == "post":
        exe = "/".join(os.getcwd().split("/")[:-2])
    else:
        exe = "/".join(os.getcwd().split("/")[:-5])

    with open(f"{exe}/configuration.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    name = config["name"].upper()

    grid = Grid(f"{exe}/deck/{name}.EGRID")

    with open("point_0.json", "r", encoding="utf-8") as f:
        points = json.load(f)

    nwells = int(len(points) / 3)

    wellij= []
    for i in range(nwells):
        wellij.append(
            (
                int(points[f"i{0 if i<10 else ''}{int(i)}"]) - 1,
                int(points[f"j{0 if i<10 else ''}{int(i)}"]) - 1,
                0 if int(points[f"k{0 if i<10 else ''}{int(i)}"]) == 1 else 4,
                2 if int(points[f"k{0 if i<10 else ''}{int(i)}"]) == 1 else 4,
            )
        )
        if not grid.active(ijk=(wellij[-1][0], wellij[-1][1], wellij[-1][2])) and not grid.active(ijk=(wellij[-1][0], wellij[-1][1], wellij[-1][3])):
            with open("func", "w", encoding="utf-8") as f:
                f.write("-1e20")
            delete()
            return [], [], [], [], []
    return exe, name, nwells, points, config


def locations():
    """Main function to set up the well location optimisation"""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--mode", type=str, default="")

    options, _ = arg_parser.parse_known_args(args=sys.argv[1:])

    exe, name, nwells, points, config = input_constraints(options)

    if not exe:
        return

    var = {
        "points": points,
        "exe": exe,
        "nwells": nwells,
        "post": options.mode,
        "time": config["time"],
        "mass": config["mass"] / (KG_TO_MT * RDEN),
    }
    mytemplate = Template(filename=f"{exe}/templates/{name.lower()}.mako")
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{name}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"{config['flow']} {name}.DATA")

    output_constraints(options, config, name)


def output_constraints(options, config, name):
    """Check the output constraints"""
    co2tot = Summary(f"{name}.SMSPEC")["FGMIP"].values[-1] * KG_TO_MT
    dz_corr = 0.5 * np.array(ResdataFile(f"{name}.INIT").iget_kw("DZ")[0])
    den1 = np.array(ResdataFile(f"{name}.UNRST").iget_kw("WAT_DEN")[-1])
    pz_c1 = 9.81*dz_corr*den1/1e5
    press_limit = STRESSC * (
        np.array(ResdataFile(f"{name}.INIT").iget_kw("DEPTH")[0])
        - 0.5 * np.array(ResdataFile(f"{name}.INIT").iget_kw("DZ")[0])
    )
    overpress = min(np.divide(
        press_limit
        - (np.array(ResdataFile(f"{name}.UNRST").iget_kw("PRESSURE")[-1])
        -pz_c1), press_limit)
    )

    if options.mode != "post":
        delete()

    if config["mass"] - co2tot > config["mthr"]:
        with open("func", "w", encoding="utf-8") as f:
            f.write("-1e10")
        return

    with open("func", "w", encoding="utf-8") as f:
        f.write(f"{overpress}")


if __name__ == "__main__":
    locations()
