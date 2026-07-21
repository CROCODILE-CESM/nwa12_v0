"""
Create the NTASKS_OCN=40 case for a location-scaling test, reusing a master
case's already-processed forcings instead of reprocessing GLORYS.

Same workaround as create_ntasks_case_workaround.py (CrocoDash's Case.__init__
requires override=True whenever inputdir exists, and override=True wipes the
whole inputdir) — give the N=40 case its own fresh inputdir/caseroot/grid name,
reconstruct Grid/Topo/VGrid directly from the master's existing ocnice/ netCDF
files, then repoint user_nl_mom's INPUTDIR/GRID_FILE/TOPO_FILE/
ALE_COORDINATE_CONFIG at the master's ocnice/ folder so MOM6 reads the
master's forcing/grid files directly instead of this case's own copies.

Usage:
    conda run -n CrocoDash python create_location_ntasks40_case.py <location_name>

<location_name> must have a corresponding master case at
    croc_input/scaling/loc_<location_name>            (inputdir, NTASKS=20)
    croc_cases_scaling/loc_<location_name>_n20         (caseroot)
"""

import json
import re
import sys
from pathlib import Path

CROC_INPUT_SCALING = Path("/glade/u/home/manishrv/scratch/croc_input/scaling")
CROC_CASES_SCALING = Path("/glade/u/home/manishrv/scratch/croc_cases_scaling")
CESMROOT = Path("/glade/u/home/manishrv/work/installs/CROCESM_workshop_2025")
COMPSET = "1850_DATM%NYF_SLND_SICE_MOM6%REGIONAL_SROF_SGLC_SWAV"
MACHINE = "derecho"
ATM_GRID_NAME = "T62"
PROJECT = "ncgd0011"
JOB_QUEUE = "develop"
DATE_RANGE = ["2020-01-01", "2020-01-25"]
NTASKS_OCN = 40


def point_case_at_master(caseroot: Path, master_ocnice: Path):
    def master_file(prefix: str) -> str:
        matches = sorted(master_ocnice.glob(f"{prefix}*.nc"))
        if not matches:
            raise FileNotFoundError(f"No {prefix}*.nc found in {master_ocnice}")
        return matches[0].name

    replacements = {
        "INPUTDIR": str(master_ocnice),
        "GRID_FILE": master_file("ocean_hgrid_"),
        "TOPO_FILE": master_file("ocean_topog_"),
        "ALE_COORDINATE_CONFIG": f"FILE:{master_file('ocean_vgrid_')}",
    }

    user_nl_mom = caseroot / "user_nl_mom"
    lines = user_nl_mom.read_text().splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(\w+)\s*=", line)
        if m and m.group(1) in replacements:
            lines[i] = f"{m.group(1)} = {replacements[m.group(1)]}"
    user_nl_mom.write_text("\n".join(lines) + "\n")


def reconstruct_grid_objects(master_ocnice: Path, grid_name: str):
    from CrocoDash.grid import Grid
    from CrocoDash.topo import Topo
    from CrocoDash.vgrid import VGrid
    import xarray as xr

    def master_file(prefix: str) -> Path:
        matches = sorted(master_ocnice.glob(f"{prefix}*.nc"))
        if not matches:
            raise FileNotFoundError(f"No {prefix}*.nc found in {master_ocnice}")
        return matches[0]

    hgrid_path = master_file("ocean_hgrid_")
    topo_path = master_file("ocean_topog_")
    vgrid_path = master_file("ocean_vgrid_")

    grid = Grid.from_supergrid(str(hgrid_path), name=grid_name)

    with xr.open_dataset(topo_path) as topo_ds:
        min_depth = float(topo_ds.attrs.get("min_depth", 0.0))
    topo = Topo.from_topo_file(grid, str(topo_path), min_depth=min_depth)

    vgrid = VGrid.from_file(str(vgrid_path), name=grid_name)

    return grid, topo, vgrid


def main(location: str):
    from CrocoDash.case import Case

    master_inputdir = CROC_INPUT_SCALING / f"loc_{location}"
    master_ocnice = master_inputdir / "ocnice"
    if not master_ocnice.exists():
        raise FileNotFoundError(f"Master ocnice dir not found: {master_ocnice}")

    caseroot = CROC_CASES_SCALING / f"loc_{location}_n{NTASKS_OCN}"
    inputdir = CROC_INPUT_SCALING / f"loc_{location}_n{NTASKS_OCN}"
    grid_name = f"loc_{location}_n{NTASKS_OCN}"

    grid, topo, vgrid = reconstruct_grid_objects(master_ocnice, grid_name)

    print(f"Creating case at {caseroot} (inputdir={inputdir}) with NTASKS_OCN={NTASKS_OCN} ...", flush=True)
    case = Case(
        cesmroot=CESMROOT,
        caseroot=caseroot,
        inputdir=inputdir,
        compset=COMPSET,
        ocn_grid=grid,
        ocn_topo=topo,
        ocn_vgrid=vgrid,
        atm_grid_name=ATM_GRID_NAME,
        machine=MACHINE,
        project=PROJECT,
        override=True,  # safe: inputdir/caseroot/grid name are fresh, per-location-n40 paths
        ntasks_ocn=NTASKS_OCN,
        job_queue=JOB_QUEUE,
    )

    print("Wiring up forcings (configure_forcings, no download/regrid) ...", flush=True)
    case.configure_forcings(
        date_range=DATE_RANGE,
        boundaries=["south", "north", "west", "east"],
        product_name="GLORYS",
        function_name="get_glorys_data_from_rda",
    )

    print("Pointing case at master's already-processed forcing/grid files ...", flush=True)
    point_case_at_master(caseroot, master_ocnice)

    status_file = inputdir / "extract_forcings" / "process_forcings_status.json"
    status_file.write_text(json.dumps({
        "status": "done",
        "processed": ["conditions"],
        "note": f"user_nl_mom repointed at {master_ocnice}, not reprocessed here",
    }, indent=2))

    print(f"Done: {caseroot}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_location_ntasks40_case.py <location_name>")
        sys.exit(1)
    main(sys.argv[1])
