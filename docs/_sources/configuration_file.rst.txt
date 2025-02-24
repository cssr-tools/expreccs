==================
Configuration file
==================
.. Note::
    The configuration files allow to set the integrated studies (generation of regional and site models,
    in addition to set the different boundary projection approaches). To use **expreccs** in any given two OPM Flow geological models
    to dynamically project pressures, this can be achieve without a configuration file, but setting
    the parameters via command lines (see the :ref:`overview` or run `pycopm -h` for the definition 
    of the argument options, as well as the example in :ref:`generic`).

We consider the configuration file (`input.toml <https://github.com/cssr-tools/expreccs/blob/main/examples/input.toml>`_) available in the 
examples folder. The parameters are chosen to show the functionality and capabilities of the **expreccs** framework regarding generation
of corner-point grids (cpg), heterogeinities (e.g., different rock properties, faults, hysteresis), adding wells, and defining schedules for the
operations. See the `example1.toml <https://github.com/cssr-tools/expreccs/blob/main/examples/example1.toml>`_ for a simpler configuration
file. 

The first input parameter in the configuration file is:

.. code-block:: python
    :linenos:

    # Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
    flow = "flow --relaxed-max-pv-fraction=0 --enable-opm-rst-file=true --newton-min-iterations=1 --enable-tuning=true"

If **flow** is not in your path, then write the full path to the executable, as well as adding mpirun if this is supported in your machine 
(e.g., mpirun -np 8 /Users/dmar/expreccs/build/opm-simulators/bin/flow). We also add in the same 
line as many flags as required (see the OPM Flow documentation `here <https://opm-project.org/?page_id=955>`_).

****************************
Reservoir-related parameters
****************************

The following input lines are:

.. code-block:: python
    :linenos:
    :lineno-start: 4

    # Set the model parameters
    regional_dims = [45000,15000,81] # Regional aquifer length, width, and depth [m]
    regional_x_n = [3,5,5] # Variable array of x-refinement (Regional)
    regional_y_n = [5,5,5] # Variable array of y-refinement (Regional)
    regional_z_n = [1,1,1] # Variable array of z-refinement (Regional)
    reference_x_n = [1,1,1,5,5,15,15,15,15,15,5,5,5,5,5] # Variable array of x-refinement (Reference)
    reference_y_n = [25,25,25] # Variable array of y-refinement (Reference)
    reference_z_n = [6,5,5,5,3,3,3,3,3] # Variable array of z-refinement (Reference)
    site_location = [18000,5000,0,27000,10000,81] # Site xi, yi, zi, xf, yf, and zf box positions [m]
    fault_regional = [10000,11000,0.01,10,22.5] # Regional fault x, and y positions [m], x and y multipliers for the trans, and height of the fault jump [m] 
    fault_site = [[21583,5710],[24081,8233],[0,0]] # Site fault x, and y positions [m] (initial and final) and x and y multipliers for the trans
    thickness = [9,9,9,9,9,9,9,9,9] # Thickness of the layers [m]
    pressure = 2E2  # Pressure on the reservoir top [Bar]
    temperature = [60,50] # Top and bottom temperatures [C]
    rock_comp = 6.11423e-5 # Rock compressibility [1/Bar]
    sensor_coords = [20000,8000,0] # Sensor position x, y, and z to assess the error over time w.r.t the reference solution [m]
    z_xy = "(20-20*mt.sin((2*mt.pi*(x+y)/10000)))" # The function for the reservoir surface
    hysteresis = 1 # Add hysteresis (1/0)
    salinity = 2.92 # Add salinity (value [1e-3 kg-M/kg])

Here we first set the dimensions of the regional model and the grid size for the discretization,
where the origen is located in the left bottom corner. Then the site model is defined by giving the coordinates
of the box. The following line defines a fault along the z-direction in the regional model. Similarly it is possible to define a fault in the site model, which extends from the given initial 
location and continues in zig-zag until the given final location. Finally, we set the thickness of the layers along the z direction, 
which allows to consider different rock and saturation function properties, as well as the reservoir conditions (pressure, temperature, and rock compressibility), 
the location of a point of interest to compare results, and the z position of the tops cells as a function of the (x,y) location. The hysteresis option activates the
Killough hysteresis model on the gas relative permeability, and salinity can be added to the system.

.. code-block:: python
    :linenos:
    :lineno-start: 24

    # Set the boundary conditions
    # Use open/closed/porv for the Regional aquifer (if porv, enter the bottom, right, top, and left values (e.g, porv 1e8 1e7 1e6 1e5))
    regional_bctype = ["open"]
    # Use open/closed/porv/porvproj/flux/pres/pres2p/wells for the BC site (if porv; bottom, right, top, and left values (e.g, porv 1e4 1e3 1e2 1e1))
    # For pres/flux BC's, add 'interp' to use linear interpolation in time
    site_bctype = ["open"]

We define the BC for the regional and site models, where flux/pres2p/pres in the site model 
projects the fluxes/pressures from the regional simulations (pres2p using only two points for the projection, while pres uses an interpolator 
along the side on the bc with all pressures), porvproj adds computed pore volumes from the regional
reservoir, and wells add 4 injectors and 4 producers on the middle points on the site boundaries.

.. note::
    The functionality for back-coupling activated by adding the entry "iterations = n", n an integer, is under development, see the :ref:`back_coupling` if you are curious.

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
    :lineno-start: 31

    # Set the saturation functions
    krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        # Wetting rel perm saturation function [-]
    krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" # Non-wetting rel perm saturation function [-]
    pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" # Capillary pressure saturation function [Bar]  

