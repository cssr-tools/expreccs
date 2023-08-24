[![Build Status](https://github.com/daavid00/expreccs/actions/workflows/CI.yml/badge.svg)](https://github.com/daavid00/expreccs/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Expansion of ResourCes for CO2 Storage on the Horda Platform (ExpReCCS)

<img src="docs/text/figs/expreccs.gif" width="830" height="500">

This repository contains scripts to set up a workflow to run site and regional reservoirs
for CO2 storage using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org)

For now you need to build OPM from source using the master branch (this since there have been updates for
the boundary conditions (BC) keywords, which will be available in the next OPM stable release 2023.10). 
You can run the script `./build_dune_and_opm-flow.bash`, which in turn should build flow in the folder 
./build/opm-simulators/bin/flow (this builds OPM without mpi support [for macOS users]; changue
the mpi cmake flags accordingly for mpi support).

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

## Running expreccs
You can run _expreccs_ as a single command line:
```
expreccs -i some_input.txt -o some_output_folder
```
Run `expreccs --help` to see all possible command line 
argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the examples
folders.

## Getting started
See the [_documentation_](https://daavid00.github.io/expreccs/introduction.html). 

## About expreccs
The expreccs package was funded by Wintershall Dea, Equinor, Shell, and the Research Council of Norway [project number 104908].
This is work in progress. [_Here_](https://www.norceresearch.no/en/projects/expansion-of-resources-for-co2-storage-on-the-horda-platform-expreccs) is the link to the project details.
Contributions are more than welcome using the fork and pull request approach.