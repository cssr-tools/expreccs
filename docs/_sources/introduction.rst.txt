============
Introduction
============

.. image:: ./figs/introduction.gif
    :scale: 50%

This documentation describes the content of the **expreccs** package.
The numerical simulations are performed using the 
`Flow <https://opm-project.org/?page_id=19>`_ simulator.

Concept
-------
Simplified and flexible testing framework for two-stage approach to improve regional and site simulations:

- Simulate the regional model (all timesteps).
- Identify connections on the regional model that corresponds to the boundary of the site model.
- Set the fluxes/pressures from the regional model as boundary conditions on the site model.
- Simulate the site model.

Overview
--------
The current implementation supports the following executable with the argument options:

.. code-block:: bash

    expreccs -i input.txt -o output -m all -c '' -p 'yes' -r opm

where 

- \-i, \-input: The base name of the :doc:`configuration file <./configuration_file>` ('input.txt' by default).
- \-o, \-output: The base name of the :doc:`output folder <./output_folder>` ('output' by default).
- \-m, \-mode: Run the whole framework ('all'), only the reference ('reference'), only the site ('site'), or only regional and site models ('noreference') ('all' by default).
- \-c, \-compare: Generate metric plots for the current outputed folders ('compare') (' ' by default).
- \-p, \-plot: Create nice figures in the postprocessing folder ('no' by default).
- \-r, \-reading: Using the 'opm' or 'ecl' python package ('opm' by default).

In the **configuration file** the geological model is defined by generation
of corner-point grids (cpg), adding heterogeinities (e.g., different rock properties, faults), wells, and defining schedules for the
operations (see the :doc:`configuration file <./configuration_file>` section). 

Installation
------------

See the `Github page <https://github.com/daavid00/expreccs>`_.

.. tip::
    Check the `CI.yml <https://github.com/daavid00/expreccs/blob/main/.github/workflows/CI.yml>`_ file.