OUT="test_outputs/regular_boundaries"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_plopm.sh
. tests/scripts/get_pytest.sh
WHR="test_outputs/popen-gw2/test_2_generic_deck0/rotate/simulations"
if [ ! -d $WHR ]; then
    pytest --basetemp=$OUT -n 2 tests/test_2_generic_deck.py tests/test_4_site_regional.py
    WHR="$OUT/popen-gw0/test_2_generic_deck0/rotate/simulations"
    WHR1="$OUT/popen-gw1/test_4_site_regional0"
else
    WHR1="test_outputs/popen-gw4/test_4_site_regional0"
fi
plopm -i "$WHR/site_closed/SITE_CLOSED $WHR/expreccs/EXPRECCS $WHR/reference/REFERENCE" -v sgas -s ',,1 ,,1 ,,1' -subfigs 1,3 -suptitle 0 -cbsfax 0.2,0.95,0.6,0.02 -d 24,8 -cformat .1f -f 20 -xunits km -yunits km -xformat .0f -yformat .0f -x '[0,15000]' -y '[0,15000]' -delax 1 -o $OUT
plopm -i "$WHR1/regional/REGIONAL $WHR1/expreccs/EXPRECCS $WHR1/expreccs_dpincrease/EXPRECCS_DPINCREASE $WHR1/expreccs_perfipnum/EXPRECCS_PERFIPNUM" -v rpr:3 -o $OUT -step 1
