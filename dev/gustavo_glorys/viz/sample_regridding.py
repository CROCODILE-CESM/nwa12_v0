
# Regridding Package
import xesmf as xe

# NetCDF Package
import xarray as xr

# Access Specific Points
from regional_mom6 import regridding as rgd

# Read in Datasets
glorys_monthly_means = xr.open_dataset("/glade/derecho/scratch/manishrv/glorys_data/nwa_2000_monthly_means/cmems_mod_glo_phy_my_0.083deg_P1M-m_zos-mlotst_100.00W-20.00W_0.00N-60.00N_2000-01-01-2000-12-01.nc")
hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_hgrid.nc")

# Get Specific Points on what to regird to, u, v or t
points = rgd.get_hgrid_arakawa_c_points(hgrid, "v")
print(points)


# Create a lat/lon field in both the destination(hgrid) and source (glorys_monthly_mean)
# Source already has it.

# I subset to the specific points I want (V points)
hgrid["lon"] = hgrid.x[points.v_points_x]
hgrid["lat"] = hgrid.y[points.v_points_y]

# Regridding is two steps
# 1. Calculate Weights -> this only needs to be done ONCE per dataset -> see rgd.create_regridder for some defaults we use. 
# In this, the destination is hgrid and the source is glorys_monthly_means, we can always switch as needed. Because the resolution was so similar for NWA, it didn't really matter.
regridder = xe.Regridder(glorys_monthly_means,hgrid, "bilinear")

# 2. Apply weights to dataset (I would subset to only variables required)
regridded_glorys = regridder(glorys_monthly_means)

#Save
regridded_glorys.to_netcdf("/glade/derecho/scratch/manishrv/glorys_data/nwa_2000_monthly_means/glorys_monthly_means_regridded_to_nwa.nc")

