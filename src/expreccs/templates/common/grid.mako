SPECGRID
${dic['site_noCells'][0]} ${dic['site_noCells'][1]} ${dic['site_noCells'][2]} 1 F
/

COORD
% for j in range(dic['site_noCells'][1] + 1):
% for i in range(dic['site_noCells'][0] + 1):
${f"{dic['site_location'][0]+i*dic['site_dsize'][0] : E}"} ${f"{dic['site_location'][1]+j*dic['site_dsize'][1] : E}"} ${f"{dic['site_location'][2]: E}"} ${f"{dic['site_location'][0]+i*dic['site_dsize'][0] : E}"} ${f"{dic['site_location'][1]+j*dic['site_dsize'][1] : E}"} ${f"{dic['site_location'][-1]  : E}"}
% endfor
% endfor
/

ZCORN
% for j in range(2*dic['site_noCells'][1]):
% for i in range(dic['site_noCells'][0]):
 ${f"{0  : E}"} ${f"{0  : E}"}
% endfor
% endfor
% for k in range(dic['site_noCells'][2] - 1):
% for h in range(2):
% for j in range(2*dic['site_noCells'][1]):
% for i in range(dic['site_noCells'][0]):
 ${f"{(k+1)*dic['site_dsize'][2]  : E}"} ${f"{(k+1)*dic['site_dsize'][2]  : E}"}
% endfor
% endfor
% endfor
% endfor
% for j in range(2*dic['site_noCells'][1]):
% for i in range(dic['site_noCells'][0]):
 ${f"{dic['site_location'][-1]  : E}"} ${f"{dic['site_location'][-1]  : E}"}
% endfor
% endfor
/

ACTNUM
% for i in range(dic['site_noCells'][0]*dic['site_noCells'][1]*dic['site_noCells'][2]):
  1
% endfor
/