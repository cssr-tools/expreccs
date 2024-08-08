CURRENT_DIRECTORY="$PWD"

for module in common
do   git clone https://gitlab.dune-project.org/core/dune-$module.git --branch v2.9.1
done
for module in common
do   ./dune-common/bin/dunecontrol --only=dune-$module cmake -DCMAKE_DISABLE_FIND_PACKAGE_MPI=1
     ./dune-common/bin/dunecontrol --only=dune-$module make -j5
done

for repo in common
do
    git clone https://github.com/OPM/opm-$repo.git
done

source vexpreccs/bin/activate

mkdir build

for repo in common
do
    mkdir build/opm-$repo
    cd build/opm-$repo
    cmake -DPYTHON_EXECUTABLE=$(which python) -DWITH_NDEBUG=1 -DUSE_MPI=0 -DOPM_ENABLE_PYTHON=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$CURRENT_DIRECTORY/dune-common/build-cmake;$CURRENT_DIRECTORY/dune-grid/build-cmake;$CURRENT_DIRECTORY/dune-geometry/build-cmake;$CURRENT_DIRECTORY/dune-istl/build-cmake;$CURRENT_DIRECTORY/build/opm-common;$CURRENT_DIRECTORY/build/opm-grid" $CURRENT_DIRECTORY/opm-$repo
    make -j5
    cd ../..
done

echo "export PYTHONPATH=\$PYTHONPATH:$CURRENT_DIRECTORY/build/opm-common/build/python" >> $CURRENT_DIRECTORY/vexpreccs/bin/activate