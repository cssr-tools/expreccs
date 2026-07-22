cd results
flow MODEL.DATA --enable-dry-run=1
flow FILLED_MODEL.DATA --enable-opm-rst-file=true # You can run in parallel (e.g., mpirun -np 32); however, this would make the time in Table 3 no comparable (these dual models cannot be run in parallel, known issue in OPM Flow side)
pycopm -i FILLED_MODEL.DATA -a max -t 2 -z 1:30,31:56,57:111,112:116,117:217 -l C -w STANDARD_COARSENED_MODEL -m prep
pycopm -i FILLED_MODEL.DATA -a max -t 2 -z 1:30,31:56,57:111,112:116,117:217 -l C -w STANDARD_COARSENED_MODEL -m deck &
pycopm -i FILLED_MODEL.DATA -a max -t 2 -z 1:30,31:56,57:111,112:116,117:217 -l D -w DUAL_VERTICAL_TF_COARSENED_MODEL -dual 'poro == 0.1' -m deck &
pycopm -i FILLED_MODEL.DATA -a max -t 2 -z 1:30,31:56,57:111,112:116,117:217 -l DNOVTF -w DUAL_NO_VERTICAL_TF_COARSENED_MODEL -dual 'poro == 0.1, vertical TF = 0' -m deck &
wait
flow STANDARD_COARSENED_MODEL.DATA --enable-opm-rst-file=true &
flow DUAL_VERTICAL_TF_COARSENED_MODEL.DATA --enable-opm-rst-file=true &
flow DUAL_NO_VERTICAL_TF_COARSENED_MODEL.DATA --enable-opm-rst-file=true & 
wait
cd ..
