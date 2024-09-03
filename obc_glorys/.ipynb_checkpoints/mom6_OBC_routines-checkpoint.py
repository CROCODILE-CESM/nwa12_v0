### set of routines to validate/analyze MOM6 output for the Carib 1/12 config
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xesmf
import xarray as xr
import os
import math
import netCDF4

#---get nominal grid from supergrid:
def get_nominal_MOM6grid(supergrid):
  '''
  Reads supergrid and returns an object with grid metrics
  '''
  # MOM6 supergrid file
  nc_sgrd = netCDF4.Dataset(supergrid)
  x = nc_sgrd.variables['x'][:]
  y = nc_sgrd.variables['y'][:]
  dx = nc_sgrd.variables['dx'][:]
  dy = nc_sgrd.variables['dy'][:]
  area = nc_sgrd.variables['area'][:]
  angle_dx = nc_sgrd.variables['angle_dx'][:]
  nc_sgrd.close()
  #################### Model grid ####################
  # T point locations
  tlon = x[1::2,1::2]
  tlat = y[1::2,1::2]
  # U point locations
  ulon = x[1::2,::2]
  ulat = y[1::2,::2]
  # V point locations
  vlon = x[::2,1::2]
  vlat = y[::2,1::2]
  # Corner point locations
  qlon = x[::2,::2]
  qlat = y[::2,::2]
  # T cell area (sum of four supergrid cells)
  tarea = area[::2,::2] + area[1::2,1::2] + area[::2,1::2] + area[::2,1::2]
  # t-point angle
  angle = angle_dx[1::2,1::2]
  # x-distance between u-points, centered at t
  dxt = dx[1::2,::2] + dx[1::2,1::2]
  # y-distance between v-points, centered at t
  dyt = dy[::2,1::2] + dy[1::2,1::2]
  # x-distance between  q-points, centered at v
  dxCv = dx[2::2,::2] + dx[2::2,1::2]
  # y-distance between  q-points, centered at u
  dyCu = dy[::2,2::2] + dy[1::2,2::2]
  # grid aspect ratio
  ar = dyt / dxt
  # grid effective grid spacing
  # A = 4*pi*r^2 , area of sphere of radius r
  # dA = (r*cos(theta)*dlambda)*(r*dtheta), differential area on sphere
  #    = r^2*domega
  # domega = dA/r^2, differential solid angle  (steradians, sr)
  # 1 sr = (180./pi)^2 square degrees
  costheta = np.cos(tlat*np.pi/180.)
  rearth = 637122000 # Earth radius in centimeter
  domega = tarea / rearth**2
  egs  = np.sqrt(domega * (180./np.pi)**2)

  # create an empty class object
  class MOM6_grd:
    pass

  # fill grid object
  MOM6_grd.tlon = tlon
  MOM6_grd.tlat = tlat
  MOM6_grd.ulon = ulon
  MOM6_grd.ulat = ulat
  MOM6_grd.vlon = vlon
  MOM6_grd.vlat = vlat
  MOM6_grd.qlon = qlon
  MOM6_grd.qlat = qlat
  MOM6_grd.dxt = dxt
  MOM6_grd.dyt = dyt
  MOM6_grd.dxCv = dxCv
  MOM6_grd.dyCu = dyCu
  MOM6_grd.angle = angle
  MOM6_grd.tarea = tarea
  MOM6_grd.L = tarea.shape[1]
  MOM6_grd.M = tarea.shape[0]
  print('MOM6 grid was successfully loaded... \n')
  return MOM6_grd


#compare dataset dates and subsample to latest first date and earliest last date between both datasets:
def comp_date_subsample(ds1,ds2):
    start_date = max(ds1.time[0],ds2.time[0])
    end_date   = min(ds1.time[-1],ds2.time[-1])
    ds1 = ds1.sel(time=slice(start_date,end_date))
    ds2 = ds2.sel(time=slice(start_date,end_date))
    return ds1, ds2

#check dir exists, if not, create it:
def make_dir(dir_str):
    if not os.path.exists(dir_str):
        os.makedirs(dir_str)
        print("new directory created: "+ dir_str)

def get_rmse(da_truth, da_estim):
    rmse =  math.sqrt(np.nanmean((da_truth.values - 
                                        da_estim.values)**2)) 
    return rmse

def get_depth_deepest_value(da):
    depth_dim = len(da['depth'])
    # Initialize variables to store the last non-NaN depth and corresponding data
    last_valid_depth = None
    last_valid_data = None

    # Iterate through depth levels
    for depth_index in range(depth_dim):
        depth_slice = da[depth_index,...]  # Extract data at the current depth level

        # Check if there are any non-NaN values in the depth slice
        if not np.all(np.isnan(depth_slice)):
            last_valid_depth = depth_index
            last_valid_data = depth_slice
        
    deepest = da['depth'][last_valid_depth]
    return deepest  

