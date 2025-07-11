import xarray as xr
import numpy as np
from pathlib import Path
import json
from CrocoDash.raw_data_access import driver as dv

south_source_points_to_fill = [4245, 4246, 4687,4244,4686] # have to unravel these bad boys
south_source_points_to_fill_with = [4247, 4247, 4688,4245,4687]
north_source_points_to_fill = [49649, 50138]
north_source_points_to_fill_with = [49650, 50139]
def main():
    input_dir = Path("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/raw_data")
    output_dir = Path("/glade/u/home/manishrv/scratch/bgc/raw_interpolated_filled_data")
    hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/nwa_in_crocesm/ocnice/ocean_hgrid.nc")
    with open("/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/list_of_physicals.json")as f:
        tracers = json.load(f)["tracers"]
    rectangular_bounds = dv.get_rectangular_segment_info(hgrid)
    
    for tracer in tracers:
        for segment in rectangular_bounds.keys():
            if segment == "west":
                continue
            input_file = str(input_dir / f"{tracer}_{segment}_unprocessed.nc")
            output_file = (output_dir / f"{tracer}_{segment}_vfilled.nc")
            if output_file.exists():
                print(f"Already processed {tracer} {segment}, skipping!")
                continue
            ds = xr.open_dataset(input_file)

            

            # Fill NaN points of interest
            if segment == "south":
                if tracer != "SSH":
                    for index,pt in enumerate(south_source_points_to_fill):
                        unraveled_nan = np.unravel_index(pt, ds[tracer][0,0].shape)
                        unraveled_fill = np.unravel_index(south_source_points_to_fill_with[index], ds[tracer][0,0].shape)
                        print("Previous",ds[tracer][0,0,unraveled_nan[0],unraveled_nan[1]].item())
                        ds[tracer][:,0,unraveled_nan[0],unraveled_nan[1]] = ds[tracer][:,0,unraveled_fill[0],unraveled_fill[1]]
                        print("After",ds[tracer][0,0,unraveled_nan[0],unraveled_nan[1]].item())
                else:
                    for index,pt in enumerate(south_source_points_to_fill):
                        unraveled_nan = np.unravel_index(pt, ds[tracer][0].shape)
                        unraveled_fill = np.unravel_index(south_source_points_to_fill_with[index], ds[tracer][0].shape)
                        print("Previous",ds[tracer][0,unraveled_nan[0],unraveled_nan[1]].item())
                        ds[tracer][:,unraveled_nan[0],unraveled_nan[1]] = ds[tracer][:,unraveled_fill[0],unraveled_fill[1]]
                        print("After",ds[tracer][0,unraveled_nan[0],unraveled_nan[1]].item())

            if segment == "north":
                if tracer != "SSH":
                    for index,pt in enumerate(north_source_points_to_fill):
                        unraveled_nan = np.unravel_index(pt, ds[tracer][0,0].shape)
                        unraveled_fill = np.unravel_index(north_source_points_to_fill_with[index], ds[tracer][0,0].shape)
                        print("Previous",ds[tracer][0,0,unraveled_nan[0],unraveled_nan[1]].item())
                        ds[tracer][:,0,unraveled_nan[0],unraveled_nan[1]] = ds[tracer][:,0,unraveled_fill[0],unraveled_fill[1]]
                        print("After",ds[tracer][0,0,unraveled_nan[0],unraveled_nan[1]].item())
                else:
                    for index,pt in enumerate(north_source_points_to_fill):
                        unraveled_nan = np.unravel_index(pt, ds[tracer][0].shape)
                        unraveled_fill = np.unravel_index(north_source_points_to_fill_with[index], ds[tracer][0].shape)
                        print("Previous",ds[tracer][0,unraveled_nan[0],unraveled_nan[1]].item())
                        ds[tracer][:,unraveled_nan[0],unraveled_nan[1]] = ds[tracer][:,unraveled_fill[0],unraveled_fill[1]]
                        print("After",ds[tracer][0,unraveled_nan[0],unraveled_nan[1]].item())


            if tracer != "SSH":
                if "z_t" in ds[tracer].dims:
                    z_dim = "z_t"
                elif "z_t_150m" in ds[tracer].dims:
                    z_dim = "z_t_150m"
                else:
                    raise ValueError(f"Neither 'z_t' nor 'z_t_150m' found in dimensions for {tracer} {segment}!")
                # Vertical Fill
                ds = ds.ffill(dim =z_dim,limit = None)
            ds.to_netcdf(str(output_file))
            print(f"Saved {tracer}_{segment} to {output_file}")
            ds.close()

if __name__ == "__main__":
    main()
    