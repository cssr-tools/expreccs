==================
Configuration file
==================
We consider the configuration file (`input.txt <https://github.com/cssr-tools/expreccs/blob/main/examples/input.txt>`_) available in the 
examples folder. The parameters are chosen to show the functionality and capabilities of the **expreccs** framework regarding generation
of corner-point grids (cpg), heterogeinities (e.g., different rock properties, faults), adding wells, and defining schedules for the
operations. See the `example1.txt <https://github.com/cssr-tools/expreccs/blob/main/examples/example1.txt>`_ for a simpler configuration
file. 

The first input parameter in the configuration file is:

.. code-block:: python
    :linenos:

    """Set the full path to the flow executable and flags"""
    flow --enable-opm-rst-file=true  --linear-solver=cprw --enable-tuning=true  

If **flow** is not in your path, then write the full path to the executable
(e.g., /Users/dmar/expreccs/build/opm-simulators/bin/flow). We also add in the same 
line as many flags as required (see the OPM Flow documentation `here <https://opm-project.org/?page_id=955>`_).

.. note::
    If you have installed flow with MPI support, then you can run the simulations in
    parallel by adding **mpirun -np N flow ...** where N is the number of cpus.

****************************
Reservoir-related parameters
****************************

The following input lines are:

.. code-block:: python
    :linenos:
    :lineno-start: 4

    """Set the model parameters"""
    45000 15000 81              #Reginonal aquifer length, width, and depth [m]
    3,5,5                       #Variable array of x-refinment (Regional)
    5,5,5                       #Variable array of y-refinment (Regional)
    1,1,1                       #Variable array of z-refinment (Regional)
    1,1,1,5,5,15,15,15,15,15,5,5,5,5,5 #Variable array of x-refinment (Reference)
    25,25,25                    #Variable array of y-refinment (Reference)
    6,5,5,5,3,3,3,3,3           #Variable array of z-refinment (Reference)
    18000 5000 27000 10000      #Site xi, yi, xf, and yf box positions [m]
    free                        #Use free/closed/porv for the Regional aquifer (if porv, enter the bottom, right, top, and left values (e.g, porv 1e8 1e7 1e6 1e5))
    free                        #Use free/closed/porv/porvproj/flux/pres/pres2p/wells for the BC site (if porv; bottom, right, top, and left values (e.g, porv 1e4 1e3 1e2 1e1)); for pres/flux, add 'interp' to use linear interpolation in time
    10000 11000 0.01 10 22.5    #Regional fault x, and y positions [m], x and y multipliers for the trans, and height of the fault jump [m]
    21583 5710 24081 8233 0.0 0.0 #Site fault x, and y positions [m] (initial and final) and x and y multipliers for the trans
    9,9,9,9,9,9,9,9,9           #Thicknes of the layers 
    2E7 60 50 6.11423e-10       #Pressure on the reservoir top [Pa], top and bottom temperatures [C], and rock compressibility [1/Pa]
    20000 8000 0                #Sensor position x, y, and z to assess the error over time w.r.t the reference solution [m]
    (20-20*mt.sin((2*mt.pi*(x+y)/10000))) #The function for the reservoir surface
    1 2.92                      #Add hysteresis (1/0) and salinity (value [1E-3 kg-M/kg])
    0                           #Number of interations for back-coupling.

Here we first set the dimensions of the regional model and the grid size for the discretization,
where the origen is located in the left bottom corner. Then the site model is defined by giving the coordinates
of the box. On lines 13 and 14 we define the BC for the regional and site models, where flux/press in the site model 
projects the fluxes/pressures from the regional simulations, porvproj adds copmputed pore volumes from the regional
reservoir, and wells add 4 injectors and 4 producers on the middle points on the site boundaries. The following line defines a fault along the z-direction in 
the regional model. Similarly it is possible to define a fault in the site model, which extends from the given initial 
location and continues in zig-zag until the given final location. Finally, we set the thicknes of the layers along the z direction, 
which allows to consider different rock and saturation function properties, as well as the reservoir conditions (pressure, temperature, and rock compressibility), 
the location of a point of interest to compare results, and the z position of the tops cells as a function of the (x,y) location. The hysteresis option activates the
Killough hysteresis model on the gas relative permeability.

.. note::
    The functionality for back-coupling in line 22 is under development, see/run `back-coupling.txt <https://github.com/cssr-tools/expreccs/blob/main/tests/configs/back-coupling.txt>`_ 
    if you are curious.

.. figure:: figs/grids.png

    The site location in the regional model (upper left), the fault in the site model (upper right), the number of rock for the different properties
    in the regional (lower left) and reference (lower right) models. We observe that for the regional model the closest
    rock properties are kept in the coarser cell. 


***********************
Rock-related parameters
***********************
The following entries define the rock related parameters:

.. code-block:: python
    :linenos:
    :lineno-start: 24

    """Set the saturation functions"""
    krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
    krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
    pec * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npe))        #Capillary pressure saturation function [Pa]  

In this example we consider properties for the sands number 1 to 5 as described in the 
`11th SPE CSP <https://www.spe.org/en/csp/>`_:

