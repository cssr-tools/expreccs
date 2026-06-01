# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0914,R0915,R1702

"""Script to read OPM Flow output files"""

import os
import datetime
import numpy as np
from opm.io.ecl import ESmry as OpmSmry
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import ERst as OpmRst
from opm.io.ecl import EGrid as OpmGrid

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108
KG_TO_KT = 1e-6


def strip_trailing_digits(name):
    """Handle the digits on the folder name"""
    i = len(name)
    while i > 0 and name[i - 1].isdigit():
        i -= 1
    if i > 0 and name[i - 1] == "_":
        i -= 1
    return name[:i]


def reading_simulations(dic):
    """Read the deck quantities using opm"""
    for fol in dic["folders"]:
        dic[fol] = {}
        cwd = os.getcwd()
        os.chdir(f"{fol}/simulations")
        folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
        dic[fol]["sites"] = folders[2:]
        os.chdir(cwd)
        if dic["plot"] in ["reference"]:
            dic[fol]["decks"] = ["reference"]
        elif dic["plot"] in ["regional"]:
            dic[fol]["decks"] = ["regional"]
        elif dic["plot"] in ["site"]:
            dic[fol]["decks"] = dic[fol]["sites"]
        elif dic["compare"]:
            dic[fol]["decks"] = ["reference"] + dic[fol]["sites"]
        else:
            dic[fol]["decks"] = ["reference", "regional"] + dic[fol]["sites"]
        for res in dic[fol]["decks"]:
            dic[fol][res] = {}
            define_cases(dic, fol, folders)
            case = fol + f"/simulations/{res}/{res.upper()}"
            dic[fol][res]["rst"] = OpmRst(case + ".UNRST")
            dic[fol][res]["ini"] = OpmFile(case + ".INIT")
            dic[fol][res]["grid"] = OpmGrid(case + ".EGRID")
            dic[fol][res]["smsp"] = OpmSmry(case + ".SMSPEC")
            dic[fol][res]["num_rst"] = len(dic[fol][res]["rst"].report_steps)
            dic[fol][res]["rst_seconds"] = []
            for i in range(len(dic[fol][res]["rst"].report_steps)):
                dic[fol][res]["rst_seconds"].append(
                    86400 * dic[fol][res]["rst"]["DOUBHEAD", i][0]
                )
            dic[fol][res]["rst_seconds"] = np.array(dic[fol][res]["rst_seconds"])
            dic[fol][res]["dates"] = [
                dic[fol][res]["smsp"].start_date + datetime.timedelta(seconds=seconds)
                for seconds in dic[fol][res]["rst_seconds"]
            ]
            dic[fol][res]["smsp_seconds"] = 86400 * dic[fol][res]["smsp"]["TIME"]
            dic[fol][res]["smsp_dates"] = 86400 * dic[fol][res]["smsp"]["TIME"]
            dic[fol][res]["smsp_dates"] = [
                dic[fol][res]["smsp"].start_date
                + datetime.timedelta(seconds=float(seconds))
                for seconds in dic[fol][res]["smsp_dates"]
            ]
            dic[fol][res]["smsp_rst"] = [
                np.abs(dic[fol][res]["smsp_seconds"] - time).argmin()
                for time in dic[fol][res]["rst_seconds"]
            ]
            dic[fol][res]["sensorijk"] = []
            dic[fol][res]["nowells"] = []
            for keys in dic[fol][res]["smsp"].keys():
                if keys.split(":")[0] == "BFLOWI":
                    for ijk in keys.split(":")[1].split(","):
                        dic[fol][res]["sensorijk"].append(int(ijk) - 1)
                elif keys.split(":")[0] == "WBHP":
                    dic[fol][res]["nowells"].append(keys.split(":")[1])
            dic[fol][res]["sensorijk"] = np.array(dic[fol][res]["sensorijk"])
            dic[fol][res]["sensor"] = dic[fol][res]["grid"].global_index(
                dic[fol][res]["sensorijk"][0],
                dic[fol][res]["sensorijk"][1],
                dic[fol][res]["sensorijk"][2],
            )
            dic[fol][res]["phiv"] = np.array(dic[fol][res]["ini"]["PORV"])
            dic[fol][res]["mask"] = dic[fol][res]["phiv"] > 0
            dic[fol][res]["poro"] = np.array(dic[fol][res]["ini"]["PORO"])
            dic[fol][res]["fipn"] = np.array(dic[fol][res]["ini"]["FIPNUM"])
            dic[fol][res]["static"] = ["fipn"]
            if dic[fol][res]["ini"].count("MULTX"):
                dic[fol][res]["multx"] = np.array(dic[fol][res]["ini"]["MULTX"])
                dic[fol][res]["multy"] = np.array(dic[fol][res]["ini"]["MULTY"])
                dic[fol][res]["static"] += ["multx", "multy"]
            else:
                dic[fol][res]["multx"] = 1 * (dic[fol][res]["fipn"] > 1)
                dic[fol][res]["multy"] = 1 * (dic[fol][res]["fipn"] > 1)
            dic[fol][res]["dx"] = np.array(dic[fol][res]["ini"]["DX"])
            dic[fol][res]["dy"] = np.array(dic[fol][res]["ini"]["DY"])
            dic[fol][res]["dz"] = np.array(dic[fol][res]["ini"]["DZ"])
            if dic[fol][res]["rst"].count("SWAT", 0):
                dic[fol][res]["liq"] = "WAT"
                dic[fol][res]["l"] = "W"
                dic[fol][res]["s"] = "W"
            else:
                dic[fol][res]["liq"] = "OIL"
                dic[fol][res]["l"] = "O"
                dic[fol][res]["s"] = ""
            for quantity in dic["quantity"]:
                dic[fol][res][f"{quantity}_array"] = []
            dic[fol][res]["indicator_array"] = []
            make_arrays(dic, fol, res)


