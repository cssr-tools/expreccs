<%
import math as mt
def mainfold(i, j, x, y):
    z = 0
    if reservoir in ["regional", "reference"]:
        if i < dic[f"{reservoir}_fault"][0] or j < dic[f"{reservoir}_fault"][1]:
            z += dic["fault_regional"][4]
    return z
%>
% for j in range(dic[f'{reservoir}_num_cells'][1]):
% for i in range(dic[f'{reservoir}_num_cells'][0]):
${f"{mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i], dic[f'{reservoir}_ymy'][j]):E}"} ${f"{mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i+1], dic[f'{reservoir}_ymy'][j]):E}"} \
% endfor
% for i in range(dic[f'{reservoir}_num_cells'][0]):
${f"{mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i], dic[f'{reservoir}_ymy'][j+1]):E}"} ${f"{mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i+1], dic[f'{reservoir}_ymy'][j+1]):E}"} \
% endfor
% endfor
% for k in range(dic[f'{reservoir}_num_cells'][2] - 1):
% for h in range(2):
% for j in range(dic[f'{reservoir}_num_cells'][1]):
% for i in range(dic[f'{reservoir}_num_cells'][0]):
${f"{dic[f'{reservoir}_zmz'][k+1] + mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i], dic[f'{reservoir}_ymy'][j]):E}"} ${f"{dic[f'{reservoir}_zmz'][k+1] +  mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i+1], dic[f'{reservoir}_ymy'][j]):E}"} \
% endfor
% for i in range(dic[f'{reservoir}_num_cells'][0]):
${f"{dic[f'{reservoir}_zmz'][k+1] + mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i], dic[f'{reservoir}_ymy'][j+1]):E}"} ${f"{dic[f'{reservoir}_zmz'][k+1] +  mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i+1], dic[f'{reservoir}_ymy'][j+1]):E}"} \
% endfor
% endfor
% endfor
% endfor
% for j in range(dic[f'{reservoir}_num_cells'][1]):
% for i in range(dic[f'{reservoir}_num_cells'][0]):
${f"{dic[f'{reservoir}_dims'][2] + mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i], dic[f'{reservoir}_ymy'][j]):E}"} ${f"{dic[f'{reservoir}_dims'][2] +  mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i+1], dic[f'{reservoir}_ymy'][j]):E}"} \
% endfor
% for i in range(dic[f'{reservoir}_num_cells'][0]):
${f"{dic[f'{reservoir}_dims'][2] +  mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i], dic[f'{reservoir}_ymy'][j+1]):E}"} ${f"{dic[f'{reservoir}_dims'][2] +  mainfold(i-1, j-1, dic[f'{reservoir}_xmx'][i+1], dic[f'{reservoir}_ymy'][j+1]):E}"} \
% endfor
% endfor