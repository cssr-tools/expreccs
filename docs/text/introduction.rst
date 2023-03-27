============
Introduction
============

This documentation describes the content of the **expreccs** package.
The numerical simulations for the CO2 are performed using the 
`Flow <https://opm-project.org/?page_id=19>`_ simulator. This framework could be ('easily') 
extended to consider additional available models in OPM.

Overview
--------

The current implementation supports the following executable with the argument options:

.. code-block:: bash

    expreccs -i input.txt -o output

where 

- \-i, \-input: The base name of the :doc:`configuration file <./configuration_file>` ('input.txt' by default).
- \-o, \-output: The base name of the :doc:`output folder <./output_folder>` ('output' by default).

Installation
------------

See the `Github page <https://github.com/daavid00/expreccs>`_.