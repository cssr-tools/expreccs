<%
import math as mt
import numpy as np
%>
-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][2]} /

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
${len(dic['site_wellijk'])+8} ${dic['site_noCells'][2]} ${2*len(dic['site_wellijk'])} ${len(dic['site_wellijk'])+8} /

UNIFIN
UNIFOUT

% if dic['site_bctype'] == 'flux':
AQUDIMS
-- MXNAQN   MXNAQC   NIFTBL  NRIFTB   NANAQU    NNCAMAX
    1*       1*        5       100      ${len(dic['AQUFLUX_top'][0][0])+len(dic['AQUFLUX_bottom'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_left'][0][0])}         1000 /
% endif
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INCLUDE
'GEOLOGY_${reservoir.upper()}.INC' /

% if dic['site_bctype'] == 'pres' or dic['site_bctype'] == 'pres2p':
BCCON
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["site_noCells"][1]):
${i+1+k*dic["site_noCells"][1]} 1  1  ${i+1} ${i+1} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}    'I-'  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["site_noCells"][1]):
${i+1+k*dic["site_noCells"][1]+dic['regional_noCells'][2]*dic["site_noCells"][1]} ${dic['site_noCells'][0]}  ${dic['site_noCells'][0]}  ${i+1} ${i+1} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}  'I'  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["site_noCells"][0]):
${i+1+k*dic["site_noCells"][0]+2*dic['regional_noCells'][2]*dic["site_noCells"][1]} ${i+1} ${i+1} 1 1 ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1} 'J-'  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["site_noCells"][0]):
${i+1+k*dic["site_noCells"][0]+2*dic['regional_noCells'][2]*dic["site_noCells"][1]+dic['regional_noCells'][2]*dic["site_noCells"][0]} ${i+1} ${i+1} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1} 'J'   /
% endfor
% endfor
/
% elif dic['site_bctype'] == 'free':
BCCON
1 1 ${dic['site_noCells'][0]} 1 1 1* 1* Y- /
2 1 ${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} 1* 1* Y /
3 1 1 1 ${dic['site_noCells'][1]} 1* 1* X- /
4 ${dic['site_noCells'][0]} ${dic['site_noCells'][0]} 1 ${dic['site_noCells'][1]} 1* 1* X /
/
% elif dic['site_bctype'] == 'porv':
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
OPERATE
PORV 1 ${dic['site_noCells'][0]} 1 1 1* 1* ADDX PORV ${dic["site_porv"][0]/(dic['site_noCells'][0]*dic['site_noCells'][2])}/
PORV ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} 1 ${dic['site_noCells'][0]} 1* 1* ADDX PORV ${dic["site_porv"][1]/(dic['site_noCells'][1]*dic['site_noCells'][2])} /
PORV 1 ${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} 1* 1* ADDX PORV ${dic["site_porv"][2]/(dic['site_noCells'][0]*dic['site_noCells'][2])} /
PORV 1 1 1 ${dic['site_noCells'][1]} 1* 1* ADDX PORV ${dic["site_porv"][3]/(dic['site_noCells'][1]*dic['site_noCells'][2])} /
/ 
% elif dic['site_bctype'] == 'porvproj':
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
OPERATE
PORV 1 ${dic['site_noCells'][0]} 1 1 1* 1* ADDX PORV ${dic["pv_bottom"]/(dic['site_noCells'][0]*dic['site_noCells'][2])} /
PORV ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} 1 ${dic['site_noCells'][0]} 1* 1* ADDX PORV ${dic["pv_right"]/(dic['site_noCells'][1]*dic['site_noCells'][2])} /
PORV 1 ${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} 1* 1* ADDX PORV ${dic["pv_top"]/(dic['site_noCells'][0]*dic['site_noCells'][2])} /
PORV 1 1 1 ${dic['site_noCells'][1]} 1* 1* ADDX PORV ${dic["pv_left"]/(dic['site_noCells'][1]*dic['site_noCells'][2])} /
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
0   ${dic['temp_top']}
${dic[f'{reservoir}_zmz'][-1]} ${dic['temp_bottom']} /

% if dic["co2store"] == "gasoil":
RSVD
0   0
${dic[f'{reservoir}_zmz'][-1]}  0 /
% endif

