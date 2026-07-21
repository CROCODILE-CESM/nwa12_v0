"""
Create one CESM case for the MOM6 NTASKS_OCN scaling sweep, working around a
CrocoDash limitation: Case.__init__ requires override=True whenever `inputdir`
already exists, and override=True unconditionally deletes+recreates the whole
inputdir (including already-processed forcings). There is no supported way to
point two different CESM cases (different caseroot/NTASKS_OCN) at one shared,
already-processed inputdir via the public API.

Workaround: give each NTASKS value its own fresh inputdir/caseroot (so
Case.__init__ never sees a collision) and its own uniquely-named Grid/VGrid
(scaling_test_n{N}) to avoid colliding with the master's entry in CIME's
*global*, cesmroot-wide component_grids_nuopc.xml grid registry (populated
when scaling_n1 was created) — overriding that shared entry risks breaking
scaling_n1's build later. Safe to rename: get_domain_dir (mom6_forge.git_utils)
hashes on grid coordinate values, not name, so the already-processed Topo is
still found under the new name.

Then, instead of copying the master's processed forcing .nc files into each
new case's own ocnice/ (extra disk, extra step), just point MOM6 at the
master's ocnice/ folder directly: `user_nl_mom`'s INPUTDIR is a plain
directory prefix that every other file parameter (GRID_FILE, TOPO_FILE,
ALE_COORDINATE_CONFIG, IC/OBC filenames) resolves against — confirmed via code
trace of CrocoDash/case.py `_update_forcing_variables`/`append_user_nl`, which
writes bare/relative filenames only, never an absolute path or a manifest
tying a case to its own inputdir. So after configure_forcings() runs (which
already writes the correct bare IC/OBC filenames — those match the master's
files as-is, e.g. "init_eta.nc"), we just rewrite INPUTDIR/GRID_FILE/TOPO_FILE/
ALE_COORDINATE_CONFIG in user_nl_mom to point at the master's ocnice/ folder
and its grid filenames instead of this case's own freshly-generated ones. The
only file this case still needs of its own is the ESMF_mesh (registered by
absolute path in the CIME grid registry, keyed by this case's unique grid
name) — untouched by this redirect.

Usage:
    conda run -n CrocoDash python create_ntasks_case_workaround.py <ntasks_ocn>
"""

import json
import re
import sys
from pathlib import Path

MASTER_CASE_DIR = Path("/glade/u/home/manishrv/scratch/croc_input/scaling_test")
CROC_INPUT = Path("/glade/u/home/manishrv/scratch/croc_input")
CESMROOT = Path("/glade/u/home/manishrv/work/installs/CROCESM_workshop_2025")
CROC_CASES = Path("/glade/u/home/manishrv/croc_cases")
COMPSET = "1850_DATM%NYF_SLND_SICE_MOM6%REGIONAL_SROF_SGLC_SWAV"
MACHINE = "derecho"
ATM_GRID_NAME = "T62"
PROJECT = "ncgd0011"
JOB_QUEUE = "develop"
DATE_RANGE = ["2020-01-01", "2020-01-31"]  # 30-day run


def point_case_at_master(caseroot: Path, master_ocnice: Path):
    """Rewrite user_nl_mom to read grid + forcing files from the master's ocnice/
    folder instead of this case's own (identical-content, differently-suffixed)
    copies. IC/OBC filenames (init_eta.nc, forcing_obc_segment_00N.nc, ...)
    already match the master's as written by configure_forcings — only the
    directory prefix and the grid-file names (which carry a per-case session
    suffix) need repointing."""

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
    """Rebuild Grid/Topo/VGrid directly from the master's existing ocnice/ netCDF
    files instead of mcp_grid_params.json + TopoLibrary — no dependency on either
    surviving (both were wiped by an earlier override=True Case() recreation)."""
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


def main(ntasks_ocn: int):
    from CrocoDash.case import Case

    caseroot = CROC_CASES / f"scaling_n{ntasks_ocn}"
    inputdir = CROC_INPUT / f"scaling_n{ntasks_ocn}"
    grid_name = f"scaling_test_n{ntasks_ocn}"
    grid, topo, vgrid = reconstruct_grid_objects(MASTER_CASE_DIR / "ocnice", grid_name)

    print(f"Creating case at {caseroot} (inputdir={inputdir}) with NTASKS_OCN={ntasks_ocn} ...", flush=True)
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
        override=True,  # safe: inputdir/caseroot are fresh per-N paths, grid name is per-N too
        ntasks_ocn=ntasks_ocn,
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
    point_case_at_master(caseroot, MASTER_CASE_DIR / "ocnice")

    status_file = inputdir / "extract_forcings" / "process_forcings_status.json"
    status_file.write_text(json.dumps({
        "status": "done",
        "processed": ["conditions"],
        "note": f"user_nl_mom repointed at {MASTER_CASE_DIR / 'ocnice'}, not reprocessed here",
    }, indent=2))

    print(f"Done: {caseroot}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_ntasks_case_workaround.py <ntasks_ocn>")
        sys.exit(1)
    main(int(sys.argv[1]))
