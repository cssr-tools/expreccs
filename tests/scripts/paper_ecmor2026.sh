HOME="$PWD"
OUT="test_outputs/paper_ecmor2026"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_plopm.sh
. tests/scripts/get_pycopm.sh
cp -r publications/ecmor2026/. $OUT
cd $OUT/method
. figure1.sh
cd $OUT/results_2d_synthetic_model
. figure2.sh
python3 figure3_table1.py
cd $OUT/results_3d_synthetic_model
python3 figure4_table2.py
cd $HOME
