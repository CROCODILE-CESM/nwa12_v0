"""
Recreate the master scaling-test case (scaling_n1 / scaling_test inputdir) with a
30-day GLORYS date range instead of the original 4-day one, then actually run
process_forcings (the slow GLORYS download + regrid step) for that wider window.

override=True is safe here because this re-creates the SAME case (same caseroot,
same inputdir, same grid name "scaling_test") rather than a second, concurrent
one — it's the intended "recreate this case" use of override, not the
global-grid-registry collision that override=True would risk for a *different*
case sharing the same grid name (see create_ntasks_case_workaround.py).

Run this BEFORE (re)creating any of the per-NTASKS_OCN cases, since they all
point their user_nl_mom INPUTDIR at this master's ocnice/ folder instead of
copying files — whatever ends up here is what every case actually reads at
build/run time.

Usage:
    conda run -n CrocoDash python reprocess_master_30day.py
"""

import json
from pathlib import Path

MASTER_CASE_DIR = Path("/glade/u/home/manishrv/scratch/croc_input/scaling_test")
MASTER_CASEROOT = Path("/glade/u/home/manishrv/croc_cases/scaling_n1")
CESMROOT = Path("/glade/u/home/manishrv/work/installs/CROCESM_workshop_2025")
COMPSET = "1850_DATM%NYF_SLND_SICE_MOM6%REGIONAL_SROF_SGLC_SWAV"
MACHINE = "derecho"
ATM_GRID_NAME = "T62"
PROJECT = "ncgd0011"
JOB_QUEUE = "develop"
DATE_RANGE = ["2020-01-01", "2020-01-31"]  # 30-day run


def reconstruct_grid_objects(case_dir: Path):
    from CrocoDash.grid import Grid
    from CrocoDash.topo import Topo
    from CrocoDash.vgrid import VGrid
    from mom6_forge.git_utils import get_domain_dir

    params = json.loads((case_dir / "mcp_grid_params.json").read_text())

    grid = Grid(
        lenx=params["lenx"],
        leny=params["leny"],
        resolution=params["resolution"],
        xstart=params["lon_min"],
        ystart=params["lat_min"],
        name=params["grid_name"],
    )

    topo_library_dir = params.get("topo_library_dir", str(case_dir / "TopoLibrary"))
    domain_dir = get_domain_dir(grid, base_dir=topo_library_dir)
    topo = Topo.from_version_control(domain_dir)

    vgrid = VGrid.uniform(nk=params["nk"], depth=params["depth"], name=params["grid_name"])

    return grid, topo, vgrid


def main():
    from CrocoDash.case import Case

    grid, topo, vgrid = reconstruct_grid_objects(MASTER_CASE_DIR)

    print(f"Recreating master case at {MASTER_CASEROOT} with override=True ...", flush=True)
    case = Case(
        cesmroot=CESMROOT,
        caseroot=MASTER_CASEROOT,
        inputdir=MASTER_CASE_DIR,
        compset=COMPSET,
        ocn_grid=grid,
        ocn_topo=topo,
        ocn_vgrid=vgrid,
        atm_grid_name=ATM_GRID_NAME,
        machine=MACHINE,
        project=PROJECT,
        override=True,
        ntasks_ocn=1,
        job_queue=JOB_QUEUE,
    )

    print(f"Configuring forcings for date_range={DATE_RANGE} ...", flush=True)
    case.configure_forcings(
        date_range=DATE_RANGE,
        boundaries=["south", "north", "west", "east"],
        product_name="GLORYS",
        function_name="get_glorys_data_from_rda",
    )

    print("Processing forcings (GLORYS download + regrid — this is the slow step) ...", flush=True)
    case.process_forcings()

    print(f"Done. Master forcings at {MASTER_CASE_DIR / 'ocnice'} now cover {DATE_RANGE}.", flush=True)


if __name__ == "__main__":
    main()
