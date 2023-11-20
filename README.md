[![Build Status](https://github.com/daavid00/expreccs/actions/workflows/CI.yml/badge.svg)](https://github.com/daavid00/expreccs/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/619946083.svg)](https://zenodo.org/badge/latestdoi/619946083)

# A Python framework for the ExpReCCS (Expansion of ResourCes for CO2 Storage on the Horda Platform) project

<img src="docs/text/figs/expreccs.gif" width="830" height="500">

This repository contains scripts to set up a workflow to run site and regional reservoirs for CO2 storage using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org)

You can install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/daavid00/expreccs.git
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

To build dune and the corresponding OPM master branches from source (e.g., you are a macOS user), you can run the script
`./build_dune_and_opm-flow.bash`, which in turn should build flow in the folder ./build/opm-simulators/bin/flow (for macOS users the dependecies such as boost can be installed using macports).
If you are a Linux user (including the windows subsystem for Linux), then you could try to build Flow with mpi support,
by running the script `./build_opm-flow_mpi.bash` instead of `./build_dune_and_opm-flow.bash`.

For macOS users with the latest chips (M1/M2, guessing also M3?), the ecl and opm packages are not available via pip install. Then before installation, remove ecl and opm from the requierements.txt, then proceed with the Python requirements installation, and  once inside the vexpreccs Python environment, add the flag `-DPYTHON_EXECUTABLE=/Users/dmar/expreccs/vexpreccs/bin/python` (by typing `which  python` in the terminal you get your path) to the cmake (lines 24 in the bash scripts), build flow by running the bash script, and finally, add to the python path the folder where you have built it, e.g., by opening in an editor the vexpreccs/bin/activate script, pasting the following line (edited with the path where you built opm with Python) 
`export PYTHONPATH=$PYTHONPATH:/Users/dmar/expreccs/build/opm-common/build/python` at the end of the script, and deactivating and activating the virtual environment.

## Running expreccs
You can run _expreccs_ as a single command line:
```
expreccs -i some_input.txt -o some_output_folder
```
Run `expreccs --help` to see all possible command line argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the examples and tests/configs folders.

## Getting started
See the [_documentation_](https://daavid00.github.io/expreccs/introduction.html). 

## About expreccs
The expreccs package is funded by Wintershall Dea, Equinor, Shell, and the Research Council of Norway [project number 336294].
This is work in progress. [_Here_](https://www.norceresearch.no/en/projects/expansion-of-resources-for-co2-storage-on-the-horda-platform-expreccs) is the link to the project details.
Contributions are more than welcome using the fork and pull request approach.
