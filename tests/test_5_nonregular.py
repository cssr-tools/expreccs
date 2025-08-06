# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality in a site deck with nonregular boundaries"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_site_regional():
    """See regional/ and site/"""
    flow = "flow"
    for name in ["site", "regional"]:
        os.chdir(f"{dirname}/{name}")
        os.system(f"{flow} {name.upper()}.DATA")
    base = "expreccs -i 'regional/REGIONAL site/SITE' -n 1 -o expreccs"
    for i, (name, flag, nlines) in enumerate(
        zip(["_zones", "_frequency"], [" -z 1", " -f 2"], [29, 53])
    ):
        os.chdir(f"{dirname}")
        os.system(f"{base}{name}{flag}")
        os.chdir(f"{dirname}/expreccs{name}")
        subprocess.run([flow, f"EXPRECCS{name.upper()}.DATA"], check=True)
        assert os.path.exists(f"{dirname}/expreccs{name}/EXPRECCS{name.upper()}.UNRST")
        with open(
            f"{dirname}/expreccs{name}/bc/BCPROP{6*(i+1)}.INC", "r", encoding="utf8"
        ) as file:
            assert len(file.readlines()) == nlines
