# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality to rotate grids and to handle generic decks"""

import shutil
import subprocess
from pathlib import Path

EPS = 1e-3

testpth = Path(__file__).parent


def test_2_generic_deck(tmp_path, monkeypatch):
    """Run rotate and check outputs."""
    monkeypatch.chdir(tmp_path)

    subprocess.run(
        [
            "expreccs",
            "-i",
            str(testpth / "configs" / "rotate.toml"),
            "-o",
            "rotate",
            "-m",
            "all",
            "-t",
            "30",
            "-p",
            "site",
        ],
        check=True,
    )

    base = tmp_path / "rotate"

    assert (base / "postprocessing" / "rotate_site_closed_pressure.png").exists()

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

    subprocess.run(
        [
            "expreccs",
            "-o",
            "expreccs",
            "-i",
            "regional/REGIONAL site_closed/SITE_CLOSED",
        ],
        check=True,
    )

    exdir = simdir / "expreccs"

    name = exdir / "EXPRECCS.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "BCCON" in content
    assert "INCLUDE\n'bc/BCPROP90.INC' /" in content

    name = exdir / "BCCON.INC"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "BCCON" in content
    assert "700 1 1 1 1 7 7 'I-' /\n/" in content

    name = exdir / "bc" / "BCPROP90.INC"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert abs(float(lines[-2].split(" ")[-2]) - 308.6318781300921) < EPS
    content = "".join(lines)
    assert "700 DIRICHLET WATER 1*" in content

    monkeypatch.chdir(exdir)

    subprocess.run(
        ["flow", "EXPRECCS.DATA", "--enable-tuning=true"],
        check=True,
    )

    assert (exdir / "EXPRECCS.UNRST").exists()
