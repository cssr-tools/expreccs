# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script"""
import os
import time
import argparse
from expreccs.utils.inputvalues import process_input
from expreccs.utils.runs import simulations, plotting
from expreccs.utils.writefile import reference_files, regional_files, site_files
from expreccs.utils.mapproperties import (
    aquaflux,
    positions_reference,
    positions_regional,
    positions_site,
)


def expreccs():
    """Main function"""
    start_time = time.monotonic()
    parser = argparse.ArgumentParser(
        description="Main script to simulate regional and site reservoirs for CO2 storage."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.txt",
        help="The base name of the input file ('input.txt' by default).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="The base name of the output folder ('output' by default).",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="all",
        help="Run the whole framework ('all') or only the regional and "
        "site models ('notall') ('all' by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    file = cmdargs["input"]  # Name of the input file
    dic = {"fol": cmdargs["output"]}  # Name for the output folder
    dic["pat"] = os.path.dirname(__file__)[:-5]  # Path to the expreccs folder
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    dic["mode"] = cmdargs["mode"]  # Parts of the workflow to run

    # Process the input file (open expreccs.utils.inputvalues to see the abbreviations meaning)
    dic = process_input(dic, file)

    # Make the output folders
    if not os.path.exists(f"{dic['exe']}/{dic['fol']}"):
        os.system(f"mkdir {dic['exe']}/{dic['fol']}")
    for fil in ["preprocessing", "jobs", "output", "postprocessing"]:
        if not os.path.exists(f"{dic['exe']}/{dic['fol']}/{fil}"):
            os.system(f"mkdir {dic['exe']}/{dic['fol']}/{fil}")
    os.chdir(f"{dic['exe']}/{dic['fol']}")

    # Get the well positions
    dic = positions_reference(dic)
    dic = positions_regional(dic)
    dic = positions_site(dic)

    # Write used opm related files
    reference_files(dic)
    regional_files(dic)

    # Run the reference model
    if dic["mode"] == "all":
        simulations(dic, "reference")
    # Run the regional model
    simulations(dic, "regional")

    # Read the flows from the regional simulation
    dic = aquaflux(dic)

    # Write used opm related files
    site_files(dic)

    # Run the site model
    simulations(dic, "site")
    simulations(dic, "site_openboundaries")

    # Make some useful plots after the studies
    plotting(dic, time.monotonic() - start_time)


def main():
    """Main function"""
    expreccs()
