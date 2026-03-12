# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CROC (CROCODILE) is a monorepo integrating multiple submodules for regional ocean modeling workflows built around MOM6. The primary production code lives in `regional_mom_workflows/`, with experimental/development code in `dev/`.

Key submodules:
- `regional_mom_workflows/CrocoDash` — Main integrated dashboard; entry point for most ocean case setup tasks
- `regional_mom_workflows/regional-mom6` — MOM6 configuration/forcing generation
- `regional_mom_workflows/mom6_bathy` — Grid and bathymetry generation
- `regional_mom_workflows/visualCaseGen` — Jupyter GUI for CESM case creation
- `dev/pyDARTdiags` — DART data assimilation diagnostics

`croc_cases/` and `croc_input/` are symlinks to scratch storage on GLADE.

## Architecture

**CrocoDash** is the integration layer. Its `CrocoDash/case.py` is the main orchestration file. It embeds copies of `visualCaseGen` and references `regional-mom6` for MOM6-specific operations. Forcing extraction modules (`extract_forcings/bgc.py`, `runoff.py`, `tides.py`, etc.) pull data from external sources and prepare it for MOM6.

**visualCaseGen** uses a constraint satisfaction approach via its `ProConPy/` library (`csp_solver.py`, `config_var.py`) to validate CESM case configurations before creation. It interfaces with CIME via `cime_interface.py`.

**regional-mom6** handles regridding, MOM6 parameter management, and grid rotation. It uses xarray/dask for data processing and xesmf for regridding.

**mom6_bathy** generates horizontal (`grid_creator.py`) and vertical (`vgrid_creator.py`) grids plus bathymetry (`topo.py`, `topo_editor.py`).

## Running Tests

Each submodule has its own test suite. Run from within the submodule directory.

**CrocoDash** (from `regional_mom_workflows/CrocoDash/`):
```bash
# Unit/integration tests (fast)
pytest --ignore=CrocoDash/visualCaseGen -m "not workflow" -vv --showlocals --tb=short

# Workflow tests (slower, may require data access)
pytest -m "workflow" -s --ignore=CrocoDash/visualCaseGen

# With coverage
pytest --ignore=CrocoDash/visualCaseGen -m "not workflow" --cov=CrocoDash --cov-report=xml --cov-branch
```

**pyDARTdiags** (from `dev/pyDARTdiags/`):
```bash
pytest --cov=pydartdiags tests/
```

**visualCaseGen** (from `regional_mom_workflows/visualCaseGen/`):
```bash
pytest tests/
```
Tests are organized in levels: `1_unit/`, `2_integration/`, `3_system/`, `4_static/`.

**regional-mom6** and **mom6_bathy**: `pytest tests/` from their respective directories.

## Linting

**pyDARTdiags** uses black:
```bash
black --check --diff ./src/pydartdiags
black ./src/pydartdiags  # to apply
```

No root-level linting config; check individual submodule configs.

## Python Version Requirements

- `visualCaseGen`: requires Python 3.11.10–3.11.* (strict)
- `pyDARTdiags`: Python 3.8+
- Others: Python 3.8+

## Submodule Management

After cloning or pulling, initialize/update submodules:
```bash
git submodule update --init --recursive
```

Some submodules contain further nested submodules (e.g., `visualCaseGen` contains `external/mom6_bathy/`).
