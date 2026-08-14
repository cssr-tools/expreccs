. tests/scripts/docs_hello_world.sh &
. tests/scripts/docs_regular_boundaries.sh &
. tests/scripts/docs_non-regular_boundaries.sh &
wait

. ./tests/scripts/docs_check_figures.sh
