#!/bin/bash -l
#PBS -N regrid_bgc
#PBS -A p93300012
#PBS -l select=1:ncpus=32:mem=55gb
#PBS -l walltime=12:00:00
#PBS -q main
#PBS -m abe


mamba activate CrocoDash
python /glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regrid_raw_data.py

