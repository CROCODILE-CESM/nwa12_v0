print("Starting, loading libraries...")
from regional_mom6 import regridding as rgd
import xarray as xr
import json
from pathlib import Path
import numpy as np

# Get all data required
print("Loading data...")
hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/nwa_in_crocesm/ocnice/ocean_hgrid.nc")
with open("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/list_of_tracers.json")as f:
    tracers = json.load(f)["tracers"]
boundary_number_conversion = {
    "south": 1,
    "north": 2,
    "east": 3,
    "west": 4
}
bathymetry = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_topo.nc")

for tracer in tracers:
    for segment in boundary_number_conversion.keys():
        if segment == "ic" or segment == "west":
            continue
        print(f"Starting {tracer} {segment} processing...")
        segment_name = "segment_{:03d}".format(boundary_number_conversion[segment])
        out_folder = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/processed_interpolated_filled_data")
        file_path = out_folder / f"{tracer}_obc_{segment_name}.nc"
        if file_path.exists():
            print(f"Already processed {tracer} {segment}, skipping!")
            continue
        # Open Dataset
        regridded_folder = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_interpolated_filled_data")
        ds = xr.open_dataset(regridded_folder/f"{tracer}_{segment}_regridded_with_fills.nc")
        if "z_t" in ds.dims:
            z_dim = "z_t"
        elif "z_t_150m" in ds.dims:
            z_dim = "z_t_150m"
        else:
            raise ValueError(f"Neither 'z_t' nor 'z_t_150m' found in dimensions for {tracer} {segment}!")


        # Convert the z_dim from cm to m
        ds[z_dim] =  ds[z_dim]/100

        
        dim_name = ds.variables["__xarray_dataarray_variable__"].dims[-1]
        coords = rgd.coords(hgrid, segment, segment_name)
        ds[tracer] = ds.__xarray_dataarray_variable__
        # First reshape err in regrid
        # if segment in ["east","west"]:
        #     ds.variables["__xarray_dataarray_variable__"].dims = ('time', z_dim, dim_name, "dummy")
        #     ds[tracer] = ds.__xarray_dataarray_variable__[:,:,:,0]
        # else:
        #     ds.variables["__xarray_dataarray_variable__"].dims = ('time', z_dim, 'dummy', dim_name)
        #     ds[tracer] = ds.__xarray_dataarray_variable__[:,:,0,:]

        # Drop old var
        ds = ds.drop_vars(["__xarray_dataarray_variable__"])

        # Rename things
        ds = ds.rename(
            {"lon": f"lon_{segment_name}", "lat": f"lat_{segment_name}"}
        )
        tracer_name = f"{tracer}_{segment_name}"
        ds = ds.rename({tracer: tracer_name})


        # Fill Missing Data
        ds[tracer] = rgd.fill_missing_data(
                    ds[tracer_name],
                    xdim=dim_name,
                    zdim=z_dim,
                )
        
        # Do vertical encoding
        ds = rgd.vertical_coordinate_encoding(
            ds, tracer_name, segment_name, z_dim
        )

        ds = rgd.add_secondary_dimension(
            ds, tracer_name, coords, segment_name
        )

        ds = rgd.generate_layer_thickness(
            ds, tracer_name, segment_name, z_dim
        )
                
        # Don't need to adjust time attribute, it's correct, or is found in the subset stage 

        # Overwrite actual lat/lon vals with grid numbers in these variables
        ds[f"{coords.attrs['parallel']}_{segment_name}"] = np.arange(
            ds[f"{coords.attrs['parallel']}_{segment_name}"].size
        )
        ds[f"{coords.attrs['parallel']}_{segment_name}"] = np.arange(
            ds[f"{coords.attrs['parallel']}_{segment_name}"].size
        )
        ds[f"{coords.attrs['perpendicular']}_{segment_name}"] = [0]

        # Mask dataset one more time for unaavoidable NaNs passed filling
       
        ds = ds.drop_vars([tracer])

        ds = rgd.mask_dataset(
            ds,
            bathymetry,
            segment,
            y_dim_name = "lath",
            x_dim_name = "lonh",
        )

        # Do Encoding
        encoding_dict = {
            "time": {"dtype": "double","_FillValue": 1.0e2},
            f"nx_{segment_name}": {
                "dtype": "int32",
            },
            f"ny_{segment_name}": {
                "dtype": "int32",
            },
        }
        
        encoding_dict = rgd.generate_encoding(
            ds,
            encoding_dict,
            default_fill_value=1.0e2,
        )

        # Save File Out
        
        ds.load().to_netcdf(
            out_folder / f"{tracer}_obc_{segment_name}.nc",
            encoding=encoding_dict,
            unlimited_dims="time",
        )
        print(f"....Finished {tracer} {segment} processing!")