def read_fluxes(case):
    """Fluxes for the back coupling"""
    rst = OpmRst(case + ".UNRST")
    nt = len(rst)

    ip, jp, im, jm = [], [], [], []
    for k in range(nt):
        ip.append(np.array(rst["FLOWATI+", k]))
        jp.append(np.array(rst["FLOWATJ+", k]))
        im.append(np.array(rst["FLOWATI-", k]))
        jm.append(np.array(rst["FLOWATJ-", k]))

    return [ip, jp, im, jm]


def read_mask(case):
    """Mask for the back coupling"""
    ini = OpmFile(case + ".INIT")
    fipn = np.array(ini["FIPNUM"])
    return fipn == 1


def define_cases(dic, fol, folders):
    """Handle the site folder names"""
    dic[fol]["sites"] = [folder for folder in folders if "site" in folder]
    if "site_pres_2" in dic[fol]["sites"]:
        n_c = len(dic[fol]["sites"]) - 1
        dic[f"lregional_{n_c}"] = "REG" + f"{n_c}"
        dic[f"lsite_pres_{n_c}"] = f"S{n_c}" + r"$_{pressure}$"
        dic[fol]["sites"] = dic[fol]["sites"][:2] + [dic[fol]["sites"][-1]]
        dic[fol]["decks"] = (
            dic[fol]["decks"][:3] + [f"regional_{n_c}"] + dic[fol]["sites"]
        )


