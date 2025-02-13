#!/bin/bash -l
#PBS -N subset_gustavo_glorys_raw
#PBS -A p93300012
#PBS -l select=1:ncpus=16:mem=50GB
#PBS -l walltime=12:00:00
#PBS -q main
#PBS -m abe
echo "Starting job at `date`"
module load nco
export OMP_NUM_THREADS=16
ncrcat -t 16 -d longitude,-37.68856021347937,-36.093333333333256 -d latitude,4.961175132990646,58.61512088772785 /lustre/desc1/mirrors/cgd/glorys/cmems_mod_glo_phy_my_0.083deg_P1D-m/mercatorglorys12v1_gl12_mean_2*.nc /glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/east_unprocessed_total.nc
ncrcat -t 16 -d longitude,-98.24,-36.093333333333256 -d latitude,4.961175132990646,5.441175132990646 /lustre/desc1/mirrors/cgd/glorys/cmems_mod_glo_phy_my_0.083deg_P1D-m/mercatorglorys12v1_gl12_mean_2*.nc /glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/south_unprocessed_total.nc
ncrcat -t 16 -d longitude,-98.98996846773888,-37.208560213479366 -d latitude,52.537190110517756,58.61512088772785 /lustre/desc1/mirrors/cgd/glorys/cmems_mod_glo_phy_my_0.083deg_P1D-m/mercatorglorys12v1_gl12_mean_2*.nc /glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/north_unprocessed_total.nc