In this example we consider properties for the sands number one to five as described in the 
`11th SPE CSP <https://www.spe.org/en/csp/>`_:

.. code-block:: python
    :linenos:
    :lineno-start: 36

    # Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-], 7) nkrn [-],
    # 8) npen [-], 9) threshold cP evaluation (entry per layer, if hysteresis, additional entries per layer)
    safu = [[0.12,0.10,1,1,3060e-5,2,2,2,1e-4],
    [0.12,0.10,1.0,1.0,3870.63e-5,2,2,2,1e-4],
    [0.12,0.10,1.0,1.0,3060.00e-5,2,2,2,1e-4],
    [0.12,0.10,1.0,1.0,3870.63e-5,2,2,2,1e-4],
    [0.32,0.10,1.0,1.0, 193531e-5,2,2,2,1e-4],
    [0.14,0.10,1.0,1.0,8654.99e-5,2,2,2,1e-4],
    [0.12,0.10,1.0,1.0,6120.00e-5,2,2,2,1e-4],
    [0.14,0.10,1.0,1.0,8654.99e-5,2,2,2,1e-4],
    [0.12,0.10,1.0,1.0,6120.00e-5,2,2,2,1e-4],
    [0.22,0.30,1.0,1.0,3060.00e-5,2,4,2,1e-4],
    [0.12,0.30,1.0,1.0,3870.63e-5,2,4,2,1e-4],
    [0.12,0.30,1.0,1.0,3060.00e-5,2,4,2,1e-4],
    [0.12,0.30,1.0,1.0,3870.63e-5,2,4,2,1e-4],
    [0.32,0.30,1.0,1.0, 193531e-5,2,4,2,1e-4],
    [0.14,0.30,1.0,1.0,8654.99e-5,2,4,2,1e-4],
    [0.12,0.30,1.0,1.0,6120.00e-5,2,4,2,1e-4],
    [0.14,0.30,1.0,1.0,8654.99e-5,2,4,2,1e-4],
    [0.12,0.30,1.0,1.0,6120.00e-5,2,4,2,1e-4]]

.. note::
    Since hysteresis is activated, then we add the values for the imbibition curves (lines 47 to 55),
    where in this example the residual saturations are changed to 0.3 and the exponent to 4.

Simillarly for the rock properties:

.. code-block:: python
    :linenos:
    :lineno-start: 57

    # Properties rock: 1) Kxy [mD], 2) Kz [mD], and 3) phi [-] (entry per layer)
    rock = [[1013.25,101.325,0.25],
    [506.625,50.6625,0.20],
    [1013.25,101.325,0.25],
    [506.625,50.6625,0.20],
    [0.10132,0.01013,0.10],
    [101.324,10.1324,0.20],
    [202.650,20.2650,0.20],
    [101.324,10.1324,0.20],
    [202.650,20.2650,0.20]]

***********************
Well-related parameters
***********************

Now we proceed to define the location of the wells:

.. code-block:: python
    :linenos:
    :lineno-start: 68

    # Wells position: 1) x, 2) y, 3) zi, and 4) zf positions [m] (entry per well)
    well_coords = [[21180,7068,0,81],[24200,7800,15,65],[21718,7122,45,81],[14518,11377,0,50],[31679,8883,0,30],[28477,2732,0,81]]

The implementation allows to add as many wells as desired in the site and regional model.

.. figure:: figs/wells.png

    The location of the wells in the regional, site, and reference models. We observe that for the regional model
    wells 0 and 2 share the same cells along the z-direction. 

The injection rates are given in the following entries:

.. code-block:: python
    :linenos:
    :lineno-start: 71

    # Define the injection values (entry per change in the schedule): 
    # 1) injection time [d], 2) time step size to write results regional [d], 3) time step size to write results site/reference [d], 4) maximum time step [d]
    # 1) fluid (0 wetting, 1 non-wetting) well 0, 2) injection rates [kg/day] well 0, 3) fluid ... well n, injection, ...well n (as many as num of wells) 
    # if 'wells' for site_bctype, then 1) bottom, 2) right, 3) top, and 4) left values (0(prod)/1(inj), pressure [Bar]))
    inj = [[[365,73,73,73],[1,3e5,1,3e5,1,3e5,1,5e6,1,5e6,0,1e7]],[[365,73,73,73],[1,3e5,1,3e5,1,3e5,1,5e6,1,0,0,1e7]]]

Since we defined six wells (three of them inside the site model), then each row of the schedule has 16 entries, corresponding to
the first four defining the injection time, number of restart files in the solution for the regional, number of restart files in the solution for the site/reference, and maximum solver time step, and 2*6 additional 
entries to define injected fluid (0 water, 1 CO2) and the injection rates from well 0 to well 5 respectively. If 'site_bctype' is set to wells, 
then at the end of each row we add the values from the wells (BHP control) on the boundaries in the order of bottom, right, top,
and left with two values respectively (0 for producers and 1 for injectors, and the BHP in Bars, see `example1_wells.toml <https://github.com/cssr-tools/expreccs/blob/main/examples/example1_wells.toml>`_). 

******************
Simulation results
******************
Since the configuration file's name is input.toml, then it can be run by the following command:

.. code-block:: bash

    expreccs

the following is a screenshot using `ResInsight <https://resinsight.org>`_ to visualize the pressure and gas saturation at the end of the simulation:

.. figure:: figs/confile.png

    Then the approach is to project the fluxes/presures on the site boundaries from the regional simulations instead of
    using open boundaries as in this example.  

See the :doc:`examples <./examples>` section for further examples of configuration files and argument options for **expreccs**.
