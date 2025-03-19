import xarray as xr
import regional_mom6 as rm6
from pathlib import Path
from datetime import datetime
import sys
from CrocoDash.data_access import glorys as gl
from CrocoDash.data_access import driver as dv
import pandas as pd
import logging
import os
from glob import glob
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def regrid_glorys_pieces(
    boundaries=["north", "south", "east", "west"],
    hgrid_path=Path(""),
    raw_input_dir=Path(""),
    output_dir=Path(""),
):
    """
    Intended to be given directory where all of the pieces of the boundary files exist, of the form "{boundary}_glorys.{start_date}_{start_date+4}.nc}

    Example: west_glorys.20000116_20000120.nc
    """

    logger.info("Starting Boundary Regridding Process")

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

    number_conv = {"south": 1, "north": 2, "east": 3, "west": 4}

    arakawa_grid = "A"

    hgrid = xr.open_dataset(hgrid_path)
    bounds = dv.get_rectangular_segment_info(hgrid)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/weights", exist_ok=True)

    for key in boundaries:
        segment_number = number_conv[key]

        file_list = list(glob(os.path.join(raw_input_dir, f"{key}*.nc")))

        for file_name in file_list:

            date = file_name.split(".")[-2]
            start_date = datetime.strptime(date.split("_")[0], "%Y%m%d").strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            seg = rm6.segment(
                hgrid=hgrid,
                infile=file_name,
                outfolder=Path(output_dir),
                varnames=varnames,
                segment_name=f"segment_00{segment_number}",
                orientation=key,
                startdate=start_date,
                arakawa_grid=arakawa_grid,
                repeat_year_forcing=False,
                optional_name=f"_{date}",
            )
            logger.info(f"Regridding {file_name}")
            seg.regrid_velocity_tracers()


hgrid_path = "/glade/work/ajanney/CrocoDash_Input/CrocCaribDefault/ocnice/ocean_hgrid_CrocCaribDefault_9419eb.nc"
raw_input_dir = "/glade/work/ajanney/CaribCrocoDash/get_carib_glorys/raw_glorys_data"
output_dir = (
    "/glade/work/ajanney/CaribCrocoDash/get_carib_glorys/coarse_regridded_glorys_data"
)

regrid_glorys_pieces(
    boundaries=["north", "south", "east", "west"],
    hgrid_path=hgrid_path,
    raw_input_dir=raw_input_dir,
    output_dir=output_dir,
)
