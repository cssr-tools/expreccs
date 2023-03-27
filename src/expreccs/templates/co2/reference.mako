----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['reference_noCells'][0]} ${dic['reference_noCells'][1]} ${dic['reference_noCells'][2]} /

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
${len(dic['reference_wellijk'])} ${dic['site_noCells'][2]} ${len(dic['reference_wellijk'])} ${len(dic['reference_wellijk'])} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT

DX 
  ${dic['reference_noCells'][0]*dic['reference_noCells'][1]*dic['reference_noCells'][2]}*${round(dic['reference_dims'][0]/dic['reference_noCells'][0])} /
DY 
  ${dic['reference_noCells'][0]*dic['reference_noCells'][1]*dic['reference_noCells'][2]}*${round(dic['reference_dims'][1]/dic['reference_noCells'][1])} /
DZ 
  ${dic['reference_noCells'][0]*dic['reference_noCells'][1]*dic['reference_noCells'][2]}*${round(dic['reference_dims'][2]/dic['reference_noCells'][2])} /
TOPS
% for k in range(dic['reference_noCells'][2]):
% for j in range(dic['reference_noCells'][1]):
% for i in range(dic['reference_noCells'][0]):
% if i >= dic["reference_fault"][0] and j >= dic["reference_fault"][1]:
${k*round(dic['reference_dims'][2]/dic['reference_noCells'][2])-0.5*round(dic['reference_dims'][2]/dic['reference_noCells'][2])}
%else:
${k*round(dic['reference_dims'][2]/dic['reference_noCells'][2])}
%endif
%endfor
%endfor
%endfor
/

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
% for k in range(dic['reference_noCells'][2]):
<%
n = 0
%>
% for j in range(dic['reference_noCells'][1]):
% for i in range(dic['reference_noCells'][0]):
% if i == dic["reference_fault"][0] and j >= dic["reference_fault"][1]:
${dic["fault_mult"][0]}
% elif i == dic["reference_site_fault"][0][0] + n and j == dic["reference_site_fault"][0][1] + n and i <= dic["reference_site_fault"][1][0] and j <= dic["reference_site_fault"][1][1]:
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
% for k in range(dic['reference_noCells'][2]):
<%
n = 0
%>
% for j in range(dic['reference_noCells'][1]):
% for i in range(dic['reference_noCells'][0]):
% if j == dic["reference_fault"][1] and i >= dic["reference_fault"][0]:
${dic["fault_mult"][1]}
% elif i == dic["reference_site_fault"][0][0] + n and j == dic["reference_site_fault"][0][1] + n and i <= dic["reference_site_fault"][1][0] and j <= dic["reference_site_fault"][1][1]:
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

----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC' /

----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/FIPNUM_REFERENCE.INC' /

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

BC 
1 ${dic['reference_noCells'][0]} 1 1 1* 1* Y- FREE /
1 ${dic['reference_noCells'][0]} ${dic['reference_noCells'][1]} ${dic['reference_noCells'][1]} 1* 1* Y FREE /
1 1 1 ${dic['reference_noCells'][1]} 1* 1* X- FREE /
${dic['reference_noCells'][0]} ${dic['reference_noCells'][0]} 1 ${dic['reference_noCells'][1]} 1* 1* X FREE /
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
% for i in range(len(dic['reference_wellijk'])):
	'INJ${i}'	'G1'	${dic['reference_wellijk'][i][0]}	${dic['reference_wellijk'][i][1]}	1*	'GAS' /
% endfor
/
COMPDAT
% for i in range(len(dic['reference_wellijk'])):
	'INJ${i}'	${dic['reference_wellijk'][i][0]}	${dic['reference_wellijk'][i][1]}	1	${dic['reference_noCells'][2]}	'OPEN'	1*	1*	0.5 /
% endfor
/
% for j in range(len(dic['inj'])):
WCONINJE
% for i in range(len(dic['reference_wellijk'])):
% if dic['inj'][j][3+2*i] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][2*(i+1)] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+1)] / 1.86843 : E}"}  1* 400/
% else:
'INJ${i}' 'OIL' ${'OPEN' if dic['inj'][j][2*(i+1)] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][2*(i+1)] / 998.108 : E}"}  1* 400/
%endif
% endfor
/
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor