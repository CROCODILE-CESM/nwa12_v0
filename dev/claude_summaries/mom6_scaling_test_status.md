# MOM6 NTASKS_OCN Scaling Test — Handoff / Status

Goal: measure how MOM6 wallclock/throughput scales with core count for a small regional
case on Derecho's `develop` queue (fast turnaround, shared nodes, ≤~20 cores), then publish
the results as a new page in the SeaSloth dashboard. Full original plan (design rationale,
grid choice, NTASKS_OCN sweep, SeaSloth publishing design) is at
`/glade/u/home/manishrv/.claude/plans/we-are-going-to-zesty-bubble.md` — read that first for
the "why", this doc is the "where things stand".

This work has doubled as a live test of the three CROC MCP servers (`crocodash`,
`cesm-runner`, `ocean-debugger`). **The user has pre-approved committing/pushing changes to
those three MCP servers directly** (no new branches needed) — this does not extend to
production submodule code (CrocoDash/regional-mom6/mom6_forge/SeaSloth proper), which still
needs explicit go-ahead before commit/push.

## Current on-disk state (as of this handoff)

- Grid + base case created and forcings fully processed:
  - `case_dir` (CrocoDash inputdir, shared across all NTASKS_OCN points):
    `/glade/u/home/manishrv/scratch/croc_input/scaling_test`
  - Grid: 100×100 horizontal points (`lon -65..-55`, `lat 25..35`, `resolution=0.1`), flat
    bathymetry at 1000 m, `nk=10` uniform vgrid. `TopoLibrary/` now correctly populated
    (see bug #2 below).
  - `~/croc_cases/scaling_n1` — CESM case created with `NTASKS_OCN=1`, `job_queue=develop`,
    compset `1850_DATM%NYF_SLND_SICE_MOM6%REGIONAL_SROF_SGLC_SWAV`, `machine=derecho`,
    `atm_grid_name=T62`, `project=ncgd0011`, `cesmroot=~/work/installs/CROCESM_workshop_2025`.
    Forcings (GLORYS, `date_range=["2020-01-01","2020-01-05"]`) processed successfully
    (`extract_forcings/process_forcings_status.json` → `{"status": "done", "processed":
    ["conditions"]}`).
  - **Not yet done**: `case_setup` / `case_build` / `case_submit` for `scaling_n1` itself,
    and creating the other 5 NTASKS_OCN cases (2, 4, 5, 10, 20).

## Bugs found and fixed in the MCP servers (uncommitted — see branches below)

All found by actually exercising the servers, not by inspection alone.

1. **`crocodash` — `process_forcings` called a removed driver API.**
   `tools/case.py` (foreground path) and `tools/_bg_worker.py` (background path) called
   `driver.process_conditions(get_dataset_piecewise=..., ...)`, but the actual
   `extract_forcings/driver.py` CrocoDash generates only exposes `run_workflow(ic=, bc=,
   bgcic=, ...)`. Fixed both call sites to `driver.run_workflow(ic=process_initial_condition,
   bc=process_velocity_tracers)`. **Verified working** — this is what got `scaling_n1`'s
   forcings to actually process.

2. **`crocodash` — `create_grid` never enabled git-based version control on the `Topo`
   object**, so `TopoLibrary/<hash>/` (which `create_case`'s reconstruction path requires via
   `Topo.from_version_control`) was never written, even though `create_grid`'s own docstring
   and `mcp_grid_params.json` output claim it is. This breaks *every* `create_case` call
   against a `case_dir` reusing an already-created grid (i.e. every NTASKS_OCN point after
   the first). Root cause: `tools/grid.py` constructs `Topo(grid=grid, min_depth=min_depth,
   version_control_dir=topo_library_dir)` without `git=True` (the mom6_forge `Topo.__init__`
   default is `git=False`). Fixed in both `create_grid` and `create_polar_grid` call sites
   (added `git=True`). **Verified**: re-running `create_grid` after the fix populated
   `TopoLibrary/73547c46.../` as expected.

3. **`crocodash` — `duplicate_case_tool` imports from the wrong module path.**
   `tools/shareable.py` did `from CrocoDash.shareable import duplicate_case`, but
   `CrocoDash/shareable/__init__.py` is empty — `duplicate_case` only exists at
   `CrocoDash.shareable.bundle.duplicate_case`. (Comment in the file suggests the MCP server
   was written against an anticipated post-PR#238 CrocoDash API that hasn't merged yet — the
   same likely applies to `bundle_case`/`fork_case`, which weren't tested/fixed here since
   they weren't on the critical path.) Fixed the one import needed for `duplicate_case_tool`.
   **Not yet verified end-to-end** (found bug #2's fix first, which unblocked the simpler
   `create_case`-reuse path, so this fallback tool wasn't actually exercised further).

4. **`ocean-debugger` — added a new tool, `read_cesm_timing(case_dir)`**, in new file
   `tools/timing.py`, registered in `server.py`. Parses CIME's native
   `case_dir/timing/cesm_timing.$CASE.$jobid` file (Model Cost, Model Throughput, per-component
   Run Time) — this is the file we'll read after each scaling-point run to build the final
   curve. No such tool existed before (confirmed via exploration — SeaSloth doesn't cover
   model-runtime timing, only Python-level benchmarks). **Not yet run against a real
   completed case** (no case has finished `case_submit` yet) — syntax-checked only.

### Repo/branch state for the edits above

- `dev/MCP_CrocoDash` — currently checked out on branch **`defer-heavy-imports`** (pre-existing
  branch name, not created by me this session). Modified: `tools/_bg_worker.py`,
  `tools/case.py`, `tools/grid.py`, `tools/shareable.py`. (Also some `tools/__pycache__/*.pyc`
  show as modified — exclude those from any commit.)
- `dev/MCP_regional_ocean_debugger` — currently checked out on branch
  **`update/interview-repo`** (also pre-existing, not created by me). Modified: `server.py`
  (registers new tool). New file: `tools/timing.py`.
- Neither has been committed yet. Given the pre-approval above, these should be committed
  (on their current branches, or a fresh branch if `defer-heavy-imports`/
  `update/interview-repo` turn out to be unrelated in-progress work you don't want mixed
  in — worth a quick look at what's already on those branches before committing).

## Separate, unresolved issue: MCP server connection flakiness

Both `crocodash` and (by extension) the other two MCP servers have disconnected/failed to
reconnect multiple times this session, independent of the code bugs above. Root cause found:
**`import fastmcp` alone takes ~20-30s cold** (mostly the `mcp` SDK's own dependency tree —
pydantic/starlette/anyio/httpx — being read from GLADE's network filesystem for the first
time; a warm-cache second import took ~8s). Even bare `import numpy` took 4.5s in this
environment, confirming it's GLADE filesystem latency, not an MCP-server code issue. All
three servers' own tool code already lazy-imports CrocoDash/mom6_forge/xesmf inside function
bodies (nothing to move there) — the slow part is `fastmcp` itself, which can't be deferred
since it's needed to register tools at all.

**Mitigation, not a fix**: restart the three MCP servers one at a time with a pause between
each (not all simultaneously) to avoid concurrent cold-cache contention on GLADE, and expect
the first restart after a while to take ~20-30s before tools appear.

## Next steps (in order)

1. Get the `crocodash`/`cesm-runner`/`ocean-debugger` MCP servers reconnected (see above).
2. Create the remaining NTASKS_OCN cases: 2, 4, 5, 10, 20 — reuse the now-fixed
   `create_case(case_dir=.../scaling_test, caseroot=~/croc_cases/scaling_n{N}, ntasks_ocn=N,
   job_queue="develop", override=False, ...)` path (same `cesmroot`/`compset`/`atm_grid_name`/
   `project` as `scaling_n1` above). No need to re-run `create_grid`/`configure_forcings`/
   `process_forcings` again — `case_dir` already has everything.
3. For each of the 6 cases (including `scaling_n1`, not yet built): `case_setup` →
   `preview_run` (sanity-check PE layout matches requested NTASKS_OCN and queue=develop) →
   `case_build` → `case_submit` (real PBS batch, not `no_batch`/container).
4. Once each finishes, run the new `read_cesm_timing(case_dir)` ocean-debugger tool against
   each caseroot; also sanity-check with `find_errors` before trusting the timing number.
5. Tabulate `(NTASKS_OCN, throughput)` across the 6 runs, compute parallel efficiency vs the
   NTASKS_OCN=1 baseline.
6. Publish to SeaSloth: new `dev/SeaSloth/results/mom6_scaling.json` (schema:
   `[{ntasks_ocn, throughput_sim_years_per_day, tot_run_time_s, ocn_cost_pe_hrs}, ...]`) +
   new `dev/SeaSloth/scripts/generate_scaling_report.py` (reuse `_linechart_svg`/
   `_ramp_color` from the existing `generate_report.py`) → `report/mom6_scaling.html`, linked
   from `report/index.html` the way `health.html` already is. Wire into
   `.github/workflows/publish.yml`. **This needs explicit go-ahead before commit/push** — it's
   outside the MCP-server pre-approval.

## Reference

Full original plan (context/design rationale for grid size, NTASKS_OCN sweep choice, why
SeaSloth needs a new page rather than a fake pytest-benchmark test, etc.):
`/glade/u/home/manishrv/.claude/plans/we-are-going-to-zesty-bubble.md`
