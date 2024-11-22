print("Importing...")
import sys

sys.path.insert(
    0,
    "/glade/u/home/manishrv/documents/nwa12_0.1/regional_mom_workflows/CrocoDash/CrocoDash/rm6",
)
import regional_mom6 as rm6
import xarray as xr
import os
from pathlib import Path
# /glade/u/home/manishrv/documents/nwa12_0.1/tides_dev


def main():
    print("Starting...")
    number_conv = {"north": 2, "south": 1, "east": 3}
    for orientation in ["north", "south", "east"]:

        segment_number = number_conv[orientation]
        arakawa_grid = "A"
        date_range = ["2005-01-01", "2000-01-02"]
        path_to_bc = os.path.join(
            "/",
            "glade",
            "derecho",
            "scratch",
            "manishrv",
            "inputs_rm6_nwa",
            "glorys",
            f"{orientation}_unprocessed.nc",
        )
        hgrid = xr.open_dataset(
            "/glade/u/home/manishrv/documents/nwa12_0.1/mom_input/2n3b.nwa-three-boundary-new-regridding/hgrid.nc"
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
                "/glade/u/home/manishrv/documents/nwa12_0.1/tides_dev/outputs"
            ),
            varnames=varnames,
            segment_name="segment_{:03d}".format(segment_number),
            orientation=orientation,  # orienataion
            startdate=date_range[0],
            arakawa_grid=arakawa_grid,
            repeat_year_forcing=False,
        )

        seg.regrid_velocity_tracers()
    print("...Finished")
    return



if __name__ == "__main__":
    main()
