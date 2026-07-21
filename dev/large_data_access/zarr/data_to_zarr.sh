#!/bin/bash -l
#PBS -N data_to_zarr
#PBS -A p93300012
#PBS -l select=1:ncpus=32:mem=50GB
#PBS -l walltime=12:00:00
#PBS -q main
#PBS -m abe
echo "Starting job at `date`"
conda activate largedata
python /glade/u/home/manishrv/documents/croc/dev/large_data_access/tpxo_to_zarr.py