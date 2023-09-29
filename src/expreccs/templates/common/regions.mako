<%
import math as mt
%>
-- Copyright (C) 2023 NORCE
INCLUDE
'FIPNUM_${reservoir.upper()}.INC' /

EQUALS
% for i in range(dic[f'{reservoir}_noCells'][2]):
SATNUM  ${mt.floor(dic[f'{reservoir}_layers'][i]+1)} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
/