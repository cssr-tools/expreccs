==================
Configuration file
==================

The current implementation allows for the following input parameters:

.. code-block:: python
    :linenos:

    """Set the full path to the flow executable and flags"""
    /Users/dmar/Github/opm/build/opm-simulators/bin/flow_gasoil --enable-opm-rst-file=true

    """Set the model parameters"""
    3030 3030 10    #Aquifer length, width, and depth [m]
    1515 1515 5     #x, y, and z position of injection well [m] 
    15 15 1         #Number of x-, y-, and z-cells [-]    

    """Set the saturation functions"""
    krw * (sew) ** 1.0       #Wetting rel perm saturation function [-]
    krc * (1 - sew) ** 1.0   #Non-wetting rel perm saturation function [-]
    pec * sew ** (-1.0)      #Capillary pressure saturation function [Pa]

    """Properties sat functions"""
    """swi [-], swrg [-], krg [-], krw [-],pe [MPa]"""
    SWI1 0.2 SWRG1 0.2 KRW1 1. KRG1 0.9 PRE1 1E-2

    """Properties rock""" 
    """K [mD], phi [-]"""
    PERM1 2E3 PORO1 0.3

    """Define the injection values 'inj[]'""" 
    """injection time [d], time step size to write results [d], injection rates [kg/day], injected fluid (0 water, 1 co2)"""
    365. 73. 1e6 1 
    365. 73. 1e6 1
    73. 73. 5e6 0
    
.. warning::
    Keep the linebreak between the sections (in the current implementation this is used for the reading of the parameters).

*****************
Injection values
****************

The implementation allows to add as many entries to the injection values as desired

.. tip::
    Check the opm user manual for additional information about the flow simulator. 
