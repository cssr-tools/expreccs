"""Test the framework"""

import os
from expreccs.core.expreccs import main


def test():
    """See configs/input.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/configs")
    main()
    os.chdir(cwd)
