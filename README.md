[![Build Status](https://github.com/cssr-tools/expreccs/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/expreccs/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20to%203.12-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/760077220.svg)](https://zenodo.org/doi/10.5281/zenodo.12100600)

# A Python framework for the ExpReCCS (Expansion of ResourCes for CO2 Storage on the Horda Platform) project

<img src="docs/text/figs/expreccs.gif" width="830" height="500">

This repository contains scripts to set up a workflow to run site and regional reservoirs for CO2 storage using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org, Release 2024.04 or current master branches)

To install the _expreccs_ executable in an existing Python environment: 

```bash
pip install git+https://github.com/cssr-tools/expreccs.git
```

If you are interested in modifying the source code, then you can clone the repository and install the Python requirements in a virtual environment with the following commands:

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
# Install the expreccs package
pip install -e .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

See the [_installation_](https://cssr-tools.github.io/exprecss/installation.html) for further details on building OPM Flow from the master branches in Linux, Windows, and macOS, as well as the opm Python package.

## Running expreccs
You can run _expreccs_ as a single command line:
```
expreccs -i some_input.txt -o some_output_folder
```
Run `expreccs --help` to see all possible command line argument options. Inside the `some_input.txt` file you provide the path to the
flow executable and simulation parameters. See the .txt files in the [_examples_](https://github.com/cssr-tools/expreccs/tree/main/examples) and [_tests_](https://github.com/cssr-tools/expreccs/tree/main/tests/configs) folders.

## Getting started
See the [_examples_](https://cssr-tools.github.io/expreccs/examples.html) in the [_documentation_](https://cssr-tools.github.io/expreccs/introduction.html). 

## About expreccs
The expreccs package is funded by Wintershall Dea, Equinor, Shell, and the Research Council of Norway [project number 336294].
This is work in progress. [_Here_](https://www.norceresearch.no/en/projects/expansion-of-resources-for-co2-storage-on-the-horda-platform-expreccs) is the link to the project details.
Contributions are more than welcome using the fork and pull request approach.
