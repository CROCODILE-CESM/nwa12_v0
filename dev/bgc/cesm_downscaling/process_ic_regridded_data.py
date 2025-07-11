print("Starting, loading libraries...")
from regional_mom6 import regridding as rgd
import xarray as xr
import json
from pathlib import Path
import numpy as np

# Get all data required
print("Loading data...")
hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/nwa_in_crocesm/ocnice/ocean_hgrid.nc")
with open("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/list_of_physicals.json")as f:
    tracers = json.load(f)["tracers"]
vgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/marbl.bio.croc.4/ocnice/ocean_vgrid_nwa4_ca99a7.nc")
bathymetry = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_topo.nc")

for tracer in tracers:

        print(f"Starting {tracer} IC processing...")
        out_folder = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/processed_interpolated_filled_data")
        file_path = out_folder / f"{tracer}_ic.nc"
        if file_path.exists():
            print(f"Already processed {tracer}, skipping!")
            continue
        # Open Dataset
        regridded_folder = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_interpolated_filled_data")
        ds = xr.open_dataset(regridded_folder/f"{tracer}_ic_regridded_with_fills.nc")
        if tracer != "SSH":
            if "z_t" in ds.dims:
                z_dim = "z_t"
            elif "z_t_150m" in ds.dims:
                z_dim = "z_t_150m"
            else:
                raise ValueError(f"Neither 'z_t' nor 'z_t_150m' found in dimensions for {tracer}!")


            # Convert the z_dim from cm to m
            ds[z_dim] =  ds[z_dim]/100

        # Slice the velocites to the u and v grid.
        u_points = rgd.get_hgrid_arakawa_c_points(hgrid, "u")
        v_points = rgd.get_hgrid_arakawa_c_points(hgrid, "v")
        t_points = rgd.get_hgrid_arakawa_c_points(hgrid, "t")  
        dim_name = ds.variables["__xarray_dataarray_variable__"].dims[-1]
        ds[tracer] = ds.__xarray_dataarray_variable__

        # Drop old var
        ds = ds.drop_vars(["__xarray_dataarray_variable__"])

        
        tracer_name = f"{tracer}"
        ds = ds.rename({tracer: tracer_name})


        # Fill Missing Data
        if tracer == "SSH":
            z_dim = None
        ds[tracer] = rgd.fill_missing_data(
                    ds[tracer_name],
                    xdim=dim_name,
                    zdim=z_dim,
                )

        # Do Encoding
        encoding_dict = {
            "time": {"dtype": "double","_FillValue": 1.0e2},
        }
        
        encoding_dict = rgd.generate_encoding(
            ds,
            encoding_dict,
            default_fill_value=1.0e2,
        )

        # Save File Out
        
        ds.load().to_netcdf(
            out_folder / f"{tracer}_ic.nc",
            encoding=encoding_dict,
            unlimited_dims="time",
        )
        print(f"....Finished {tracer} processing!")