def weighted_temporal_mean(ds, var):
    """
    weight by days in each month
    """
    # Determine the month length
    month_length = ds.time.dt.days_in_month

    # Calculate the weights
    wgts = month_length.groupby("time.year") / month_length.groupby("time.year").sum()

    # Make sure the weights in each year add up to 1
    np.testing.assert_allclose(wgts.groupby("time.year").sum(xr.ALL_DIMS), 1.0)

    # Subset our dataset for our variable
    obs = ds

    # Setup our masking for nan values
    cond = obs.isnull()
    ones = xr.where(cond, 0.0, 1.0)

    # Calculate the numerator
    obs_sum = (obs * wgts).resample(time="AS").sum(dim="time")

    # Calculate the denominator
    ones_out = (ones * wgts).resample(time="AS").sum(dim="time")

    # Return the weighted average
    return obs_sum / ones_out


#find index of point nearest to value:
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

#used to standardize variable names across datasets:
def standardize_var_names(data,var_names_dictionary):
    #standardize the variable names in the specified dataset
    #Inputs: data (dataset), var_names_dictionary is a dictionary conatining the varibale names and their new name (i.e. same way that it is  specified in dataset.rename)
    data = data.rename(var_names_dictionary)
    
    return data

def calculate_layer_interfaces(layer_centers):
    """
    Calculate the depth of the layer interfaces from the depth of the layer centers.
    Parameters:
        layer_centers (list or numpy.ndarray): Depths of the layer centers.
    Returns:
        list: Depths of the layer interfaces.
    """
    num_layers = len(layer_centers)
    layer_interfaces = [0.0]  # The depth of the first layer interface is always 0.

    for i in range(1, num_layers):
        interface_depth = (layer_centers[i] + layer_centers[i - 1]) / 2.0
        layer_interfaces.append(interface_depth)

    # The depth of the last layer interface is equal to the depth of the last layer center.
    layer_interfaces.append(layer_centers[-1])

    return layer_interfaces

#calculate an areaweighted mean of 2d field
def areaweighted_region_mean(dxr,latstr,lonstr):
    # given an xarray dataset <grid> for a given depth and time,
    # calculate the mean of the gridded data variable, weighted by grid cell area
    if latstr == 'latitude':
        bfr = dxr.latitude
    elif latstr == 'yh':
        bfr = dxr.yh
    weights = np.cos(np.deg2rad(bfr))
    weights.name = "weights"
    dxr_weighted = dxr.weighted(weights)
    
    return dxr_weighted.mean((lonstr, latstr))

#convert daily dataset to monthly and set timestamp to day of month specified by the offset value
def daily_to_monthly(data,offset):
    #provide daily data and resample to monthly means with desired offset for output date
    bfr = data.resample(time='1MS',loffset=pd.Timedelta(offset,'d')).mean(dim='time')
    
    return bfr

#calculate seasonal cycle and remove from data:
def remove_seasonal(data):
    seas_cycle = data.groupby('time.month').mean(dim='time')
    seas_cycle = seas_cycle.broadcast_like(data)
    data_noseas= data.groupby('time.month') - seas_cycle
    
    return data_noseas

#group data by seasons
def get_seasonal(data):
    bfr = data.groupby("time.season").mean()
    
    return bfr

#get difference between two datasets/fields    
def gridded_dif(data1,data2,varname):
    bfr = data1[varname] - data2[varname]
    
    return bfr

#specify a depth level and subset dataset to nearest level
def get_depth(data_in,depth2plot):
    #find nearest depth in data_in to depth2plot and subset the dataset to only that level
    bfr = data_in.sel(depth=depth2plot,method='nearest')
    
    return bfr

#horizontal regridding of a dataset to mom6 hgrid
def regrid2mom6_horizontal(data2regrid,target_grid,method):
    target = (target_grid
        [['x', 'y']]
        .isel(nxp=slice(1, None, 2), nyp=slice(1, None, 2))
        .rename({'y': 'lat', 'x': 'lon', 'nxp': 'xh', 'nyp': 'yh'})
    )

    regrid_kws      =  dict(method=method, reuse_weights=False, periodic=False)
    ds_regridder    = xesmf.Regridder(data2regrid, target, **regrid_kws)
    bfr_regridded   = ds_regridder(data2regrid)
    
    return bfr_regridded

#vertical regridding of a dataset to mom6 vertical grid
def regrid2mom6_vertical(data2regrid,target_grid):
    z       = vgrid_to_layers(target_grid)
    ztarget = xr.DataArray(z,
                    name='zl',
                    dims=['zl'], 
                    coords={'zl': z}, 
                    )
    bfr_regridded = data2regrid.interp(depth=ztarget)
    
    return bfr_regridded

