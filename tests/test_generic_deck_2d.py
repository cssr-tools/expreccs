# SPDX-FileCopyrightText: 2025 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality to rotate grids and to handle generic 2D decks"""

import os
import pathlib

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_generic_deck_2d():
    """See configs/rotate_2d.txt"""
    os.chdir(f"{dirname}/configs")
    os.system("expreccs -i rotate_2d.txt -o rotate_2d -m all -t 30 -r opm -p site -w 1")
    assert os.path.exists(
        "./rotate_2d/postprocessing/rotate_2d_site_closed_pressure.png"
    )
    os.system(
        f"scp -r {dirname}/configs/rotate_2d/preprocessing/regional/. "
        f"{dirname}/configs/rotate_2d/output/regional"
    )
    os.system(
        f"scp -r {dirname}/configs/rotate_2d/preprocessing/site_closed/. "
        f"{dirname}/configs/rotate_2d/output/site_closed"
    )
    os.chdir(f"{dirname}/configs/rotate_2d/output")
    os.system(
        "expreccs -o expreccs -i 'regional/REGIONAL site_closed/SITE_CLOSED' -w 1 "
        "-f 3 -a 3.2"
    )
    assert os.path.exists(f"{dirname}/configs/rotate_2d/output/expreccs/BCCON.INC")
    os.chdir(f"{dirname}/configs/rotate_2d/output/expreccs")
    os.system("flow EXPRECCS.DATA --enable-tuning=true")
    assert os.path.exists(f"{dirname}/configs/rotate_2d/output/expreccs/EXPRECCS.UNRST")
