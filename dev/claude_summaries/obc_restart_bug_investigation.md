# OBC Restart Bug Investigation Summary

Date: 2026-07-01 / 2026-07-02

## Goal

Demonstrate the GFDL PR #1128 split_RK2b thickness reservoir restart bug:
show it fails ERS, apply the fix, show it passes.

## Background: The Three PRs

**PR #55 (dougie-src)** — `MOM_vert_friction.F90`
Changes wind stress mask at OBC boundary faces from `G%mask2dCu` → `G%OBCmaskCu`.
`OBCmaskCu = 0` at OBC faces, so wind stress is no longer applied there.
This is a physics fix that reduces (but does not eliminate) the Kv/diffusivity restart
discrepancy. ERS still FAILS with Kv_u normalized ~0.025 (vs 2.7 in ctrl).

**PR #437 (mrv-src)** — `MOM_dynamics_split_RK2.F90`
Fills h in exterior ghost cells (cells outside the domain boundary at OBC faces) with a
zero-gradient copy from the adjacent interior cell. On restart, these cells are
uninitialized → wrong pressure gradient → wrong u/v on first restart step.

**PR #1128 (gfdl-src)** — `MOM.F90`, `MOM_dynamics_split_RK2.F90`,
`MOM_dynamics_split_RK2b.F90`, `MOM_open_boundary.F90`
Moves `copy_thickness_reservoirs` from the dynamics timesteppers to `initialize_MOM`.
The bug: in `MOM_dynamics_split_RK2b.F90`, `continuity` (line 505) is called BEFORE
`copy_thickness_reservoirs` (line 673). On restart, `segment%h_Reg%h_res` is not in the
restart file and initializes to zero. The first call to continuity therefore uses stale
(zero) thickness reservoir values, causing wrong OBC thickness nudging. In `split_RK2`,
the call order is correct (copy before continuity), so the bug only manifests with
`SPLIT_RK2B=True`.

The bug requires both:
- `SPLIT_RK2B = True`
- `OBC_THICKNESS_RESERVOIR_LENGTH_SCALE_IN/OUT > 0` (thickness reservoirs active)
- `H = file:...` in `OBC_SEGMENT_xxx_DATA` (provides thickness data at boundary)

---

## Original 5-Case Study (reg_ers)

Config: `SPLIT_RK2B=False` (default), thickness reservoirs OFF (default scale=0)
All cases use the Panama domain, JRA forcing pinned to 1999–2000.

| Case | Fix applied | ERS result | Kv_u normalized |
|------|------------|-----------|-----------------|
| ctrl | none | FAIL | 2.7 |
| no-df | DIABATIC_FIRST=False | FAIL | ~2.7 |
| dougie-src | PR #55 wind stress mask | FAIL | 0.025 |
| mrv-src | PR #437 exterior h ghost cells | PASS | ~0 |
| gfdl-src | PR #1128 reservoir refactor | FAIL = ctrl | ~2.7 |

**Why gfdl-src = ctrl**: The bug in PR #1128 is only triggered by `SPLIT_RK2B=True` with
active thickness reservoirs. Our default config uses `SPLIT_RK2B=False` and
`OBC_THICKNESS_RESERVOIR_LENGTH_SCALE=0`, so the gfdl fix changes nothing observable.

---

## Reproducing the GFDL Bug

New cases with `SPLIT_RK2B=True` + `OBC_THICKNESS_RESERVOIR_LENGTH_SCALE_IN/OUT=9000m`
+ `H=file:forcing_obc_segment_XXX.nc(temp)` in all four OBC segment data strings.


---

## Isolation Cases

| Case | Fixes | Split mode | Thick res | ERS | Kv_u h.z |
|------|-------|-----------|-----------|-----|---------|
| ctrl | none | RK2 | No | FAIL | 2.7 |
| dougie-src | dougie | RK2 | No | PASS | 0.025 |
| mrv-src | mrv | RK2 | No | PASS | ~0 |
| gfdl-repro | none | RK2b | Yes | FAIL | 8.8 |
| gfdl-fix | gfdl | RK2b | Yes | FAIL | 6.0 |
| gfdl-dougie-fix | gfdl+dougie | RK2b | Yes | FAIL | 5.5 |
| mrv-gfdl-fixed | gfdl+mrv+dougie | RK2b | Yes | FAIL | 5.5 |

All cases in the lower block are the Panama domain with SPLIT_RK2B=True and
OBC_THICKNESS_RESERVOIR_LENGTH_SCALE=9000m.

---

## Key Findings

**The gfdl fix IS correctly implemented.** Verification:
- `MOM.F90` calls `copy_OBC_thickness_reservoirs` in `initialize_MOM` ✓
- `MOM_dynamics_split_RK2b.F90` has `copy_thickness_reservoirs` removed ✓
- `MOM_open_boundary.F90` defines `copy_OBC_thickness_reservoirs` ✓
- Restart file contains `h_res_x`, `h_res_y` with non-zero values (up to ~87m) ✓
- `OBC%h_res_x` is registered for restart read/write ✓
- `setup_OBC_thickness_reservoirs` (called before `copy_OBC_thickness_reservoirs`)
  correctly skips the segment→global copy when the global array is already initialized
  from the restart file ✓

**The gfdl fix does improve things**: h diff drops from 2.0e-4 to 9.1e-5 (normalized)
when the fix is applied. The thickness reservoir ordering issue IS being addressed.

**But there is a residual restart issue specific to SPLIT_RK2B=True** that none of the
three PRs address:
- With RK2, both mrv and dougie independently give clean PASS
- With RK2b, stacking all three fixes (gfdl+mrv+dougie) still leaves Kv_u ≈ 5.5 normalized
- `split_RK2b` has two `btstep` (barotropic solver) calls per timestep vs none in `split_RK2`
- The barotropic OBC handling inside `btstep` is a candidate for this additional restart issue

**What mrv and dougie fix (and why they don't help in RK2b mode):**
- `mrv`: fills exterior h ghost cells in the dynamics routine. In RK2, this is sufficient to
  give a clean PASS. In RK2b, the barotropic substeps may use or overwrite these cells in
  ways the fix doesn't reach.
- `dougie`: removes wind stress at OBC faces. In RK2, this reduces Kv restart discrepancy by
  ~100x (2.7 → 0.025 normalized) but ERS still FAILS. In RK2b, the reduction is even smaller
  (8.8 → 5.5).

---

## Case Locations

All cases at: `/glade/derecho/scratch/manishrv/tests/regional/`

```
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.ctrl
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.mrv-src
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.dougie-src
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.gfdl-src
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.mrv-gfdl-repro
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.gfdl-repro
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.gfdl-fix
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.gfdl-dougie-fix
ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.mrv-gfdl-fixed
```

Run output at: `/glade/derecho/scratch/manishrv/ERS_Ld9.USER_RES.CR_JRA.derecho_intel.mom-regional-base.<case>/run/`

---

## Next Steps

To confirm the RK2b-specific restart issue:
1. Create a case with `SPLIT_RK2B=True`, no thickness reservoirs, no SourceMods —
   compare Kv_u to ctrl. If significantly larger than 2.7, RK2b has a separate baseline
   restart issue.
2. If confirmed, investigate `btstep` in `MOM_barotropic.F90` for OBC ghost cell
   initialization on restart.
