<%
import math as mt
%>
-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['reference_noCells'][0]} ${dic['reference_noCells'][1]} ${dic['reference_noCells'][2]} /

EQLDIMS
/

TABDIMS
${dic['satnum']} 1* 10000 /

OIL
GAS
CO2STORE

METRIC

START
1 'JAN' 2025 /

WELLDIMS
${len(dic['reference_wellijk'])} ${dic['reference_noCells'][2]} ${len(dic['reference_wellijk'])} ${len(dic['reference_wellijk'])} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INCLUDE
'GEOLOGY_${reservoir.upper()}.INC' /
% if dic['reference_bctype'] == 'free':
BCCON 
1 1 ${dic[f'{reservoir}_noCells'][0]} 1 1 1* 1* Y- /
2 1 ${dic[f'{reservoir}_noCells'][0]} ${dic[f'{reservoir}_noCells'][1]} ${dic[f'{reservoir}_noCells'][1]} 1* 1* Y /
3 1 1 1 ${dic[f'{reservoir}_noCells'][1]} 1* 1* X- /
4 ${dic[f'{reservoir}_noCells'][0]} ${dic[f'{reservoir}_noCells'][0]} 1 ${dic[f'{reservoir}_noCells'][1]} 1* 1* X /
/
% endif
% if dic['reference_bctype'] == 'porv':
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
BOX
1 1 1 ${dic['reference_noCells'][0]} 1* 1* / 
MULTPV
% for _ in range(dic['reference_noCells'][2]):
% for i in range(dic['reference_noCells'][0]):
${'\t\t{0:.15e}'.format(dic["reference_porv"]) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
1 ${dic['reference_noCells'][0]} 1 1 1* 1* / 
MULTPV
% for _ in range(dic['reference_noCells'][2]):
% for i in range(dic['reference_noCells'][0]):
${'\t\t{0:.15e}'.format(dic["reference_porv"]) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
${dic['reference_noCells'][1]} ${dic['reference_noCells'][1]} 1 ${dic['reference_noCells'][0]} 1* 1* / 
MULTPV
% for _ in range(dic['reference_noCells'][2]):
% for i in range(dic['reference_noCells'][0]):
${'\t\t{0:.15e}'.format(dic["reference_porv"]) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
1 ${dic['reference_noCells'][0]} ${dic['reference_noCells'][1]} ${dic['reference_noCells'][1]} 1* 1* / 
MULTPV
% for _ in range(dic['reference_noCells'][2]):
% for i in range(dic['reference_noCells'][0]):
${'\t\t{0:.15e}'.format(dic["reference_porv"]) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX
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
% for i in range(len(dic['reference_wellijk'])):
	'INJ${i}'	'G1'	${dic['reference_wellijk'][i][0]}	${dic['reference_wellijk'][i][1]}	1*	'GAS' /
% endfor
/
COMPDAT
% for i in range(len(dic['reference_wellijk'])):
	'INJ${i}'	${dic['reference_wellijk'][i][0]}	${dic['reference_wellijk'][i][1]}	${dic['reference_wellijk'][i][2]}	${dic['reference_wellijk'][i][3]}	'OPEN'	1*	1*	0.5 /
% endfor
/
% for j in range(len(dic['inj'])):
TUNING
${min(1, dic['inj'][j][2])} ${dic['inj'][j][2]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(len(dic['reference_wellijk'])):
% if dic['inj'][j][3+2*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][2*(i+2)] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+2)] / 1.86843 : E}"}  1* 400/
% else:
'INJ${i}' 'OIL' ${'OPEN' if dic['inj'][j][2*(i+2)] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+2)] / 998.108 : E}"}  1* 400/
%endif
% endfor
/
%if dic['reference_bctype'] == 'free':
BCPROP 
1 FREE /
2 FREE /
3 FREE /
4 FREE /
/
%endif
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor