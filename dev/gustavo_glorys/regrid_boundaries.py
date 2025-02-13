import xarray as xr
import regional_mom6 as rm6
from pathlib import Path 
import sys

def main(orientation):
    print("Starting...")
    number_conv = {"north": 2, "south": 1, "east": 3}


    segment_number = number_conv[orientation]
    arakawa_grid = "A"
    date_range = ["2000-01-01", "2020-12-31"]
    path_to_bc = Path("/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year")/(orientation+"_unprocessed_total.nc")
    hgrid = xr.open_dataset(
        "/glade/u/home/manishrv/documents/croc/mom_input/gfdl_copy.4.n3b/hgrid.nc"
    )
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
            "/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year"
        ),
        varnames=varnames,
        segment_name="segment_{:03d}".format(segment_number),
        orientation=orientation,  # orienataion
        startdate=date_range[0],
        arakawa_grid=arakawa_grid,
        repeat_year_forcing=False,
    )
    print("Regridding...")
    seg.regrid_velocity_tracers()
    print("...Finished")
    return



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python regrid_boundaries.py <orientation>")
        sys.exit(1)
    orientation = sys.argv[1]
    main(orientation)
