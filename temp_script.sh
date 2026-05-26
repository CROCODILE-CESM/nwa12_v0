#!/bin/bash

SRC="/glade/campaign/cesm/cesmdata/inputdata/ocn/mom/croc/rof/glofas/dis24/merged_yearly_nc3_files"
DST="/glade/campaign/cesm/cesmdata/inputdata/ocn/glofas/v4"

for f in "$SRC"/GloFAS_*.nc; do
    year=$(basename "$f" | sed 's/GloFAS_\([0-9]\{4\}\)\.nc/\1/')
    cp "$f" "$DST/GLOFAS.v4.dis24.${year}.nc"
    echo "Copied: GloFAS_${year}.nc -> GLOFAS.v4.dis24.${year}.nc"
done

echo "Done."