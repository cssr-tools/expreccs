if [ -d "test_outputs/non-regular_boundaries" ]; then
    rm -rf "test_outputs/non-regular_boundaries"
fi
mkdir test_outputs/non-regular_boundaries
pycopm -i examples/SIMPLE.DATA -l R -w REFINED -g 199,319,0 -o test_outputs/non-regular_boundaries
cd test_outputs/non-regular_boundaries
pycopm -i REFINED.DATA -l S -w SUBMODEL -v 'xypolygon [15e3,80e3] [60e3,80e3] [60e3,10e3] [55e3,10e3] [55e3,05e3] [50e3,05e3] [50e3,10e3] [33e3,10e3] [33e3,24e3] [15e3,24e3] [15e3,80e3]' -p 0 -m all
mpirun -np 8 flow REFINED.DATA & mpirun -np 8 flow SUBMODEL.DATA & wait
expreccs -i "REFINED SUBMODEL" -n 1 -o expreccs
sed -i.bak "s|REGIONS|REGIONS\nINCLUDE\nOPERNUM_EXPRECCS.INC/\n|g" REFINED.DATA
rm -f REFINED.DATA.bak
mpirun -np 8 flow REFINED.DATA & mpirun -np 8 flow expreccs/EXPRECCS.DATA
plopm -i 'REFINED expreccs/EXPRECCS' -v opernum -s ',,1 ,,1' -r 0 -xunits km -xlnum 5 -yunits km -yformat .0f -ylnum 5 -xformat .0f -subfigs 1,2 -d 16,12 -cbsfax 0.1,0.95,0.8,0.02 -f 30 -c Set1_r
cd ../..