RPTRST 
'BASIC=2' FLOWS FLORES FLOWS- FLORES- DEN ${'PCOG' if dic["co2store"] == "gasoil" else 'PCGW'} /

% if dic['site_bctype'] == 'flux': 
AQUANCON
-- Aq#  I1 I2  J1   J2  K1 K2 FACE
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["left_noCells"]):
${i+1+k*dic["left_noCells"]} 1  1  ${1+i*mt.floor(dic['site_noCells'][1]/dic["left_noCells"])} ${(i+1)*mt.floor(dic['site_noCells'][1]/dic["left_noCells"])} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'I-'	  1.00      1  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["right_noCells"]):
${i+1+k*dic["right_noCells"]+len(dic['AQUFLUX_left'][0][0])} ${dic['site_noCells'][0]}  ${dic['site_noCells'][0]}  ${1+i*mt.floor(dic['site_noCells'][1]/dic["right_noCells"])} ${(i+1)*mt.floor(dic['site_noCells'][1]/dic["right_noCells"])} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'I'	  1.00      1  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["bottom_noCells"]):
% if ((i+1)*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"]) != 1 and 1+i*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"])!=dic['site_noCells'][0]) and dic["bottom_noCells"]>2:
% if i==0:
${i+1+k*dic["bottom_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${2} ${(i+1)*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"])} 1 1 ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'J-'	  1.00      1  /
% elif i==dic["bottom_noCells"]-1:
${i+1+k*dic["bottom_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${1+i*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"])} ${dic['site_noCells'][0]-1} 1 1 ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'J-'	  1.00      1  /
% else:
${i+1+k*dic["bottom_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${1+i*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"])} ${(i+1)*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"])} 1 1 ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'J-'	  1.00      1  /
% endif
% endif
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["top_noCells"]):
% if ((i+1)*mt.floor(dic['site_noCells'][0]/dic["top_noCells"]) != 1 and 1+i*mt.floor(dic['site_noCells'][0]/dic["top_noCells"])!=dic['site_noCells'][0]) and dic["top_noCells"]>2:
% if i==0:
${i+1+k*dic["top_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${2} ${(i+1)*mt.floor(dic['site_noCells'][0]/dic["top_noCells"])} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'J'	  1.00      1  /
% elif i==dic["top_noCells"]-1:
${i+1+k*dic["top_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${1+i*mt.floor(dic['site_noCells'][0]/dic["top_noCells"])} ${dic['site_noCells'][0]-1} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'J'	  1.00      1  /
% else:
${i+1+k*dic["top_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${1+i*mt.floor(dic['site_noCells'][0]/dic["top_noCells"])} ${(i+1)*mt.floor(dic['site_noCells'][0]/dic["top_noCells"])} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${np.where(dic["site_zmaps"]==k)[0][0]+1} ${np.where(dic["site_zmaps"]==k)[0][-1]+1}	'J'	  1.00      1  /
% endif
% endif
% endfor
% endfor
/
% endif
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
${dic["site_sensor"][0]+1} ${dic["site_sensor"][1]+1} ${dic["site_sensor"][2]+1} /
/
BGIP
${dic["site_sensor"][0]+1} ${dic["site_sensor"][1]+1} ${dic["site_sensor"][2]+1} /
/
BGIPG
${dic["site_sensor"][0]+1} ${dic["site_sensor"][1]+1} ${dic["site_sensor"][2]+1} /
/
BGIPL
${dic["site_sensor"][0]+1} ${dic["site_sensor"][1]+1} ${dic["site_sensor"][2]+1} /
/
% if dic["co2store"] == "gaswater":
BFLOWI
${dic["site_sensor"][0]+1} ${dic["site_sensor"][1]+1} ${dic["site_sensor"][2]+1} /
/
BFLOWJ
${dic["site_sensor"][0]+1} ${dic["site_sensor"][1]+1} ${dic["site_sensor"][2]+1} /
/
% endif
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
'BASIC=2' FLOWS FLORES FLOWS- FLORES- DEN ${'PCOG' if dic["co2store"] == "gasoil" else 'PCGW'} /

WELSPECS
% for i in range(len(dic['site_wellijk'])):
'INJ${i}' 'G1' ${dic['site_wellijk'][i][0]}	${dic['site_wellijk'][i][1]} 1* 'GAS' /
% endfor
% if dic['site_bctype'] == 'wells':
'BCINJ0' 'W' ${mt.ceil(dic['site_noCells'][0]/2)} 1 1* ${dic["liq"]} /
'BCINJ1' 'W' ${dic['site_noCells'][0]} ${mt.ceil(dic['site_noCells'][1]/2)} 1* ${dic["liq"]} /
'BCINJ2' 'W' ${mt.ceil(dic['site_noCells'][0]/2)} ${dic['site_noCells'][1]} 1* ${dic["liq"]} /
'BCINJ3' 'W' 1 ${mt.ceil(dic['site_noCells'][1]/2)} 1* ${dic["liq"]} /
'BCPRO0' 'W' ${mt.ceil(dic['site_noCells'][0]/2)} 1 1* ${dic["liq"]} /
'BCPRO1' 'W' ${dic['site_noCells'][0]} ${mt.ceil(dic['site_noCells'][1]/2)} 1* ${dic["liq"]} /
'BCPRO2' 'W' ${mt.ceil(dic['site_noCells'][0]/2)} ${dic['site_noCells'][1]} 1* ${dic["liq"]} /
'BCPRO3' 'W' 1 ${mt.ceil(dic['site_noCells'][1]/2)} 1* ${dic["liq"]} /
% endif
/
COMPDAT
% for i in range(len(dic['site_wellijk'])):
'INJ${i}' ${dic['site_wellijk'][i][0]} ${dic['site_wellijk'][i][1]}	${dic['site_wellijk'][i][2]} ${dic['site_wellijk'][i][3]} 'OPEN' 1*	1* 0.2 /
% endfor
% if dic['site_bctype'] == 'wells':
'BCINJ0' ${mt.ceil(dic['site_noCells'][0]/2)} 1 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCINJ1' ${dic['site_noCells'][0]} ${mt.ceil(dic['site_noCells'][1]/2)} 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCINJ2' ${mt.ceil(dic['site_noCells'][0]/2)} ${dic['site_noCells'][1]} 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCINJ3' 1 ${mt.ceil(dic['site_noCells'][1]/2)} 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCPRO0' ${mt.ceil(dic['site_noCells'][0]/2)} 1 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCPRO1' ${dic['site_noCells'][0]} ${mt.ceil(dic['site_noCells'][1]/2)} 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCPRO2' ${mt.ceil(dic['site_noCells'][0]/2)} ${dic['site_noCells'][1]} 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
'BCPRO3' 1 ${mt.ceil(dic['site_noCells'][1]/2)} 1 ${dic['site_noCells'][2]} 'OPEN' 1* 1* 0.2/
% endif
/
<%
n = 0
%>
% for j in range(len(dic['inj'])):
% for k in range(round(dic['inj'][j][0]/dic['inj'][j][2])):
TUNING
${min(1, dic['inj'][j][3])} ${dic['inj'][j][3]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(len(dic['site_wellijk'])):
% if dic['inj'][j][4+2*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][2*(i+2)+1] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+2)+1] / 1.86843 : E}"}  1* 480/
% else:
'INJ${i}' ${dic["liq"]} ${'OPEN' if dic['inj'][j][2*(i+2)+1] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+2)+1] / 998.108 : E}"}  1* 'RATE' ${f"{dic['inj'][j][2*(i+2)+1] / 1.86843 : E}"}  1* 480/
/
% endif
% endfor
% if dic['site_bctype'] == "wells":
'BCINJ0' ${dic["liq"]} ${'OPEN' if dic['bc_wells'][j][0] > 0 else 'SHUT'} 'BHP' 2* ${dic['bc_wells'][j][1]}/
'BCINJ1' ${dic["liq"]} ${'OPEN' if dic['bc_wells'][j][2] > 0 else 'SHUT'} 'BHP' 2* ${dic['bc_wells'][j][3]}/
'BCINJ2' ${dic["liq"]} ${'OPEN' if dic['bc_wells'][j][4] > 0 else 'SHUT'} 'BHP' 2* ${dic['bc_wells'][j][5]}/
'BCINJ3' ${dic["liq"]} ${'OPEN' if dic['bc_wells'][j][6] > 0 else 'SHUT'} 'BHP' 2* ${dic['bc_wells'][j][7]}/
% endif
/
%if dic['site_bctype'] == 'flux':
AQUFLUX
% for i in range(len(dic['AQUFLUX_left'][0][0])):
${i+1} ${dic['AQUFLUX_left'][n+k+1][0][i]} /
% endfor
% for i in range(len(dic['AQUFLUX_right'][0][0])):
${i+1+len(dic['AQUFLUX_left'][0][0])} ${dic['AQUFLUX_right'][n+k+1][0][i]} / 
% endfor
% for i in range(len(dic['AQUFLUX_bottom'][0][0])):
% if ((i%dic["bottom_noCells"]+1)*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"]) != 1 and 1+(i%dic["bottom_noCells"])*mt.floor(dic['site_noCells'][0]/dic["bottom_noCells"])!=dic['site_noCells'][0]) and dic["bottom_noCells"]>2:
${i+1+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${dic['AQUFLUX_bottom'][n+k+1][0][i]} /
% endif
% endfor
% for i in range(len(dic['AQUFLUX_top'][0][0])):
% if ((i%dic["top_noCells"]+1)*mt.floor(dic['site_noCells'][0]/dic["top_noCells"]) != 1 and 1+(i%dic["top_noCells"])*mt.floor(dic['site_noCells'][0]/dic["top_noCells"])!=dic['site_noCells'][0]) and dic["top_noCells"]>2:
${i+1+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${dic['AQUFLUX_top'][n+k+1][0][i]} /
% endif
% endfor
/
% elif dic['site_bctype']== 'pres' or dic['site_bctype'] == 'pres2p':
BCPROP
% for i in range(len(dic['PRESSURE_left'][0][0])):
${i+1} DIRICHLET ${dic["lin"]} 1* ${dic['PRESSURE_left'][n+k+1][0][i]} /
% endfor
% for i in range(len(dic['PRESSURE_right'][0][0])):
${i+1+len(dic['PRESSURE_left'][0][0])} DIRICHLET ${dic["lin"]} 1* ${dic['PRESSURE_right'][n+k+1][0][i]} / 
% endfor
% for i in range(len(dic['PRESSURE_bottom'][0][0])):
${i+1+len(dic['PRESSURE_left'][0][0])+len(dic['PRESSURE_right'][0][0])} DIRICHLET ${dic["lin"]} 1* ${dic['PRESSURE_bottom'][n+k+1][0][i]} /
% endfor
% for i in range(len(dic['PRESSURE_top'][0][0])):
${i+1+len(dic['PRESSURE_left'][0][0])+len(dic['PRESSURE_right'][0][0])+len(dic['PRESSURE_bottom'][0][0])} DIRICHLET ${dic["lin"]} 1* ${dic['PRESSURE_top'][n+k+1][0][i]} /
% endfor
/
%elif dic['site_bctype'] == "free":
BCPROP 
1 FREE /
2 FREE /
3 FREE /
4 FREE /
/
% elif dic['site_bctype'] == "wells":
WCONPROD
'BCPRO0' ${'OPEN' if dic['bc_wells'][j][0] == 0 else 'SHUT'} 'BHP' 5* ${dic['bc_wells'][j][1]}/
'BCPRO1' ${'OPEN' if dic['bc_wells'][j][2] == 0 else 'SHUT'} 'BHP' 5* ${dic['bc_wells'][j][3]}/
'BCPRO2' ${'OPEN' if dic['bc_wells'][j][4] == 0 else 'SHUT'} 'BHP' 5* ${dic['bc_wells'][j][5]}/
'BCPRO3' ${'OPEN' if dic['bc_wells'][j][6] == 0 else 'SHUT'} 'BHP' 5* ${dic['bc_wells'][j][7]}/
/
% endif
TSTEP
${dic['inj'][j][2]}
/
% endfor
<%
n += round(dic['inj'][j][0]/dic['inj'][j][2])
%>
% endfor