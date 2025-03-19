import xarray as xr
import zarr
from pathlib import Path

gebco_path = Path("/glade/u/home/manishrv/scratch/ice/croc/zarr/gebco")
tpxo_path = Path("/glade/u/home/manishrv/scratch/ice/croc/zarr/tpxo")

# Open NetCDF with spatial chunking
print("Opening NetCDF...")
ds = xr.open_dataset("/glade/derecho/scratch/manishrv/ice/croc/gebco/GEBCO_2024.nc", chunks={"lat": 100, "lon": 100})

# Apply Blosc compression
print("Applying Blosc compression...")
encoding = {var: {"compressor": zarr.Blosc(cname="zstd", clevel=3)} for var in ds.data_vars}

# Save to Zarr
print("Saving to Zarr...")
ds.to_zarr(gebco_path/"GEBCO_2024.zarr", encoding=encoding, consolidated=True)

