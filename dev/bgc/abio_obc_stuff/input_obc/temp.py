import xarray as xr
import numpy as np
ds = xr.open_dataset("/glade/u/home/manishrv/documents/croc/dev/bgc/input_obc/salt_001_2005.nc")
print(ds.isel(time=0,ny_segment_001=0,nx_segment_001=0)["dz_salt_segment_001"].data)

print(np.sum(ds.isel(time=0,ny_segment_001=0,nx_segment_001=0)["dz_salt_segment_001"].data))