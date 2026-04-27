# CrocoDash — Claude Code Summary

## Purpose

CrocoDash is the primary integration layer for the CROCODILE project. It sets up regional MOM6 ocean model cases within CESM (Community Earth System Model). The three core phases are:

1. **Grid Definition** — Create horizontal grid (`Grid`), vertical grid (`VGrid`), and bathymetry (`Topo`)
2. **Case Setup** — Configure and create the CESM case directory
3. **Forcing & Boundary Conditions** — Extract, regrid, and format forcing data from external sources

---

## Repository Layout

```
CrocoDash/
├── CrocoDash/                        # Main Python package
│   ├── case.py                       # Core Case class (~1,042 lines) — primary entry point
│   ├── grid.py / vgrid.py / topo.py  # Wrappers re-exporting from mom6_forge
│   ├── logging.py                    # setup_logger() for consistent stdout logging
│   ├── extract_forcings/             # Data retrieval, regridding, merging, BGC, tides, runoff
│   │   ├── get_dataset_piecewise.py
│   │   ├── regrid_dataset_piecewise.py
│   │   ├── merge_piecewise_dataset.py
│   │   ├── bgc.py
│   │   ├── runoff.py
│   │   ├── tides.py
│   │   ├── utils.py
│   │   └── case_setup/driver.py      # Forcing processing driver (dynamically loaded by Case)
│   ├── forcing_configurations/       # Registry + configurator classes per forcing type
│   │   ├── base.py                   # ForcingConfigRegistry, InputParam, OutputParam, BaseConfigurator
│   │   └── configurations.py         # TidesConfigurator, BiogeochemistryConfigurator, etc.
│   └── raw_data_access/              # Abstraction layer for external data products
│       ├── base.py                   # BaseProduct, DatedBaseProduct, ForcingProduct, @accessmethod
│       ├── registry.py               # ProductRegistry — static registry for all data products
│       ├── utils.py
│       └── datasets/                 # Concrete implementations (glorys, glofas, tides, seawifs, gebco, etc.)
├── visualCaseGen/                    # Submodule: CESM case creation + ProConPy constraint framework
├── rm6/                              # Submodule: regional_mom6 (regridding, OBC generation)
├── tests/
│   ├── test_case.py / test_workflow.py / test_installation.py / test_minimal_modules.py
│   ├── extract_forcings/
│   ├── forcing_configurations/
│   ├── raw_data_access/
│   └── fixtures/                     # Dynamic pytest plugin fixtures (grid_gen, objects, data_gen, state)
├── pytest.ini
├── environment.yml
└── setup.py
```

---

## Key Classes and Design Patterns

### `Case` (case.py)
The main orchestration class. Users instantiate it with grid/topo/vgrid objects plus CESM config, then call methods in sequence.

**Constructor key args:**
```python
Case(
    cesmroot, caseroot, inputdir,
    compset,           # e.g. "G_JRA"
    ocn_grid, ocn_topo, ocn_vgrid,
    atm_grid_name="TL319",
    rof_grid_name=None,
    machine=None, project=None,
    override=False,
    ntasks_ocn=None, job_queue=None, job_wallclock_time=None
)
```

**Key methods:**
- `configure_forcings(specs: dict)` — Registers forcing configurations via ForcingConfigRegistry
- `configure_initial_and_boundary_conditions()` — Sets up open boundary conditions
- `process_forcings()` — Runs the extract_forcings driver

**Key properties:**
- `expt` — Returns the underlying `regional_mom6.experiment` object
- `cice_in_compset`, `runoff_in_compset`, `bgc_in_compset` — Bool checks on compset components

### Registry Pattern
Used in two places:
- **`ForcingConfigRegistry`** (`forcing_configurations/base.py`) — Auto-discovers configurators via `__init_subclass__`, validates compset compatibility
- **`ProductRegistry`** (`raw_data_access/registry.py`) — Static registry for all data product classes and their access methods

### `@accessmethod` Decorator
Marks static functions on data product classes as callable access methods. Enforces required arguments and attaches metadata. The registry calls these via `ProductRegistry.call()`.

### Constraint Satisfaction
`ProConPy` (inside `visualCaseGen/`) validates CESM configurations before case creation using a CSP solver. This prevents invalid compset/grid/forcing combinations early.

---

## Data Flow

```
User creates Grid + VGrid + Topo
        ↓
Case.__init__() → initializes visualCaseGen/CIME interface, creates CESM case dir
        ↓
configure_forcings() → validates specs via ForcingConfigRegistry
        ↓
process_forcings() → calls extract_forcings/case_setup/driver.py
        ↓
Driver uses ProductRegistry to retrieve raw data (GLORYS, GLOFAS, TPXO, etc.)
        ↓
regrid_dataset_piecewise() maps data to regional grid
        ↓
Output files placed in inputdir/ocnice/ for CESM ingestion
```

---

## Submodules

| Submodule | Embedded at | Role |
|-----------|-------------|------|
| `regional_mom6` | `rm6/` | MOM6 param management, OBC generation, grid rotation |
| `visualCaseGen` | `visualCaseGen/` | CESM case creation, ProConPy CSP validation |
| `mom6_forge` | `visualCaseGen/external/mom6_forge/` | Grid/mapping utilities (re-exported by grid.py, vgrid.py, topo.py) |

---

## Running Tests

From `regional_mom_workflows/CrocoDash/`:

```bash
# Fast unit/integration tests
pytest --ignore=CrocoDash/visualCaseGen -m "not workflow" -vv --showlocals --tb=short

# Workflow tests (slower, may need data access)
pytest -m "workflow" -s --ignore=CrocoDash/visualCaseGen

# With coverage
pytest --ignore=CrocoDash/visualCaseGen -m "not workflow" --cov=CrocoDash --cov-report=xml --cov-branch
```

Test markers: `slow`, `workflow`

---

## Environment and Dependencies

- **Python:** 3.11.10–<3.12 (strict)
- **Key deps:** `xarray`, `xesmf`, `esmpy`, `copernicusmarine`, `cdsapi`, `regional_mom6`, `ProConPy`
- **Install:** `conda env create -f environment.yml` then `pip install -e .`
- **Submodules must be initialized:** `git submodule update --init --recursive`

---

## Extending CrocoDash

**Add a new forcing type:**
1. Create a class in `forcing_configurations/configurations.py` inheriting `BaseConfigurator`
2. Implement `validate_compset_compatibility()`, `is_required()`, `configure()`
3. Auto-registered via `__init_subclass__` hook

**Add a new data source:**
1. Create a class in `raw_data_access/datasets/` inheriting from `BaseProduct`, `DatedBaseProduct`, or `ForcingProduct`
2. Implement `@accessmethod`-decorated static functions
3. Auto-registered via `ProductRegistry`

---

## CI/CD Workflows (`.github/workflows/`)

| Workflow | Purpose |
|----------|---------|
| `testing.yml` | Main pytest suite |
| `quality_control.yml` | Code quality checks |
| `docker_build.yml` | Docker image builds |
| `deploy_sphinx_docs.yml` | Sphinx documentation deployment |
| `raw_data_access_testing.yml` | Data access validation |
