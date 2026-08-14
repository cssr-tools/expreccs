files=(
  "test_outputs/hello_world/hello_world_distance_from_border.png"
  "test_outputs/hello_world/hello_world_reference_watfluxi+.png"
  "test_outputs/hello_world/hello_world_regional_watfluxi+.png"
  "test_outputs/hello_world/hello_world_sensor_pressure_over_time.png"
  "test_outputs/hello_world/hello_world_site_flux_watfluxi+.png"
  "test_outputs/hello_world/hello_world_summary_BHP_site_reference.png"
  "test_outputs/non-regular_boundaries/expreccs_opernum_i,j,1_t0.png"
  "test_outputs/regular_boundaries/reference_sgas_i,j,1_t90.png"
  "test_outputs/regular_boundaries/regional_rpr-3.png"
)

missing_file="test_outputs/missing_figures.txt"
missing=0

rm -f "$missing_file"

for f in "${files[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "$f" >> "$missing_file"
        ((missing++))
    fi
done

if (( missing == 0 )); then
    echo "All figures exist."
else
    echo "$missing figure(s) missing."
    echo "See $missing_file"
fi
