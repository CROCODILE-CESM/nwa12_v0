import xarray as xr
from pathlib import Path
from datetime import date


def create_seawifs_mask(seawifs_path: str | Path):
    """
    Generate land and ocean masks regridded to SeaWiFS chlorophyll data resolution.

    Parameters
    ----------
    seawifs_path : str or Path
        Path to the directory containing the SeaWiFS chlorophyll and land-water mask NetCDF files.
        Must contain:
            - 'LandWater15ARC.nc' for the original land-water classification.
            - 'SEASTAR_SEAWIFS_GAC.19971001_20101031.L3m.MC.CHL.chlor_a.9km.nc' for chlorophyll data (coordinates used for regridding).

    Returns
    -------
    ds_out : xarray.Dataset
        Dataset containing regridded masks:

        - `LandWater` : xarray.DataArray
            Integer array indicating the original land-water classification.

        - `Ocean` : xarray.DataArray
            Binary ocean mask (1 for ocean, 0 for land or inland water).
            Attributes:
                - `long_name` : "Ocean Mask"
                - `flag_values` : "0, 1"
                - `flag_meanings` : "0=Land or Inland Water, 1=Ocean"

        - `Land` : xarray.DataArray
            Binary land mask (1 for land or inland water, 0 for ocean).
            Attributes:
                - `long_name` : "Land Mask"
                - `flag_values` : "0, 1"
                - `flag_meanings` : "1=Land or Inland Water, 0=Ocean"

        Coordinates are aligned exactly to the chlorophyll dataset.

    Other Effects
    -------------
    - Saves the output dataset to `LandWater_SeaWIFS.nc` in the same directory as `seawifs_path`.
    - Adds a `history` attribute with creation date and source file path.

    """

    # Get Data
    seawifs_path = Path(seawifs_path)
    # Get Land Mask
    LandWaterMask = xr.open_dataset(seawifs_path / "LandWater15ARC.nc")

    # Get a SEAWIFS file (only need the coordinates)
    file_chl = "SEASTAR_SEAWIFS_GAC.19970901_20100930.L3m.MC.CHL.chlor_a.9km.nc"
    ds_chl = xr.open_dataset(seawifs_path / file_chl)

    # Chunk it
    LandWaterMask = LandWaterMask.chunk({"lat": 500, "lon": 500})
    ds_chl = ds_chl.chunk({"lat": 500, "lon": 500})

    # Regrid to CHL

    Mask_lores = (
        LandWaterMask["LandWater"]
        .sel(lon=ds_chl["lon"], lat=ds_chl["lat"], method="nearest")
        .astype("int")
    )

    # Create a corresponding mask of all ocean areas (shallow=0,shelf=6,deep=7)
    Ocean_lores = xr.where(Mask_lores == 0, 1, 0)
    Ocean_lores = xr.where(Mask_lores >= 6, 1, Ocean_lores)
    Ocean_lores = Ocean_lores.astype("int")

    # Create the reciprocal land mask
    Land_lores = (1 - Ocean_lores).astype("int")

    # Put the masks in a dataset
    ds_out = xr.Dataset({"LandWater": Mask_lores})

    ds_out["Ocean"] = Ocean_lores
    ds_out["Ocean"].attrs["long_name"] = "Ocean Mask"
    ds_out["Ocean"].attrs["flag_values"] = "0, 1"
    ds_out["Ocean"].attrs["flag_meanings"] = "0=Land or Inland Water, 1=Ocean"

    ds_out["Land"] = Land_lores
    ds_out["Land"].attrs["long_name"] = "Land Mask"
    ds_out["Land"].attrs["flag_values"] = "0, 1"
    ds_out["Land"].attrs["flag_meanings"] = "1=Land or Inland Water, 0=Ocean"

    # Tweak the coordinates to agree exactly with SeaWIFS
    ds_out.coords["lon"] = ds_chl["lon"]
    ds_out.coords["lat"] = ds_chl["lat"]

    # Add a history attribute
    today = date.today()
    dstr = today.strftime("%Y-%m-%d")
    astr = "Created " + dstr + " from input file " + str(seawifs_path / "LandWater15ARC.nc")
    astr
    ds_out.attrs["history"] = astr

    fileout = seawifs_path / "LandWater_SeaWIFS.nc"
    ds_out.to_netcdf(fileout)


if __name__ == "__main__":
    create_seawifs_mask()