#mom6 vertical grid to layers
def vgrid_to_layers(vgrid, max_depth=6500.0):
    if isinstance(vgrid, xr.DataArray):
        vgrid = vgrid.data
    ints = vgrid_to_interfaces(vgrid, max_depth=max_depth)
    z = (ints + np.roll(ints, shift=1)) / 2
    layers = z[1:]
    
    return layers

#mom6 vertical grid to interfaces
def vgrid_to_interfaces(vgrid, max_depth=6500.0):
    if isinstance(vgrid, xr.DataArray):
        vgrid = vgrid.data
    zi = np.concatenate([[0], np.cumsum(vgrid)])
    zi[-1] = max_depth
    return zi


#creates a merged ocean mask between mom6 mask and glorys mask
def merge_mom6_glorys_mask(mom,glorys,field):
    bfr_temp = glorys.copy(deep=True)
    bfr_ocnmask = mom.copy(deep=True).values
    mask_merged = bfr_temp[field].sum(dim='time').values * np.nan
    
    mom.plot()
    plt.show()
    for iz in range(len(bfr_temp['depth'].values)):
        bfr_temp2 = bfr_temp[field][:,iz,:,:].sum(dim='time').values

        bfr_temp2[bfr_temp2!=0]=1
        mask_merged[iz,:,:]=bfr_temp2+bfr_ocnmask
    
    plt.pcolormesh(mask_merged[-1,:,:],vmin=0,vmax=3)
    plt.colorbar()
    plt.title('only keep values=2')
    plt.show()    
    return mask_merged

# plots the name of transects on map (used for mom6_section_transport_validation.ipynb)
def plot_tsec_name(tsec_lon,tsec_lat, lon_offset,lat_offset,tsec_name,orientation,box_type='square',edge_color='k',face_color='w'):
    ax = plt.gca()
    ax.text(tsec_lon + lon_offset,tsec_lat + lat_offset,tsec_name,rotation=orientation,fontsize=15,bbox=dict(boxstyle=box_type,ec=edge_color,fc=face_color))
    return ax

# masking
def ice9_v2(i, j, source, xcyclic=False, tripolar=False):
  """
  An iterative (stack based) implementation of "Ice 9".

  The flood fill starts at [j,i] and treats any positive value of "source" as
  passable. Zero and negative values block flooding.

  xcyclic = True allows cyclic behavior in the last index. (default)
  tripolar = True allows a fold across the top-most edge. (default)

  Returns an array of 0's and 1's.
  """
  wetMask = 0*source
  (nj,ni) = wetMask.shape
  stack = set()
  stack.add( (j,i) )
  while stack:
    (j,i) = stack.pop()
    if wetMask[j,i] or source[j,i] <= 0: continue
    wetMask[j,i] = 1
    if i>0: stack.add( (j,i-1) )
    elif xcyclic: stack.add( (j,ni-1) )
    if i<ni-1: stack.add( (j,i+1) )
    elif xcyclic: stack.add( (j,0) )
    if j>0: stack.add( (j-1,i) )
    if j<nj-1: stack.add( (j+1,i) )
    elif tripolar: stack.add( (j,ni-1-i) ) # Tri-polar fold
  
  return wetMask

#used in generating sponges from glorys, and obc
def regrid_tracer_sponge(fld, ds_in, ds_out, method='bilinear',extrap_method = None):

    regrid = xesmf.Regridder(
        ds_in,
        ds_out,
        method=method,
        periodic=False,
        extrap_method=extrap_method
        
    )
       
    fld_out = regrid(ds_in)

    return fld_out

def regrid_tracer_obc(ds_in, ds_out, method='bilinear',extrap_method = None):

    regrid = xesmf.Regridder(
        ds_in,
        ds_out,
        method=method,
        periodic=False,
        extrap_method=extrap_method   
    )
       
    fld_out = regrid(ds_in)

    return fld_out

#
def regrid_zfill_extrapolate(var_name,ds_in,ds_out_tracer,ztarget,extrap_method):
    # Interpolate Data vertically onto target grid.
    regridded_var = ds_in[var_name].interp(depth=ztarget)

    #use kara.flood (Raph) to flood over land
    #regridded_var = flood.flood_kara(regridded_var, zdim='zl')

    #regrid horizontal:
    regridded_var = regrid_tracer(var_name, regridded_var, ds_out_tracer)
    #regridded_var = regrid_tracer(var_name, regridded_var, ds_out_tracer,extrap_method=extrap_method)
    regridded_var = flood.flood_kara(regridded_var,xdim='xh', ydim='yh', zdim='zl')
    for i in range(len(regridded_var['zl'])-1):
        bfr = regridded_var[:,i+1,:,:].values
        bfr[mask.values==0] = np.nan
        #bfr = xr.where(mask['mask']==1,bfr,np.nan)
        regridded_var[:,i+1,:,:] = bfr
    regridded_var = regridded_var.ffill('zl', limit=None)
    #regridded_var = regridded_var.rename({'zl':'depth'})

    var_filled = regridded_var.copy()
    return var_filled 

