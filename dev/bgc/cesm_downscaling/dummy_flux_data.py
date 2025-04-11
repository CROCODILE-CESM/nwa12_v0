import xarray as xr
import numpy as np

# Set grid dimensions
depth = 103
depth_edges = depth + 1
ny = 780
nx = 740

# Create coordinate variables
ds = xr.Dataset(
    {
        "DEPTH": (["DEPTH"], np.linspace(0, 6000, depth)),
        "DEPTH_EDGES": (["DEPTH_EDGES"], np.linspace(0, 6000, depth_edges)),
        "FESEDFLUXIN": (["DEPTH", "ny", "nx"], np.zeros((depth, ny, nx), dtype=np.float32)),
        "FESEDFLUXIN_oxic": (["DEPTH", "ny", "nx"], np.zeros((depth, ny, nx), dtype=np.float32)),
        "FESEDFLUXIN_reduce": (["DEPTH", "ny", "nx"], np.zeros((depth, ny, nx), dtype=np.float32)),
        "KMT": (["ny", "nx"], np.zeros((ny, nx), dtype=np.int32)),
        "TAREA": (["ny", "nx"], np.zeros((ny, nx), dtype=np.float64)),
    }
)

# Assign attributes
ds["DEPTH"].attrs = {"units": "m", "edges": "DEPTH_EDGES"}
ds["DEPTH_EDGES"].attrs = {"units": "m"}
ds["FESEDFLUXIN"].attrs = {
    "_FillValue": 1.e+20,
    "units": "micromol/m^2/d",
    "long_name": "Fe sediment flux (total)"
}
ds["FESEDFLUXIN_oxic"].attrs = {
    "_FillValue": 1.e+20,
    "units": "micromol m$^{-2}$ d$^{-1}$",
    "long_name": "Fe sediment flux (oxic)"
}
ds["FESEDFLUXIN_reduce"].attrs = {
    "long_name": "Longitude of tracer (T) points",
    "units": "micromol m$^{-2}$ d$^{-1}$",
    "cell_methods": "time: point"
}
ds["TAREA"].attrs = {"units": "m^2"}

# Add global attributes
ds.attrs = {
    "history": "Created with xarray",
    "NCO": "netCDF Operators version 4.9.5"
}

# Save to NetCDF
output_file = "/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/fesedflux_total_reduce_oxic_tx0.66v1.c230817.nc"
ds.to_netcdf(output_file)
print(f"File saved: {output_file}")