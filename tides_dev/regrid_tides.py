print("Importing...")
import sys

sys.path.insert(
    0,
    "/glade/u/home/manishrv/documents/nwa12_0.1/regional_mom_workflows/crr/crocodileregionalruckus/rm6",
)
import regional_mom6 as rm6
from regional_mom6.utils import ap2ep, ep2ap
import xarray as xr
import os
import pandas as pd
from pathlib import Path
import numpy as np
import xesmf as xe
import regridding as rgd
import netCDF4

def main():
    print("Starting...")
    date_range = ["2000-01-01", "2000-01-02"]
    cts = [0, 1, 2, 3,4,5,6,7,8,9]
    path_to_td = Path(
        "/glade/u/home/manishrv/manish_scratch_symlink/inputs_rm6/tidal_data"
    )
    tidal_filename = Path("tpxo9.v1.nc")
    tpxo_h = (
        xr.open_dataset(Path(path_to_td / f"h_{tidal_filename}"))
        .rename({"lon_z": "lon", "lat_z": "lat", "nc": "constituent"})
        .isel(constituent=cts)
    )

    h = tpxo_h["ha"] * np.exp(-1j * np.radians(tpxo_h["hp"]))
    tpxo_h["hRe"] = np.real(h)
    tpxo_h["hIm"] = np.imag(h)
    tpxo_u = (
        xr.open_dataset(Path(path_to_td / f"u_{tidal_filename}"))
        .rename({"lon_u": "lon", "lat_u": "lat", "nc": "constituent"})
        .isel(constituent=cts)
    )
    tpxo_u["ua"] *= 0.01  # convert to m/s
    u = tpxo_u["ua"] * np.exp(-1j * np.radians(tpxo_u["up"]))
    tpxo_u["uRe"] = np.real(u)
    tpxo_u["uIm"] = np.imag(u)
    tpxo_v = (
        xr.open_dataset(Path(path_to_td / f"u_{tidal_filename}"))
        .rename({"lon_v": "lon", "lat_v": "lat", "nc": "constituent"})
        .isel(constituent=cts)
    )
    tpxo_v["va"] *= 0.01  # convert to m/s
    v = tpxo_v["va"] * np.exp(-1j * np.radians(tpxo_v["vp"]))
    tpxo_v["vRe"] = np.real(v)
    tpxo_v["vIm"] = np.imag(v)
    times = xr.DataArray(
        pd.date_range(
            date_range[0], periods=1
        ),  # Import pandas for this shouldn't be a big deal b/c it's already required in rm6 dependencies
        dims=["time"],
    )
    
    number_conv = {"north": 2, "south": 1, "east": 3}
    for orientation in ["north", "south", "east"]:

        segment_number = number_conv[orientation]
        arakawa_grid = "A"
        path_to_bc = os.path.join(
            "/",
            "glade",
            "derecho",
            "scratch",
            "manishrv",
            "inputs_rm6_nwa_small",
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

        seg.outfolder = Path(
           "/glade/u/home/manishrv/documents/nwa12_0.1/tides_dev/outputs"
        )
        seg.regrid_tides( tpxo_v, tpxo_u, tpxo_h, times)
    print("...Finished")
    return


if __name__ == "__main__":
    main()
