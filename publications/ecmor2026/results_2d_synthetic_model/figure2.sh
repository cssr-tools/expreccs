flow FIGURE2.DATA --relaxed-max-pv-fraction=0 --enable-tuning=true --enable-dry-run=1 --output-dir=figure2
plopm -i figure2/FIGURE2 -v 'fluxnum - 1' -grid 'black,1e-2' -clabel 'Net 0, non-net 1' -f 8 -save figure2 -remove 0,0,0,1
