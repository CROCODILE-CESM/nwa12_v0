#!/bin/bash
#PBS -N process_forcings
#PBS -A ncgd0011
#PBS -q develop
#PBS -l select=1:ncpus=4:mem=64GB
#PBS -l walltime=01:00:00
#PBS -j oe

# Runs CrocoDash's process_forcings background worker on a compute node instead of a
# login node, to avoid the login node's memory ulimit OOM-killing the GLORYS
# download+regrid step. Usage: qsub -v CASE_DIR=/path/to/case_dir pbs_process_forcings.sh

set -euo pipefail

export ESMFMKFILE=/glade/work/manishrv/conda-envs/CrocoDash/lib/esmf.mk

conda run -n CrocoDash python \
    /glade/u/home/manishrv/documents/croc/dev/MCP_CrocoDash/tools/_bg_worker.py \
    "${CASE_DIR}"
