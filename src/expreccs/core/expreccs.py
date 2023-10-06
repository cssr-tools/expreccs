# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script"""
import os
import time
import argparse
from expreccs.utils.inputvalues import process_input
from expreccs.utils.runs import simulations, plotting
from expreccs.utils.writefile import write_folders, write_files, write_properties
from expreccs.utils.mapproperties import mapping_properties
from expreccs.visualization.plotting import plot_results
from expreccs.utils.mapboundaries import (
    aquaflux_ecl,
    aquaflux_opm,
    porv_projections,
    porv_regional_segmentation,
)


def expreccs():
    """Main function"""
    start_time = time.monotonic()
    parser = argparse.ArgumentParser(
        description="Main method to simulate regional and site reservoirs for CO2 storage."
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
        help="Run the whole framework ('all'), only the reference ('reference'), "
        "only the site ('site'), only regional and site models ('noreference') "
        " or none 'none' ('all' by default).",
    )
    parser.add_argument(
        "-c",
        "--compare",
        default="",
        help="Generate a common plot for the current folders ('' by default).",
    )
    parser.add_argument(
        "-p",
        "--plot",
        default="no",
        help="Create useful figures in the postprocessing folder ('no' by default).",
    )
    parser.add_argument(
        "-r",
        "--reading",
        default="ecl",
        help="Using the 'opm' or 'ecl' python package (ecl by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    file = cmdargs["input"]  # Name of the input file
    dic = {"fol": cmdargs["output"]}  # Name for the output folder
    dic["pat"] = os.path.dirname(__file__)[:-5]  # Path to the expreccs folder
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    dic["mode"] = cmdargs["mode"]  # Parts of the workflow to run
    dic["plot"] = cmdargs["plot"]  # Generate some nice plots
    dic["reading"] = cmdargs["reading"]  # Ecl or opm python package
    dic["compare"] = cmdargs[
        "compare"
    ]  # If not empty, then the folder 'compare' is created.
    # If the compare plots are generated, then we exit right afterwards
    if dic["compare"]:
        plot_results(dic)
        return

    # Process the input file (open expreccs.utils.inputvalues to see the abbreviations meaning)
    dic = process_input(dic, file)

    # Make the output folders
    write_folders(dic)

    # Get the location of wells and faults in the reservoirs
    dic = mapping_properties(dic)
    write_properties(dic)

    # Run the models
    if dic["mode"] in ["all", "reference"]:
        write_files(dic, "reference")
        simulations(dic, "reference")
    if dic["mode"] in ["all", "regional", "noreference"]:
        dic = porv_regional_segmentation(dic)
        write_files(dic, "regional")
        simulations(dic, "regional")
    if dic["mode"] in ["all", "site", "noreference"]:
        if dic["site_bctype"] in ["flux", "pres"]:
            if dic["reading"] == "ecl":
                dic = aquaflux_ecl(dic)
            else:
                dic = aquaflux_opm(dic)
        elif dic["site_bctype"] == "porvproj":
            dic = porv_projections(dic)
        write_files(dic, f"site_{dic['site_bctype']}")
        simulations(dic, f"site_{dic['site_bctype']}")

    # Generate some useful plots after the studies
    if dic["plot"] == "yes":
        plotting(dic, time.monotonic() - start_time)


def main():
    """Main function"""
    expreccs()
