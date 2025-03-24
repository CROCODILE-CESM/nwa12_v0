import xesmf as xe
import xarray as xr
import sys
sys.path.append('/glade/u/home/manishrv/documents/croc/dev/CrocoLens')
from CrocoLens.obc import OBC
from CrocoLens.regional_domain import RegionalDomain

glorys_monthly_means = xr.open_dataset("/glade/derecho/scratch/manishrv/glorys_data/nwa_2000_monthly_means/cmems_mod_glo_phy_my_0.083deg_P1M-m_zos-mlotst_100.00W-20.00W_0.00N-60.00N_2000-01-01-2000-12-01.nc")
hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_hgrid.nc")
hgrid["lon"] = hgrid.x
hgrid["lat"] = hgrid.y
#Plot Raw
# rd = RegionalDomain("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_hgrid.nc")
# rd.plot_map()
# glorys_monthly_means.zos[0].plot()
# regridder = xe.Regridder(glorys_monthly_means,hgrid, "bilinear")
# regridded_glorys = regridder(glorys_monthly_means)
# regridded_glorys.to_netcdf("/glade/derecho/scratch/manishrv/glorys_data/nwa_2000_monthly_means/glorys_monthly_means_regridded_to_nwa.nc")
# regridded_glorys.zos[0].plot()
print(glorys_monthly_means)