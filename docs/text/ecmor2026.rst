*********
ECMOR2026
*********

Here we describe the steps to reproduce the results in:

* Landa-Marbán, D., Sandve, T.H., and Gasda, S.E. 2026. Improving pressure communication in coarsened aquifer models for CO2 storage via explicit non-net cell treatment. ECMOR 2026 (to appear by first week of September 2026).

To this end, we use mainly bash files, while Python scripts are used for more comprehensive tasks.

The core tools for the preprocessing and postprocessings are `pycopm <https://github.com/cssr-tools/pycopm>`_ and `plopm <https://github.com/cssr-tools/plopm>`_, which can be installed by:

.. code-block:: bash

    pip install git+https://github.com/cssr-tools/pycopm.git
    pip install git+https://github.com/cssr-tools/plopm.git

======
Method
======

Run `figure1.sh <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/method/figure1.sh>`_:

.. code-block:: bash

    . ./figure1.sh

.. note::

    PowerPoint is used to put all together the subfigures and add the colorful connections.

=======
Results
=======

2D synthetic model
------------------

Run `figure2.sh <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_2d_synthetic_model/figure2.sh>`_ and `figure3_table1.py <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_2d_synthetic_model/figure3_table1.py>`_:

.. code-block:: bash

    . ./figure2.sh
    python3 figure3_table1.py

.. note::

    PowerPoint is used to set the sensor, region, and well in Figure 2.

3D synthetic model
------------------

Run `figure4_table2.py <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_3d_synthetic_model/figure4_table2.py>`_:

.. code-block:: bash

    python3 figure4_table2.py

.. note::

    The graphics in Figure 4 are generated via screenshots using `ParaView <https://resinsight.org>`_.

Troll aquifer model
-------------------

To this end, the decks `MODEL.DATA <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/results/MODEL.DATA>`_ and
`FILLED_MODEL.DATA <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/results/FILLED_MODEL.DATA>`_ have the 
same dimensions and number of total cells (12,450,809) as the Troll aquifer model, and the rest of the properties are 
set to common homogeneous values from literature, while the well locations match the ones described in the ecmor2026 paper.
Then, you could contact the `Norwegian Offshore Directorate <https://www.sodir.no/en/>`_ to get the actual Troll aquifer model,
and adapt those files to the ones in the `results_troll folder <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/results>`_.
To get the FILLED_MODEL, using the petrel model provided by the Norwegian Offshore Directorate one can export the non-net cells IDs to FLUXNUM and set those
values to 0, then EQUALREG can be used to assign the PORO and PERMS in the non-net cells (see the `FILLED_MODEL.DATA <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/results/FILLED_MODEL.DATA>`_).

.. warning::

    You should not run the MODEL.DATA and FILLED_MODEL.DATA decks before adapting it with the actual Troll aquifer model, since they have a lot of active cells.

First, we generate the results by creating the dual models and running all simulations (`run_results.sh <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/run_results.sh>`_):

.. code-block:: bash

    . ./run_results.sh

Then, we can obtained Table 3 (`table3.py <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/table3.py>`_):

.. code-block:: bash

    python3 table3.py
 
Finally, we generate figures 5 to 9 (`figure5-9.sh <https://github.com/cssr-tools/expreccs/blob/main/publications/ecmor2026/results_troll/figure5-9.sh>`_):

.. code-block:: bash

    . ./figure5-9.sh

.. note::

    Figures 5c and 5d are generated via screenshots using `ResInsight <https://resinsight.org>`_. PowerPoint is used to set the wells in Figure 7 and to put 
    together Figure 9 (using the indiviudal generated Figures from plopm (figure9a.png, figure9b.png, and figure9c.png) and using the color bar from to_extract_colorbar_for_figure9.png).
