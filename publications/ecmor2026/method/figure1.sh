flow METHOD --output-dir=figure1
pycopm -i METHOD.DATA -t 2 -a max -z 1:4 -l D -dual 'poro == 0.1' -o figure1
flow figure1/METHOD_PYCOPM
plopm -i figure1/METHOD -v 'fluxnum - 1' -xlnum 5 -ylnum 5 -grid black,1e-2 -clabel 'Net 0, non-net 1' -f 16 -t "Input grid $\Omega$" -save figure1a
plopm -i figure1/METHOD_PYCOPM -v 'fluxnum - 1' -xlnum 5 -ylnum 5 -grid black,1e-2 -clabel 'Net 0, non-net 1' -f 16 -t "Standard $\Omega^{*}$" -global 1 -remove 0,0,1,0 -save figure1b
plopm -i figure1/METHOD_PYCOPM -v 'fluxnum - 1' -xlnum 5 -ylnum 5 -grid black,1e-2 -clabel 'Net 0, non-net 1' -f 16 -t "Dual (vertical TF) $\Omega_\epsilon^{*,net}$, j=1" -global 1 -remove 0,1,1,0 -save figure1c_top
plopm -i figure1/METHOD_PYCOPM -v 'fluxnum - 1' -s ,3, -xlnum 5 -ylnum 5 -grid black,1e-2 -clabel 'Net 0, non-net 1' -f 16 -t "Dual (vertical TF) $\Omega_\epsilon^{*,non-net}$, j=3" -global 1 -remove 0,0,1,0 -save figure1c_bottom
plopm -i figure1/METHOD_PYCOPM -v 'fluxnum - 1' -xlnum 5 -ylnum 5 -grid black,1e-2 -clabel 'Net 0, non-net 1' -f 16 -t "Dual (no vertical TF) $\Omega_\epsilon^{*,net}$, j=1" -global 1 -remove 0,1,1,0 -save figure1d_top
plopm -i figure1/METHOD_PYCOPM -v 'fluxnum - 1' -s ,3, -xlnum 5 -ylnum 5 -grid black,1e-2 -clabel 'Net 0, non-net 1' -f 16 -t "Dual (no vertical TF) c $\Omega_\epsilon^{*,non-net}$, j=3" -global 1 -remove 0,0,1,0 -save figure1d_bottom
