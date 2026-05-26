# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Overview

CROC (CROCODILE) is a monorepo of Git submodules for building and running regional ocean model configurations inside CESM with MOM6. Primary production code is in `regional_mom_workflows/`; exploratory/dev work is in `dev/`.

GitHub org: https://github.com/CROCODILE-CESM — all remote repos live here. Development follows standard GitHub flow: feature branches, PRs, review, merge.

Key submodules:
- `regional_mom_workflows/CrocoDash` — Main integration layer; entry point for most case setup tasks
- `regional_mom_workflows/regional-mom6` — MOM6 configuration, forcing generation, regridding
- `regional_mom_workflows/mom6_forge` — Grid, bathymetry, and vertical grid generation
- `regional_mom_workflows/visualCaseGen` — Jupyter GUI for CESM case creation (constraint-satisfaction driven)
- `regional_mom_workflows/diag_manager` — MOM6 diagnostics GUI
- `dev/pyDARTdiags` — DART data assimilation diagnostics

## Important Paths on GLADE

| Purpose | Path |
|---|---|
| CESM installs (with MOM6) | `~/work/installs/` |
| CESM cases | `~/croc_cases/` (symlink → `croc_cases/`) |
| MOM6 input data | `~/scratch/croc_input/` (symlink → `croc_input/`) |

`croc_cases/` and `croc_input/` at the repo root are symlinks to the above scratch locations.

## Architecture

**CrocoDash** (`regional_mom_workflows/CrocoDash/CrocoDash/`) is the integration layer:
- `case.py` — main `Case` class; orchestrates CESM init, grid, forcing, and regional-mom6 operations
- `extract_forcings/` — forcing extraction modules: `bgc.py`, `runoff.py`, `tides.py`, regrid utilities
- `raw_data_access/` — data registry and product access
- `forcing_configurations/` — forcing config registry
- `rm6/` — embedded submodule copy of regional-mom6
- `visualCaseGen/` — embedded submodule copy of visualCaseGen

**visualCaseGen** uses constraint satisfaction (via `ProConPy/csp_solver.py` and `config_var.py`) to validate CESM case configs before creation. Interfaces with CIME through `cime_interface.py`.

**regional-mom6** (`regional_mom6/`) handles regridding (`regridding.py`), MOM6 parameter management (`MOM_parameter_tools.py`), grid rotation (`rotation.py`), and the main `Experiment` class (`regional_mom6.py`). Uses xarray/dask + xesmf.

**mom6_forge** (`mom6_forge/`) generates horizontal grids (`grid.py`, `grid_creator.py`), vertical grids (`vgrid.py`, `vgrid_creator.py`), and bathymetry (`topo.py`, `topo_editor.py`).

## Linting

All packages use **black**. Always run before committing.

```bash
# Check
black --check --diff <package_src_dir>

# Apply
black <package_src_dir>
```

Per-package source paths:
- CrocoDash: `CrocoDash/`
- regional-mom6: `regional_mom6/`
- mom6_forge: `mom6_forge/`
- visualCaseGen: `visualCaseGen/` and `ProConPy/`
- pyDARTdiags: `src/pydartdiags/`

## Conda Environments

Each submodule under `regional_mom_workflows/` has its own dedicated conda environment that installs the package in editable mode (`-e ./`). Always use the matching env when running tests or working in a submodule:

| Submodule | Conda env |
|---|---|
| `CrocoDash` | `CrocoDash` |
| `mom6_forge` | `mom6_forge` |
| `regional-mom6` | (uses CrocoDash env) |
| `visualCaseGen` | (uses CrocoDash env) |
| `pyDARTdiags` | (its own env) |

Example: `conda run -n mom6_forge pytest tests/`

## Running Tests

Each submodule has its own test suite. Run from within the submodule directory using the matching conda environment (see above).

**CrocoDash** (from `regional_mom_workflows/CrocoDash/`):
```bash
# Fast unit/integration tests
pytest --ignore=CrocoDash/visualCaseGen -m "not workflow" -vv --showlocals --tb=short

# Workflow tests (slower, may require data access)
pytest -m "workflow" -s --ignore=CrocoDash/visualCaseGen

# With coverage
pytest --ignore=CrocoDash/visualCaseGen -m "not workflow" --cov=CrocoDash --cov-report=xml --cov-branch
```

**regional-mom6** (from `regional_mom_workflows/regional-mom6/`):
```bash
pytest tests/
```

**mom6_forge** (from `regional_mom_workflows/mom6_forge/`):
```bash
pytest tests/
```

**visualCaseGen** (from `regional_mom_workflows/visualCaseGen/`):
```bash
pytest tests/
```
Tests are tiered: `1_unit/`, `2_integration/`, `3_system/`, `4_static/`.

**pyDARTdiags** (from `dev/pyDARTdiags/`):
```bash
pytest --cov=pydartdiags tests/
```

## Python Version Requirements

- `visualCaseGen`: `>=3.11.10,<3.13` (strict; enforced in pyproject.toml)
- `CrocoDash` environment: `>=3.11.10,<3.12`
- `mom6_forge`: `>=3.11,<3.15`
- `pyDARTdiags`: 3.8+
- `regional-mom6`: 3.8+

## Submodule Management

Initialize or sync all submodules after clone or pull:
```bash
git submodule update --init --recursive
```

Several submodules contain nested submodules (e.g., `visualCaseGen` embeds `external/mom6_forge/` and `external/ipyfilechooser/`; `CrocoDash` embeds `rm6/` and `visualCaseGen/`). Always use `--recursive`.

When making changes that span the outer repo and a submodule, commit the submodule first, then update the pointer in the outer repo.

## Development Workflow

- All remote repos are in the [CROCODILE-CESM GitHub org](https://github.com/CROCODILE-CESM)
- Use feature branches and open PRs for all non-trivial changes
- Each submodule is its own repo with its own CI (`.github/workflows/`): tests, coverage, docs, black check
- PRs should pass CI before merging
- `dev/` is for local experimentation — notebooks and scripts here are not held to the same standards as production submodule code
- **Always ask before committing or pushing.** Do not commit or push changes without explicit user approval, even after making requested edits.
