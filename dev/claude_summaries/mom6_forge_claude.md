# mom6_forge — CLAUDE.md

## Project Overview

**mom6_forge** (formerly `mom6_bathy`) is a Python toolkit for generating MOM6 ocean model grids, bathymetry, and related input data for regional and idealized ocean modeling. It lives at `regional_mom_workflows/mom6_forge/` within the CROC monorepo.

- **GitHub**: https://github.com/NCAR/mom6_forge
- **Docs**: https://ncar.github.io/mom6_forge/
- **Python**: 3.11–3.14
- **License**: MIT

## Architecture

The package is organized into several layers:

### Horizontal Grid
- **`_supergrid.py`** — Low-level MOM6 supergrid metric calculations
  - `SupergridBase`: Abstract base class
  - `UniformSphericalSupergrid`: Constant-degree lat/lon grids
  - `RectilinearCartesianSupergrid`: Uniform Cartesian grids
  - Computes: x/y coords, dx/dy cell widths, area, angle_dx
- **`grid.py`** — Primary user-facing horizontal grid class
  - `Grid`: Creates/manipulates MOM6 horizontal grids; computes staggered-grid points (tlon/tlat, ulon/ulat, vlon/vlat, qlon/qlat)
  - Key methods: `from_supergrid()`, `from_supergrid_ds()`, `write_supergrid()`, `get_indices()`, `plot()`, `is_rectangular()`, `is_tripolar()`, `is_cyclic_x()`
- **`grid_creator.py`** — `GridCreator`: ipywidgets-based Jupyter UI for interactive horizontal grid creation, with grid library save/load

### Vertical Grid
- **`vgrid.py`** — `VGrid`: dz (layer thicknesses), nk, depth; factory methods `uniform()`, `hyperbolic()`, `from_file()`; properties `zl` (cell centers), `zi` (interfaces)
- **`vgrid_creator.py`** — `VGridCreator`: Jupyter widget for interactive vertical grid creation

### Bathymetry
- **`topo.py`** — `Topo`: Bathymetry generation for MOM6 grids
  - Methods: `set_depth_via_topog_file()`, `set_flat()`, `write_topo()`, `write_cice_grid()`
  - Maintains version-controlled edit history via git
- **`topo_editor.py`** — `TopoEditor`: Interactive Jupyter widget for bathymetry editing with undo/redo

### Edit/Command System
- **`edit_command.py`** — Abstract `EditCommand` base class; supports serialize/deserialize for persistence
- **`command_manager.py`** — `CommandManager` with git-backed undo/redo; `TopoCommandManager` specializes this for bathymetry edits

### Regridding and Data
- **`mapping.py`** — `regrid_dataset_via_xesmf()` (conservative/bilinear/nearest), `grid_from_esmf_mesh()`, `extract_coastline_mask()`
- **`chl.py`** — `interpolate_and_fill_seawifs()`: Process and interpolate SeaWiFS chlorophyll data to model grid

### Utilities and Plotting
- **`utils.py`** — `normalize_deg()`, `cell_area_rad()`, `get_avg_resolution()`, `fill_missing_data()`, `longitude_slicer()`, etc.
- **`plotting.py`** — `plot_esmf_mesh()`: Visualize ESMF meshes
- **`git_utils.py`** — `get_domain_dir()` (hash-based grid directory naming), `get_repo()`

## Installation and Development

```bash
# Conda environment (recommended)
conda env create -f environment.yml
conda activate mom6_forge

# Editable install
pip install -e ./
```

Key dependencies: numpy, xarray, scipy, netcdf4, xesmf, matplotlib, cartopy, jupyterlab, ipywidgets, gitpython, black, pytest.

## Running Tests

From `regional_mom_workflows/mom6_forge/`:

```bash
# All tests with coverage
pytest -v --cov=mom6_forge --cov-branch --cov-report=xml

# Specific test file
pytest tests/test_grid.py -v

# With stdout output
pytest -s tests/test_notebooks.py
```

**Test files:**
- `test_grid.py` — Grid creation, rectangular/tripolar/cyclic detection
- `test_topo.py` — Bathymetry operations
- `test_supergrid.py` — Supergrid metric calculations
- `test_vgrid.py` — Vertical grid operations
- `test_rotation.py` — Grid rotation angles
- `test_edit_commands.py` — Edit command serialization
- `test_topo_command_manager.py` — Command history and undo/redo
- `test_topo_editor.py` — TopoEditor widget
- `test_chl.py` — Chlorophyll data processing
- `test_utils.py` — Utility functions
- `test_notebooks.py` — Notebook execution

Some tests require GLADE data access and are skipped on non-NCAR machines via `on_cisl_machine()`.

## Linting

Uses **black**. Check formatting with:

```bash
black --check mom6_forge/
black mom6_forge/  # to apply
```

Enforced on all PRs via `.github/workflows/quality_control.yml`.

## CI/CD

- **Build & Test** (`.github/workflows/build-test-docs.yml`): Tests Python 3.11–3.14 on Ubuntu using micromamba; coverage uploaded to CodeCov
- **Docs**: Sphinx (`sphinx_rtd_theme`), built from `.docstr/`, deployed to GitHub Pages; PR previews auto-commented

## Notebooks / Tutorials

Located in `notebooks/`:
1. Spherical Grid — Basic grid creation
2. Equatorial Refinement — Enhanced equatorial resolution
3. Custom Bathymetry — Generate from topography files
4. Ingest Land Mask — Apply external land masks
5. Modify Existing — Edit existing grids/bathymetry
6. Demo Editors — Interactive widget demos

## Key Design Notes

- **Supergrid convention**: MOM6 uses a supergrid that is 2x the resolution of the model grid; all metric calculations operate on this supergrid and are then subsampled for model grid points.
- **Git-backed edits**: Bathymetry edits are tracked as git commits in a per-grid repository (keyed by deterministic hash of grid parameters), enabling full undo/redo history.
- **Interactive widgets**: Heavy use of ipywidgets + cartopy for Jupyter-based grid/topo creation and editing — intended to be run in JupyterLab.
- **xesmf regridding**: Conservative regridding via xesmf; some tests/functionality may require a separate xesmf-compatible environment.
- **GLADE data paths**: Several operations reference NCAR GLADE scratch storage; use `on_cisl_machine()` to guard GLADE-specific code paths in tests.
