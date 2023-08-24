-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][2]} /

EQLDIMS
/

TABDIMS
${dic['satnum']} /

OIL
GAS
CO2STORE

METRIC

START
1 'JAN' 2025 /

WELLDIMS
${len(dic['site_wellijk'])} ${dic['site_noCells'][2]} ${len(dic['site_wellijk'])} ${len(dic['site_wellijk'])} /

UNIFIN
UNIFOUT

AQUDIMS
-- MXNAQN   MXNAQC   NIFTBL  NRIFTB   NANAQU    NNCAMAX
    1*       1*        5       100      ${len(dic['AQUFLUX_top'][0][0])+len(dic['AQUFLUX_bottom'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_left'][0][0])}         1000 /
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/SITE.GRDECL'/

EQUALS
% for i in range(dic['satnum']):
PERMX  ${dic['rock'][i][0]} 1* 1* 1* 1* ${1+i*round(dic['site_noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['site_noCells'][2]/dic['satnum'])} /
% endfor
/

COPY 
PERMX PERMY /
PERMX PERMZ /
/

EQUALS
% for i in range(dic['satnum']):
PORO  ${dic['rock'][i][1]} 1* 1* 1* 1* ${1+i*round(dic['site_noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['site_noCells'][2]/dic['satnum'])} /
% endfor
/

MULTX
% for k in range(dic['site_noCells'][2]):
<%
n = 0
%>
% for j in range(dic['site_noCells'][1]):
% for i in range(dic['site_noCells'][0]):
% if i == dic["site_fault"][0][0] + n and j == dic["site_fault"][0][1] + n and i <= dic["site_fault"][1][0] and j <= dic["site_fault"][1][1]:
${dic["fault_site_mult"][0]}
<%
n += 1
%>
%else:
1.0
%endif
%endfor
%endfor
%endfor
/
MULTY
% for k in range(dic['site_noCells'][2]):
<%
n = 0
%>
% for j in range(dic['site_noCells'][1]):
% for i in range(dic['site_noCells'][0]):
% if j == dic["site_fault"][0][1] + n and i == dic["site_fault"][0][0] + n and i <= dic["site_fault"][1][0] and j <= dic["site_fault"][1][1]:
${dic["fault_site_mult"][1]}
<%
n += 1
%>
%else:
1.0
%endif
%endfor
%endfor
%endfor
/

BCCON 
${1+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])+len(dic['AQUFLUX_top'][0][0])} 1 1 1 1 1 1 Y-/
/

----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC' /

----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------

EQUALS
 'FIPNUM' 1 /
/

EQUALS
% for i in range(dic['satnum']):
SATNUM  ${i+1} 1* 1* 1* 1* ${1+i*round(dic['site_noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['site_noCells'][2]/dic['satnum'])} /
% endfor
/

----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 200 1000 0 0 0 1 1 0 /

RPTRST 
 'BASIC=2' FLOWS FLORES DEN/

AQUANCON
-- Aq#  I1 I2  J1   J2  K1 K2 FACE
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["left_noCells"]):
${i+1+k*dic["left_noCells"]} 1  1  ${1+i*round(dic['site_noCells'][1]/dic["left_noCells"])} ${(i+1)*round(dic['site_noCells'][1]/dic["left_noCells"])} ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'I-'	  1.00      1  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["right_noCells"]):
${i+1+k*dic["right_noCells"]+len(dic['AQUFLUX_left'][0][0])} ${dic['site_noCells'][0]}  ${dic['site_noCells'][0]}  ${1+i*round(dic['site_noCells'][1]/dic["right_noCells"])} ${(i+1)*round(dic['site_noCells'][1]/dic["right_noCells"])} ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'I'	  1.00      1  /
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["bottom_noCells"]):
% if ((i+1)*round(dic['site_noCells'][0]/dic["bottom_noCells"]) != 1 and 1+i*round(dic['site_noCells'][0]/dic["bottom_noCells"])!=dic['site_noCells'][0]) and dic["bottom_noCells"]>2:
% if i==0:
${i+1+k*dic["bottom_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${2} ${(i+1)*round(dic['site_noCells'][0]/dic["bottom_noCells"])} 1 1 ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'J-'	  1.00      1  /
% elif i==dic["bottom_noCells"]-1:
${i+1+k*dic["bottom_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${1+i*round(dic['site_noCells'][0]/dic["bottom_noCells"])} ${dic['site_noCells'][0]-1} 1 1 ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'J-'	  1.00      1  /
%else:
${i+1+k*dic["bottom_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${1+i*round(dic['site_noCells'][0]/dic["bottom_noCells"])} ${(i+1)*round(dic['site_noCells'][0]/dic["bottom_noCells"])} 1 1 ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'J-'	  1.00      1  /
% endif
% endif
% endfor
% endfor
% for k in range(dic['regional_noCells'][2]):
% for i in range(dic["top_noCells"]):
% if ((i+1)*round(dic['site_noCells'][0]/dic["top_noCells"]) != 1 and 1+i*round(dic['site_noCells'][0]/dic["top_noCells"])!=dic['site_noCells'][0]) and dic["top_noCells"]>2:
% if i==0:
${i+1+k*dic["top_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${2} ${(i+1)*round(dic['site_noCells'][0]/dic["top_noCells"])} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'J'	  1.00      1  /
% elif i==dic["top_noCells"]-1:
${i+1+k*dic["top_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${1+i*round(dic['site_noCells'][0]/dic["top_noCells"])} ${dic['site_noCells'][0]-1} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'J'	  1.00      1  /
%else:
${i+1+k*dic["top_noCells"]+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${1+i*round(dic['site_noCells'][0]/dic["top_noCells"])} ${(i+1)*round(dic['site_noCells'][0]/dic["top_noCells"])} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} ${k*round(dic['site_noCells'][2]/dic["regional_noCells"][2])+1} ${(k+1)*round(dic['site_noCells'][2]/dic["regional_noCells"][2])}	'J'	  1.00      1  /
% endif
% endif
% endfor
% endfor
/

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
% for i in range(len(dic['site_wellijk'])):
	'INJ${i}'	'G1'	${dic['site_wellijk'][i][0]}	${dic['site_wellijk'][i][1]}	1*	'GAS' /
% endfor
/
COMPDAT
% for i in range(len(dic['site_wellijk'])):
	'INJ${i}'	${dic['site_wellijk'][i][0]}	${dic['site_wellijk'][i][1]}	1	${dic['reference_noCells'][2]}	'OPEN'	1*	1*	0.5 /
% endfor
/
% for j in range(len(dic['inj'])):
WCONINJE
% for i in range(len(dic['site_wellijk'])):
% if dic['inj'][0][3+2*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][0][2*(i+1)] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][0][2*(i+1)] / 1.86843 : E}"}  1* 400/
% else:
'INJ${i}' 'OIL' ${'OPEN' if dic['inj'][0][2*(i+1)] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][0][2*(i+1)] / 998.108 : E}"}  1* 400/
%endif
% endfor
/
AQUFLUX
% for i in range(len(dic['AQUFLUX_left'][0][0])):
${i+1} ${dic['AQUFLUX_left'][j+1][0][i]} /
% endfor
% for i in range(len(dic['AQUFLUX_right'][0][0])):
${i+1+len(dic['AQUFLUX_left'][0][0])} ${dic['AQUFLUX_right'][j+1][0][i]} / 
% endfor
% for i in range(len(dic['AQUFLUX_bottom'][0][0])):
% if ((i%dic["bottom_noCells"]+1)*round(dic['site_noCells'][0]/dic["bottom_noCells"]) != 1 and 1+(i%dic["bottom_noCells"])*round(dic['site_noCells'][0]/dic["bottom_noCells"])!=dic['site_noCells'][0]) and dic["bottom_noCells"]>2:
${i+1+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])} ${dic['AQUFLUX_bottom'][j+1][0][i]} /
% endif
% endfor
% for i in range(len(dic['AQUFLUX_top'][0][0])):
% if ((i%dic["top_noCells"]+1)*round(dic['site_noCells'][0]/dic["top_noCells"]) != 1 and 1+(i%dic["top_noCells"])*round(dic['site_noCells'][0]/dic["top_noCells"])!=dic['site_noCells'][0]) and dic["top_noCells"]>2:
${i+1+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])} ${dic['AQUFLUX_top'][j+1][0][i]} /
% endif
% endfor
/
BCPROP
${1+len(dic['AQUFLUX_left'][0][0])+len(dic['AQUFLUX_right'][0][0])+len(dic['AQUFLUX_bottom'][0][0])+len(dic['AQUFLUX_top'][0][0])} DIRICHLET OIL 1* ${dic['PRESSURE_bottom'][j+1][0][0]} /
/
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor