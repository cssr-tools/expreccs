# SPDX-FileCopyrightText: 2024 NORCE
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
    os.system("expreccs -i wells.toml -m site -w 1")
    os.chdir(f"{dirname}/configs")
    os.system("expreccs -i interp.toml -m site -w 1")
    os.chdir(f"{dirname}/configs")
    os.system("expreccs -i flux.toml -m site -p all -r opm -w 1")
    assert os.path.exists(
        f"{dirname}/configs/output/postprocessing/output_difference_site_wells_pressure.png"
    )
    assert os.path.exists(
        f"{dirname}/configs/output/postprocessing/output_difference_site_pres_pressure.png"
    )
    assert os.path.exists(
        f"{dirname}/configs/output/postprocessing/output_difference_site_flux_pressure.png"
    )
    os.system("expreccs -c compare -w 1")
    assert os.path.exists(
        f"{dirname}/configs/compare/compareoutput_distance_from_border.png"
    )
