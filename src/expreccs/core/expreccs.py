# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script for expreccs"""
import os
import time
import argparse
from expreccs.utils.inputvalues import process_input
from expreccs.utils.runs import run_models, plotting
from expreccs.utils.writefile import write_folders, write_properties
from expreccs.utils.mapproperties import mapping_properties
from expreccs.visualization.plotting import plot_results
from expreccs.utils.reg_sit_given_decks import create_deck
from expreccs.utils.backcoupling import (
    init_multipliers,
    backcoupling,
)


def expreccs():
    """Main function for the expreccs executable"""
    start_time = time.monotonic()
    cmdargs = load_parser()
    file = cmdargs["input"]  # Name of the input file
    dic = {"fol": cmdargs["output"]}  # Name for the output folder
    dic["pat"] = os.path.dirname(__file__)[:-5]  # Path to the expreccs folder
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    dic["mode"] = cmdargs["mode"]  # Parts of the workflow to run
    dic["plot"] = cmdargs["plot"]  # Generate some nice plots
    dic["co2store"] = cmdargs["use"]  # Implementation of co2store
    dic["reading"] = cmdargs["reading"]  # Resdata or opm python package
    dic["rotate"] = int(cmdargs["transform"])  # Rotate the site model
    dic["expreccs"] = str(cmdargs["expreccs"])  # Name of regional and site models
    dic["compare"] = cmdargs[
        "compare"
    ]  # If not empty, then the folder 'compare' is created.
    # If the compare plots are generated, then we exit right afterwards
    if dic["compare"]:
        plot_results(dic)
        return

    # For regional and site given decks, then we create a new deck with the proyected pressures
    if dic["expreccs"]:
        dic["reg"] = dic["expreccs"].split(",")[0]
        dic["sit"] = dic["expreccs"].split(",")[1]
        create_deck(dic)
        return

    # Process the input file (open expreccs.utils.inputvalues to see the abbreviations meaning)
    process_input(dic, file)

    # Make the output folders
    write_folders(dic)

    # Get the location of wells and faults in the reservoirs
    mapping_properties(dic)
    write_properties(dic)
    init_multipliers(dic)

    # Run the models
    run_models(dic)

    if dic["mode"] in ["all"]:
        backcoupling(dic)

    # Generate some useful plots after the studies
    if dic["plot"] != "no":
        plotting(dic, time.monotonic() - start_time)


def load_parser():
    """Argument options"""
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
        "only the site ('site'), only regional and site models ('noreference'), "
        "or none 'none' ('all' by default).",
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
        help="Plot 'all', 'reference', 'regional', 'site', or no ('no' by default).",
    )
    parser.add_argument(
        "-u",
        "--use",
        default="gaswater",
        help="Using 'gasoil' or 'gaswater' co2store implementation ('gaswater' by "
        + "default).",
    )
    parser.add_argument(
        "-r",
        "--reading",
        default="resdata",
        help="Using the 'opm' or 'resdata' python package ('resdata' by default).",
    )
    parser.add_argument(
        "-t",
        "--transform",
        default=0,
        help="Grades to rotate the site geological model ('0' by default).",
    )
    parser.add_argument(
        "-e",
        "--expreccs",
        default="",
        help="Name of the regional and site folders to project pressures.",
    )
    return vars(parser.parse_known_args()[0])


def main():
    """Main function"""
    expreccs()
