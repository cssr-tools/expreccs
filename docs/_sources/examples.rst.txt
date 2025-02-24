********
Examples
********

=======================
Via configuration files
=======================

Hello world
-----------

We consider the configuration file `example1.toml <https://github.com/cssr-tools/expreccs/blob/main/examples/example1.toml>`_ in the 
examples folder (the animation in the `GitHub home page <https://github.com/cssr-tools/expreccs>`_ was based on this configuration file). 
If the results are to be saved in a folder called 'hello_world', this is achieved by the following command: 

.. code-block:: bash

    expreccs -i example1.toml -o hello_world

Then we can change in line 25 the BC type for the site from
'flux' to 'pres', and run the following command to only simulate the site model:

.. code-block:: bash

    expreccs -i example1_pres.toml -o hello_world -m site

We can do the same to add the pore volumes from the regional reservoir on the site boundaries by setting in line 25
'porvproj':

.. code-block:: bash

    expreccs -i example1_porvproj.toml -o hello_world -m site

Finally, we consider the case where we add injector/producers on the site boundary, and to also visualize the results 
in PNGs figures, we run the following command:

.. code-block:: bash

    expreccs -i example1_wells.toml -o hello_world -m site -p yes

Below are some of the figures generated inside the postprocessing folder:

.. figure:: figs/hello_world_reference_watfluxi+.png
    :scale: 80%
.. figure:: figs/hello_world_regional_watfluxi+.png
    :scale: 80%
.. figure:: figs/hello_world_site_flux_watfluxi+.png
    :scale: 80%

    Final water velocity (m/day) in the x direction for (top) the reference, (middle) regional, and 
    (bottom) site (with fluxes as BC). The figure names in the postprocessing folder are hello_world_reference_watfluxi+.png,
    hello_world_regional_watfluxi+.png, and hello_world_site_flux_watfluxi+.png respectively. 

.. figure:: figs/hello_world_sensor_pressure_over_time.png
.. figure:: figs/hello_world_summary_BHP_site_reference.png
.. figure:: figs/hello_world_distance_from_border.png
    
    Comparison of cell pressures on the sensor location (top), well BHPs (middle), and minimum
    distance from the CO2 plume to the site boundaries (bottom). The figure names in the postprocessing folder are 
    hello_world_sensor_pressure_over_time.png, hello_world_summary_BHP_site_reference.png, and 
    hello_world_distance_from_border.png respectively


Layered model 
-------------

The configuration file example2.toml set a more complex geological model with more grid cells (1 417 500). This was used
to generate the animation (using ResInsight) in the :doc:`introduction section <./introduction>` by running

.. code-block:: bash

    expreccs -i example2.toml -m reference

.. tip::

    This example shows how **expreccs** can be used to generate the requiered input files to run OPM Flow for heterogenous
    layered models at different grid sizes, which can be used for further studies such as optimization. Regarding the configuration 
    files in `examples/paper_2025 <https://github.com/cssr-tools/expreccs/tree/main/examples/paper_2025>`_, these are explained in 
    `this manuscript <https://doi.org/10.1016/j.geoen.2025.213733>`_.

.. _back_coupling:

Back-coupling (under development)
---------------------------------

We consider the configuration file `example1_back.toml <https://github.com/cssr-tools/expreccs/blob/main/examples/example1_back.toml>`_ in the examples folder.
The plan is to update properties (e.g., transmissibility multipliers) in the regional model from features (e.g., faults) in the site model (i.e., not included in the regional model).
By running:

.. code-block:: bash

    expreccs -i example1_back.toml -o back-coupling -m all -p yes

This is one of the generated figures in the back-coupling/postprocessing folder (named as back-coupling_summary_BPR_regional_reference.png):

.. image:: ./figs/back-coupling_summary_BPR_regional_reference.png

The figures in the postprocessing includes the results for the first two iterations and the last one (in this case 9 since the number of 
iteration is set to 10 in the `configuration_file <https://github.com/cssr-tools/expreccs/blob/main/examples/example1_back.toml>`_, "iterations = 10" in line 20).

For example, to show the difference in the spatial maps for pressure between iteration 4 and 7 at the third restart, this can be achieved using 
`plopm <https://github.com/cssr-tools/plopm>`_ by executing:

.. code-block:: bash

    plopm -i back-coupling/output/regional_7/regional_7 -diff back-coupling/output/regional_4/regional_4 -v pressure -r 3 -s ,,1 -c rainbow -cformat .2f -d 5,5

.. image:: ./figs/pressure_plopm.png

and to show the comparison for the summary vector FPR for iterations 1, 5, 7, and 9:

.. code-block:: bash

    plopm -i 'back-coupling/output/regional_1/regional_1 back-coupling/output/regional_5/regional_5 back-coupling/output/regional_7/regional_7 back-coupling/output/regional_9/regional_9' -v fpr -d 5,5 -f 10

.. image:: ./figs/fpr_plopm.png

.. tip::
    You can install `plopm <https://github.com/cssr-tools/plopm>`_ by executing in the terminal: **pip install git+https://github.com/cssr-tools/plopm.git**.

.. _generic:

==================
Via OPM Flow decks 
==================

See/run the `test_2_generic_deck.py <https://github.com/cssr-tools/expreccs/blob/main/tests/test_2_generic_deck.py>`_ 
for an example where **expreccs** is used in two given models (regional and site, in this case they are created using
the **expreccs** package, but in general can be any given geological models), generating a new input deck where
the pressures are projected.

.. code-block:: bash

    expreccs -i 'path_to_the_regional_model path_to_the_site_model'

In the current implementation, the name of the decks need to match the name of the given folder (e.g., regional/REGIONAL.DATA).
For example, to run the test, this can be achieved by executing:

.. code-block:: bash

    pytest --cov=expreccs --cov-report term-missing tests/test_2_generic_deck.py

To visualize/compare results between the model with static (input) and dynamic (generated by expreccs) boundary conditions, 
we can use our friend `plopm <https://github.com/cssr-tools/plopm>`_: 

.. code-block:: bash

    plopm -i 'tests/configs/rotate/output/site_closed/SITE_CLOSED tests/configs/rotate/output/expreccs/EXPRECCS tests/configs/rotate/output/reference/REFERENCE' -v sgas -s ',,1 ,,1 ,,1' -subfigs 1,3 -suptitle 0 -cbsfax 0.2,0.95,0.6,0.02 -d 24,8 -cformat .1f -f 20 -xunits km -yunits km -xformat .0f -yformat .0f -x '[0,15000]' -y '[0,15000]' -delax 1

.. figure:: figs/reference_sgas.png
    
    Comparison of the gas saturation on the top cells at the end of the simulations.