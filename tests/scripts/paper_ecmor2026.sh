WHR="$PWD"
OUT="test_outputs/paper_ecmor2026"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_plopm.sh
. tests/scripts/get_pycopm.sh
cp -r publications/ecmor2026/. $OUT
cd $OUT/method
. figure1.sh
cd ../results_2d_synthetic_model
. figure2.sh
python3 figure3_table1.py
cd ../results_3d_synthetic_model
python3 figure4_table2.py
cd $WHR

files="
$OUT/method/figure1d_bottom.png
$OUT/method/figure1b.png
$OUT/method/figure1d_top.png
$OUT/method/figure1c_bottom.png
$OUT/method/figure1a.png
$OUT/method/figure1c_top.png
$OUT/results_2d_synthetic_model/figure2.png
$OUT/results_2d_synthetic_model/figureb_dual_vertical_tf_absolute_error_extremes_8.png
$OUT/results_2d_synthetic_model/figurea_dual_no_vertical_tf_absolute_error_extremes_8.png
$OUT/results_2d_synthetic_model/table1_error_summary.csv
$OUT/results_2d_synthetic_model/figurea_standard_absolute_error_extremes_8.png
$OUT/results_2d_synthetic_model/standard_absolute_errors.csv
$OUT/results_2d_synthetic_model/dual_no_vertical_tf_absolute_errors.csv
$OUT/results_2d_synthetic_model/dual_vertical_tf_absolute_errors.csv
$OUT/results_3d_synthetic_model/figure4a_shortest.pvd
$OUT/results_3d_synthetic_model/figure4b_intermediate-0011.vtu
$OUT/results_3d_synthetic_model/table2.csv
$OUT/results_3d_synthetic_model/figure4b_intermediate.pvd
$OUT/results_3d_synthetic_model/figure4c_longest.pvd
$OUT/results_3d_synthetic_model/figure4a_shortest-0011.vtu
$OUT/results_3d_synthetic_model/figure4c_longest-0011.vtu
"

missing_file="test_outputs/missing_publication_files.txt"
missing=0

printf '%s\n' "$files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ ! -f "$f" ]; then
        echo "$f" >> "$missing_file"
        missing=$((missing + 1))
    fi
done

if [ "$missing" -eq 0 ]; then
    echo "All figures and files exist."
    return 0
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
    return 1
fi
