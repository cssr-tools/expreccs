********
Examples
********

Example 1
---------

We consider the configuration file 'example1.txt' in the 
examples folder (the animation in the `Github home page <https://github.com/cssr-tools/expreccs>`_ was based on this configuration file). 
If the results are to be saved in a folder called 'hello_world', this is achieved by the following command: 

.. code-block:: bash

    expreccs -i example1.txt -o hello_world 

Then we can change in line 14 the BC projections from the regional simulations from
'flux' to 'pres', and run the following command to only simulate the site model:

.. code-block:: bash

    expreccs -i example1_pres.txt -o hello_world -m site

We can do the same to add the pore volumes from the regional reservoir on the site boundaries by setting in line 14
'porvproj', and to also visualize the results in PNGs figures, we run the following command:

.. code-block:: bash

    expreccs -i example1_porvproj.txt -o hello_world -m site

Finally, we consider the case where we add injector/producers on the site boundary, and to also visualize the results 
in PNGs figures, we run the following command:

.. code-block:: bash

    expreccs -i example1_wells.txt -o hello_world -m site -p yes

Below are some of the figures generated inside the postprocessing folder:

.. figure:: figs/reference_watfluxi+.png
    :scale: 80%
.. figure:: figs/regional_watfluxi+.png
    :scale: 80%
.. figure:: figs/site_flux_watfluxi+.png
    :scale: 80%

    Final water flux (sm3/day) in the x direction for (top) the reference, (middle) regional, and 
    (bottom) site (with fluxes as BC). 

.. figure:: figs/sensor_pressure_over_time.png
.. figure:: figs/wells_pressure_site_reference.png
.. figure:: figs/distance_from_border.png
    
    Comparison of cell pressures on the sensor location (top), well BHPs (middle), and minimum
    distance from the CO2 plume to the site boundaries (bottom). 


Example 2
---------

The configuration file example2.txt set a more complex geological model with more grid cells (1 417 500). This was used
to generate the animation (using ResInsight) in the :doc:`introduction section <./introduction>` by running

.. code-block:: bash

    expreccs -i example2.txt -m reference