.. code-block:: python
    :linenos:
    :lineno-start: 29

    """Properties sat functions"""
    """swi [-], sni [-], krw [-], krn [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation"""
    SWI5 0.12 SNI5 0.10 KRW5 1. KRN5 1. PRE4 3060.00 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI4 0.12 SNI4 0.10 KRW4 1. KRN4 1. PRE4 3870.63 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI5 0.12 SNI5 0.10 KRW5 1. KRN5 1. PRE5 3060.00 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI4 0.12 SNI4 0.10 KRW4 1. KRN4 1. PRE4 3870.63 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI1 0.32 SNI1 0.10 KRW1 1. KRN1 1. PRE1 193531. NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI2 0.14 SNI2 0.10 KRW2 1. KRN2 1. PRE2 8654.99 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI3 0.12 SNI3 0.10 KRW3 1. KRN3 1. PRE3 6120.00 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI2 0.14 SNI2 0.10 KRW2 1. KRN2 1. PRE2 8654.99 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI3 0.12 SNI3 0.10 KRW3 1. KRN3 1. PRE3 6120.00 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4
    SWI5 0.12 SNI5 0.30 KRW5 1. KRN5 1. PRE4 3060.00 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI4 0.12 SNI4 0.30 KRW4 1. KRN4 1. PRE4 3870.63 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI5 0.12 SNI5 0.30 KRW5 1. KRN5 1. PRE5 3060.00 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI4 0.12 SNI4 0.30 KRW4 1. KRN4 1. PRE4 3870.63 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI1 0.32 SNI1 0.30 KRW1 1. KRN1 1. PRE1 193531. NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI2 0.14 SNI2 0.30 KRW2 1. KRN2 1. PRE2 8654.99 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI3 0.12 SNI3 0.30 KRW3 1. KRN3 1. PRE3 6120.00 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI2 0.14 SNI2 0.30 KRW2 1. KRN2 1. PRE2 8654.99 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4
    SWI3 0.12 SNI3 0.30 KRW3 1. KRN3 1. PRE3 6120.00 NKRW1 2 NKRN1 4 NPE1 2 THRE1 1e-4

.. note::
    Since hysteresis is activated (line 21), then we add the values for the imbibition curves (lines 39 to 47),
    where in this example the residual saturations are changed to 0.3 and the exponent to 4.

Simillarly for the rock properties:

.. code-block:: python
    :linenos:
    :lineno-start: 50

    """Properties rock"""
    """Kxy [mD], Kz [mD], phi [-]"""
    PERMXY5 1013.25 PERMZ5 101.325 PORO5 0.25
    PERMXY4 506.625 PERMZ4 50.6625 PORO4 0.20
    PERMXY5 1013.25 PERMZ5 101.325 PORO5 0.25
    PERMXY4 506.625 PERMZ4 50.6625 PORO4 0.20
    PERMXY1 0.10132 PERMZ1 .010132 PORO1 0.10
    PERMXY2 101.324 PERMZ2 10.1324 PORO2 0.20
    PERMXY3 202.650 PERMZ3 20.2650 PORO3 0.20
    PERMXY2 101.324 PERMZ2 10.1324 PORO2 0.20
    PERMXY3 202.650 PERMZ3 20.2650 PORO3 0.20

As seen from the previous values, the finnest rock corresponds to No. 1 and it gets coarser
towards rock No. 5.

.. note::
    The names for the saturation functions and rock properties are not used in the framework (they are used to
    ease the visualization of the parameter values in the configuration file, i.e., writing PERMABC in line 51 has 
    no impact, so far the name has at least one character since this is used in the reading of the values).

***********************
Well-related parameters
***********************

Now we proceed to define the location of the wells:

.. code-block:: python
    :linenos:
    :lineno-start: 62

    """Wells position"""
    """x, y, zi, and zf positions [m]"""
    21180 7068  0 81 #Well 0 
    24200 7800 15 65 #Well 1
    21718 7122 45 81 #Well 2
    14518 11377 0 50 #Well 3 
    31679 8883  0 30 #Well 4
    28477 2732  0 81 #Well 5

The implementation allows to add as many wells as desired in the site and regional model.

.. figure:: figs/wells.png

    The location of the wells in the regional, site, and reference models. We observe that for the regional model
    wells 0 and 2 share the same cells along the z-direction. 

The injection rates are given in the following entries:

.. code-block:: python
    :linenos:
    :lineno-start: 71

    """Define the injection values""" 
    """injection time [d], time step size to write results regional [d], time step size to write results site/reference [d], maximum time step [d], fluid (0 wetting, 1 non-wetting) well 0, injection rates [kg/day] well 0, fluid ... well n, injection, ...well n, (if 'wells' for BC in site (Line 14); bottom, right, top, and left values (0(prod)/1(inj), pressure [Pa]))"""
    365. 73. 73. 73. 1 3e5 1 3e5 1 3e5 1 5e6 1 5e6 0 1e7 
    365. 73. 73. 73. 1 3e5 1 3e5 1 3e5 1 5e6 1   0 0 1e7

Since we defined six wells (three of them inside the site model), then each row of the schedule has 16 entries, corresponding to
the first three defining the injection time, number of restart files in the solution for the regional, number of restart files in the solution for the site/reference, and maximum solver time step, and 2*6 additional 
entries to define injected fluid (0 water, 1 CO2) and the injection rates from well 0 to well 5 respectively. If in line 14 the wells
option is activated, then at the end of each row we add the values from the wells (BHP control) on the boundaries in the order of bottom, right, top,
and left with two values respectively (0 for producers and 1 for injectors, and the BHP in Pascals, see `example1_wells.txt <https://github.com/cssr-tools/expreccs/blob/main/examples/example1_wells.txt>`_). 

.. warning::
    Keep the linebreak between the sections in the whole configuration file and do not add linebreaks inside the sections
    (in the current implementation this is used for the reading of the parameters).

******************
Simulation results
******************
Since the configuration file's name is input.txt, then it can be run by the following command:

.. code-block:: bash

    expreccs

the following is a screenshot using ResInsight to visualize the pressure and gas saturation at the end of the simulation:

.. figure:: figs/confile.png

    Then the approach is to project the fluxes/presures on the site boundaries from the regional simulations instead of
    using free flow as in this example.  

See the :doc:`examples <./examples>` section for further examples of configuration files and argument options for **expreccs**.
