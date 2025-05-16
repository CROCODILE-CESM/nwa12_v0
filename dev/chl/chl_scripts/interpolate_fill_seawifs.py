from CrocoDash.grid import Grid
import xarray as xr
import numpy as np
from datetime import datetime
from pathlib import Path
from gen_chl_netcdf_file import gen_chl_empty_dataset
from ocean_utils import super_interp, fill_missing_data, super_sample_grid


def interpolate_and_fill_seawifs(
    supergrid_path: str | Path,
    topo_path: str | Path,
    seawifs_processed_path: Path | str,
    grid_name="region",
):
    grid = Grid.from_supergrid(supergrid_path)
    grid.name = grid_name
    ocn_mask = xr.open_dataset(topo_path)["mask"]
    ocn_nj, ocn_ni = ocn_mask.shape

    src_nc = xr.open_dataset(seawifs_processed_path)
    src_data = src_nc["chlor_a"]
    src_nj, src_ni = src_data.shape[-2], src_data.shape[-1]
    src_lon = src_nc[src_data.dims[-1]]
    src_lat = src_nc[src_data.dims[-2]]
    src_lat = ((np.arange(src_nj) + 0.5) / src_nj - 0.5) * 180.0  # Recompute as doubles
    src_x0 = int((src_lon[0] + src_lon[-1]) / 2 + 0.5) - 180.0
    src_lon = (
        (np.arange(src_ni) + 0.5) / src_ni
    ) * 360.0 + src_x0  # Recompute as doubles

    spr_lat, spr_lon = super_sample_grid(grid.qlat, grid.qlon, ocn_mask, src_nj, src_ni)
    
    output_path = (
        Path(__file__).resolve().parent.parent
        / "ncfiles"
        / f"NEWseawifs-clim-1997-2010-{grid.name}.nc"
    )
    chla_tx06 = gen_chl_empty_dataset(output_path, grid.tlon, grid.tlat)
    chlor_a = chla_tx06["CHL_A"]

    for t in range(src_data.shape[0]):
        # for t in range(1):
        q_int = super_interp(src_lat, src_lon, src_data[t, ::-1, :], spr_lat, spr_lon)
        q_int = (
            q_int.swapaxes(1, 2)
            .reshape((ocn_nj, ocn_ni, q_int.shape[3] * q_int.shape[-1]))
            .mean(axis=-1)
        )
        q = q_int * ocn_mask
        chlor_a[t, :] = fill_missing_data(q, ocn_mask)


    # Global attrs
    chla_tx06.title = (
        "Chlorophyll Concentration, OCI Algorithm, interpolated and objectivelly filled to "
        + grid.name
    )
    chla_tx06.repository = "https://github.com/NCAR/SeaWIFS_MOM6"
    chla_tx06.authors = (
        "Gustavo Marques (gmarques@ucar.edu) and Frank Bryan (bryan@ucar.edu )"
    )
    chla_tx06.date = datetime.now().isoformat()

    chla_tx06.variables["CHL_A"][:, :, :] = chlor_a[:, :, :]
    chla_tx06.variables["LON"][:] = grid.tlon[grid.ny, :]
    chla_tx06.variables["LAT"][:] = grid.tlat[:, grid.nx]

    chla_tx06.close()


if __name__ == "__main__":
    interpolate_and_fill_seawifs()
