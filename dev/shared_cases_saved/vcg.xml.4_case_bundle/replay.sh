#!/bin/bash

set -e

# Created 2026-03-30 10:41:56

CASEDIR="/glade/u/home/manishrv/croc_cases/vcg.xml.4"

/glade/u/home/manishrv/work/installs/CROCESM_testing/cime/scripts/create_newcase --compset 1850_DATM%NYF_SLND_SICE_MOM6%REGIONAL_SROF_SGLC_SWAV --res USER_RES --case "${CASEDIR}" --machine derecho --run-unsupported --project NCGD0011 --non-local

cd "${CASEDIR}"

./xmlchange OCN_NX=60 --non-local

./xmlchange OCN_NY=60 --non-local

./xmlchange OCN_DOMAIN_MESH=/glade/u/home/manishrv/scratch/croc_input/vcg.xml.4/ocnice/ESMF_mesh_panama1_5b36e8.nc --non-local

./xmlchange ICE_DOMAIN_MESH=/glade/u/home/manishrv/scratch/croc_input/vcg.xml.4/ocnice/ESMF_mesh_panama1_5b36e8.nc --non-local

./xmlchange MASK_MESH=/glade/u/home/manishrv/scratch/croc_input/vcg.xml.4/ocnice/ESMF_mesh_panama1_5b36e8.nc --non-local

./xmlchange ATM_GRID=T62 --non-local

./xmlchange LND_GRID=T62 --non-local

./xmlchange ATM_DOMAIN_MESH=/glade/campaign/cesm/cesmdata/inputdata/share/meshes/T62_040121_ESMFmesh.nc --non-local

./xmlchange LND_DOMAIN_MESH=/glade/campaign/cesm/cesmdata/inputdata/share/meshes/T62_040121_ESMFmesh.nc --non-local

./case.setup --non-local

./xmlchange MOM6_MEMORY_MODE=dynamic_symmetric --non-local

./xmlchange RUN_STARTDATE=2000-01-01 --non-local

./xmlchange STOP_OPTION=ndays --non-local

./xmlchange STOP_N=2 --non-local

./xmlchange NTASKS_OCN=12

./case.setup --reset

./case.build

./case.submit

./preview_namelists

./xmlchange STOP_N=2

./case.submit

