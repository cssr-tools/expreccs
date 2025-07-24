# SPDX-FileCopyrightText: 2023-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0914,R0915,R1702

"""
Script to read OPM Flow output files
"""

import os
import datetime
import numpy as np
import pandas as pd
from resdata.summary import Summary
from resdata.grid import Grid
from resdata.resfile import ResdataFile

try:
    from opm.io.ecl import ESmry as OpmSmry
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import ERst as OpmRst
    from opm.io.ecl import EGrid as OpmGrid
except ImportError:
    pass

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108
KG_TO_KT = 1e-6


def reading_resdata(dic, doplot=True):
    """
    Read the deck quantities using resdata

    Args:
        dic (dict): Global dictionary\n
        doplot (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{fol}/simulations")
        folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
        dic[f"{fol}_sites"] = folders[2:]
        os.chdir(cwd)
        if dic["plot"] in ["reference"]:
            dic[f"{fol}_decks"] = ["reference"]
        elif dic["plot"] in ["regional"]:
            dic[f"{fol}_decks"] = ["regional"]
        elif dic["plot"] in ["site"]:
            dic[f"{fol}_decks"] = dic[f"{fol}_sites"]
        elif dic["compare"]:
            dic[f"{fol}_decks"] = ["reference"] + dic[f"{fol}_sites"]
        else:
            dic[f"{fol}_decks"] = ["reference", "regional"] + dic[f"{fol}_sites"]
        if not doplot:
            dic[f"{fol}_decks"] = folders
        elif dic["iterations"] > 5:
            for i in range(dic["iterations"] - 2):
                if i == int(dic["iterations"] / 2 - 1):
                    continue
                dic[f"{fol}_decks"].remove(f"regional_{i+1}")
        for res in dic[f"{fol}_decks"]:
            if f"{fol}/{res}_rst" in dic and not doplot:
                continue
            case = fol + f"/simulations/{res}/{res.upper()}"
            dic[f"{fol}/{res}_rst"] = ResdataFile(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = ResdataFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = Grid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = Summary(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = dic[f"{fol}/{res}_rst"].num_report_steps()
            if doplot:
                define_cases(dic, fol, folders)
                resdata_load_data(dic, fol, res)
            dic[f"{fol}/{res}_phiv"] = np.array(
                dic[f"{fol}/{res}_ini"].iget_kw("PORV")[0]
            )
            dic[f"{fol}/{res}_mask"] = dic[f"{fol}/{res}_phiv"] > 0
            dic[f"{fol}/{res}_poro"] = dic[f"{fol}/{res}_ini"].iget_kw("PORO")[0]
            dic[f"{fol}/{res}_fipn"] = np.array(
                dic[f"{fol}/{res}_ini"].iget_kw("FIPNUM")
            )[0]
            dic[f"{fol}/{res}_static"] = ["fipn"]
            if dic[f"{fol}/{res}_ini"].has_kw("MULTX"):
                dic[f"{fol}/{res}_multx"] = np.array(
                    dic[f"{fol}/{res}_ini"].iget_kw("MULTX")
                )[0]
                dic[f"{fol}/{res}_multy"] = np.array(
                    dic[f"{fol}/{res}_ini"].iget_kw("MULTY")
                )[0]
                dic[f"{fol}/{res}_static"] += ["multx", "multy"]
            else:
                dic[f"{fol}/{res}_multx"] = 1 * (dic[f"{fol}/{res}_fipn"] > 1)
                dic[f"{fol}/{res}_multy"] = 1 * (dic[f"{fol}/{res}_fipn"] > 1)
            dic[f"{fol}/{res}_dx"] = np.array(dic[f"{fol}/{res}_ini"].iget_kw("DX")[0])
            dic[f"{fol}/{res}_dy"] = np.array(dic[f"{fol}/{res}_ini"].iget_kw("DY")[0])
            dic[f"{fol}/{res}_dz"] = np.array(dic[f"{fol}/{res}_ini"].iget_kw("DZ")[0])
            dic[f"{fol}/{res}_indicator_array"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
            resdata_arrays(dic, fol, res, doplot)


def resdata_load_data(dic, fol, res):
    """
    Read the data needed for the plotting

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model

    Returns:
        dic (dict): Modified global dictionary

    """
    dic[f"{fol}/{res}_rst_seconds"] = []
    for i in range(dic[f"{fol}/{res}_rst"].num_report_steps()):
        dic[f"{fol}/{res}_rst_seconds"].append(
            86400 * dic[f"{fol}/{res}_rst"].iget_kw("DOUBHEAD")[i][0]
        )
    dic[f"{fol}/{res}_rst_seconds"] = np.array(dic[f"{fol}/{res}_rst_seconds"])
    dic[f"{fol}/{res}_sensorijk"] = []
    dic[f"{fol}/{res}_nowells"] = []
    for keys in dic[f"{fol}/{res}_smsp"].keys():
        if keys.split(":")[0] == "BFLOWI":
            for ijk in keys.split(":")[1].split(","):
                dic[f"{fol}/{res}_sensorijk"].append(int(ijk) - 1)
        elif keys.split(":")[0] == "WBHP":
            dic[f"{fol}/{res}_nowells"].append(keys.split(":")[1])
    dic[f"{fol}/{res}_sensorijk"] = np.array(dic[f"{fol}/{res}_sensorijk"])
    dic[f"{fol}/{res}_sensor"] = dic[f"{fol}/{res}_grid"].get_global_index(
        ijk=[
            dic[f"{fol}/{res}_sensorijk"][0],
            dic[f"{fol}/{res}_sensorijk"][1],
            dic[f"{fol}/{res}_sensorijk"][2],
        ]
    )
    dic[f"{fol}/{res}_dates"] = dic[f"{fol}/{res}_rst"].dates
    dic[f"{fol}/{res}_smsp_dates"] = dic[f"{fol}/{res}_smsp"].dates
    ini = dic[f"{fol}/{res}_smsp"].start_date
    day_0 = datetime.datetime(
        year=ini.year, month=ini.month, day=ini.day, hour=0, minute=0, second=0
    )
    dic[f"{fol}/{res}_dates"] = [
        day_0 + datetime.timedelta(seconds=seconds)
        for seconds in dic[f"{fol}/{res}_rst_seconds"]
    ]
    handle_smsp_time(dic, fol, res)


def resdata_arrays(dic, fol, res, doplot):
    """
    From simulation data to arrays

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model\n
        doplot (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    phiva = np.array([porv for porv in dic[f"{fol}/{res}_phiv"] if porv > 0])
    for i in range(dic[f"{fol}/{res}_num_rst"]):
        temp = dic[f"{fol}/{res}_phiv"] < 0
        sgas = np.array(dic[f"{fol}/{res}_rst"]["SGAS"][i])
        rhog = np.array(dic[f"{fol}/{res}_rst"]["GAS_DEN"][i])
        rhow = np.array(dic[f"{fol}/{res}_rst"]["WAT_DEN"][i])
        rss = np.array(dic[f"{fol}/{res}_rst"]["RSW"][i])
        co2_g = sgas * rhog * phiva
        co2_d = rss * rhow * (1.0 - sgas) * phiva * GAS_DEN_REF / WAT_DEN_REF
        for quantity in dic["quantity"]:
            if quantity == "saturation":
                dic[f"{fol}/{res}_{quantity}_array"].append(sgas)
                temp[dic[f"{fol}/{res}_mask"]] = sgas > dic["sat_thr"]
                dic[f"{fol}/{res}_indicator_array"].append(temp)
            elif quantity == "mass":
                dic[f"{fol}/{res}_{quantity}_array"].append((co2_g + co2_d) * KG_TO_KT)
            elif quantity == "diss":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_d * KG_TO_KT)
            elif quantity == "gas":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_g * KG_TO_KT)
            elif quantity in ["FLOWATI+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOWAT{quantity[-2:]}"][i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOWATJ+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOWAT{quantity[-2:]}"][i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dx"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASI+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOGAS{quantity[-2:]}"][i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASJ+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOGAS{quantity[-2:]}"][i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dx"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            else:
                if dic[f"{fol}/{res}_rst"].has_kw(quantity.upper()):
                    dic[f"{fol}/{res}_{quantity}_array"].append(
                        np.array(dic[f"{fol}/{res}_rst"][f"{quantity.upper()}"][i])
                    )
                else:
                    dic[f"{fol}/{res}_{quantity}_array"].append(
                        0.0 * np.array(dic[f"{fol}/{res}_rst"]["SGAS"][0])
                    )
    manage_names(dic, res)
    dic[f"{fol}/{dic['namel']}_boxi"] = dic[f"{fol}/{res}_grid"].getNodePos(0, 0, 0)
    dic[f"{fol}/{dic['namel']}_boxf"] = dic[f"{fol}/{res}_grid"].getNodePos(
        dic[f"{fol}/{res}_grid"].getNX(),
        dic[f"{fol}/{res}_grid"].getNY(),
        dic[f"{fol}/{res}_grid"].getNZ(),
    )
    if doplot:
        xyz = dic[f"{fol}/{res}_grid"].export_corners(
            dic[f"{fol}/{res}_grid"].export_index()
        )
        dic[f"{fol}/{dic['namel']}_xmx"] = []
        dic[f"{fol}/{dic['namel']}_xmx"].append(xyz[0][0])
        for i in range(dic[f"{fol}/{res}_grid"].nx):
            dic[f"{fol}/{dic['namel']}_xmx"].append(xyz[i][3])
        dic[f"{fol}/{dic['namel']}_ymy"] = []
        dic[f"{fol}/{dic['namel']}_ymy"].append(xyz[0][1])
        for j in range(dic[f"{fol}/{res}_grid"].ny):
            n = j * dic[f"{fol}/{res}_grid"].nx
            dic[f"{fol}/{dic['namel']}_ymy"].append(xyz[n][7])
        dic[f"{fol}/{dic['namel']}_xmx"] = np.array(dic[f"{fol}/{dic['namel']}_xmx"])
        dic[f"{fol}/{dic['namel']}_ymy"] = np.array(dic[f"{fol}/{dic['namel']}_ymy"])
        (
            dic[f"{fol}/{dic['namel']}_xcor"],
            dic[f"{fol}/{dic['namel']}_ycor"],
        ) = np.meshgrid(
            dic[f"{fol}/{dic['namel']}_xmx"], dic[f"{fol}/{dic['namel']}_ymy"][::-1]
        )


def handle_smsp_time(dic, fol, res):
    """
    Handle the times in the summary files

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model

    Returns:
        dic (dict): Modified global dictionary

    """
    dic[f"{fol}/{res}_smsp_report_step"] = dic[f"{fol}/{res}_smsp"][
        "WBHP:INJS0"
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


def reading_opm(dic, doplot=True):  # pylint: disable=R0915, R0912
    """
    Read the deck quantities using opm

    Args:
        dic (dict): Global dictionary\n
        doplot (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{fol}/simulations")
        folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
        dic[f"{fol}_sites"] = folders[2:]
        os.chdir(cwd)
        if dic["plot"] in ["reference"]:
            dic[f"{fol}_decks"] = ["reference"]
        elif dic["plot"] in ["regional"]:
            dic[f"{fol}_decks"] = ["regional"]
        elif dic["plot"] in ["site"]:
            dic[f"{fol}_decks"] = dic[f"{fol}_sites"]
        elif dic["compare"]:
            dic[f"{fol}_decks"] = ["reference"] + dic[f"{fol}_sites"]
        else:
            dic[f"{fol}_decks"] = ["reference", "regional"] + dic[f"{fol}_sites"]
        for res in dic[f"{fol}_decks"]:
            if res[-3].isdigit():
                name = res[:-4]
            if res[-2].isdigit():
                name = res[:-3]
            if res[-1].isdigit():
                name = res[:-2]
            else:
                name = res
            if doplot:
                define_cases(dic, fol, folders)
            case = fol + f"/simulations/{res}/{res.upper()}"
            dic[f"{fol}/{res}_rst"] = OpmRst(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = OpmFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = OpmGrid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = OpmSmry(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = len(dic[f"{fol}/{res}_rst"].report_steps)
            if doplot:
                dic[f"{fol}/{res}_rst_seconds"] = []
                for i in range(len(dic[f"{fol}/{res}_rst"].report_steps)):
                    dic[f"{fol}/{res}_rst_seconds"].append(
                        86400 * dic[f"{fol}/{res}_rst"]["DOUBHEAD", i][0]
                    )
                dic[f"{fol}/{res}_rst_seconds"] = np.array(
                    dic[f"{fol}/{res}_rst_seconds"]
                )
                dic[f"{fol}/{res}_dates"] = [
                    dic[f"{fol}/{res}_smsp"].start_date
                    + datetime.timedelta(seconds=seconds)
                    for seconds in dic[f"{fol}/{res}_rst_seconds"]
                ]
                dic[f"{fol}/{res}_smsp_seconds"] = (
                    86400 * dic[f"{fol}/{res}_smsp"]["TIME"]
                )
                dic[f"{fol}/{res}_smsp_dates"] = (
                    86400 * dic[f"{fol}/{res}_smsp"]["TIME"]
                )
                dic[f"{fol}/{res}_smsp_dates"] = [
                    dic[f"{fol}/{res}_smsp"].start_date
                    + datetime.timedelta(seconds=float(seconds))
                    for seconds in dic[f"{fol}/{res}_smsp_dates"]
                ]
                dic[f"{fol}/{res}_smsp_rst"] = [
                    pd.Series(abs(dic[f"{fol}/{res}_smsp_seconds"] - time)).argmin()
                    for time in dic[f"{fol}/{res}_rst_seconds"]
                ]
                dic[f"{fol}/{res}_sensorijk"] = []
                dic[f"{fol}/{res}_nowells"] = []
                for keys in dic[f"{fol}/{res}_smsp"].keys():
                    if keys.split(":")[0] == "BFLOWI":
                        for ijk in keys.split(":")[1].split(","):
                            dic[f"{fol}/{res}_sensorijk"].append(int(ijk) - 1)
                    elif keys.split(":")[0] == "WBHP":
                        dic[f"{fol}/{res}_nowells"].append(keys.split(":")[1])
                dic[f"{fol}/{res}_sensorijk"] = np.array(dic[f"{fol}/{res}_sensorijk"])
                dic[f"{fol}/{res}_sensor"] = dic[f"{fol}/{res}_grid"].global_index(
                    dic[f"{fol}/{res}_sensorijk"][0],
                    dic[f"{fol}/{res}_sensorijk"][1],
                    dic[f"{fol}/{res}_sensorijk"][2],
                )
            dic[f"{fol}/{res}_phiv"] = np.array(dic[f"{fol}/{res}_ini"]["PORV"])
            dic[f"{fol}/{res}_mask"] = dic[f"{fol}/{res}_phiv"] > 0
            dic[f"{fol}/{res}_poro"] = np.array(dic[f"{fol}/{res}_ini"]["PORO"])
            dic[f"{fol}/{res}_fipn"] = np.array(dic[f"{fol}/{res}_ini"]["FIPNUM"])
            dic[f"{fol}/{res}_static"] = ["fipn"]
            if dic[f"{fol}/{res}_ini"].count("MULTX"):
                dic[f"{fol}/{res}_multx"] = np.array(dic[f"{fol}/{res}_ini"]["MULTX"])
                dic[f"{fol}/{res}_multy"] = np.array(dic[f"{fol}/{res}_ini"]["MULTY"])
                dic[f"{fol}/{res}_static"] += ["multx", "multy"]
            else:
                dic[f"{fol}/{res}_multx"] = 1 * (dic[f"{fol}/{res}_fipn"] > 1)
                dic[f"{fol}/{res}_multy"] = 1 * (dic[f"{fol}/{res}_fipn"] > 1)
            dic[f"{fol}/{res}_dx"] = np.array(dic[f"{fol}/{res}_ini"]["DX"])
            dic[f"{fol}/{res}_dy"] = np.array(dic[f"{fol}/{res}_ini"]["DY"])
            dic[f"{fol}/{res}_dz"] = np.array(dic[f"{fol}/{res}_ini"]["DZ"])
            if dic[f"{fol}/{res}_rst"].count("SWAT", 0):
                dic[f"{fol}/{res}liq"] = "WAT"
                dic[f"{fol}/{res}l"] = "W"
                dic[f"{fol}/{res}s"] = "W"
            else:
                dic[f"{fol}/{res}liq"] = "OIL"
                dic[f"{fol}/{res}l"] = "O"
                dic[f"{fol}/{res}s"] = ""
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
            dic[f"{fol}/{res}_indicator_array"] = []
            opm_arrays(dic, fol, res, doplot)


def define_cases(dic, fol, folders):
    """
    Only plot the first two and last cases for the back-coupling

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        folders (list): Names of the cases

    Returns:
        dic (dict): Modified global dictionary

    """
    dic[f"{fol}_sites"] = [folder for folder in folders if "site" in folder]
    if "site_pres_2" in dic[f"{fol}_sites"]:
        n_c = len(dic[f"{fol}_sites"]) - 1
        dic[f"lregional_{n_c}"] = "REG" + f"{n_c}"
        dic[f"lsite_pres_{n_c}"] = f"S{n_c}" + r"$_{pressure}$"
        dic[f"{fol}_sites"] = dic[f"{fol}_sites"][:2] + [dic[f"{fol}_sites"][-1]]
        dic[f"{fol}_decks"] = (
            dic[f"{fol}_decks"][:3] + [f"regional_{n_c}"] + dic[f"{fol}_sites"]
        )


def opm_arrays(dic, fol, res, doplot):
    """
    From simulation data to arrays

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model\n
        doplot (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    phiva = np.array([porv for porv in dic[f"{fol}/{res}_phiv"] if porv > 0])
    for i in range(dic[f"{fol}/{res}_num_rst"]):
        temp = dic[f"{fol}/{res}_phiv"] < 0
        sgas = np.array(dic[f"{fol}/{res}_rst"]["SGAS", i])
        rhog = np.array(dic[f"{fol}/{res}_rst"]["GAS_DEN", i])
        rhow = np.array(dic[f"{fol}/{res}_rst"]["WAT_DEN", i])
        rss = np.array(dic[f"{fol}/{res}_rst"]["RSW", i])
        co2_g = sgas * rhog * phiva
        co2_d = rss * rhow * (1.0 - sgas) * phiva * GAS_DEN_REF / WAT_DEN_REF
        for quantity in dic["quantity"]:
            if quantity == "saturation":
                dic[f"{fol}/{res}_{quantity}_array"].append(sgas)
                temp[dic[f"{fol}/{res}_mask"]] = sgas > dic["sat_thr"]
                dic[f"{fol}/{res}_indicator_array"].append(temp)
            elif quantity == "mass":
                dic[f"{fol}/{res}_{quantity}_array"].append((co2_g + co2_d) * KG_TO_KT)
            elif quantity == "diss":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_d * KG_TO_KT)
            elif quantity == "gas":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_g * KG_TO_KT)
            elif quantity in ["FLOWATI+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOWAT{quantity[-2:]}", i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOWATJ+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOWAT{quantity[-2:]}", i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dx"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASI+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOGAS{quantity[-2:]}", i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASJ+"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOGAS{quantity[-2:]}", i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dx"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            else:
                if dic[f"{fol}/{res}_rst"].count(quantity.upper(), 0):
                    dic[f"{fol}/{res}_{quantity}_array"].append(
                        np.array(dic[f"{fol}/{res}_rst"][f"{quantity.upper()}", i])
                    )
                else:
                    dic[f"{fol}/{res}_{quantity}_array"].append(
                        0.0 * np.array(dic[f"{fol}/{res}_rst"]["SGAS", 0])
                    )

    manage_names(dic, res)
    dic[f"{fol}/{dic['namel']}_boxi"] = [
        dic[f"{fol}/{res}_grid"].xyz_from_ijk(0, 0, 0)[i][0] for i in range(3)
    ]
    dic[f"{fol}/{dic['namel']}_boxf"] = [
        dic[f"{fol}/{res}_grid"].xyz_from_ijk(
            dic[f"{fol}/{res}_grid"].dimension[0] - 1,
            dic[f"{fol}/{res}_grid"].dimension[1] - 1,
            dic[f"{fol}/{res}_grid"].dimension[2] - 1,
        )[i][-1]
        for i in range(3)
    ]
    if doplot:
        dic[f"{fol}/{dic['namel']}_xmx"] = []
        dic[f"{fol}/{dic['namel']}_xmx"].append(
            dic[f"{fol}/{res}_grid"].xyz_from_ijk(0, 0, 0)[0][0]
        )
        for i in range(dic[f"{fol}/{res}_grid"].dimension[0]):
            dic[f"{fol}/{dic['namel']}_xmx"].append(
                dic[f"{fol}/{res}_grid"].xyz_from_ijk(i, 0, 0)[0][1]
            )
        dic[f"{fol}/{dic['namel']}_xmx"] = np.array(dic[f"{fol}/{dic['namel']}_xmx"])
        dic[f"{fol}/{dic['namel']}_ymy"] = []
        dic[f"{fol}/{dic['namel']}_ymy"].append(
            dic[f"{fol}/{res}_grid"].xyz_from_ijk(0, 0, 0)[1][1]
        )
        for j in range(dic[f"{fol}/{res}_grid"].dimension[1]):
            dic[f"{fol}/{dic['namel']}_ymy"].append(
                dic[f"{fol}/{res}_grid"].xyz_from_ijk(0, j, 0)[1][2]
            )
        dic[f"{fol}/{dic['namel']}_ymy"] = np.array(dic[f"{fol}/{dic['namel']}_ymy"])
        (
            dic[f"{fol}/{dic['namel']}_xcor"],
            dic[f"{fol}/{dic['namel']}_ycor"],
        ) = np.meshgrid(
            dic[f"{fol}/{dic['namel']}_xmx"], dic[f"{fol}/{dic['namel']}_ymy"][::-1]
        )


def manage_names(dic, res):
    """
    Figure out the folder names

    Args:
        dic (dict): Global dictionary\n
        res (str): Complete name of the simulated model

    Returns:
        dic (dict): Modified global dictionary

    """
    if res[-3].isdigit():
        dic["namef"] = res[:-4]
    if res[-2].isdigit():
        dic["namef"] = res[:-3]
    if res[-1].isdigit():
        dic["namef"] = res[:-2]
    else:
        dic["namef"] = res
    dic["namel"] = "site" if "site" in res else dic["namef"]
