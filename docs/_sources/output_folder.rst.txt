=============
Output folder
=============

The following screenshot shows the generated files in the selected output folder after 
executing **expreccs**.

.. figure:: figs/output.png

    Generated files after executing **expreccs**.

The simulation results are saved in the output folder, and
`ResInsight <https://resinsight.org>`_ can be used for the visualization.
Then after running **expreccs**, one could modify the generated OPM related files and 
run directly the simulations calling the Flow solvers, e.g., to add tracers 
(see the OPM Flow documentation `here <https://opm-project.org/?page_id=955>`_).
In addition, some plots comparing the site simulations to the reference 
and the site with open boundaries are generated in the postprocessing folder. Then the
**plotting.py** script in the src/expreccs/visualization folder can be modified/extended
to consider additional metrics.