def make_arrays(dic, fol, res):
    """Handle the quantities to plot"""
    phiv = dic[fol][res]["phiv"]
    mask = dic[fol][res]["mask"]
    poro = dic[fol][res]["poro"]
    dx = dic[fol][res]["dx"]
    dy = dic[fol][res]["dy"]
    dz = dic[fol][res]["dz"]
    rst = dic[fol][res]["rst"]
    phiva = phiv[phiv > 0]
    for i in range(dic[fol][res]["num_rst"]):
        temp = phiv < 0
        sgas = np.array(rst["SGAS", i])
        rhog = np.array(rst["GAS_DEN", i])
        rhow = np.array(rst["WAT_DEN", i])
        rss = np.array(rst["RSW", i])
        co2_g = sgas * rhog * phiva
        co2_d = rss * rhow * (1.0 - sgas) * phiva * GAS_DEN_REF / WAT_DEN_REF
        for quantity in dic["quantity"]:
            if quantity == "saturation":
                dic[fol][res][f"{quantity}_array"].append(sgas)
                temp[mask] = sgas > dic["sat_thr"]
                dic[fol][res]["indicator_array"].append(temp)
            elif quantity == "mass":
                dic[fol][res][f"{quantity}_array"].append((co2_g + co2_d) * KG_TO_KT)
            elif quantity == "diss":
                dic[fol][res][f"{quantity}_array"].append(co2_d * KG_TO_KT)
            elif quantity == "gas":
                dic[fol][res][f"{quantity}_array"].append(co2_g * KG_TO_KT)
            elif quantity.endswith("I+") or quantity.endswith("J+"):
                base = quantity[:-2]
                flow = np.array(rst[f"{base}{quantity[-2:]}", i])
                area = dy * dz * poro if quantity.endswith("I+") else dx * dz * poro
                dic[fol][res][f"{quantity}_array"].append(np.divide(flow, area))
            else:
                if rst.count(quantity.upper(), 0):
                    dic[fol][res][f"{quantity}_array"].append(
                        np.array(rst[quantity.upper(), i])
                    )
                else:
                    dic[fol][res][f"{quantity}_array"].append(0.0 * sgas)
    manage_names(dic, res)
    dic[fol][dic["namel"] + "_boxi"] = [
        dic[fol][res]["grid"].xyz_from_ijk(0, 0, 0)[i][0] for i in range(3)
    ]
    dic[fol][dic["namel"] + "_boxf"] = [
        dic[fol][res]["grid"].xyz_from_ijk(
            dic[fol][res]["grid"].dimension[0] - 1,
            dic[fol][res]["grid"].dimension[1] - 1,
            dic[fol][res]["grid"].dimension[2] - 1,
        )[i][-1]
        for i in range(3)
    ]
    dic[fol].setdefault(dic["namel"], {})
    dic[fol][dic["namel"]]["xmx"] = []
    dic[fol][dic["namel"]]["xmx"].append(
        dic[fol][res]["grid"].xyz_from_ijk(0, 0, 0)[0][0]
    )
    for i in range(dic[fol][res]["grid"].dimension[0]):
        dic[fol][dic["namel"]]["xmx"].append(
            dic[fol][res]["grid"].xyz_from_ijk(i, 0, 0)[0][1]
        )
    dic[fol][dic["namel"]]["xmx"] = np.array(dic[fol][dic["namel"]]["xmx"])
    dic[fol][dic["namel"]]["ymy"] = []
    dic[fol][dic["namel"]]["ymy"].append(
        dic[fol][res]["grid"].xyz_from_ijk(0, 0, 0)[1][1]
    )
    for j in range(dic[fol][res]["grid"].dimension[1]):
        dic[fol][dic["namel"]]["ymy"].append(
            dic[fol][res]["grid"].xyz_from_ijk(0, j, 0)[1][2]
        )
    dic[fol][dic["namel"]]["ymy"] = np.array(dic[fol][dic["namel"]]["ymy"])
    dic[fol][dic["namel"]]["xcor"], dic[fol][dic["namel"]]["ycor"] = np.meshgrid(
        dic[fol][dic["namel"]]["xmx"], dic[fol][dic["namel"]]["ymy"][::-1]
    )


def manage_names(dic, res):
    """Figure out the folder names"""
    dic["namef"] = strip_trailing_digits(res)
    dic["namel"] = "site" if "site" in res else dic["namef"]
