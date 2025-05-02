import xarray as xr
from CrocoDash.grid import Grid # Can replace with mom6_bathy.grid
from CrocoDash.topo import Topo # Can replace with mom6_bathy.topo
import numpy as np
import netCDF4
in_supergrid_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/ocean_hgrid_cice_test_1_eaf771.nc"
in_topo_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/ocean_topog_cice_test_1_eaf771.nc"
in_grid = Grid.from_supergrid(in_supergrid_path)
in_topo = Topo.from_topo_file(
    grid = in_grid,
    topo_file_path=in_topo_path,
    min_depth = 5,
)
out_hgrid_path = "/glade/u/home/manishrv/documents/croc/dev/regional_cice_mom6/cice_grid_2.nc"
output_hgrid = xr.Dataset()


output_hgrid["tlong"]= ("nlat","nlon"),in_grid.tlon.values
output_hgrid["tlat"]= ("nlat","nlon"),in_grid.tlat.values
output_hgrid["ulong"]= ("nlat","nlon"),in_grid.qlon.values[1:,1:]
output_hgrid["ulat"]= ("nlat","nlon"),in_grid.qlat.values[1:,1:]
output_hgrid["tarea"]= ("nlat","nlon"),in_grid.tarea.values
output_hgrid["kmt"]= ("nlat","nlon"),in_topo.tmask.values

# Set attributes directly
output_hgrid["tlong"].attrs = {
    "long_name": "array of t-grid longitudes",
    "units": "degrees_east",
    "missing_value": netCDF4.default_fillvals["f8"],
}
output_hgrid["tlat"].attrs = {
    "long_name": "array of t-grid latitudes",
    "units": "degrees_north",
    "missing_value": netCDF4.default_fillvals["f8"],
}
output_hgrid["ulong"].attrs = {
    "long_name": "array of u-grid longitudes",
    "units": "degrees_east",
    "missing_value": netCDF4.default_fillvals["f8"],
}
output_hgrid["ulat"].attrs = {
    "long_name": "array of u-grid latitudes",
    "units": "degrees_north",
    "missing_value": netCDF4.default_fillvals["f8"],
}
output_hgrid["tarea"].attrs = {
    "long_name": "area of T cells",
    "units": "meter^2",
    "missing_value": netCDF4.default_fillvals["f8"],
}
output_hgrid["kmt"].attrs = {
    "long_name": "TMASK",
    "coordinates": "tlong tlat",
    "missing_value": -2147483647,
}

encoding = {
    "tlong": {"dtype": "float64","_FillValue": netCDF4.default_fillvals["f8"]},
    "tlat": {"dtype": "float64","_FillValue": netCDF4.default_fillvals["f8"]},
    "ulong": {"dtype": "float64","_FillValue": netCDF4.default_fillvals["f8"]},
    "ulat": {"dtype": "float64","_FillValue": netCDF4.default_fillvals["f8"]},
    "tarea": {"dtype": "float64","_FillValue": netCDF4.default_fillvals["f8"]},
    "kmt": { "dtype": "int32" , "_FillValue": -2147483647,},
}

output_hgrid.to_netcdf(out_hgrid_path, encoding=encoding)
