# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to read OPM Flow output files
"""

import os
import datetime
import numpy as np
import pandas as pd

try:
    from opm.io.ecl import ESmry as OpmSmry
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import ERst as OpmRst
    from opm.io.ecl import EGrid as OpmGrid
except ImportError:
    print("The opm Python package was not found, using ecl")
try:
    from resdata.summary import Summary
    from resdata.grid import Grid
    from resdata.resfile import ResdataFile
except ImportError:
    print("The ecl Python package was not found, using opm")


def reading_ecl(dic):
    """
    Function to read the deck quantities using ecl

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["quantity"] = ["saturation", "pressure", "flooili+", "flooilj+"]
    dic["names"] = ["saturation", "pressure", "watfluxi+", "watfluxj+"]
    dic["units"] = ["-", "bar", "sm$^3$/day", "sm$^3$/day"]
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{dic['exe']}/{fol}/output")
        dic[f"{fol}_sites"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )[2:]
        os.chdir(cwd)
        if dic["mode"] in ["reference"]:
            dic[f"{fol}_decks"] = ["reference"]
        elif dic["compare"]:
            dic[f"{fol}_decks"] = ["reference"] + dic[f"{fol}_sites"]
        else:
            dic[f"{fol}_decks"] = ["reference", "regional"] + dic[f"{fol}_sites"]
        for res in dic[f"{fol}_decks"]:
            case = dic["exe"] + "/" + fol + f"/output/{res}/{res.upper()}"
            dic[f"{fol}/{res}_nowells"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells.npy"
            )
            dic[f"{fol}/{res}_sensor"] = int(
                np.load(dic["exe"] + "/" + fol + f"/output/{res}/sensor.npy")
            )
            dic[f"{fol}/{res}_sensor_location"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/sensor_location.npy"
            )
            dic[f"{fol}/{res}_nowells_site"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells_site.npy"
            )
            dic[f"{fol}/{res}_rst"] = ResdataFile(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = ResdataFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = Grid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = Summary(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = dic[f"{fol}/{res}_rst"].num_report_steps()
            dic[f"{fol}/{res}_dates"] = dic[f"{fol}/{res}_rst"].dates
            dic[f"{fol}/{res}_smsp_dates"] = dic[f"{fol}/{res}_smsp"].dates
            dic[f"{fol}/{res}_saturation"] = dic[f"{fol}/{res}_rst"].iget_kw("SGAS")
            dic[f"{fol}/{res}_pressure"] = dic[f"{fol}/{res}_rst"].iget_kw("PRESSURE")
            dic[f"{fol}/{res}_flooili+"] = dic[f"{fol}/{res}_rst"].iget_kw("FLOOILI+")
            dic[f"{fol}/{res}_flooilj+"] = dic[f"{fol}/{res}_rst"].iget_kw("FLOOILJ+")
            dic[f"{fol}/{res}_phiv"] = dic[f"{fol}/{res}_ini"].iget_kw("PORV")[0]
            dic[f"{fol}/{res}_density"] = dic[f"{fol}/{res}_rst"].iget_kw("GAS_DEN")
            dic[f"{fol}/{res}_fipn"] = np.array(
                dic[f"{fol}/{res}_ini"].iget_kw("FIPNUM")
            )[0]
            dic = handle_smsp_time(dic, fol, res)
            dic[f"{fol}/{res}_indicator_array"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
                for i in range(dic[f"{fol}/{res}_num_rst"]):
                    if quantity == "saturation":
                        dic[f"{fol}/{res}_indicator_array"].append(
                            np.array(dic[f"{fol}/{res}_saturation"][i]) > dic["sat_thr"]
                        )
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_saturation"][i])
                        )
                    else:
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_{quantity}"][i])
                        )
            name = "site" if "site" in res else res
            dic[f"{fol}/{name}_boxi"] = dic[f"{fol}/{res}_grid"].getNodePos(0, 0, 0)
            dic[f"{fol}/{name}_boxf"] = dic[f"{fol}/{res}_grid"].getNodePos(
                dic[f"{fol}/{res}_grid"].getNX(),
                dic[f"{fol}/{res}_grid"].getNY(),
                dic[f"{fol}/{res}_grid"].getNZ(),
            )
            dic[f"{fol}/{name}_xmx"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_xmx.npy"
            )
            dic[f"{fol}/{name}_ymy"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_ymy.npy"
            )
            dic[f"{fol}/{res}_xcor"], dic[f"{fol}/{res}_ycor"] = np.meshgrid(
                dic[f"{fol}/{name}_xmx"], dic[f"{fol}/{name}_ymy"][::-1]
            )
    return dic


def handle_smsp_time(dic, fol, res):
    """
    Function to chandle the times in the summary files

    Args:
        dic (dict): Global dictionary with required parameters
        str (study): Name of the folder containing the results

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic[f"{fol}/{res}_rst_seconds"] = np.load(
        dic["exe"] + "/" + fol + f"/output/{res}/schedule.npy"
    )
    dic[f"{fol}/{res}_smsp_report_step"] = dic[f"{fol}/{res}_smsp"][
        "WBHP:INJ0"
    ].report_step
    dic[f"{fol}/{res}_report_time"] = dic[f"{fol}/{res}_rst"].dates
    dic[f"{fol}/{res}_smsp_seconds"] = [
        (
            dic[f"{fol}/{res}_smsp"].numpy_dates[i + 1]
            - dic[f"{fol}/{res}_smsp"].numpy_dates[i]
        )
        / np.timedelta64(1, "s")
        for i in range(len(dic[f"{fol}/{res}_smsp"].numpy_dates) - 1)
    ]
    dic[f"{fol}/{res}_smsp_seconds"].insert(
        0,
        (
            dic[f"{fol}/{res}_smsp"].numpy_dates[0]
            - np.datetime64(dic[f"{fol}/{res}_smsp"].get_start_time())
        )
        / np.timedelta64(1, "s"),
    )
    for i in range(len(dic[f"{fol}/{res}_smsp"].numpy_dates) - 1):
        dic[f"{fol}/{res}_smsp_seconds"][i + 1] += dic[f"{fol}/{res}_smsp_seconds"][i]
    dic[f"{fol}/{res}_smsp_rst"] = [
        pd.Series(abs(dic[f"{fol}/{res}_smsp_seconds"] - time)).argmin()
        for time in dic[f"{fol}/{res}_rst_seconds"]
    ]
    dic[f"{fol}/{res}_smsp_seconds"] = np.insert(
        dic[f"{fol}/{res}_smsp_seconds"], 0, 0.0
    )
    return dic


def reading_opm(dic):
    """
    Function to read the deck quantities using opm

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["quantity"] = ["saturation", "pressure", "flooili+", "flooilj+"]
    dic["names"] = ["saturation", "pressure", "watfluxi+", "watfluxj+"]
    dic["units"] = ["-", "bar", "sm$^3$/day", "sm$^3$/day"]
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{dic['exe']}/{fol}/output")
        dic[f"{fol}_sites"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )[2:]
        os.chdir(cwd)
        if dic["mode"] in ["reference"]:
            dic[f"{fol}_decks"] = ["reference"]
        elif dic["compare"]:
            dic[f"{fol}_decks"] = ["reference"] + dic[f"{fol}_sites"]
        else:
            dic[f"{fol}_decks"] = ["reference", "regional"] + dic[f"{fol}_sites"]
        for res in dic[f"{fol}_decks"]:
            dic[f"{fol}/{res}_rst_seconds"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/schedule.npy"
            )
            dic[f"{fol}/{res}_nowells"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells.npy"
            )
            dic[f"{fol}/{res}_nowells_site"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/nowells_site.npy"
            )
            dic[f"{fol}/{res}_sensor"] = int(
                np.load(dic["exe"] + "/" + fol + f"/output/{res}/sensor.npy")
            )
            dic[f"{fol}/{res}_sensor_location"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/sensor_location.npy"
            )
            case = dic["exe"] + "/" + fol + f"/output/{res}/{res.upper()}"
            dic[f"{fol}/{res}_rst"] = OpmRst(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = OpmFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = OpmGrid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = OpmSmry(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = len(dic[f"{fol}/{res}_rst"].report_steps)
            dic[f"{fol}/{res}_dates"] = [
                dic[f"{fol}/{res}_smsp"].start_date
                + datetime.timedelta(seconds=seconds)
                for seconds in dic[f"{fol}/{res}_rst_seconds"]
            ]
            dic[f"{fol}/{res}_smsp_seconds"] = 86400 * dic[f"{fol}/{res}_smsp"]["TIME"]
            dic[f"{fol}/{res}_smsp_dates"] = 86400 * dic[f"{fol}/{res}_smsp"]["TIME"]
            dic[f"{fol}/{res}_smsp_dates"] = [
                dic[f"{fol}/{res}_smsp"].start_date
                + datetime.timedelta(seconds=seconds)
                for seconds in dic[f"{fol}/{res}_smsp_dates"]
            ]
            dic[f"{fol}/{res}_smsp_rst"] = [
                pd.Series(abs(dic[f"{fol}/{res}_smsp_seconds"] - time)).argmin()
                for time in dic[f"{fol}/{res}_rst_seconds"]
            ]
            dic[f"{fol}/{res}_phiv"] = np.array(dic[f"{fol}/{res}_ini"]["PORV"])
            dic[f"{fol}/{res}_fipn"] = np.array(dic[f"{fol}/{res}_ini"]["FIPNUM"])
            dic[f"{fol}/{res}_indicator_array"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
                for i in range(dic[f"{fol}/{res}_num_rst"]):
                    if quantity == "saturation":
                        dic[f"{fol}/{res}_indicator_array"].append(
                            np.array(dic[f"{fol}/{res}_rst"]["SGAS", i])
                            > dic["sat_thr"]
                        )
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_rst"]["SGAS", i])
                        )
                    else:
                        dic[f"{fol}/{res}_{quantity}_array"].append(
                            np.array(dic[f"{fol}/{res}_rst"][f"{quantity.upper()}", i])
                        )
            name = "site" if "site" in res else res
            dic[f"{fol}/{name}_boxi"] = [
                dic[f"{fol}/{res}_grid"].xyz_from_ijk(0, 0, 0)[i][0] for i in range(3)
            ]
            dic[f"{fol}/{name}_boxf"] = [
                dic[f"{fol}/{res}_grid"].xyz_from_ijk(
                    dic[f"{fol}/{res}_grid"].dimension[0] - 1,
                    dic[f"{fol}/{res}_grid"].dimension[1] - 1,
                    dic[f"{fol}/{res}_grid"].dimension[2] - 1,
                )[i][-1]
                for i in range(3)
            ]
            dic[f"{fol}/{name}_xmx"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_xmx.npy"
            )
            dic[f"{fol}/{name}_ymy"] = np.load(
                dic["exe"] + "/" + fol + f"/output/{res}/{name}_ymy.npy"
            )
            dic[f"{fol}/{res}_xcor"], dic[f"{fol}/{res}_ycor"] = np.meshgrid(
                dic[f"{fol}/{name}_xmx"], dic[f"{fol}/{name}_ymy"][::-1]
            )
    return dic
