# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality to rotate grids and to handle generic 2D decks"""

import shutil
import subprocess
from pathlib import Path

from expreccs.core.expreccs import main

testpth = Path(__file__).parent


def test_1_generic_deck_2d(tmp_path, monkeypatch):
    """Run rotate_2d and check outputs."""
    monkeypatch.chdir(tmp_path)

    main(
        [
            "-i",
            str(testpth / "configs" / "rotate_2d.toml"),
            "-o",
            "rotate_2d",
            "-m",
            "all",
            "-t",
            "30",
            "-p",
            "site",
        ]
    )

    base = tmp_path / "rotate_2d"

    assert (base / "postprocessing" / "rotate_2d_site_closed_pressure.png").exists()

    shutil.copytree(
        base / "preprocessing" / "regional",
        base / "simulations" / "regional",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        base / "preprocessing" / "site_closed",
        base / "simulations" / "site_closed",
        dirs_exist_ok=True,
    )

    simdir = base / "simulations"
    monkeypatch.chdir(simdir)

    main(
        [
            "-o",
            "expreccs",
            "-i",
            "regional/REGIONAL site_closed/SITE_CLOSED",
            "-f",
            "3",
            "-a",
            "3.2",
        ]
    )

    exdir = simdir / "expreccs"

    name = exdir / "EXPRECCS.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "BCCON" in content
    assert "INCLUDE\n'bc/BCPROP270.INC' /" in content

    name = exdir / "BCCON.INC"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "BCCON" in content
    assert "69 1 1 1 1 1 1 'I-' /\n/" in content

    name = exdir / "bc" / "BCPROP270.INC"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "100 DIRICHLET WATER 1*" in content

    monkeypatch.chdir(exdir)

    subprocess.run(
        ["flow", "EXPRECCS.DATA", "--enable-tuning=true"],
        check=True,
    )

    assert (exdir / "EXPRECCS.UNRST").exists()
