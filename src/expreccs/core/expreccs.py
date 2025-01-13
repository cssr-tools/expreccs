# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script for expreccs"""
import os
import time
import argparse
import warnings
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
    if int(cmdargs["warnings"]) == 0:
        warnings.warn = lambda *args, **kwargs: None
    file = (cmdargs["input"].strip()).split(" ")  # Name of the input file
    dic = {"fol": cmdargs["output"]}  # Name for the output folder
    dic["pat"] = os.path.dirname(__file__)[:-5]  # Path to the expreccs folder
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    dic["mode"] = cmdargs["mode"]  # Parts of the workflow to run
    dic["plot"] = cmdargs["plot"]  # Generate some nice plots
    dic["co2store"] = cmdargs["use"]  # Implementation of co2store
    dic["reading"] = cmdargs["reading"]  # Resdata or opm python package
    dic["rotate"] = int(cmdargs["transform"])  # Rotate the site model
    dic["freq"] = (cmdargs["frequency"].strip()).split(",")  # Frequency bc evaluations
    dic["acoeff"] = (cmdargs["acoeff"].strip()).split(
        ","
    )  # Coefficient telescopic partition
    dic["latex"] = int(cmdargs["latex"])  # LaTeX formatting
    dic["boundaries"] = (cmdargs["boundaries"].strip()).split(",")  # Boundaries
    dic["boundaries"] = [int(val) for val in dic["boundaries"]]
    dic["compare"] = cmdargs[
        "compare"
    ]  # If not empty, then the folder 'compare' is created.
    # If the compare plots are generated, then we exit right afterwards
    if dic["compare"]:
        plot_results(dic)
        return

    # For regional and site given decks, then we create a new deck with the proyected pressures
    if len(file) > 1:
        for i, name in enumerate(["reg", "sit"]):
            dic[name] = file[i].split("/")[-1]
            if "/" in file[i]:
                dic[f"f{name}"] = "/".join(file[i].split("/")[:-1])
            else:
                dic[f"f{name}"] = dic["exe"]
        create_deck(dic)
        return

    # Process the input file (open expreccs.utils.inputvalues to see the abbreviations meaning)
    process_input(dic, file[0])

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
        help="The base name of the configuration file; or paths (space between them and "
        "quotation marks) to the regional and site models ('input.txt' by default).",
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
        "-b",
        "--boundaries",
        default="0,0,0,0",
        help="Set the number of entries to skip the bc projections on "
        "the site, where 'j=0,i=nx,j=ny,i=0', e.g., '0,2,0,0' would skip all cells "
        "with i=nx and i=nx-1; this becomes handly for models where all cells in a "
        "given site are inactive along a side ('0,0,0,0' by default).",
    )
    parser.add_argument(
        "-f",
        "--frequency",
        default="1",
        help="Frequency to evaluate the boundary pressures on the site between "
        "report steps in the site. Write an array, e.g., '2,7,3', to set the "
        "frequency in each site report step ('1' by default).",
    )
    parser.add_argument(
        "-a",
        "--acoeff",
        default="3.2",
        help="Exponential 'a' coefficient for the telescopic time-discretization "
        "for the given frequency '-f'. Write an array, e.g., '2.2,0,3.1', to set "
        "the coefficient in each site report step ('3.2' by default, use 0 for an "
        "equidistance partition).",
    )
    parser.add_argument(
        "-w",
        "--warnings",
        default=0,
        help="Set to 1 to print warnings ('0' by default).",
    )
    parser.add_argument(
        "-l",
        "--latex",
        default=1,
        help="Set to 0 to not use LaTeX formatting (1' by default).",
    )
    return vars(parser.parse_known_args()[0])


def main():
    """Main function"""
    expreccs()
