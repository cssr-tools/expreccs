# SPDX-FileCopyrightText: 2025 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality in a site and regional deck"""

import os
import pathlib

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_site_regional():
    """See regional/ and site/"""
    flow = "flow --relaxed-max-pv-fraction=0 "
    for name in ["site", "regional"]:
        os.chdir(f"{dirname}/{name}")
        os.system(f"{flow} {name.upper()}.DATA")
    base = "expreccs -i 'regional/REGIONAL site/SITE' -o expreccs"
    for name, flag, nlines in zip(
        ["", "_dpincrease", "_perfipnum"], ["", " -e 0", " -z 1"], [65, 65, 35]
    ):
        os.chdir(f"{dirname}")
        os.system(f"{base}{name}{flag}")
        os.chdir(f"{dirname}/expreccs{name}")
        os.system(f"{flow} EXPRECCS{name.upper()}.DATA")
        with open(
            f"{dirname}/expreccs{name}/bc/BCPROP6.INC", "r", encoding="utf8"
        ) as file:
            assert len(file.readlines()) == nlines
