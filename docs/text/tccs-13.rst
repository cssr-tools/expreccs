*******
TCCS-13
*******

Here we describe the steps to reproduce the results in:

Landa-Marbán, D., Sandve, T.H., and Gasda, S.E. 2025. A Coarsening Approach to the Troll Aquifer Model. Submitted to SINTEF Proceedings. https://doi.org/10.13140/RG.2.2.24886.41283

To this end, the deck `ORIGINAL.DATA <https://github.com/cssr-tools/expreccs/blob/main/tccs-13/ORIGINAL.DATA>`_ has the 
same dimensions and number of total cells (12,450,809) as the Troll aquifer model, and the rest of the properties are 
set to common homogeneous values from literature, while the well locations match the ones described in the TCCS-13 paper.
Then, you could contact the `Norwegian Offshore Directorate <https://www.sodir.no/en/>`_ to get the actual Troll aquifer model,
and adapt those files to the ones in the `tccs-13 folder <https://github.com/cssr-tools/expreccs/blob/main/tccs-13/>`_.

.. warning::

    You should not run the ORIGINAL.DATA file before adapting it with the actual Troll aquifer model, since it has a lot of active cells.

For the first figures, `plopm <https://github.com/cssr-tools/plopm.git>`_ and `pycopm <https://github.com/cssr-tools/pycopm.git>`_ are used, which can be installed by:

.. code-block:: bash

    pip install git+https://github.com/cssr-tools/plopm.git
    pip install git+https://github.com/cssr-tools/pycopm.git

The following commands generate Figures 1 and 2 (a few features such as the transmissibilities, wells, and sensor are added using PowerPoint) using 
`FIG1.DATA <https://github.com/cssr-tools/expreccs/blob/main/tccs-13/methodology/FIG1.DATA>`_:

.. code-block:: bash

    pycopm -i FIG1.DATA -z 1:4 -m all -a max -w COARSENED_TRANS -l TRANS -t 2
    pycopm -i FIG1.DATA -c 1,1,4 -m all -a max -w COARSENED_PERMS -l PERMS
    flow FIG1.DATA
    flow COARSENED_TRANS.DATA
    flow COARSENED_PERMS.DATA
    plopm -i FIG1 -v poro -c '#bfebf2' -z 0 -grid 'black,1e0' -y '[5,-1]' -ylnum 5 -xlnum 7 -r 0 -remove 0,0,1,1 -d 24,16 -f 60 -save fig1
    plopm -i 'COARSENED_PERMS FIG1 COARSENED_TRANS' -v 'pressure - 0pressure' -subfigs 3,1 -r 1 -z 0 -delax 1 -y '[5,-1]' -cformat .0f -grid 'black,1e0' -cbsfax 0.1,0.95,0.8,0.02 -suptitle 0 -clabel 'Pressure increase [bar]' -cnum 5 -t 'Coarsened (permeabilities)  Before coarsening  Coarsened (transmissibilities)' -d 24,48 -f 80 -save fig2

For Figs. 3b, 5, 6, and 8, 9, and 10:

