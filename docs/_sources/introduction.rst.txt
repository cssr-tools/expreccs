============
Introduction
============

.. image:: ./figs/introduction.gif
    :scale: 50%

This documentation describes the content of the **expreccs** package.
The numerical simulations for the CO2 are performed using the 
`Flow <https://opm-project.org/?page_id=19>`_ simulator.

Concept
-------
Simplified and flexible testing framework for two-stage approach to improve regional (purple+blue regions)/site (blue region) simulations:

- Simulate the regional model (all timesteps).
- Identify connections on the regional model that corresponds to the boundary of the site model.
- Set the fluxes/pressures from the regional model as boundary conditions on the site model.
- Simulate the site model

Overview
--------

The current implementation supports the following executable with the argument options:

.. code-block:: bash

    expreccs -i input.txt -o output -m all

where 

- \-i, \-input: The base name of the :doc:`configuration file <./configuration_file>` ('input.txt' by default).
- \-o, \-output: The base name of the :doc:`output folder <./output_folder>` ('output' by default).
- \-m, \-mode: Run the whole framework ('all') or only the regional and site models ('notall') ('all' by default).

Installation
------------

See the `Github page <https://github.com/daavid00/expreccs>`_.

.. tip::
    Check the `expreccs.yml <https://github.com/daavid00/expreccs/blob/main/.github/workflows/expreccs.yml>`_ file.