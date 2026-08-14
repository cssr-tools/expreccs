if ! command -v pytest &> /dev/null; then
    pip install pytest-xdist pytest-cov
fi
