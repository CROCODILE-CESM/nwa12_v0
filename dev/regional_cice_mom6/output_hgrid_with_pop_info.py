import xarray as xr
from CrocoDash.grid import Grid  # Can replace with mom6_bathy.grid
from CrocoDash.topo import Topo  # Can replace with mom6_bathy.topo
import numpy as np
import netCDF4
import xarray as xr
from regional_mom6 import rotation as rot
from regional_mom6 import regridding as rgd

in_supergrid_path = "/glade/u/home/manishrv/documents/croc/dev/regional_cice_mom6/new_grid.nc"
in_topo_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/ocean_topog_cice_test_1_eaf771.nc"
in_grid = Grid.from_supergrid(in_supergrid_path)
in_topo = Topo.from_topo_file(
    grid=in_grid,
    topo_file_path=in_topo_path,
    min_depth=5,
)
out_hgrid_path = (
    "/glade/u/home/manishrv/documents/croc/dev/regional_cice_mom6/cice_grid_14_test.nc"
)
in_topo.write_cice_grid(out_hgrid_path)

# output_hgrid = xr.Dataset()


# # Calculate Correct Angle
# hgrid = xr.open_dataset(in_supergrid_path)
# hgrid["angle"] = rot.initialize_grid_rotation_angles_using_expanded_hgrid(hgrid)
# qpoints = rgd.get_hgrid_arakawa_c_points(hgrid, "q")
# u_angle = np.deg2rad((hgrid["angle"][qpoints.q_points_y, qpoints.q_points_x])[1:, 1:])

# output_hgrid["tlon"] = ("nlat", "nlon"), np.deg2rad(in_grid.tlon.values)
# output_hgrid["tlat"] = ("nlat", "nlon"), np.deg2rad(in_grid.tlat.values)
# output_hgrid["ulon"] = ("nlat", "nlon"), np.deg2rad(in_grid.qlon.values[1:, 1:])
# output_hgrid["ulat"] = ("nlat", "nlon"), np.deg2rad(in_grid.qlat.values[1:, 1:])
# # output_hgrid["tarea"]= ("nlat","nlon"),in_grid.tarea.values
# output_hgrid["kmt"] = ("nlat", "nlon"), in_topo.tmask.values
# output_hgrid["angle"] = ("nlat", "nlon"), u_angle.values
# output_hgrid["anglet"] = ("nlat", "nlon"), in_grid.angle.values
# output_hgrid["htn"] = ("nlat", "nlon"), in_grid.dxCv.values * 100
# output_hgrid["hte"] = ("nlat", "nlon"), in_grid.dyCu.values * 100

# # Set attributes directly
# output_hgrid["tlon"].attrs = {
#     "long_name": "array of t-grid longitudes",
#     "units": "radians",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# output_hgrid["tlat"].attrs = {
#     "long_name": "array of t-grid latitudes",
#     "units": "radians",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# output_hgrid["ulon"].attrs = {
#     "long_name": "array of u-grid longitudes",
#     "units": "radians",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# output_hgrid["ulat"].attrs = {
#     "long_name": "array of u-grid latitudes",
#     "units": "radians",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# # output_hgrid["tarea"].attrs = {
# #     "long_name": "area of T cells",
# #     "units": "meter^2",
# #     "missing_value": netCDF4.default_fillvals["f8"],
# # }
# output_hgrid["kmt"].attrs = {
#     "long_name": "TMASK",
#     "coordinates": "tlon tlat",
#     "missing_value": -2147483647,
# }
# output_hgrid["angle"].attrs = {
#     "long_name": "angle between grid x-axis and east",
#     "units": "radians",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# output_hgrid["anglet"].attrs = {
#     "long_name": "angle between grid x-axis and east",
#     "units": "radians",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# output_hgrid["htn"].attrs = {
#     "long_name": "x-distance between  q-points, centered at v",
#     "units": "cm",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }
# output_hgrid["hte"].attrs = {
#     "long_name": "y-distance between  q-points, centered at u",
#     "units": "cm",
#     "missing_value": netCDF4.default_fillvals["f8"],
# }

# encoding = {
#     "tlon": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     "tlat": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     "ulon": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     "ulat": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     # "tarea": {"dtype": "float64","_FillValue": netCDF4.default_fillvals["f8"]},
#     "kmt": {
#         "dtype": "int32",
#         "_FillValue": -2147483647,
#     },
#     "angle": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     "anglet": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     "htn": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
#     "hte": {"dtype": "float64", "_FillValue": netCDF4.default_fillvals["f8"]},
# }

# output_hgrid.to_netcdf(out_hgrid_path, encoding=encoding)
