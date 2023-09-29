<%
import math as mt
%>
-- Copyright (C) 2023 NORCE

INIT

INCLUDE
  'GRID_${reservoir.upper()}.INC' /

EQUALS
% for i in range(dic[f'{reservoir}_noCells'][2]):
PERMX  ${dic['rock'][int(dic[f"{reservoir}_layers"][i])][0]} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
/

EQUALS
% for i in range(dic[f'{reservoir}_noCells'][2]):
PERMZ  ${dic['rock'][int(dic[f"{reservoir}_layers"][i])][1]} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
/

COPY 
PERMX PERMY /
/

EQUALS
% for i in range(dic[f'{reservoir}_noCells'][2]):
PORO  ${dic['rock'][int(dic[f"{reservoir}_layers"][i])][2]} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
/

% if reservoir == "regional":

MULTX
% for k in range(dic['regional_noCells'][2]):
% for j in range(dic['regional_noCells'][1]):
% for i in range(dic['regional_noCells'][0]):
% if i == dic["regional_fault"][0] and j > dic["regional_fault"][1]:
${dic["fault_mult"][0]}
%else:
1.0
%endif
%endfor
%endfor
%endfor
/

MULTY
% for k in range(dic['regional_noCells'][2]):
% for j in range(dic['regional_noCells'][1]):
% for i in range(dic['regional_noCells'][0]):
% if j == dic["regional_fault"][1] and i > dic["regional_fault"][0]:
${dic["fault_mult"][1]}
%else:
1.0
%endif
%endfor
%endfor
%endfor
/

% elif reservoir == "reference":

MULTX
% for k in range(dic['reference_noCells'][2]):
<%
n = 0
%>
% for j in range(dic['reference_noCells'][1]):
% for i in range(dic['reference_noCells'][0]):
% if i == dic["reference_fault"][0] and j > dic["reference_fault"][1]:
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
% if j == dic["reference_fault"][1] and i > dic["reference_fault"][0]:
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


% else:
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
% endif