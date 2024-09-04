#!/usr/bin/env python
import numpy as np
import xarray as xr
import numpy as np
from mpl_toolkits.basemap import pyproj
from datetime import datetime


# decimation factor
k=2

kp2=k//2

# MOM6 supergrid file
hgrd = xr.open_dataset('input_files/ocean_hgrid.nc')
x = hgrd['x'].values
y = hgrd['y'].values
dx = hgrd['dx'].values
dy = hgrd['dy'].values
area = hgrd['area'].values
angle_dx = hgrd['angle_dx'].values
hgrd.close()

# Wet/dry mask
if k==2:
  try:
    msk = xr.open_dataset('input_files/ocean_mask.nc')
    tmask = msk['mask']
    msk.close()
  except:
    tmask=None
    print('No land mask provided')
  # topo
  try:
    topo = xr.open_dataset('input_files/ocean_topo.nc')
    depth = topo['depth']
    topo.close()
  except:
    depth=None
    print('No topo provided')
else:
  tmask=None
  depth=None

####################################################
#################### Model grid ####################
####################################################


# T point locations
tlon = x[kp2::k,kp2::k]
tlat = y[kp2::k,kp2::k]

# U point locations
ulon = x[kp2::k,::k]
ulat = y[kp2::k,::k]

# V point locations
vlon = x[::k,kp2::k]
vlat = y[::k,kp2::k]

# Corner point locations
qlon = x[::k,::k]
qlat = y[::k,::k]

# t-point angle
angle = angle_dx[kp2::k,kp2::k]



# T cell area (sum of four supergrid cells)
tarea = area[::k,::k] + area[1::k,1::k] + area[::k,1::k] + area[::k,1::k]

# x-distance between u-points, centered at t
dxt = dx[kp2::k,::k] + dx[kp2::k,1::k]

# y-distance between v-points, centered at t
dyt = dy[::k,kp2::k] + dy[1::k,kp2::k]

# x-distance between  q-points, centered at v
dxCv = dx[k::k,::k] + dx[k::k,1::k]

# y-distance between  q-points, centered at u
dyCu = dy[::k,k::k] + dy[1::k,k::k]

# x-distance between t-points, centered at u
dxr = np.roll(dx, -kp2, axis=1)
dxCu =  dxr[kp2::k,::k] + dxr[kp2::k,1::k]

# y-distance between t-points, centered at v
dyr = np.roll(dy, -kp2, axis=0)
#north seam periodicity
dyr[-1,:] = dyr[-4,::-1]
dyr[-2,:] = dyr[-3,::-1]
dyCv =  dyr[::k,kp2::k] + dyr[1::k,kp2::k]



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


####################################################################
#################### write MOM6 model grid file ####################
####################################################################
import netCDF4

def write_nc_var(var, name, dimensions, long_name=None, units=None, coordinates=None):
    nc.createVariable(name, 'f8', dimensions)
    if long_name is not None:
        nc.variables[name].long_name = long_name
    if units is not None:
        nc.variables[name].units = units
    if coordinates is not None:
        nc.variables[name].coordinates = coordinates
    nc.variables[name][:] = var
    print(' ... wrote variable {}'.format(name))


# create netcdf file
filename = 'input_files/NWA12_grid.nc'
nc = netCDF4.Dataset(filename, 'w', format='NETCDF4')
nc.Description = 'MOM6 NCAR NWA12 grid (ORCA type)'
nc.Author = 'Fred Castruccio (fredc@ucar.edu)'
nc.Created = datetime.now().isoformat()
nc.type = 'NWA12v1 file'


# create netcdf dimension
M, L = qlon.shape
nc.createDimension('nyp', M)
nc.createDimension('nxp', L)
nc.createDimension('ny', M-1)
nc.createDimension('nx', L-1)


# write variable
write_nc_var(tlon, 'tlon', ('ny', 'nx'), 'array of t-grid longitudes', 'degrees_east')
write_nc_var(tlat, 'tlat', ('ny', 'nx'), 'array of t-grid latitudes', 'degrees_north')
write_nc_var(ulon, 'ulon', ('ny', 'nxp'), 'array of u-grid longitudes', 'degrees_east')
write_nc_var(ulat, 'ulat', ('ny', 'nxp'), 'array of u-grid latitudes', 'degrees_north')
write_nc_var(vlon, 'vlon', ('nyp', 'nx'), 'array of v-grid longitudes', 'degrees_east')
write_nc_var(vlat, 'vlat', ('nyp', 'nx'), 'array of v-grid latitudes', 'degrees_north')
write_nc_var(qlon, 'qlon', ('nyp', 'nxp'), 'array of q-grid longitudes', 'degrees_east')
write_nc_var(qlat, 'qlat', ('nyp', 'nxp'), 'array of q-grid latitudes', 'degrees_north')

write_nc_var(dxt, 'dxt', ('ny', 'nx'), 'x-distance between u-points, centered at t', 'meters')
write_nc_var(dyt, 'dyt', ('ny', 'nx'), 'y-distance between v-points, centered at t', 'meters')
write_nc_var(dxCv, 'dxCv', ('ny', 'nx'), 'x-distance between  q-points, centered at v', 'meters')
write_nc_var(dyCu, 'dyCu', ('ny', 'nx'), 'y-distance between  q-points, centered at u', 'meters')
write_nc_var(dxCu, 'dxCu', ('ny', 'nx'), 'x-distance between  t-points, centered at u', 'meters')
write_nc_var(dyCv, 'dyCv', ('ny', 'nx'), 'y-distance between  t-points, centered at v', 'meters')

write_nc_var(tarea, 'tarea', ('ny', 'nx'), 'area of t-cells', 'meters^2')

if isinstance(tmask, xr.DataArray):
  write_nc_var(tmask, 'tmask', ('ny', 'nx'), 'ocean fraction at t-cell centers', 'none')

write_nc_var(angle, 'angle', ('ny', 'nx'), 'angle grid makes with latitude line', 'degrees')

if isinstance(depth, xr.DataArray):
  write_nc_var(depth, 'depth', ('ny', 'nx'), 'depth at h points', 'meters')

write_nc_var(ar, 'ar', ('ny', 'nx'), 'grid aspect ratio (dyt/dxt)', 'none')

write_nc_var(egs, 'egs', ('ny', 'nx'), 'grid effective grid spacing', 'degrees')

# close files
nc.close()
