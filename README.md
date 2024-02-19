[![Build Status](https://github.com/cssr-tools/expreccs/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/expreccs/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/619946083.svg)](https://zenodo.org/badge/latestdoi/619946083)

# A Python framework for the ExpReCCS (Expansion of ResourCes for CO2 Storage on the Horda Platform) project

<img src="docs/text/figs/expreccs.gif" width="830" height="500">

This repository contains scripts to set up a workflow to run site and regional reservoirs for CO2 storage using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org) (current master branches)

You can install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/expreccs.git
# Get inside the folder
cd expreccs
# Create the virtual environment
python3 -m venv vexpreccs
# Activate the virtual environment
source vexpreccs/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the expreccs package (in editable mode for contributions/modifications; otherwise, pip install .)
pip install -e .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

If you are a Linux user (including the Windows subsystem for Linux), then you could try to build Flow from the master branches with mpi support, by running the script `./build_opm-flow_mpi.bash` (see the [_CI.yml_](https://github.com/cssr-tools/expreccs/blob/main/.github/workflows/CI.yml)), which in turn should build the executable in ./build/opm-simulators/bin/flow_gaswater_dissolution. 

For macOS users with the latest chips (M1/M2, guessing also M3?), the opm Python package is not available via pip install, while resdata might not be available depending on the Python version (e.g., it is not found using Python 3.9, but it is installed using Python 3.10). If you face this issue, then before installation, remove resdata and opm from the `requirements.txt`, then proceed with the Python requirements installation, install the OPM Flow dependencies (using macports or brew), and once inside the vexpreccs Python environment, run the `./build_opm-flow_macOS.bash`, and deactivate and activate the virtual environment (this script builds OPM Flow as well as the opm Python package, and it exports the required PYTHONPATH).

## Running expreccs
You can run _expreccs_ as a single command line:
```
expreccs -i some_input.txt -o some_output_folder
```
Run `expreccs --help` to see all possible command line argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the examples and tests/configs folders.

## Getting started
See the [_documentation_](https://cssr-tools.github.io/expreccs/introduction.html). 

## About expreccs
The expreccs package is funded by Wintershall Dea, Equinor, Shell, and the Research Council of Norway [project number 336294].
This is work in progress. [_Here_](https://www.norceresearch.no/en/projects/expansion-of-resources-for-co2-storage-on-the-horda-platform-expreccs) is the link to the project details.
Contributions are more than welcome using the fork and pull request approach.
