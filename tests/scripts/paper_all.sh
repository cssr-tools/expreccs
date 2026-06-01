if [ ! -d "test_outputs" ]; then
    mkdir "test_outputs"
fi
if [ -d "test_outputs/paper" ]; then
    rm -rf "test_outputs/paper"
fi
mkdir "test_outputs/paper"
cp -r examples/paper_2025/. test_outputs/paper
WHR="test_outputs/paper"
python3 $WHR/Case1/run_case1.py & python3 $WHR/Case2/run_case2.py & python3 $WHR/Case3/run_case3.py & python3 $WHR/Case4/run_case4.py & wait
