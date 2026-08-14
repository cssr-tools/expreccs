OUT="test_outputs/paper_2025"
. tests/scripts/initialize_output_folders.sh $OUT
cp -r examples/paper_2025/. $OUT
python3 $OUT/Case1/run_case1.py &
python3 $OUT/Case2/run_case2.py &
python3 $OUT/Case3/run_case3.py &
python3 $OUT/Case4/run_case4.py &
wait

files=(
    "$OUT/Case4/Case_4_site_pres_pressure.png"
    "$OUT/Case4/Case_4_reference_saturation.png"
    "$OUT/Case4/Case_4_difference_site_pres_pressure.png"
    "$OUT/Case4/Case_4_reference_pressure.png"
    "$OUT/Case4/Case_4_difference_site_pres_saturation.png"
    "$OUT/Case4/Case_4_regional_pressure.png"
    "$OUT/Case4/Case_4_site_pres_saturation.png"
    "$OUT/Case4/Case_4_regional_saturation.png"
    "$OUT/Case2/comparegrid_0_40m_sensor_pressure_over_time.png"
    "$OUT/Case2/comparegrid_0_40m_sensor_gasfluxi+_over_time.png"
    "$OUT/Case3/compareeveryday_sensor_pressure_over_time.png"
    "$OUT/Case1/Case_1_maximum_pressure_difference_over_time.png"
    "$OUT/Case1/Case_1_difference_site_flux_pressure.png"
    "$OUT/Case1/Case_1_difference_site_flux_gasfluxi+.png"
    "$OUT/Case1/Case_1_maximum_gasfluxi+_difference_over_time.png"
    "$OUT/Case1/Case_1_reference_saturation.png"
    "$OUT/Case1/Case_1_reference_pressure.png"
    "$OUT/Case1/Case_1_reference_watfluxi+.png"
    "$OUT/Case1/Case_1_distance_from_border.png"
    "$OUT/Case1/Case_1_difference_site_flux_saturation.png"
    "$OUT/Case1/Case_1_difference_site_pres_saturation.png"
    "$OUT/Case1/Case_1_summary_PR_site_reference.png"
    "$OUT/Case1/Case_1_difference_site_pres_gasfluxi+.png"
    "$OUT/Case1/Case_1_difference_site_pres_pressure.png"
)

missing_file="test_outputs/missing_paper_2025_files.txt"
missing=0

rm -f "$missing_file"

for f in "${files[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "$f" >> "$missing_file"
        ((missing++))
    fi
done

if (( missing == 0 )); then
    echo "All figures and files exist."
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
fi
