============
Introduction
============

.. image:: ./figs/introduction.gif
    :scale: 50%

This documentation describes the content of the **expreccs** package.
The numerical simulations are performed using the 
`OPM Flow <https://opm-project.org/?page_id=19>`_ simulator.

Concept
-------
Simplified and flexible testing framework for two-stage approach to improve regional and site simulations:

- Simulate the regional model (all timesteps).
- Identify connections on the regional model that corresponds to the boundary of the site model.
- Set the fluxes/pressures from the regional model as boundary conditions on the site model.
- Simulate the site model.

.. _overview:

Overview
--------
The current implementation supports the following executable with the argument options:

.. code-block:: bash

    expreccs -i input.txt -o output -m all -c '' -p 'no' -r resdata -u gaswater -t 0 -e ''

where 

- \-i: The base name of the :doc:`configuration file <./configuration_file>` ('input.txt' by default).
- \-o: The base name of the :doc:`output folder <./output_folder>` ('output' by default).
- \-m: Run the whole framework ('all'), only the reference ('reference'), only the site ('site'), or only regional and site models ('noreference') ('all' by default).
- \-c: Generate metric plots for the current outputed folders ('compare') ('' by default).
- \-p: Create nice figures in the postprocessing folder ('no' by default).
- \-r: Using the 'opm' or 'resdata' python package ('resdata' by default).
- \-u: Using 'gasoil' or 'gaswater' co2store implementation ('gaswater' by default).
- \-t: Grades to rotate the site geological model ('0' by default).
- \-e: Name of the regional and site folders to project pressures ('' by default).

In the **configuration file** the geological model is defined by generation
of corner-point grids (cpg), adding heterogeinities (e.g., different rock properties, faults), wells, and defining schedules for the
operations (see the :doc:`configuration file <./configuration_file>` section).