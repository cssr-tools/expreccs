if [ -d "test_outputs/hello_world" ]; then
    rm -rf "test_outputs/hello_world"
fi
expreccs -i examples/example1.toml -o test_outputs/hello_world
expreccs -i examples/example1_pres.toml -o test_outputs/hello_world -m site
expreccs -i examples/example1_porvproj.toml -o test_outputs/hello_world -m site
expreccs -i examples/example1_wells.toml -o test_outputs/hello_world -m site -p all
cp test_outputs/hello_world/postprocessing/hello_world_sensor_pressure_over_time.png test_outputs/hello_world
cp test_outputs/hello_world/postprocessing/hello_world_summary_BHP_site_reference.png test_outputs/hello_world
cp test_outputs/hello_world/postprocessing/hello_world_distance_from_border.png test_outputs/hello_world
cp test_outputs/hello_world/postprocessing/hello_world_reference_watfluxi+.png test_outputs/hello_world
cp test_outputs/hello_world/postprocessing/hello_world_regional_watfluxi+.png test_outputs/hello_world
cp test_outputs/hello_world/postprocessing/hello_world_site_flux_watfluxi+.png test_outputs/hello_world