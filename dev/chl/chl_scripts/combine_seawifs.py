import xarray as xr
import numpy as np
from pathlib import Path
from ocean_utils import lateral_fill

def main():
    # File locations
    path_in = Path('/glade/work/gmarques/cesm/tx2_3/chlorophyll/ncfiles/')

    file_ext_in = '.L3m_MC_CHL_chlor_a_9km.nc' # SeaWIFS 9km product
    file_ext_out = '.L3m_MC_CHL_chlor_a_0.25deg.nc'
    var_name = 'chlor_a'

    file_mask = 'LandWater_SeaWIFS.nc'
    ds_mask = xr.open_dataset(path_in/file_mask)

    path_out = Path("/glade/u/home/manishrv/documents/croc/dev/chl/SeaWIFS_MOM6/ncfiles")
    file_out = 'NEWSeaWIFS' / file_ext_out

    # Parameters for median filter
    filt_size = 3

    # Parameters for fill procedure
    eps_std = 1.0e-5
    nmax_std = 1000
    omega_best=1.96

    # Dates for month boundaries
    dbeg = np.array([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    dend = np.zeros_like(dbeg)
    dend[:-1] = dbeg[1:]-1
    dend[-1] = 365
    dmid = 0.5*(dbeg + dend)

sybeg = ['1998','1998','1998','1998','1998','1998','1998','1998','1997','1997','1997','1997']
syend= 12*['2010']

def gen_datestr(ybeg,dbeg,yend,dend) :
    datestr = '{:s}{:03d}{:s}{:03d}'.format(ybeg,dbeg,yend,dend)
    return datestr
# Get the first file to grab the dimensions, coordinates
file_in = 'S' + gen_datestr(sybeg[0],dbeg[0],syend[0],dend[0]) + file_ext_in
print('Input file: ',file_in)
ds0 = xr.open_dataset(path_in+file_in)

nlat=ds0.dims['lat']
lat = ds0['lat']

nlon=ds0.dims['lon']
lon = ds0['lon']

ntime=12
time = xr.DataArray(dmid,dims=("time",),
                    attrs={"long_name":'Mid-Month Day of Climatological Year',
                           "units":'days'})

# Set up masking arrays
OceanArea = ds_mask['Ocean'].astype('bool').compute() # area we want to fill
LandArea = ds_mask['Land'].astype('bool').compute() # area with values we don't want used
Everywhere = xr.ones_like(LandArea).astype('bool')

# Sample the data to get reduced grid lat/lon and masks
chl_c = ds0[var_name].coarsen(lon=filt_size,lat=filt_size,coord_func='median').median().compute() # Removed ,keep_attrs=True

lon_c = chl_c.lon
nlon_c = lon_c.size
lat_c = chl_c.lat
nlat_c = lat_c.size

land_c = LandArea.sel(lon=lon_c,lat=lat_c,method='nearest').compute()
ocn_c = OceanArea.sel(lon=lon_c,lat=lat_c,method='nearest').compute()
all_c = xr.ones_like(chl_c).astype('bool')  # everywhere on the coarse grid    # Set a bogus value for the north pole

# Create a DataArray array to hold the input data
Chl_c = xr.DataArray(np.zeros((ntime,nlat_c,nlon_c)),
                        dims=("time","lat","lon"),
                        coords={"time":time,"lat":lat_c,"lon":lon_c}
                       )
Chl_cf = xr.ones_like(Chl_c)
Chl_cfm = xr.ones_like(Chl_c)


# Read the SeaWIFS data, coarsen, fill NaNs and store in DataArray
for n,d in enumerate(dbeg):
    file_in = 'S' + gen_datestr(sybeg[n],dbeg[n],syend[n],dend[n]) + file_ext_in
    print(n,file_in)
    ds=xr.open_dataset(path_in+file_in)

    # Error Adjustment
    tolerance = 1e-5

    # Check if the latitudes and longitudes in both datasets are close enough
    lat_diff = np.abs(LandArea['lat'].values - ds[var_name]['lat'].values)
    lon_diff = np.abs(LandArea['lon'].values - ds[var_name]['lon'].values)
    
    # Create boolean masks where the differences are smaller than the tolerance
    lat_close = np.all(np.isclose(LandArea['lat'].values, ds[var_name]['lat'].values, atol=tolerance))
    lon_close = np.all(np.isclose(LandArea['lon'].values, ds[var_name]['lon'].values, atol=tolerance))
    
    # If the differences are too large, raise an error
    if not lat_close or not lon_close:
        raise ValueError("The latitude or longitude values differ too much between the datasets!")
    else:
        ds["lat"] = LandArea.lat
        ds["lon"] = LandArea.lon
    
        # Mask out values in lakes and inland waters
    print(' ... masking')
    Chl_src = xr.where(LandArea,np.nan,ds[var_name])
    
    # Coarsen with a median filter
    print(' ... coarsening')
    c = Chl_src.coarsen(lon=filt_size,lat=filt_size,coord_func='median').median().compute()

    # Fill NaNs in ocean areas
    print(' ... filling')
    cf = lateral_fill(c.compute(),all_c,
            tol=eps_std,rc=omega_best,max_iter=nmax_std,use_sor=True)
    
    print(' ... masking')
    cfm = xr.where(land_c,np.nan,cf)
    
    # Put result in 3D array
    Chl_c.loc[dict(time=time[n])] = c
    Chl_cf.loc[dict(time=time[n])] = cf
    Chl_cfm.loc[dict(time=time[n])] = cfm
    
Chl_c.attrs = ds0[var_name].attrs
Chl_cf.attrs = ds0[var_name].attrs
Chl_cfm.attrs = ds0[var_name].attrs

ds_out = xr.Dataset({var_name:Chl_c,
                     var_name+'_cf':Chl_cf,
                     var_name+'_cfm':Chl_cfm,
                     'ocean_mask':ocn_c,
                     'land_mask':land_c})
ds_out.to_netcdf(path_out/file_out)


if __name__ == "__main__":
    main()