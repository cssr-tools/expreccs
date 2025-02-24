<%
import math as mt
%>
-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['reference_num_cells'][0]} ${dic['reference_num_cells'][1]} ${dic['reference_num_cells'][2]} /

EQLDIMS
/

TABDIMS
${(dic["hysteresis"]+1)*dic['satnum']} 1* 1000 /

CO2STORE
GAS
% if dic["co2store"] == "gaswater":
WATER
DISGASW
% else:
OIL
DISGAS
% endif

METRIC

START
1 'JAN' 2025 /

% if dic["hysteresis"] ==1:
SATOPTS
HYSTER  /
% endif

WELLDIMS
${len(dic['reference_wellijk'])} ${dic['reference_num_cells'][2]} ${len(dic['reference_wellijk'])} ${len(dic['reference_wellijk'])} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INCLUDE
'GEOLOGY_${reservoir.upper()}.INC' /

% if dic['regional_bctype'][0] == 'open':
BCCON 
1 1 ${dic[f'{reservoir}_num_cells'][0]} 1 1 1* 1* Y- /
2 1 ${dic[f'{reservoir}_num_cells'][0]} ${dic[f'{reservoir}_num_cells'][1]} ${dic[f'{reservoir}_num_cells'][1]} 1* 1* Y /
3 1 1 1 ${dic[f'{reservoir}_num_cells'][1]} 1* 1* X- /
4 ${dic[f'{reservoir}_num_cells'][0]} ${dic[f'{reservoir}_num_cells'][0]} 1 ${dic[f'{reservoir}_num_cells'][1]} 1* 1* X /
/
% endif
% if dic['regional_bctype'][0] == 'porv':
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
OPERATE
PORV 1 ${dic['reference_num_cells'][0]} 1 1 1* 1* ADDX PORV ${1.*dic["regional_bctype"][1]/(dic['reference_num_cells'][0]*dic['reference_num_cells'][2])}/
PORV ${dic['reference_num_cells'][0]} ${dic['reference_num_cells'][0]} 1 ${dic['reference_num_cells'][1]} 1* 1* ADDX PORV ${1.*dic["regional_bctype"][2]/(dic['reference_num_cells'][1]*dic['reference_num_cells'][2])} /
PORV 1 ${dic['reference_num_cells'][0]} ${dic['reference_num_cells'][1]} ${dic['reference_num_cells'][1]} 1* 1* ADDX PORV ${1.*dic["regional_bctype"][3]/(dic['reference_num_cells'][0]*dic['reference_num_cells'][2])} /
PORV 1 1 1 ${dic['reference_num_cells'][1]} 1* 1* ADDX PORV ${1.*dic["regional_bctype"][4]/(dic['reference_num_cells'][1]*dic['reference_num_cells'][2])} /
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
0 ${dic['pressure']} ${1000 if dic["co2store"] == "gasoil" else 0} 0 0 0 1 1 0 /

RTEMPVD
0   ${dic['temperature'][0]}
${dic[f'{reservoir}_zmz'][-1]} ${dic['temperature'][1]} /

% if dic["co2store"] == "gasoil":
RSVD
0   0
${dic[f'{reservoir}_zmz'][-1]}  0 /
% endif

RPTRST 
'BASIC=2' FLOWS FLORES FLOWS- FLORES- DEN ${'PCOG' if dic["co2store"] == "gasoil" else 'PCGW'} /
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
FPR
FGIP
F${dic["l"]}IP
FGIR
FGIT
FGIP
FGIPL
FGIPG
WGIR
/
W${dic["l"]}IR
/
WGIT
/
WBHP
/
RPR
/
RGIP
/
RGIPL
/
RGIPG
/
BPR
${dic["reference_sensor"][0]+1} ${dic["reference_sensor"][1]+1} ${dic["reference_sensor"][2]+1} /
/
BGIP
${dic["reference_sensor"][0]+1} ${dic["reference_sensor"][1]+1} ${dic["reference_sensor"][2]+1} /
/
BGIPG
${dic["reference_sensor"][0]+1} ${dic["reference_sensor"][1]+1} ${dic["reference_sensor"][2]+1} /
/
BGIPL
${dic["reference_sensor"][0]+1} ${dic["reference_sensor"][1]+1} ${dic["reference_sensor"][2]+1} /
/
% if dic["co2store"] == "gaswater":
BFLOWI
${dic["reference_sensor"][0]+1} ${dic["reference_sensor"][1]+1} ${dic["reference_sensor"][2]+1} /
/
BFLOWJ
${dic["reference_sensor"][0]+1} ${dic["reference_sensor"][1]+1} ${dic["reference_sensor"][2]+1} /
/
% endif
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
'BASIC=2' FLOWS FLORES FLOWS- FLORES- DEN ${'PCOG' if dic["co2store"] == "gasoil" else 'PCGW'} /

WELSPECS
% for i in range(len(dic['reference_wellijk'])):
'INJ${i}' 'G1' ${dic['reference_wellijk'][i][0]} ${dic['reference_wellijk'][i][1]} 1* 'GAS' /
% endfor
/
COMPDAT
% for i in range(len(dic['reference_wellijk'])):
'INJ${i}' ${dic['reference_wellijk'][i][0]} ${dic['reference_wellijk'][i][1]} ${dic['reference_wellijk'][i][2]} ${dic['reference_wellijk'][i][3]} 'OPEN' 1*	1* 0.2 /
% endfor
/
% for j in range(len(dic['inj'])):
TUNING
${min(1, dic['inj'][j][0][3])} ${dic['inj'][j][0][3]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(len(dic['reference_wellijk'])):
% if dic['inj'][j][1][2*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][1][2*i+1] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][1][2*i+1] / 1.86843 : E}"}  1* 480/
% else:
'INJ${i}' ${dic["liq"]} ${'OPEN' if dic['inj'][j][1][2*i+1] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][1][2*i+1] / 998.108 : E}"}  1* 480/
%endif
% endfor
/
%if dic['regional_bctype'][0] == 'open':
BCPROP 
1 FREE /
2 FREE /
3 FREE /
4 FREE /
/
%endif
TSTEP
${round(dic['inj'][j][0][0]/dic['inj'][j][0][2])}*${dic['inj'][j][0][2]}
/
% endfor