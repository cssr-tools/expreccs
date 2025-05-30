# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality for back-coupling"""

import os
import pathlib

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_back_coupling():
    """See configs/back-coupling.toml"""
    os.chdir(f"{dirname}/configs")
    os.system("expreccs -i back-coupling.toml -o back -p yes -w 1")
    assert os.path.exists(
        f"{dirname}/configs/back/postprocessing/back_difference_site_porvproj_watfluxi+.png"
    )
