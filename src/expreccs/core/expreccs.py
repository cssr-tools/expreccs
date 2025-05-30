# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0915

"""Main script for expreccs"""

import os
import sys
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
    cmdargs = load_parser()
    check_cmdargs(cmdargs)
    if int(cmdargs["warnings"]) == 0:
        warnings.warn = lambda *args, **kwargs: None
    file = (cmdargs["input"].strip()).split(" ")  # Name of the input file
    dic = {"fol": os.path.abspath(cmdargs["output"])}  # Name for the output folder
    dic["pat"] = os.path.dirname(__file__)[:-5]  # Path to the expreccs folder
    dic["mode"] = cmdargs["mode"]  # Parts of the workflow to run
    dic["plot"] = cmdargs["plot"]  # Generate some nice plots
    dic["use"] = cmdargs["use"]  # Resdata or opm python package
    dic["rotate"] = int(cmdargs["transform"])  # Rotate the site model
    dic["explicit"] = int(cmdargs["explicit"]) == 1  # Explicit regional pressure bc
    dic["zones"] = int(cmdargs["zones"]) == 1  # Pressure projections per fipnum
    dic["freq"] = (cmdargs["frequency"].strip()).split(",")  # Frequency bc evaluations
    dic["subfolders"] = int(cmdargs["subfolders"]) == 1  # Create subfolders
    dic["acoeff"] = (cmdargs["acoeff"].strip()).split(
        ","
    )  # Coefficient telescopic partition
    dic["latex"] = int(cmdargs["latex"])  # LaTeX formatting
    dic["boundaries"] = (cmdargs["boundaries"].strip()).split(",")  # Boundaries
    dic["boundaries"] = [int(val) for val in dic["boundaries"]]
    dic["compare"] = cmdargs["compare"]
    # If the compare plots are generated, then we exit right afterwards
    if dic["compare"]:
        if not dic["subfolders"]:
            print(
                "\nCompare requires the subfolder structure, "
                "i.e., by running expreccs with the default value for the "
                "flag '-s 1'. Please rerun 'expreccs -c compare' without the "
                "'-s' flag.\n"
            )
            sys.exit()
        print("\nExecuting the compare functionality in expreccs, please wait.")
        dic["iterations"] = 0
        plot_results(dic)
        print(
            "\nThe execution of expreccs succeeded. "
            + f"The generated files have been written to {os.getcwd()}/compare/\n"
        )
        return

    # For regional and site given decks, then we create a new deck with the proyected pressures
    print("\nExecuting expreccs, please wait.")
    text = (
        "\nThe execution of expreccs succeeded. "
        + f"The generated files have been written to {dic['fol']}/\n"
    )
    if len(file) > 1:
        for i, name in enumerate(["reg", "sit"]):
            dic[name] = file[i].split("/")[-1]
            if "/" in file[i]:
                dic[f"f{name}"] = os.path.abspath("/".join(file[i].split("/")[:-1]))
            else:
                dic[f"f{name}"] = os.path.abspath(".")
        create_deck(dic)
        print(text)
        return
    # Process the input file (open expreccs.utils.inputvalues to see the abbreviations meaning)
    process_input(dic, file[0])

    # Make the output folders
    dic["fpos"] = (
        f"{dic['fol']}/postprocessing/" if dic["subfolders"] else f"{dic['fol']}/"
    )
    for iteration in range(0, dic["iterations"] + 1):
        fil = ""
        if iteration > 1:
            fil = f"_{iteration-1}"
        for name in ["reference", "regional", f"site_{dic['site_bctype'][0]}"]:
            if dic["subfolders"]:
                dic[f"fpre{name}{fil}"] = f"{dic['fol']}/preprocessing/{name}{fil}/"
                dic[f"fsim{name}{fil}"] = f"{dic['fol']}/simulations/{name}{fil}/"
            else:
                dic[f"fpre{name}{fil}"] = f"{dic['fol']}/"
                dic[f"fsim{name}{fil}"] = f"{dic['fol']}/"
    write_folders(dic)

    # Get the location of wells and faults in the reservoirs
    os.chdir(f"{dic['fol']}")
    mapping_properties(dic)
    write_properties(dic)
    init_multipliers(dic)

    # Run the models
    run_models(dic)

    if dic["iterations"] > 0 and dic["mode"] != "none":
        if not dic["subfolders"]:
            print(
                "\nBackcpupling requires the subfolder structure, "
                "i.e., by running expreccs with the default value for the "
                "flag '-s 1'. Please rerun expreccs without the '-s' flag.\n"
            )
            sys.exit()
        backcoupling(dic)

    # Generate some useful plots after the studies
    if dic["plot"] != "no":
        if not dic["subfolders"]:
            print(
                "\nThe generation of plots requires the subfolder structure, "
                "i.e., by running expreccs with the default value for the "
                "flag '-s 1'.\nThen you could rerun expreccs without the '-s' "
                "flag, or you could use the plopm tool to generate plots (see "
                "https://github.com/cssr-tools/plopm)\n"
            )
            sys.exit()
        plotting(dic)
    print(text)


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="Main method to simulate regional and site reservoirs for CO2 storage. "
        "The valid flags for toml configuration files are -i, -o, -m, -c, -p, -u, -r, -t, "
        "-w, -l. The valid flags for paths to the regional and site folders are -i, -o, -b, "
        "-f, -a, -w, -e, -z",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.toml",
        help="The base name of the configuration file; or paths (space between them and "
        "quotation marks) to the regional and site models ('input.toml' by default).",
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
        "only the site ('site'), only the regional ('regional'), only regional and site "
        "models ('regional_site'), or none 'none' ('all' by default).",
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
        help="Plot 'all', 'reference', 'regional', 'site', or 'no' ('no' by default).",
    )
    parser.add_argument(
        "-u",
        "--use",
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
    parser.add_argument(
        "-e",
        "--explicit",
        default=1,
        help="Set to 0 to write the pressure increase on the site bc from "
        "the regional values ('1' by default, i.e., the pressure values on the "
        "boundaries correspond to the explicit values on the regional simulations).",
    )
    parser.add_argument(
        "-z",
        "--zones",
        default=0,
        help="Set to 1 to project the regional pressures per fipnum zones, i.e., "
        "the pressure maps to the site bcs are written for equal fipnum numbers in "
        "the whole xy layer ('0' by default, i.e., the projections include the z "
        "location offset between regional and site models).",
    )
    parser.add_argument(
        "-s",
        "--subfolders",
        default=1,
        help="Set to 0 to not create the subfolders preprocessing, output, and "
        "postprocessing, i.e., to write all generated files in the output directory "
        "('1' by default).",
    )
    return vars(parser.parse_known_args()[0])


def check_cmdargs(cmdargs):
    """
    Check for invalid combinations of command arguments

    Args:
        cmdargs (dict): Command flags

    Returns:
        None

    """
    if len((cmdargs["input"].strip()).split(" ")) == 1:
        if not (cmdargs["input"].strip()).endswith(".toml"):
            print(
                f"\nInvalid extension for '-i {cmdargs['input'].strip()}', "
                "the valid extension is .toml, or give the path to the "
                "two folders to apply the dynamic pressure bcs.\n"
            )
            sys.exit()


def main():
    """Main function"""
    expreccs()
