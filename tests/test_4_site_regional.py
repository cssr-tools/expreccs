# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the expreccs functionality in a site/regional deck with nonregular boundaries"""

import shutil
import subprocess
from pathlib import Path

from expreccs.core.expreccs import main

EPS = 1e-3

testpth = Path(__file__).parent


def test_4_site_regional(tmp_path, monkeypatch):
    """Run site/regional workflow and check outputs."""
    shutil.copytree(testpth / "site", tmp_path / "site")
    shutil.copytree(testpth / "regional", tmp_path / "regional")

    flow_relaxed = ["flow", "--relaxed-max-pv-fraction=0"]
    flow = ["flow"]

    for name in ["site", "regional"]:
        subprocess.run(
            flow_relaxed + [f"{name.upper()}.DATA"],
            cwd=tmp_path / name,
            check=True,
        )

    monkeypatch.chdir(tmp_path)

    base_cmd = ["-i", "regional/REGIONAL site/SITE"]

    for name, flag, nlines, pressure in zip(
        ["", "_dpincrease", "_perfipnum"],
        [[], ["-e", "0"], ["-z", "1"]],
        [65, 65, 35],
        [367.6365236622162, 367.63575533221535, 365.74737548828125],
    ):
        outname = f"expreccs{name}"

        main(base_cmd + ["-o", outname] + flag)

        exdir = tmp_path / outname

        subprocess.run(
            flow_relaxed + [f"{outname.upper()}.DATA"],
            cwd=exdir,
            check=True,
        )

        assert (exdir / f"{outname.upper()}.UNRST").exists()

        with open(exdir / "bc" / "BCPROP6.INC", encoding="utf8") as f:
            lines = f.readlines()
        assert len(lines) == nlines
        assert abs(float(lines[-2].split(" ")[-2]) - pressure) < EPS

    for i, (name, flag, nlines, pressure) in enumerate(
        zip(
            ["_zones", "_frequency"],
            [["-z", "1"], ["-f", "2"]],
            [29, 53],
            [365.74737548828125, 367.6366322835287],
        )
    ):
        outname = f"expreccs{name}"

        main(base_cmd + ["-n", "1", "-o", outname] + flag)

        exdir = tmp_path / outname

        subprocess.run(
            flow + [f"{outname.upper()}.DATA"],
            cwd=exdir,
            check=True,
        )

        assert (exdir / f"{outname.upper()}.UNRST").exists()

        with open(
            exdir / "bc" / f"BCPROP{6 * (i + 1)}.INC",
            encoding="utf8",
        ) as f:
            lines = f.readlines()
        assert len(lines) == nlines
        assert abs(float(lines[-2].split(" ")[-2]) - pressure) < EPS
