import xarray as xr
import numpy as np

# Define dimensions
dims = {
    "string255": 255,
    "nyp": 473,
    "nxp": 681,
    "nx": 680,
    "ny": 472
}

# Create the dataset
ds = xr.Dataset(
    {
        "tile": (["string255"], np.empty(dims["string255"], dtype="S1")),
        "x": (["nyp", "nxp"], np.full((dims["nyp"], dims["nxp"]), np.nan)),
        "y": (["nyp", "nxp"], np.full((dims["nyp"], dims["nxp"]), np.nan)),
        "dx": (["nyp", "nx"], np.full((dims["nyp"], dims["nx"]), np.nan)),
        "dy": (["ny", "nxp"], np.full((dims["ny"], dims["nxp"]), np.nan)),
        "area": (["ny", "nx"], np.full((dims["ny"], dims["nx"]), np.nan)),
        "angle_dx": (["nyp", "nxp"], np.full((dims["nyp"], dims["nxp"]), np.nan)),
        "arcx": (["string255"], np.empty(dims["string255"], dtype="S1"))
    },
    coords={
        "string255": np.arange(dims["string255"]),
        "nyp": np.arange(dims["nyp"]),
        "nxp": np.arange(dims["nxp"]),
        "nx": np.arange(dims["nx"]),
        "ny": np.arange(dims["ny"])
    }
)

# Set attributes for variables
ds["tile"].attrs = {
    "standard_name": "grid_tile_spec",
    "geometry": "spherical",
    "north_pole": "0.0 90.0",
    "discretization": "logically_rectangular",
    "conformal": "true"
}
ds["x"].attrs = {
    "_FillValue": np.nan,
    "standard_name": "geographic_longitude",
    "units": "degree_east"
}
ds["y"].attrs = {
    "_FillValue": np.nan,
    "standard_name": "geographic_latitude",
    "units": "degree_north"
}
ds["dx"].attrs = {
    "_FillValue": np.nan,
    "standard_name": "grid_edge_x_distance",
    "units": "meters"
}
ds["dy"].attrs = {
    "_FillValue": np.nan,
    "standard_name": "grid_edge_y_distance",
    "units": "meters"
}
ds["area"].attrs = {
    "_FillValue": np.nan,
    "standard_name": "grid_cell_area",
    "units": "m**2"
}
ds["angle_dx"].attrs = {
    "_FillValue": np.nan,
    "standard_name": "grid_vertex_x_angle_WRT_geographic_east",
    "units": "degrees_east"
}
ds["arcx"].attrs = {
    "standard_name": "grid_edge_x_arc_type",
    "north_pole": "0.0 90.0"
}

# Save to a NetCDF file
ds.to_netcdf("crazy_hgrid.nc")