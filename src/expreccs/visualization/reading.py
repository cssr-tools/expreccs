# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912

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


def reading_resdata(dic, loadnpy=True):
    """
    Read the deck quantities using resdata

    Args:
        dic (dict): Global dictionary\n
        loadnpy (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{fol}/output")
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
            case = fol + f"/output/{res}/{res.upper()}"
            dic[f"{fol}/{res}_rst"] = ResdataFile(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = ResdataFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = Grid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = Summary(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = dic[f"{fol}/{res}_rst"].num_report_steps()
            if loadnpy:
                define_cases(dic, fol, folders)
                resdata_load_data(dic, fol, res, name)
            dic[f"{fol}/{res}_phiv"] = dic[f"{fol}/{res}_ini"].iget_kw("PORV")[0]
            dic[f"{fol}/{res}_poro"] = dic[f"{fol}/{res}_ini"].iget_kw("PORO")[0]
            dic[f"{fol}/{res}_fipn"] = np.array(
                dic[f"{fol}/{res}_ini"].iget_kw("FIPNUM")
            )[0]
            dic[f"{fol}/{res}_dx"] = np.array(dic[f"{fol}/{res}_ini"].iget_kw("DX")[0])
            dic[f"{fol}/{res}_dy"] = np.array(dic[f"{fol}/{res}_ini"].iget_kw("DY")[0])
            dic[f"{fol}/{res}_dz"] = np.array(dic[f"{fol}/{res}_ini"].iget_kw("DZ")[0])
            if dic[f"{fol}/{res}_rst"].has_kw("SWAT"):
                dic[f"{fol}/{res}liq"] = "WAT"
                dic[f"{fol}/{res}l"] = "W"
                dic[f"{fol}/{res}s"] = "W"
            else:
                dic[f"{fol}/{res}liq"] = "OIL"
                dic[f"{fol}/{res}l"] = "O"
                dic[f"{fol}/{res}s"] = ""
            dic[f"{fol}/{res}_indicator_array"] = []
            for quantity in dic["quantity"]:
                dic[f"{fol}/{res}_{quantity}_array"] = []
            resdata_arrays(dic, fol, res, loadnpy)


def resdata_load_data(dic, fol, res, name):
    """
    Read the data needed for the plotting

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model\n
        name (str): Name of the type of simulated model (e.g., site)

    Returns:
        dic (dict): Modified global dictionary

    """
    dic[f"{fol}/{res}_rst_seconds"] = np.load(fol + f"/output/{name}/schedule.npy")
    dic[f"{fol}/{res}_nowells"] = np.load(fol + f"/output/{name}/nowells.npy")
    dic[f"{fol}/{res}_sensor"] = int(np.load(fol + f"/output/{name}/sensor.npy"))
    dic[f"{fol}/{res}_sensor_coords"] = np.load(
        fol + f"/output/{name}/sensor_coords.npy"
    )
    dic[f"{fol}/{res}_nowells_site"] = np.load(fol + f"/output/{name}/nowells_site.npy")
    dic[f"{fol}/{res}_sensorijk"] = np.load(fol + f"/output/{name}/sensorijk.npy")
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
    handle_smsp_time(dic, fol, res, name)


def resdata_arrays(dic, fol, res, loadnpy):
    """
    From simulation data to arrays

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model\n
        loadnpy (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    phiva = np.array([porv for porv in dic[f"{fol}/{res}_phiv"] if porv > 0])
    for i in range(dic[f"{fol}/{res}_num_rst"]):
        sgas = np.array(dic[f"{fol}/{res}_rst"]["SGAS"][i])
        rhog = np.array(dic[f"{fol}/{res}_rst"]["GAS_DEN"][i])
        rhow = np.array(dic[f"{fol}/{res}_rst"][f"{dic[f'{fol}/{res}liq']}_DEN"][i])
        rss = np.array(dic[f"{fol}/{res}_rst"][f"RS{dic[f'{fol}/{res}s']}"][i])
        co2_g = sgas * rhog * phiva
        co2_d = rss * rhow * (1.0 - sgas) * phiva * GAS_DEN_REF / WAT_DEN_REF
        for quantity in dic["quantity"]:
            if quantity == "saturation":
                dic[f"{fol}/{res}_{quantity}_array"].append(sgas)
                dic[f"{fol}/{res}_indicator_array"].append(sgas > dic["sat_thr"])
            elif quantity == "mass":
                dic[f"{fol}/{res}_{quantity}_array"].append((co2_g + co2_d) * KG_TO_KT)
            elif quantity == "diss":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_d * KG_TO_KT)
            elif quantity == "gas":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_g * KG_TO_KT)
            elif quantity in ["FLOWATI+", "FLOWATI-"]:
                flow = np.array(
                    dic[f"{fol}/{res}_rst"][
                        f"FLO{dic[f'{fol}/{res}liq']}{quantity[-2:]}"
                    ][i]
                )
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOWATJ+", "FLOWATJ-"]:
                flow = np.array(
                    dic[f"{fol}/{res}_rst"][
                        f"FLO{dic[f'{fol}/{res}liq']}{quantity[-2:]}"
                    ][i]
                )
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dx"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASI+", "FLOGASI-"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOGAS{quantity[-2:]}"][i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASJ+", "FLOGASJ-"]:
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
    if loadnpy:
        dic[f"{fol}/{dic['namel']}_xmx"] = np.load(
            fol + f"/output/{dic['namef']}/{dic['namel']}_xmx.npy"
        )
        dic[f"{fol}/{dic['namel']}_ymy"] = np.load(
            fol + f"/output/{dic['namef']}/{dic['namel']}_ymy.npy"
        )
        (
            dic[f"{fol}/{dic['namel']}_xcor"],
            dic[f"{fol}/{dic['namel']}_ycor"],
        ) = np.meshgrid(
            dic[f"{fol}/{dic['namel']}_xmx"], dic[f"{fol}/{dic['namel']}_ymy"][::-1]
        )