.. code-block:: bash

    flow ORIGINAL.DATA --enable-opm-rst-file=true --linear-solver=cpr_trueimpes --time-step-control=newtoniterationcount --newton-min-iterations=1 --tolerance-cnv-relaxed=1e-2 --relaxed-max-pv-fraction=0
    pycopm -i ORIGINAL.DATA -t 2 -a max -z 1:30,31:56,57:111,112:116,117:217 -w COARSENED -l C
    flow COARSENED.DATA --enable-opm-rst-file=true --linear-solver=cpr_trueimpes --time-step-control=newtoniterationcount --newton-min-iterations=1 --tolerance-cnv-relaxed=1e-2 --relaxed-max-pv-fraction=0
    plopm -i ORIGINAL -v 'depth * 0.001' -s ,,1:217 -how min -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -clabel 'Depth [km]' -cnum 5 -cformat .2f -c managua_r -save fig3b
    plopm -i 'ORIGINAL ORIGINAL ORIGINAL' -v 'porv' -s ',,1:30 ,,57:111 ,,117:217' -r 0 -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -subfigs 1,3 -d 24,12 -cbsfax 0.1,0.95,0.8,0.02 -cformat .1f -f 24 -cnum 5 -suptitle 0 -clabel 'Total pore volume [m$^3$]' -log 1 -c brg -t 'Cook  Johansen  Statfjord' -delax 1 -save fig5
    plopm -i 'ORIGINAL' -v 'faults' -s ',,1:217' -r 0 -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -f 8 -global 1 -t 'Total no. faults = 65' -save fig6a
    plopm -i 'ORIGINAL' -v 'faults' -s ',,30:117' -r 0 -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -f 8 -how max -t 'Cook-Johansen-Statfjord' -remove 1,0,0,0 -save fig6b
    plopm -i 'ORIGINAL ORIGINAL ORIGINAL' -v 'pressure - 0pressure' -s ',,1:30 ,,57:111 ,,117:217' -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -subfigs 1,3 -d  24,12 -cbsfax 0.1,0.95,0.8,0.02 -f 24 -cnum 5 -suptitle 0 -clabel 'Pore-volume-weighted-average pressure increase [bar]' -delax 1 -r 25 -b '[0,80]' -t 'Cook, t=25 years  Johansen, t=25 years  Statfjord, t=25 years' -b '[0,80]' -save fig8upper
    plopm -i 'ORIGINAL ORIGINAL ORIGINAL' -v 'pressure - 0pressure' -s ',,1:30 ,,57:111 ,,117:217' -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -subfigs 1,3 -d  24,12 -cbsfax 0.1,0.95,0.8,0.02 -f 24 -cnum 5 -suptitle 0 -clabel 'Pore-volume-weighted-average pressure increase [bar]' -delax 1 -r 30 -b '[0,80]' -t 'Cook, t=525 years  Johansen, t=525 years  Statfjord, t=525 years' -b '[0,80]' -save fig8lower
    plopm -i 'ORIGINAL ORIGINAL ORIGINAL' -v 'limipres' -s ',,1:30 ,,57:111 ,,117:217' -r 0 -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -subfigs 1,3 -d 24,12 -cbsfax 0.1,0.95,0.8,0.02 -cformat .1f -f 24 -cnum 5 -suptitle 0 -clabel 'Maximum allowable pressure increase limit [bar]' -c gnuplot2 -t 'Cook  Johansen  Statfjord' -delax 1 -save fig9
    plopm -i 'ORIGINAL' -v 'imbnum' -s ',,1:217' -r 0 -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -remove 0,0,1,1 -c '203;203;203' -save fig10a
    plopm -i 'ORIGINAL COARSENED' -v 'overpres' -s ',,1:217 ,,1:5' -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -subfigs 1,2 -d 16,12 -cbsfax 0.1,0.95,0.8,0.02 -f 24 -cnum 5 -suptitle 0 -clabel 'Overpressure (p - p$_{lim}$) [bar], t=25 years' -delax 1 -remove 1,0,0,0 -t 'Troll aquifer model  Coarsened version' -b '[-126.7,-1.1]' -c cet_diverging_rainbow_bgymr_45_85_c67 -save fig10bc

Figs. 4 and 7 are generated using `ResInsight <https://resinsight.org>`_. To run the optimization, `Everest <https://github.com/equinor/everest>`_ is needed. Since it has been merged to 
`ERT <https://github.com/equinor/ert>`_, it seems there are some issues using it via ERT. Then, the walk around is to use the version before merging. One way to get this installed is to
create a new virtual environment (to avoid version conflicts) and execute:

.. code-block:: bash

    pip install ert==11.0.8
    pip install git+https://github.com/equinor/everest.git
    pip install mako

Once installed, then you could adapt the coarsened generated files in the `coarsened folder <https://github.com/cssr-tools/expreccs/blob/main/tccs-13/coarsened/>`_ to run the optimization:

.. code-block:: bash

    everest run coarsened.yml

.. note::

    You might need to adapt the number of cores and mpirun depending on your resources, i.e., the current file is set to use mpirun -np 5 flow ... and 14 cores in parallel.

After the study, to generate Fig. 11, execute the `postprocessing.py file <https://github.com/cssr-tools/expreccs/blob/main/tccs-13/postprocessing.py>`_:

.. code-block:: bash

    python3 postprocessing.py

Finally, you can look at the improved well locations in the generated figures/optimal_solution folder, and take those locations in the ORGININAL.DATA deck 
and save it as IMPROVED.DATA, similar to the coarsened version to COARSENED_IMPROVED.DATA, to generate Fig. 12:

.. code-block:: bash
    
    flow IMPROVED.DATA --enable-opm-rst-file=true --linear-solver=cpr_trueimpes --time-step-control=newtoniterationcount --newton-min-iterations=1 --tolerance-cnv-relaxed=1e-2 --relaxed-max-pv-fraction=0
    flow COARSENED_IMPROVED.DATA --enable-opm-rst-file=true --linear-solver=cpr_trueimpes --time-step-control=newtoniterationcount --newton-min-iterations=1 --tolerance-cnv-relaxed=1e-2 --relaxed-max-pv-fraction=0
    plopm -i 'IMPROVED' -v 'imbnum' -s ',,1:217' -r 0 -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -remove 0,0,1,1 -c '203;203;203' -save fig12a
    plopm -i 'IMPROVED COARSENED_IMPROVED' -v 'overpres' -s ',,1:217 ,,1:5' -translate '[-495000,-6.605e6]' -x '[0,95000]' -xunits km -xlnum 2 -y '[0,160000]' -yunits km -yformat .0f -ylnum 2 -xformat .0f -subfigs 1,2 -d 16,12 -cbsfax 0.1,0.95,0.8,0.02 -f 24 -cnum 5 -suptitle 0 -clabel 'Overpressure (p - p$_{lim}$) [bar], t=25 years' -delax 1 -remove 1,0,0,0 -t 'Troll aquifer model  Coarsened version' -b '[-126.7,-1.1]' -c cet_diverging_rainbow_bgymr_45_85_c67 -save fig10bc