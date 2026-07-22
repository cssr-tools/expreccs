-- This reservoir simulation deck is made available under the Open Database
-- License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in
-- individual contents of the database are licensed under the Database Contents
-- License: http://opendatacommons.org/licenses/dbcl/1.0/
-- Copyright (C) 2026 NORCE Research AS
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
8 1 4 /

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

COORD
     0   0 0      0   0 2e3
 2.5e3   0 0  2.5e3   0 2e3
   5e3   0 0    5e3   0 2e3
 7.5e3   0 0  7.5e3   0 2e3
  10e3   0 0   10e3   0 2e3
12.5e3   0 0 12.5e3   0 2e3
  15e3   0 0   15e3   0 2e3
17.5e3   0 0 17.5e3   0 2e3
  20e3   0 0   20e3   0 2e3
     0 1e3 0      0 1e3 2e3
 2.5e3 1e3 0  2.5e3 1e3 2e3
   5e3 1e3 0    5e3 1e3 2e3
 7.5e3 1e3 0  7.5e3 1e3 2e3
  10e3 1e3 0   10e3 1e3 2e3
12.5e3 1e3 0 12.5e3 1e3 2e3
  15e3 1e3 0   15e3 1e3 2e3
17.5e3 1e3 0 17.5e3 1e3 2e3
  20e3 1e3 0   20e3 1e3 2e3 /

ZCORN
 5e2  5e2    12*0  5e2  5e2 5e2   5e2    12*0  5e2  5e2
15e2 15e2  12*5e2 15e2 15e2 15e2 15e2  12*5e2 15e2 15e2

15e2 15e2  12*5e2 15e2 15e2 15e2 15e2  12*5e2 15e2 15e2
15e2 15e2 12*10e2 15e2 15e2 15e2 15e2 12*10e2 15e2 15e2

15e2 15e2 12*10e2 15e2 15e2 15e2 15e2 12*10e2 15e2 15e2
15e2 15e2 12*15e2 15e2 15e2 15e2 15e2 12*15e2 15e2 15e2

15e2 15e2 12*15e2 15e2 15e2 15e2 15e2 12*15e2 15e2 15e2
15e2 15e2 12*20e2 15e2 15e2 15e2 15e2 12*20e2 15e2 15e2
/

FLUXNUM
1 1 ${configuration[0]+1} ${configuration[1]+1} ${configuration[2]+1} ${configuration[3]+1} 1 1
0 1 ${configuration[4]+1} ${configuration[5]+1} ${configuration[6]+1} ${configuration[7]+1} 1 0
0 1 ${configuration[8]+1} ${configuration[9]+1} ${configuration[10]+1} ${configuration[11]+1} 1 0
0 1 ${configuration[12]+1} ${configuration[13]+1} ${configuration[14]+1} ${configuration[15]+1} 1 0
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
0 200.0 0 0 0 0 1 1 0 /

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
1 1 1 WATER 8.015165e6 /
/
TSTEP
9131.25 /

TUNING
/
/
/
SOURCE
1 1 1 WATER 0 /
/
TSTEP
10*365.25 /
