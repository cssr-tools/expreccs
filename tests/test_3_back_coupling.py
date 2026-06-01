# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality for back-coupling"""

import subprocess
from pathlib import Path

testpth = Path(__file__).parent


def test_3_back_coupling(tmp_path):
    """Run back-coupling and check output."""
    subprocess.run(
        [
            "expreccs",
            "-i",
            str(testpth / "configs" / "back-coupling.toml"),
            "-o",
            str(tmp_path / "back"),
            "-p",
            "all",
        ],
        check=True,
    )

    assert (
        tmp_path
        / "back"
        / "postprocessing"
        / "back_difference_site_porvproj_watfluxi+.png"
    ).exists()
