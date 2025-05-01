import xarray as xr
import numpy as np
from pathlib import Path
import json
from CrocoDash.raw_data_access import driver as dv


def main():
    
    raw_interpolated_data_path = Path("/glade/u/home/manishrv/scratch/bgc/raw_interpolated_data")
    hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/nwa_in_crocesm/ocnice/ocean_hgrid.nc")
    with open("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/list_of_tracers.json")as f:
        tracers = json.load(f)["tracers"]
    rectangular_bounds = dv.get_rectangular_segment_info(hgrid)
    input_dir = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/raw_data")
    output_dir = raw_interpolated_data_path
    for tracer in tracers:
        for segment in rectangular_bounds.keys():
            input_file = str(input_dir / f"{tracer}_{segment}_unprocessed.nc")
            output_file = (output_dir / f"{tracer}_{segment}_vfilled.nc")
            if output_file.exists():
                print(f"Already processed {tracer} {segment}, skipping!")
                continue
            ds = xr.open_dataset(input_file)
            if "z_t" in ds.dims:
                z_dim = "z_t"
            elif "z_t_150m" in ds.dims:
                z_dim = "z_t_150m"
            else:
                raise ValueError(f"Neither 'z_t' nor 'z_t_150m' found in dimensions for {tracer} {segment}!")
            ds = ds.ffill(dim =z_dim,limit = None)
            ds.to_netcdf(str(output_file))
            print(f"Saved {tracer}_{segment} to {output_file}")
            ds.close()

if __name__ == "__main__":
    main()
    