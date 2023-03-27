[![Build Status](https://github.com/daavid00/expreccs/actions/workflows/expreccs.yml/badge.svg)](https://github.com/daavid00/expreccs/actions/workflows/expreccs.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Expansion of ResourCes for CO2 Storage on the Horda Platform (ExpReCCS)

<img src="docs/text/figs/expreccs.gif" width="830" height="400">

This repository contains scripts to set up a workflow to run site and regional reservoirs
for CO2 storage using the [_OPM-Flow_](https://opm-project.org/?page_id=19) simulator.

## Installation
You will first need to install
* Flow (https://opm-project.org)

You can install the requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/daavid00/expreccs.git
# Get inside the folder
cd expreccs
# Create virtual environment
python3 -m venv vexpreccs
# Activate virtual environment
source vexpreccs/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the expreccs package
pip install .
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
