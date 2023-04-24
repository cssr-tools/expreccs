"""
Utiliy functions to run the studies.
"""
import os
import subprocess


def simulations(dic, name):
    """
    Function to Run Flow

    Args:
        dic (dict): Global dictionary with required parameters

    """
    os.chdir(f"{dic['exe']}/{dic['fol']}/output")
    os.system(
        f"{dic['flow']} --output-dir={dic['exe']}/{dic['fol']}/output "
        f"{dic['exe']}/{dic['fol']}/preprocessing/{name.upper()}.DATA  & wait\n"
    )


def plotting(dic, time):
    """
    Function to run the plotting.py file

    Args:
        dic (dict): Global dictionary with required parameters

    """
    os.chdir(f"{dic['exe']}/{dic['fol']}/postprocessing")
    prosc = subprocess.run(
        [
            "python",
            f"{dic['pat']}/visualization/plotting.py",
            f"-t {time}",
            "-p " + f"{dic['exe']}/{dic['fol']}/output/",
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
