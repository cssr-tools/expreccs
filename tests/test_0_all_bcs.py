# SPDX-FileCopyrightText: 2024-2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs framework"""

import os
import pathlib
from expreccs.core.expreccs import main

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_all_bcs():
    """See configs/*.toml"""
    os.chdir(f"{dirname}/configs")
    main()
    os.chdir(f"{dirname}/configs")
    for name in ["wells", "interp"]:
        os.system(f"expreccs -i{name}.toml -m site -w 1")
        os.chdir(f"{dirname}/configs")
    os.system("expreccs -i flux.toml -m site -p all -w 1")
    for name in ["wells_pressure", "pres_pressure", "flux_pressure"]:
        assert os.path.exists(
            f"{dirname}/configs/output/postprocessing/output_difference_site_{name}.png"
        )
    os.system("expreccs -c compare -w 1")
    assert os.path.exists(
        f"{dirname}/configs/compare/compareoutput_distance_from_border.png"
    )