def handle_smsp_time(dic, fol, res, name):
    """
    Handle the times in the summary files

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model\n
        name (str): Name of the type of simulated model (e.g., site)

    Returns:
        dic (dict): Modified global dictionary

    """
    dic[f"{fol}/{res}_rst_seconds"] = np.load(fol + f"/output/{name}/schedule.npy")
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


def reading_opm(dic, loadnpy=True):  # pylint: disable=R0915, R0912
    """
    Read the deck quantities using opm

    Args:
        dic (dict): Global dictionary\n
        loadnpy (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    for fol in dic["folders"]:
        cwd = os.getcwd()
        os.chdir(f"{fol}/output")
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
            if loadnpy:
                define_cases(dic, fol, folders)
                dic[f"{fol}/{res}_rst_seconds"] = np.load(
                    fol + f"/output/{name}/schedule.npy"
                )
                dic[f"{fol}/{res}_nowells"] = np.load(
                    fol + f"/output/{name}/nowells.npy"
                )
                dic[f"{fol}/{res}_nowells_site"] = np.load(
                    fol + f"/output/{name}/nowells_site.npy"
                )
                dic[f"{fol}/{res}_sensor"] = int(
                    np.load(fol + f"/output/{name}/sensor.npy")
                )
                dic[f"{fol}/{res}_sensor_coords"] = np.load(
                    fol + f"/output/{name}/sensor_coords.npy"
                )
                dic[f"{fol}/{res}_sensorijk"] = np.load(
                    fol + f"/output/{name}/sensorijk.npy"
                )
            case = fol + f"/output/{res}/{res.upper()}"
            dic[f"{fol}/{res}_rst"] = OpmRst(case + ".UNRST")
            dic[f"{fol}/{res}_ini"] = OpmFile(case + ".INIT")
            dic[f"{fol}/{res}_grid"] = OpmGrid(case + ".EGRID")
            dic[f"{fol}/{res}_smsp"] = OpmSmry(case + ".SMSPEC")
            dic[f"{fol}/{res}_num_rst"] = len(dic[f"{fol}/{res}_rst"].report_steps)
            if loadnpy:
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

            dic[f"{fol}/{res}_phiv"] = np.array(dic[f"{fol}/{res}_ini"]["PORV"])
            dic[f"{fol}/{res}_poro"] = np.array(dic[f"{fol}/{res}_ini"]["PORO"])
            dic[f"{fol}/{res}_fipn"] = np.array(dic[f"{fol}/{res}_ini"]["FIPNUM"])
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
            opm_arrays(dic, fol, res, loadnpy)


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


def opm_arrays(dic, fol, res, loadnpy):
    """
    From simulation data to arrays

    Args:
        dic (dict): Global dictionary\n
        fol (str): Name of the output folder\n
        res (str): Complete name of the simulated model\n
        loadnpy (bool): True for plotting, False for back-coupling

    Returns:
        dic (dict): Modified global dictionary

    """
    phiva = np.array([porv for porv in dic[f"{fol}/{res}_phiv"] if porv > 0])
    for i in range(dic[f"{fol}/{res}_num_rst"]):
        sgas = np.array(dic[f"{fol}/{res}_rst"]["SGAS", i])
        rhog = np.array(dic[f"{fol}/{res}_rst"]["GAS_DEN", i])
        rhow = np.array(dic[f"{fol}/{res}_rst"][f"{dic[f'{fol}/{res}liq']}_DEN", i])
        rss = np.array(dic[f"{fol}/{res}_rst"][f"RS{dic[f'{fol}/{res}s']}", i])
        co2_g = sgas * rhog * phiva
        co2_d = rss * rhow * (1.0 - sgas) * phiva * GAS_DEN_REF / WAT_DEN_REF
        for quantity in dic["quantity"]:
            if quantity == "saturation":
                dic[f"{fol}/{res}_{quantity}_array"].append(sgas)
                dic[f"{fol}/{res}_indicator_array"].append(sgas > dic["sat_thr"])
            elif quantity == "mass":
                dic[f"{fol}/{res}_{quantity}_array"].append((co2_g + co2_d) * KG_TO_KT)
            elif quantity == "diss":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_d * KG_TO_KT)
            elif quantity == "gas":
                dic[f"{fol}/{res}_{quantity}_array"].append(co2_g * KG_TO_KT)
            elif quantity in ["FLOWATI+", "FLOWATI-"]:
                flow = np.array(
                    dic[f"{fol}/{res}_rst"][
                        f"FLO{dic[f'{fol}/{res}liq']}{quantity[-2:]}", i
                    ]
                )
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOWATJ+", "FLOWATJ-"]:
                flow = np.array(
                    dic[f"{fol}/{res}_rst"][
                        f"FLO{dic[f'{fol}/{res}liq']}{quantity[-2:]}", i
                    ]
                )
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dx"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASI+", "FLOGASI-"]:
                flow = np.array(dic[f"{fol}/{res}_rst"][f"FLOGAS{quantity[-2:]}", i])
                dic[f"{fol}/{res}_{quantity}_array"].append(
                    np.divide(
                        flow,
                        dic[f"{fol}/{res}_dy"]
                        * dic[f"{fol}/{res}_dz"]
                        * dic[f"{fol}/{res}_poro"],
                    )
                )
            elif quantity in ["FLOGASJ+", "FLOGASJ-"]:
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
    if loadnpy:
        dic[f"{fol}/{dic['namel']}_xmx"] = np.load(
            fol + f"/output/{dic['namef']}/{dic['namel']}_xmx.npy"
        )
        dic[f"{fol}/{dic['namel']}_ymy"] = np.load(
            fol + f"/output/{dic['namef']}/{dic['namel']}_ymy.npy"
        )
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
