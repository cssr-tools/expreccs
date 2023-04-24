********
Examples
********

In this example we consider the configuration file in the
:doc:`configuration file<./configuration_file>` section.

If the configuration file is saved as 'example.txt' and the generated files are to be
saved in a folder called 'results', then this is achieved by the following command:

.. code-block:: bash

    expreccs -i example.txt -o results

The execution time was less than a minute and the following are some of the generated figures:

.. figure:: figs/reference_saturation.png
.. figure:: figs/site_saturation.png
.. figure:: figs/distance_from_border.png

    Simulation results of the gas saturation (top) in the reference and (middle) site and (bottom)
    distance from the CO2 plume to the border.
