# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0914,R0915

"""Test the expreccs framework"""

import shutil
import subprocess
from pathlib import Path

import numpy as np
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid

from expreccs.core.expreccs import main

EPS = 1e-6

testpth = Path(__file__).parent


def test_0_all_bcs(tmp_path, monkeypatch):
    """Run configs and check outputs."""
    monkeypatch.chdir(tmp_path)

    shutil.copy(testpth / "configs" / "input.toml", tmp_path)

    main()

    name = tmp_path / "output" / "preprocessing" / "site_pres" / "SITE_PRES.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "BCCON" in content
    assert "4500 125 125 25 25 15 15 J /\n/" in content
    assert content.count("BCPROP") == 5
    assert content.count("DIRICHLET WATER") == 22500

    porv = [5.215e09, 5.0125e09, 1.35e08]
    nxr = [163, 63, 125]
    nyr = [75, 15, 25]
    nzr = [15, 3, 15]
    dxmin = [40, 200, 40]
    dxmax = [1000, 1000, 40]
    dymin = [200, 1000, 200]
    dymax = [200, 1000, 200]
    dzmin = [0.99999726, 8.999996, 0.99999726]
    dzmax = [3.0000038, 9.000003, 3.0000012]
    for i, name in enumerate(["reference", "regional", "site_pres"]):
        egrid = OpmGrid(f"{tmp_path}/output/simulations/{name}/{name.upper()}.EGRID")
        nx, ny, nz = egrid.dimension
        assert nx == nxr[i]
        assert ny == nyr[i]
        assert nz == nzr[i]
        init = OpmFile(f"{tmp_path}/output/simulations/{name}/{name.upper()}.INIT")
        assert abs(np.sum(np.array(init["PORV"])) - porv[i]) < EPS
        assert abs(min(init["DX"]) - dxmin[i]) < EPS
        assert abs(max(init["DX"]) - dxmax[i]) < EPS
        assert abs(min(init["DY"]) - dymin[i]) < EPS
        assert abs(max(init["DY"]) - dymax[i]) < EPS
        assert abs(min(init["DZ"]) - dzmin[i]) < EPS
        assert abs(max(init["DZ"]) - dzmax[i]) < EPS

    for name in ["wells", "interp", "porvproj", "open", "closed"]:
        subprocess.run(
            ["expreccs", "-i", str(testpth / "configs" / f"{name}.toml"), "-m", "site"],
            cwd=tmp_path,
            check=True,
        )

    config = str(testpth / "configs" / "flux.toml")
    main(["-i", config, "-m", "site", "-p", "all"])

    name = tmp_path / "output" / "preprocessing" / "site_flux" / "SITE_FLUX.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "AQUANCON" in content
    assert "180 121 124 25 25 13 15	'J' 1.00 1 /\n/" in content
    assert content.count("180 ") == 7
    assert content.count("AQUFLUX") == 5

    name = tmp_path / "output" / "preprocessing" / "site_wells" / "SITE_WELLS.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert content.count("BCINJ0") == 7
    assert content.count("BCINJ1 WAT OPEN") == 5
    assert content.count("BCINJ2 WAT OPEN") == 5
    assert content.count("BCINJ3") == 7
    assert content.count("WCONPROD") == 5
    assert content.count("BCPRO3 OPEN BHP") == 5

    name = tmp_path / "output" / "preprocessing" / "site_open" / "SITE_OPEN.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "BCCON" in content
    assert content.count("BCPROP\n1 FREE /\n2 FREE /\n3 FREE /\n4 FREE /\n/") == 5
    assert content.count("BCPROP") == 5

    post = tmp_path / "output" / "postprocessing"

    for name in ["wells_pressure", "pres_pressure", "flux_pressure"]:
        assert (post / f"output_difference_site_{name}.png").exists()

    assert len(list(Path(post).glob("*.png"))) == 191

    subprocess.run(
        ["expreccs", "-c", "compare"],
        cwd=tmp_path,
        check=True,
    )

    compare = tmp_path / "compare"

    assert (compare / "compareoutput_distance_from_border.png").exists()
    assert len(list(Path(compare).glob("*.png"))) == 41
