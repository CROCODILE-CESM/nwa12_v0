import s3fs
import xarray as xr
from pathlib import Path

gebco_path = Path("/glade/u/home/manishrv/scratch/ice/croc/zarr/gebco")
tpxo_path = Path("/glade/u/home/manishrv/scratch/ice/croc/zarr/tpxo")

fs = s3fs.S3FileSystem()

# Open the Zarr dataset locally
print("Opening Zarr...")
ds = xr.open_zarr(
    tpxo_path/"u_tpxo9.v1.zarr"
)
# Define S3 path
print("Defining S3 path...")
zarr_s3_path = "s3://crocodile-cesm/CrocoDash/data/tpxo/u_tpxo9.v1.zarr"

# Upload Zarr dataset
print("Uploading Zarr...")
ds.to_zarr(zarr_s3_path, storage_options={"s3": {"anon": False}}, consolidated=True)