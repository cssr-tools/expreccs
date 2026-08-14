# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality for back-coupling"""

from pathlib import Path

from expreccs.core.expreccs import main

testpth = Path(__file__).parent


def test_3_back_coupling(tmp_path):
    """Run back-coupling and check output."""
    main(
        [
            "-i",
            str(testpth / "configs" / "back-coupling.toml"),
            "-o",
            str(tmp_path / "back"),
            "-p",
            "all",
        ]
    )

    assert (
        tmp_path
        / "back"
        / "postprocessing"
        / "back_difference_site_porvproj_watfluxi+.png"
    ).exists()
