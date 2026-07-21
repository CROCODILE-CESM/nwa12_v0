#!/bin/bash -l
#PBS -N gustavo_glorys_merged
#PBS -A p93300012
#PBS -l select=1:ncpus=4:mem=100GB
#PBS -l walltime=12:00:00
#PBS -q main
#PBS -m abe
echo "Starting job at `date`"
conda activate CrocoDash
python /glade/u/home/manishrv/documents/croc/dev/gustavo_glorys/merge_rm6_output_files.py