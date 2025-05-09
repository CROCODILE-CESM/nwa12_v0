import xarray as xr
import regridding_analysis as ra
import numpy as np
import matplotlib.pyplot as plt
from CrocoDash.topo import Topo
from CrocoDash.grid import Grid
from pathlib import Path

grid = Grid.from_supergrid("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_hgrid.nc")
topo = Topo.from_topo_file(grid,"/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_topo.nc", min_depth = 5)

keys = ["north","south","east"]
info = {}
for key in keys:
    info[key] = {
        "weights": xr.open_dataset(f"/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_interpolated_data/{key}_weights.nc"),
        "raw_ds":xr.open_dataset(f"/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/raw_interpolated_data/DIC_{key}_vfilled.nc"),
        "regridded_ds":xr.open_dataset(f"/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_interpolated_data/DIC_{key}_regridded.nc"),
       
    }
    info[key]["analysis_obj"] =  ra.RegriddingAnalysis(raw_ds = info[key]["raw_ds"],regridded_ds=info[key]["regridded_ds"],weights = info[key]["weights"],  regrid_var_name = "__xarray_dataarray_variable__")

output_folder = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_masked_interpolated_data")
for key in keys:
    source_mask = info[key]["analysis_obj"].generate_source_mask()
    dest_mask =  info[key]["analysis_obj"].generate_boundary_dest_mask(topo)
    dest_mask = xr.Dataset({
    "mask": (["index"], dest_mask)
    })
    source_mask.name = "mask"
    source_mask.to_netcdf(output_folder/f"source_mask_{key}.nc")
    dest_mask.to_netcdf(output_folder/f"dest_mask_{key}.nc")