import xarray as xr
import regional_mom6 as rm6
from pathlib import Path 
import sys
from CrocoDash.data_access.datasets import glorys as gl
from CrocoDash.data_access import driver as dv
import pandas as pd
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def main():
    print("Starting...")

    hgrid = xr.open_dataset(
        "/glade/u/home/manishrv/documents/croc/mom_input/gfdl_copy.4.n3b/hgrid.nc"
    )
    bounds = dv.get_rectangular_segment_info(hgrid)


    start_date = '2000-01-01'
    end_date = '2005-12-31'

    # Generate monthly start dates
    timeseries = pd.date_range(start=start_date, end=end_date, freq='5D').strftime('%Y-%m-%d')
    if pd.to_datetime(end_date).strftime('%Y-%m-%d') not in timeseries:
        timeseries = timeseries.append(pd.Index([pd.to_datetime(end_date).strftime('%Y-%m-%d')]))


    for ind in range(len(timeseries)-1):
        logger.info(f"Iteration at {timeseries[ind]}")

        
        start_date_iter = timeseries[ind]
        date_obj = datetime.strptime(start_date_iter, "%Y-%m-%d")  # Convert to datetime object
        new_date = date_obj + timedelta(days=4)  # Add to the 5th day
        end_date_iter = new_date.strftime("%Y-%m-%d")  # Convert back to string
        str_folder = start_date_iter+"_to_"+end_date_iter
        raw_data_sub_folder = "/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/fix/raw_input/"+str_folder
        rm6_data_sub_folder = "/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/fix/rm6_output/"+str_folder
        info_path = Path(rm6_data_sub_folder)/"fix2.txt"
        if (os.path.exists(info_path)) and os.path.exists(rm6_data_sub_folder) and os.path.exists(Path(rm6_data_sub_folder)/"forcing_obc_segment_003.nc"):
            logger.info(f"Skipping {str_folder}, Files already fixed and all files processed")
            continue
        os.makedirs(raw_data_sub_folder, exist_ok = True)
        os.makedirs(rm6_data_sub_folder, exist_ok = True)
        os.makedirs(Path(rm6_data_sub_folder)/"weights", exist_ok = True)

        for key in ["north","east", "south"]:
            gl.get_glorys_data_from_rda([start_date_iter,end_date_iter], bounds[key]["lat_min"], bounds[key]["lat_max"], bounds[key]["lon_min"], bounds[key]["lon_max"], output_dir = raw_data_sub_folder, output_file = key+"_unprocessed.nc")
            number_conv = {"north": 2, "south": 1, "east": 3}
            segment_number = number_conv[key]
            arakawa_grid = "A"

            path_to_bc = Path(raw_data_sub_folder)/(key+"_unprocessed.nc")

            varnames = {
                "time": "time",
                "yh": "latitude",   
                "xh": "longitude",
                "zl": "depth",
                "eta": "zos",
                "u": "uo",
                "v": "vo",
                "tracers": {"salt": "so", "temp": "thetao"},
            }
            seg = rm6.segment(
                hgrid=hgrid,
                infile=path_to_bc,  # location of raw boundary
                outfolder=Path(
                    rm6_data_sub_folder
                ),
                varnames=varnames,
                segment_name="segment_{:03d}".format(segment_number),
                orientation=key,  # orienataion
                startdate=start_date_iter,
                arakawa_grid=arakawa_grid,
                repeat_year_forcing=False,
            )
            logger.info("Regridding...")
            seg.regrid_velocity_tracers()
        with open(info_path, 'w') as file:
            pass
        
    print("...Finished")
    return



if __name__ == "__main__":
    main()
