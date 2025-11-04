INCLUDE
'${exe}/deck/RUNSPEC.INC' /

% if post != "post":
GRIDFILE                               
0 0 /
% endif

INCLUDE                                
'${exe}/deck/CGRID.INC' /

INCLUDE                                
'${exe}/deck/CPORO.INC' /

INCLUDE                                
'${exe}/deck/CPERMX.INC' /

COPY 
PERMX PERMY /
PERMX PERMZ /
/

EDIT

INCLUDE
'${exe}/deck/CPORV.INC' /

INCLUDE
'${exe}/deck/CTRANX.INC' /

INCLUDE
'${exe}/deck/CTRANY.INC' /

INCLUDE
'${exe}/deck/CTRANZ.INC' /

INCLUDE
'${exe}/deck/CEDITNNC.INC' /

INCLUDE                                
'${exe}/deck/PROPS.INC' /

INCLUDE                                
'${exe}/deck/SCHEDULE.INC' /

WELSPECS
% for i in range(nwells):
INJ${0 if i<10 else ''}${int(i)} G1 ${int(points[f"i{0 if i<10 else ''}{int(i)}"])} ${int(points[f"j{0 if i<10 else ''}{int(i)}"])} 1* GAS /
% endfor
/

COMPDAT
% for i in range(nwells):
INJ${0 if i<10 else ''}${int(i)} ${int(points[f"i{0 if i<10 else ''}{int(i)}"])} ${int(points[f"j{0 if i<10 else ''}{int(i)}"])} ${1 if int(points[f"k{0 if i<10 else ''}{int(i)}"])==1 else 5} ${3 if int(points[f"k{0 if i<10 else ''}{int(i)}"])==1 else 5} OPEN 2* 0.2 /
% endfor
/

WCONINJE
% for i in range(nwells):
INJ${0 if i<10 else ''}${int(i)} GAS OPEN RATE ${mass/(time*365.25*nwells)} 1* 480 /
% endfor
/
TSTEP
${time*365.25} /
