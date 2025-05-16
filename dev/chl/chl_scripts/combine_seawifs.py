import xarray as xr
import numpy as np
from pathlib import Path
from ocean_utils import lateral_fill
from datetime import datetime, timedelta


def combine_seawifs(
    seawifs_path: Path | str,
    output_path: Path | str = None,
    file_ext_in: str = ".L3m.MC.CHL.chlor_a.9km.nc",
    file_ext_out: str = ".L3m.MC.CHL.chlor_a.0.25deg.nc",
):
    """
    Process and coarsen SeaWiFS chlorophyll data into monthly climatologies with land/ocean masking and NaN filling.

    This function reads SeaWiFS chlorophyll (`chlor_a`) data files for each month of a climatological year,
    applies land/ocean masks, coarsens the data spatially using a median filter, fills NaN values in ocean
    regions using a smoothing method, and writes the result to a NetCDF file.

    Parameters
    ----------
    seawifs_path : Path or str
        Path to the directory containing SeaWiFS data files and the land-water mask file (`LandWater_SeaWIFS.nc`).
    output_path : Path or str, optional
        Directory to which the output file should be written. If not specified, defaults to `seawifs_path`.
    file_ext_in : str, optional
        File extension for the input SeaWiFS chlorophyll files. Default is '.L3m.MC.CHL.chlor_a.9km.nc'.
    file_ext_out : str, optional
        File extension for the output coarsened file. Default is '.L3m.MC.CHL.chlor_a.0.25deg.nc'.

    Returns
    -------
    None
        Writes the processed dataset to a NetCDF file at `output_path`.

    Notes
    -----
    - The function assumes a monthly climatological structure, using 8 months from 1998 and 4 from 1997.
    - Uses a 3x3 median filter to coarsen the chlorophyll data.
    - Fills missing values in the ocean using a Successive Over-Relaxation (SOR)-based lateral fill method.
    - Outputs include:
        - `chlor_a`: Coarsened chlorophyll data.
        - `chlor_a_cf`: NaN-filled version of `chlor_a`.
        - `chlor_a_cfm`: Same as `chlor_a_cf` but with land masked out.
        - `ocean_mask`, `land_mask`: Coarsened boolean masks aligned to output grid.

    Raises
    ------
    ValueError
        If latitude or longitude values in the chlorophyll files differ too much from those in the land-water mask.
    """
    seawifs_path = Path(seawifs_path)

    var_name = "chlor_a"

    file_mask = "LandWater_SeaWIFS.nc"
    ds_mask = xr.open_dataset(seawifs_path / file_mask)
    if output_path is None:
        output_path = seawifs_path
    else:
        output_path = Path(output_path)
    file_out = "NEW_SeaWIFS" / file_ext_out

    # Calculate Date Stuffs
    # First 8 months: 1998, last 4 months: 1997
    date_starts = [datetime(1998, m, 1) for m in range(1, 9)] + [
        datetime(1997, m, 1) for m in range(9, 13)
    ]
    date_ends = [
        (
            (datetime(1998, m + 1, 1) - timedelta(days=1))
            if m < 8
            else (
                (datetime(1997, m + 1, 1) - timedelta(days=1))
                if m < 12
                else datetime(1997, 12, 31)
            )
        )
        for m in range(1, 13)
    ]
    dmid = np.array(
        [
            (
                date_starts[i]
                + (date_ends[i] - date_starts[i]) / 2
                - datetime(date_starts[i].year, 1, 1)
            ).total_seconds()
            / 86400.0
            + 1
            for i in range(12)
        ]
    )

    # Read one SeaWifs File

    file_in = (
        "SEASTAR_SEAWIFS_GAC."
        + date_starts[0].strftime("%Y%j")
        + "_"
        + date_ends[0].strftime("%Y%j")
        + file_ext_in
    )
    ds0 = xr.open_dataset(seawifs_path / file_in)

    # Parameters

    filt_size = 3  # median filter
    # Parameters for fill procedure
    eps_std = 1.0e-5
    nmax_std = 1000
    omega_best = 1.96
    # Start Setting Up Fields
    ntime = 12
    time = xr.DataArray(
        dmid,
        dims=("time",),
        attrs={"long_name": "Mid-Month Day of Climatological Year", "units": "days"},
    )

    # Set up masking arrays
    OceanArea = ds_mask["Ocean"].astype("bool").compute()  # area we want to fill
    LandArea = (
        ds_mask["Land"].astype("bool").compute()
    )  # area with values we don't want used

    # Sample the data to get reduced grid lat/lon and masks
    chl_c = (
        ds0[var_name]
        .coarsen(lon=filt_size, lat=filt_size, coord_func="median")
        .median()
        .compute()
    )  # Removed ,keep_attrs=True

    lon_c = chl_c.lon
    nlon_c = lon_c.size
    lat_c = chl_c.lat
    nlat_c = lat_c.size

    land_c = LandArea.sel(lon=lon_c, lat=lat_c, method="nearest").compute()
    ocn_c = OceanArea.sel(lon=lon_c, lat=lat_c, method="nearest").compute()
    all_c = xr.ones_like(chl_c).astype(
        "bool"
    )  # everywhere on the coarse grid    # Set a bogus value for the north pole

    # Create a DataArray array to hold the input data
    Chl_c = xr.DataArray(
        np.zeros((ntime, nlat_c, nlon_c)),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": lat_c, "lon": lon_c},
    )
    Chl_cf = xr.ones_like(Chl_c)
    Chl_cfm = xr.ones_like(Chl_c)

    # Read the SeaWIFS data, coarsen, fill NaNs and store in DataArray
    for n, d in enumerate(date_starts):

        # Open Dataset
        file_in = (
            "SEASTAR_SEAWIFS_GAC."
            + date_starts[n].strftime("%Y%j")
            + "_"
            + date_ends[n].strftime("%Y%j")
            + file_ext_in
        )
        ds = xr.open_dataset(seawifs_path / file_in)

        # Error Adjustment
        tolerance = 1e-5

        # Create boolean masks where the differences are smaller than the tolerance
        lat_close = np.all(
            np.isclose(
                LandArea["lat"].values, ds[var_name]["lat"].values, atol=tolerance
            )
        )
        lon_close = np.all(
            np.isclose(
                LandArea["lon"].values, ds[var_name]["lon"].values, atol=tolerance
            )
        )

        # If the differences are too large, raise an error
        if not lat_close or not lon_close:
            raise ValueError(
                "The latitude or longitude values differ too much between the datasets!"
            )
        else:
            ds["lat"] = LandArea.lat
            ds["lon"] = LandArea.lon

        # Mask out values in lakes and inland waters
        Chl_src = xr.where(LandArea, np.nan, ds[var_name])

        # Coarsen with a median filter
        c = (
            Chl_src.coarsen(lon=filt_size, lat=filt_size, coord_func="median")
            .median()
            .compute()
        )

        # Fill NaNs in ocean areas
        cf = lateral_fill(
            c.compute(),
            all_c,
            tol=eps_std,
            rc=omega_best,
            max_iter=nmax_std,
            use_sor=True,
        )

        cfm = xr.where(land_c, np.nan, cf)

        # Put result in 3D array
        Chl_c.loc[dict(time=time[n])] = c
        Chl_cf.loc[dict(time=time[n])] = cf
        Chl_cfm.loc[dict(time=time[n])] = cfm

    # Set Attrs
    Chl_c.attrs = ds0[var_name].attrs
    Chl_cf.attrs = ds0[var_name].attrs
    Chl_cfm.attrs = ds0[var_name].attrs

    # Create output dataset
    ds_out = xr.Dataset(
        {
            var_name: Chl_c,
            var_name + "_cf": Chl_cf,
            var_name + "_cfm": Chl_cfm,
            "ocean_mask": ocn_c,
            "land_mask": land_c,
        }
    )
    ds_out.to_netcdf(output_path / file_out)


if __name__ == "__main__":
    combine_seawifs()
