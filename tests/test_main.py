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
    os.system("expreccs -i flux.txt -m site -p all")
    assert os.path.exists(
        "./output/postprocessing/output_difference_site_wells_pressure.png"
    )
    assert os.path.exists(
        "./output/postprocessing/output_difference_site_pres_pressure.png"
    )
    assert os.path.exists(
        "./output/postprocessing/output_difference_site_flux_pressure.png"
    )
    os.chdir(f"{cwd}/tests/configs")
    os.system("expreccs -c compare")
    assert os.path.exists("./compare/compareoutput_distance_from_border.png")
    os.system("expreccs -i back-coupling.txt -o back -p yes -r opm")
    assert os.path.exists(
        "./back/postprocessing/back_difference_site_pres_watfluxi-.png"
    )
    os.system("expreccs -i rotate.txt -o rotate -m all -t 30 -r resdata -p site")
    assert os.path.exists("./rotate/postprocessing/rotate_site_closed_pressure.png")
    os.system("scp -r ./rotate/preprocessing/regional/. ./rotate/output/regional")
    os.system("scp -r ./rotate/preprocessing/site_closed/. ./rotate/output/site_closed")
    os.system("scp rotate.txt ./rotate/output")
    os.chdir(f"{cwd}/tests/configs/rotate/output")
    os.system("expreccs -i rotate.txt -o expreccs -e regional,site_closed")
    assert os.path.exists("./expreccs/BCCON.INC")
    os.chdir(f"{cwd}/tests/configs/rotate/output/expreccs")
    os.system("flow EXPRECCS.DATA --enable-tuning=true --linear-solver=cprw")
    assert os.path.exists("./EXPRECCS.UNRST")
    os.chdir(cwd)