#subset input data to desired segment
def get_segment_fill(segment,data_in):
    
    #data_in = data_in.rename({'latitude':'lat','longitude':'lon'})
    if segment == 1:
        data = data_in[:,:,:,-1]
        data = data.ffill(dim='nyp', limit=None).bfill(dim='nyp', limit=None)
        data = data.ffill(dim='depth',limit=None)
    elif segment == 2:
        data = data_in[:,:,-1,:]
        data = data.ffill(dim='nxp', limit=None).bfill(dim='nxp', limit=None)
        data = data.ffill(dim='depth',limit=None)
    elif segment == 3:
        data = data_in[:,:,:,0]
        data = data.ffill(dim='nyp', limit=None).bfill(dim='nyp', limit=None)
        data = data.ffill(dim='depth',limit=None)
    elif segment == 4:
        data = data_in[:,:,0,:]
        data = data.ffill(dim='nxp', limit=None).bfill(dim='nxp', limit=None)
        data = data.ffill(dim='depth',limit=None)
        
    return data

def get_segment_fill_le2(segment,data_in):
    
    #data_in = data_in.rename({'latitude':'lat','longitude':'lon'})
    if segment == 1:
        data = data_in[:,:,:,-1]
        data = data.ffill(dim='nyp', limit=None).bfill(dim='nyp', limit=None)
        data = data.ffill(dim='z_t',limit=None)
    elif segment == 2:
        data = data_in[:,:,-1,:]
        data = data.ffill(dim='nxp', limit=None).bfill(dim='nxp', limit=None)
        data = data.ffill(dim='z_t',limit=None)
    elif segment == 3:
        data = data_in[:,:,:,0]
        data = data.ffill(dim='nyp', limit=None).bfill(dim='nyp', limit=None)
        data = data.ffill(dim='z_t',limit=None)
    elif segment == 4:
        data = data_in[:,:,0,:]
        data = data.ffill(dim='nxp', limit=None).bfill(dim='nxp', limit=None)
        data = data.ffill(dim='z_t',limit=None)
        
    return data

def get_segment_fill_zeta(segment,data_in):
    if segment == 1:
        data = data_in[:,:,-1]
        data = data.ffill(dim='nyp', limit=None).bfill(dim='nyp', limit=None)
    elif segment == 2:
        data = data_in[:,-1,:]
        data = data.ffill(dim='nxp', limit=None).bfill(dim='nxp', limit=None)
    elif segment == 3:
        data = data_in[:,:,0]
        data = data.ffill(dim='nyp', limit=None).bfill(dim='nyp', limit=None)
    elif segment == 4:
        data = data_in[:,0,:]
        data = data.ffill(dim='nxp', limit=None).bfill(dim='nxp', limit=None)
        
    return data

def create_obcs(data_in,z_target,x_target,topo_data):

    # Note: depending on the geometry of the source and target grids, this code may need rethinking.
    # For example: in our case, the southeastern most points in our grid are shallower in the source grid than the target grid.

    #interpolate vertical grid (no extrapolation)
    regridded_var = ds_in['so'].interp(depth=ztarget)
    #interpolate horizontally (no extrapolation)
    regridded_var = regrid_tracer('so', regridded_var, target_horizontal_grid)
    #fill vertically:
    regridded_var = regridded_var.ffill(dim='zl', limit=None)
    #apply bathy mask:
    topo4d = np.copy(regridded_var)
    for t in range(len(regridded_var['time'])):
        for z in range(len(regridded_var['zl'])):
            topo4d[t,z,:,:] = topo['depth'].values        
    k = len(regridded_var['zl'])
    a = regridded_var['zl']
    j = len(regridded_var['xh'])
    i = len(regridded_var['yh'])
    l = len(regridded_var['time'])
    depth4d = np.transpose(np.tile(a,j*i*l).reshape((i,j,l,k)),(2,3,0,1))
    #appply mask
    regridded_var = regridded_var.where(depth4d<topo4d,np.nan) 
    #fill horizontally (longitude first)
    regridded_var = regridded_var.bfill(dim='xh', limit=None).ffill(dim='xh', limit=None)
    
    return regridded_var            
