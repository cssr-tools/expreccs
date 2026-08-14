OUT="test_outputs/paper_2025"
. tests/scripts/initialize_output_folders.sh $OUT
cp -r examples/paper_2025/. $OUT
python3 $OUT/Case1/run_case1.py &
python3 $OUT/Case2/run_case2.py &
python3 $OUT/Case3/run_case3.py &
python3 $OUT/Case4/run_case4.py &
wait
