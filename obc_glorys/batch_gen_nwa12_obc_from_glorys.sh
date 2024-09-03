#!/bin/bash -l
#PBS -N gen_nwa12_obc
#PBS -A NCGD0011
#PBS -l select=1:ncpus=1:mem=80GB
#PBS -l walltime=12:00:00
#PBS -q casper
#PBS -m abe
#PBS -M fredc@ucar.edu


#module load nco
conda activate sparse

jupyter nbconvert --to notebook  --ExecutePreprocessor.kernel_name=python3 --execute gen_nwa12_obc_from_glorys.ipynb
