-- This reservoir simulation deck is made available under the Open Database
-- License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in
-- individual contents of the database are licensed under the Database Contents
-- License: http://opendatacommons.org/licenses/dbcl/1.0/
-- Copyright (C) 2026 NORCE Research AS
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
4 4 4 /

EQLDIMS
/

TABDIMS
/

CO2STORE
GAS
WATER

METRIC

START
1 JAN 2025 /

WELLDIMS
/

UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT

DX
64*2.5e3 /

DY
64*2.5e3 /

DZ
64*5e2 /

TOPS
16*0 /

FLUXNUM
% for index, value in enumerate(configuration):
% if (index + 1) % 16 == 0:
${value + 1}\

% else:
${value + 1} \
% endif
% endfor
/

EQUALREG
PORO        0 0 F /
PORO     0.25 1 F /
PORO     1e-1 2 F /
PERMX       0 0 F /
PERMX 101.325 1 F /
PERMX    1e-2 2 F /
PERMY       0 0 F /
PERMY 101.325 1 F /
PERMY    1e-2 2 F /
PERMZ       0 0 F /
PERMZ 101.325 1 F /
PERMZ    1e-2 2 F /
/
----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------
SGWFN
0 0 1 0
1 1 0 0 /

SALINITY
2.92 /

ROCK
276 4.934e-5 /
----------------------------------------------------------------------------
SOLUTION
----------------------------------------------------------------------------
EQUIL
0 200 0 0 0 0 1 1 0 /

RTEMPVD
0 40
1000 40 /

RPTRST 
BASIC=2 /
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
BASIC=2 /

TUNING
/
/
/
SOURCE
4 4 4 WATER 8.015165e6 /
/
TSTEP
9131.25 /

TUNING
/
/
/
SOURCE
4 4 4 WATER 0 /
/
TSTEP
10*365.25 /
