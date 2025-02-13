print("Starting")
import xarray as xr
from pathlib import Path
east = {
        "name":"east",
        "lat_min":4.961175132990646,
        "lat_max":58.61512088772785,
        "lon_min":-37.68856021347937,
        "lon_max":-36.093333333333256,

}
south = {
    "name":"south",
        "lat_min":4.961175132990646,
        "lat_max":5.441175132990646,
        "lon_min":-98.24,
        "lon_max":-36.093333333333256,
    }
north = {   
    "name":"north",
        "lat_min":52.537190110517756,
        "lat_max":58.61512088772785,
        "lon_min":-98.98996846773888,
        "lon_max":-37.208560213479366,
     }
glorys_ds = xr.open_mfdataset("/lustre/desc1/mirrors/cgd/glorys/cmems_mod_glo_phy_my_0.083deg_P1D-m/mercatorglorys12v1_gl12_mean_2*", parallel=True)

output_dir = Path("/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year")
for dict in [east, south, north]:
    # Subset the dataset based on lat/lon bounds
    ds_subset = glorys_ds.sel(longitude=slice(dict["lon_min"], dict["lon_max"]), latitude=slice(dict["lat_min"], dict["lat_max"]))
    # Write the subsetted dataset to a new NetCDF file
    ds_subset.to_netcdf(output_dir/(dict["name"]+"_processed_total.nc"))

print("Ending")