# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality to rotate grids and to handle generic decks"""

import os
import pathlib

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_generic_deck():
    """See configs/rotate.txt"""
    os.chdir(f"{dirname}/configs")
    os.system("expreccs -i rotate.txt -o rotate -m all -t 30 -r opm -p site -w 1")
    assert os.path.exists("./rotate/postprocessing/rotate_site_closed_pressure.png")
    os.system(
        f"scp -r {dirname}/configs/rotate/preprocessing/regional/. "
        f"{dirname}/configs/rotate/output/regional"
    )
    os.system(
        f"scp -r {dirname}/configs/rotate/preprocessing/site_closed/. "
        f"{dirname}/configs/rotate/output/site_closed"
    )
    os.chdir(f"{dirname}/configs/rotate/output")
    os.system("expreccs -o expreccs -e regional,site_closed -w 1")
    assert os.path.exists(f"{dirname}/configs/rotate/output/expreccs/BCCON.INC")
    os.chdir(f"{dirname}/configs/rotate/output/expreccs")
    os.system("flow EXPRECCS.DATA --enable-tuning=true")
    assert os.path.exists(f"{dirname}/configs/rotate/output/expreccs/EXPRECCS.UNRST")
