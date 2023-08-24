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
    1*       1*        5       100      1         1000 /
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
1 1 ${dic['site_noCells'][0]} 1 1 1* 1* Y- /
2 1 ${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][1]} 1* 1* Y /
3 1 1 1 ${dic['site_noCells'][1]} 1* 1* X- /
4 ${dic['site_noCells'][0]} ${dic['site_noCells'][0]} 1 ${dic['site_noCells'][1]} 1* 1* X /
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
BCPROP 
1 FREE /
2 FREE /
3 FREE /
4 FREE /
/
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor