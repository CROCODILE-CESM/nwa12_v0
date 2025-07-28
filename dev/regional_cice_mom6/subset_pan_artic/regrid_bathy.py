import xesmf as xe
import xarray as xr
import numpy as np
ds = xr.open_dataset("/glade/u/home/manishrv/scratch/croc_input/cice.kate.1/ocnice/ocean_topog_cice_test_1_eaf771.nc")
target = xr.open_dataset("bathymetry_unfinished.nc")
ds["lon"] = ds.x
ds["lat"] = ds.y

# Save or pass this modified dataset to xesmf
gebco_bathy = ds  # or whatever variable you want
weights = xe.Regridder(gebco_bathy, target,"nearest_s2d", filename = "gebco_weights.nc", periodic = True)
gebco_bathy_regrid = weights(gebco_bathy)
gebco_bathy_regrid.to_netcdf("/glade/u/home/manishrv/documents/croc/dev/regional_cice_mom6/subset_pan_artic/gebco_bathy_regrid.nc")
bathy = xr.open_dataset("bathymetry_unfinished.nc")
bathy_regrid = xr.open_dataset("gebco_bathy_regrid.nc")
bathy["depth"] = bathy_regrid.depth
bathy.to_netcdf("bathymetry_unfinished_2.nc")