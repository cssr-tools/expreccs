<%
import math as mt
%>
-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['regional_noCells'][0]} ${dic['regional_noCells'][1]} ${dic['regional_noCells'][2]} /

EQLDIMS
/

TABDIMS
${(dic["hysteresis"]+1)*dic['satnum']} 1* 100000 /

OIL
GAS
DISGAS
CO2STORE

METRIC

START
1 'JAN' 2025 /

% if dic["hysteresis"] ==1:
SATOPTS
HYSTER  /
% endif

WELLDIMS
${len(dic['regional_wellijk'])} ${dic['regional_noCells'][2]} ${len(dic['regional_wellijk'])} ${len(dic['regional_wellijk'])} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INCLUDE
'GEOLOGY_${reservoir.upper()}.INC' /
% if dic['regional_bctype'] == 'free':
BCCON 
1 1 ${dic[f'{reservoir}_noCells'][0]} 1 1 1* 1* Y- /
2 1 ${dic[f'{reservoir}_noCells'][0]} ${dic[f'{reservoir}_noCells'][1]} ${dic[f'{reservoir}_noCells'][1]} 1* 1* Y /
3 1 1 1 ${dic[f'{reservoir}_noCells'][1]} 1* 1* X- /
4 ${dic[f'{reservoir}_noCells'][0]} ${dic[f'{reservoir}_noCells'][0]} 1 ${dic[f'{reservoir}_noCells'][1]} 1* 1* X /
/
% endif
% if dic['regional_bctype'] == 'porv':
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
OPERATE
	PORV 1 ${dic['regional_noCells'][0]} 1 1 1* 1* ADDX PORV ${dic["regional_porv"][0]/(dic['regional_noCells'][0]*dic['regional_noCells'][2])}/
	PORV ${dic['regional_noCells'][0]} ${dic['regional_noCells'][0]} 1 ${dic['regional_noCells'][1]} 1* 1* ADDX PORV ${dic["regional_porv"][1]/(dic['regional_noCells'][1]*dic['regional_noCells'][2])} /
	PORV 1 ${dic['regional_noCells'][0]} ${dic['regional_noCells'][1]} ${dic['regional_noCells'][1]} 1* 1* ADDX PORV ${dic["regional_porv"][2]/(dic['regional_noCells'][0]*dic['regional_noCells'][2])} /
	PORV 1 1 1 ${dic['regional_noCells'][1]} 1* 1* ADDX PORV ${dic["regional_porv"][3]/(dic['regional_noCells'][1]*dic['regional_noCells'][2])} /
 / 
 % endif
----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------
INCLUDE
'PROPS_${reservoir.upper()}.INC' /
----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------
INCLUDE
'REGIONS_${reservoir.upper()}.INC' /
----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 ${dic['pressure']} 1000 0 0 0 1 1 0 /

RTEMPVD
0   ${dic['temp_top']}
${dic[f'{reservoir}_zmz'][-1]} ${dic['temp_bottom']} /

RSVD
0   0
${dic[f'{reservoir}_zmz'][-1]} 0 /

RPTRST 
 'BASIC=2' FLOWS FLORES DEN/
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
FPR
FGIP
FOIP
FGIR
FGIT
WGIR
/
WOIR
/
WGIT
/
WBHP
/
RPR
/
ROIP
/
RGIP
/
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
 'BASIC=2' FLOWS FLORES DEN /

WELSPECS
% for i in range(len(dic['regional_wellijk'])):
	'INJ${i}'	'G1'	${dic['regional_wellijk'][i][0]}	${dic['regional_wellijk'][i][1]}	1*	'GAS' /
% endfor
/
COMPDAT
% for i in range(len(dic['regional_wellijk'])):
	'INJ${i}'	${dic['regional_wellijk'][i][0]}	${dic['regional_wellijk'][i][1]}	${dic['regional_wellijk'][i][2]}	${dic['regional_wellijk'][i][3]}	'OPEN'	1*	1*	0.2 /
% endfor
/
% for j in range(len(dic['inj'])):
TUNING
${min(1, dic['inj'][j][3])} ${dic['inj'][j][3]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(len(dic['regional_wellijk'])):
% if dic['inj'][j][4+2*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][2*(i+2)+1] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+2)+1] / 1.86843 : E}"}  1* 400/
% else:
'INJ${i}' 'OIL' ${'OPEN' if dic['inj'][j][2*(i+2)+1] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+2)+1] / 998.108 : E}"}  1* 400/
%endif
% endfor
/
% if dic['regional_bctype'] == 'free':
BCPROP 
1 FREE /
2 FREE /
3 FREE /
4 FREE /
/
% endif
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor