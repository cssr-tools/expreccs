if [ -d "test_outputs/regular_boundaries" ]; then
    rm -rf "test_outputs/regular_boundaries"
fi
mkdir test_outputs/regular_boundaries
WHR="test_outputs/popen-gw2/test_2_generic_deck0/rotate/simulations"
plopm -i "$WHR/site_closed/SITE_CLOSED $WHR/expreccs/EXPRECCS $WHR/reference/REFERENCE" -v sgas -s ',,1 ,,1 ,,1' -subfigs 1,3 -suptitle 0 -cbsfax 0.2,0.95,0.6,0.02 -d 24,8 -cformat .1f -f 20 -xunits km -yunits km -xformat .0f -yformat .0f -x '[0,15000]' -y '[0,15000]' -delax 1 -o test_outputs/regular_boundaries

WHR="test_outputs/popen-gw4/test_4_site_regional0"
plopm -i "$WHR/regional/REGIONAL $WHR/expreccs/EXPRECCS $WHR/expreccs_dpincrease/EXPRECCS_DPINCREASE $WHR/expreccs_perfipnum/EXPRECCS_PERFIPNUM" -v rpr:3 -o test_outputs/regular_boundaries
