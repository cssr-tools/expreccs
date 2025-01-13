[![Build Status](https://github.com/cssr-tools/expreccs/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/expreccs/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20to%203.12-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/760077220.svg)](https://zenodo.org/doi/10.5281/zenodo.12100600)
<img src="docs/text/figs/expreccs.gif" width="830" height="500">

# expreccs: A Python framework using OPM Flow to simulate regional and site reservoirs for CO2 storage

## Main feature
Simplified and flexible software for two-stage approach (dynamic pressure boundary conditions) to improve CO2 storage regional and site simulations.

## Installation
You will first need to install
* Flow (https://opm-project.org, Release 2024.10 or current master branches)

To install the _expreccs_ executable in an existing Python environment: 

```bash
pip install git+https://github.com/cssr-tools/expreccs.git
```

If you are interested in a specific version (e.g., v2024.10) or in modifying the source code, then you can clone the repository and install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/expreccs.git
# Get inside the folder
cd expreccs
# For a specific version (e.g., v2024.10), or skip this step (i.e., edge version)
git checkout v2024.10
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

See the [_installation_](https://cssr-tools.github.io/exprecss/installation.html) for further details on installing binaries or building OPM Flow from the master branches in Linux, Windows, and macOS, as well as the opm Python package and LaTeX dependencies.

## Running expreccs
You can run _expreccs_ as a single command line:
```
expreccs -i name(s)_of_input_file(s)
```
Run `expreccs --help` to see all possible command line argument options. Inside the `configuration_file.txt` file you provide the path to the
flow executable and simulation parameters. To write dynamic boundary conditions from a given regional model to a site model, this can be achieved by giving the path to the models (i.e., without a configuration file). See the [_examples_](https://github.com/cssr-tools/expreccs/tree/main/examples) and [_tests_](https://github.com/cssr-tools/expreccs/tree/main/tests/configs) folders.

## Getting started
See the [_examples_](https://cssr-tools.github.io/expreccs/examples.html) in the [_documentation_](https://cssr-tools.github.io/expreccs/introduction.html).

## Citing
If you would like to cite this repository:

* Landa-Marbán, D. 2024. expreccs: A Python framework using OPM Flow to simulate regional and site reservoirs for CO2 storage. https://doi.org/10.5281/zenodo.12100600.

## Publications
The following is a list of manuscripts in which _expreccs_ is used:

1. Tveit, S., Gasda, S.E., Landa-Marbán, D., Sandve, T.H., submitted. A hierarchical approach for modeling regional pressure interference in multi-site CO2 operations. http://dx.doi.org/10.2139/ssrn.5005237.
1. Gasda, S.E., et al., 2024. Quantifying the impact of regional-scale pressure interference on commercial CO2 storage targets for multiple licenses. http://dx.doi.org/10.2139/ssrn.5053633.

## About expreccs
The _expreccs_ package is funded by Harbour Energy, Equinor, Shell, and the Research Council of Norway [project number 336294].
This is work in progress. [_Here_](https://www.norceresearch.no/en/projects/expansion-of-resources-for-co2-storage-on-the-horda-platform-expreccs) is the link to the project details.
Contributions are more than welcome using the fork and pull request approach. For new features, please request them raising an issue.
