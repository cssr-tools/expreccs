"""Test the framework"""

import os
from expreccs.core.expreccs import main


def test():
    """See configs/*.txt"""
    cwd = os.getcwd()
    os.chdir(f"{cwd}/tests/configs")
    main()
    os.chdir(f"{cwd}/tests/configs")
    os.system("expreccs -i wells.txt -m site")
    os.chdir(f"{cwd}/tests/configs")
    os.system("expreccs -i interp.txt -m site")
    os.chdir(f"{cwd}/tests/configs")
    os.system("expreccs -i flux.txt -m site -p yes")
    os.chdir(f"{cwd}/tests/configs")
    os.system("expreccs -c compare")
    assert os.path.exists("./compare/compareoutput_distance_from_border.png")
    os.system("expreccs -i back-coupling.txt -o back -p yes -r opm")
    assert os.path.exists(
        "./back/postprocessing/back_difference_site_pres_watfluxi-.png"
    )
    os.chdir(cwd)
