# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to run the studies.
"""
import os
from expreccs.visualization.plotting import plot_results


def simulations(dic, name):
    """
    Function to Run Flow

    Args:
        dic (dict): Global dictionary with required parameters

    """
    os.system(
        f"{dic['flow']} --output-dir={dic['exe']}/{dic['fol']}/output/{name} "
        f"{dic['exe']}/{dic['fol']}/preprocessing/{name}/{name.upper()}.DATA  & wait\n"
    )


def plotting(dic, time):
    """
    Function to run the plotting.py file

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["folders"] = [dic["fol"]]
    dic["time"] = time
    os.chdir(f"{dic['exe']}/{dic['fol']}/postprocessing")
    plot_exe = [
        "python",
        f"{dic['pat']}/visualization/plotting.py",
        f"-t {time}",
        f"-f {dic['fol']}",
        f"-m {dic['mode']}",
        f"-r {dic['reading']}",
    ]
    print(" ".join(plot_exe))
    plot_results(dic)
