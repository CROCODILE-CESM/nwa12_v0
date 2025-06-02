print("Starting, loading libraries...")
from regional_mom6 import regridding as rgd
import xarray as xr
import json
from CrocoDash.raw_data_access import driver as dv
from pathlib import Path
import dask


# Get all data required
print("Loading data...")
hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/nwa_in_crocesm/ocnice/ocean_hgrid.nc")
rectangular_bounds = dv.get_rectangular_segment_info(hgrid)
with open("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/list_of_tracers.json")as f:
    tracers = json.load(f)["tracers"]
boundary_number_conversion = {
    "south": 1,
    "north": 2,
    "east": 3,
}

# print("Reading Masks...")
# mask_folder = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_masked_interpolated_data/")
# masks = {}
# for key in boundary_number_conversion:
#     masks[key] = {
#         "source":xr.open_dataset(mask_folder/f"source_mask_{key}.nc")["mask"].values,
#         "dest":xr.open_dataset(mask_folder/f"dest_mask_{key}.nc")["mask"].values
#     }

print("Creating regridders...")
# Create regridders for each segment
tracer = "PO4"
regridders = {}
for segment in rectangular_bounds:
    print("Creating",segment, "regridder")
    if segment == "ic" or segment == "west":
        continue
    ds = xr.open_dataset(f"/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/raw_interpolated_filled_data/{tracer}_{segment}_vfilled.nc")
    coords = rgd.coords(hgrid, segment, "segment_{:03d}".format(boundary_number_conversion[segment]))
    ds["lon"] = ds["TLONG"]
    ds["lat"] = ds["TLAT"]
    regridders[segment] = rgd.create_regridder(
        ds[["lon", "lat", tracer]],
        coords,
        locstream_out = True,
        outfile = f"/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_interpolated_filled_data/{segment}_weights.nc"
    )

#Do IC regridder
# ds = xr.open_dataset("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/raw_data/PO4_ic_unprocessed.nc")
# ds["lon"] = ds["TLONG"]
# ds["lat"] = ds["TLAT"]
# hgrid["lon"] = hgrid["x"]
# hgrid["lat"] = hgrid["y"]
# regridders["ic"] = rgd.create_regridder(
#     ds[["lon", "lat", tracer]],
#     hgrid,
#     locstream_out = False,
#     outfile = f"/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_data/ic_weights.nc"
# )
input_dir = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/raw_interpolated_filled_data")
output_dir = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/regridded_interpolated_filled_data")

def regrid_and_save(tracer, segment, regridders, input_file, output_file):
    """Regrids and saves the dataset for a specific tracer-segment pair."""
    try:
        print(f"Regridding {tracer} {segment}")

        with xr.open_dataset(input_file, chunks="auto") as ds:
            ds = ds.rename({"TLONG": "lon", "TLAT": "lat"})
            
            # Perform regridding
            regridded = regridders[segment](ds[tracer])
            
            # Save regridded dataset
            regridded.to_netcdf(output_file)
            regridded.close()

        print(f"{tracer} {segment} regridded")

    except Exception as e:
        print(f"Failed to regrid {tracer} {segment}: {e}")

# ------------------------------
# BUILD TASKS AND EXECUTE
# ------------------------------

for tracer in tracers:
    for segment in rectangular_bounds:
        if  segment == "west" or segment == "ic":
            continue
        input_file = str(input_dir / f"{tracer}_{segment}_vfilled.nc")
        output_file = str(output_dir / f"{tracer}_{segment}_regridded_with_fills.nc")
        if Path(output_file).exists():
            print(f"File {output_file} already exists. Skipping.")
            continue
        print(f"Regridding {tracer} {segment}")
        regrid_and_save(tracer, segment, regridders, input_file, output_file)



