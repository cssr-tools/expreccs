OUT="test_outputs/hello_world"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_plopm.sh
expreccs -i examples/example1.toml -o $OUT
expreccs -i examples/example1_pres.toml -o $OUT -m site
expreccs -i examples/example1_porvproj.toml -o $OUT -m site
expreccs -i examples/example1_wells.toml -o $OUT -m site -p all
cp $OUT/postprocessing/hello_world_sensor_pressure_over_time.png $OUT
cp $OUT/postprocessing/hello_world_summary_BHP_site_reference.png $OUT
cp $OUT/postprocessing/hello_world_distance_from_border.png $OUT
cp $OUT/postprocessing/hello_world_reference_watfluxi+.png $OUT
cp $OUT/postprocessing/hello_world_regional_watfluxi+.png $OUT
cp $OUT/postprocessing/hello_world_site_flux_watfluxi+.png $OUT
