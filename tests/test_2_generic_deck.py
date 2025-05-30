# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality to rotate grids and to handle generic decks"""

import os
import pathlib

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_generic_deck():
    """See configs/rotate.toml"""
    os.chdir(f"{dirname}/configs")
    os.system("expreccs -i rotate.toml -o rotate -m all -t 30 -u opm -p site -w 1")
    assert os.path.exists("./rotate/postprocessing/rotate_site_closed_pressure.png")
    os.system(
        f"scp -r {dirname}/configs/rotate/preprocessing/regional/. "
        f"{dirname}/configs/rotate/simulations/regional"
    )
    os.system(
        f"scp -r {dirname}/configs/rotate/preprocessing/site_closed/. "
        f"{dirname}/configs/rotate/simulations/site_closed"
    )
    os.chdir(f"{dirname}/configs/rotate/simulations")
    os.system(
        "expreccs -o expreccs -i 'regional/REGIONAL site_closed/SITE_CLOSED' -w 1"
    )
    assert os.path.exists(f"{dirname}/configs/rotate/simulations/expreccs/BCCON.INC")
    os.chdir(f"{dirname}/configs/rotate/simulations/expreccs")
    os.system("flow EXPRECCS.DATA --enable-tuning=true")
    assert os.path.exists(
        f"{dirname}/configs/rotate/simulations/expreccs/EXPRECCS.UNRST"
    )
