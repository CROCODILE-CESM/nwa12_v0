
import sys
sys.path.append('/glade/u/home/manishrv/documents/croc/dev/CrocoLens')
from CrocoLens.regional_domain import RegionalDomain
import calendar
import xarray as xr
from dask.diagnostics import ProgressBar


print("Reading Datasets")
glorys_monthly_means = xr.open_dataset("/glade/derecho/scratch/manishrv/glorys_data/nwa_2000_monthly_means/glorys_monthly_means_regridded_to_nwa.nc", chunks={"time": 12, "nyp": 10, "nxp": 10})
cesm_monthly_means = xr.open_dataset("/glade/u/home/manishrv/documents/croc/dev/gustavo_glorys/cesm_important_2d_fields.nc", chunks={"time": 12, "xh": 10, "yh": 100})
hgrid = xr.open_dataset("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_hgrid.nc")
diffs = xr.open_dataset("/glade/u/home/manishrv/documents/croc/dev/gustavo_glorys/cesm_glorys_diffs.nc", chunks={"time": 12, "xh": 10, "yh": 10})
#Plot Raw
print("Config")
rd = RegionalDomain("/glade/derecho/scratch/manishrv/croc_input/gustavo-glorys-1/ocnice/ocean_hgrid.nc")
# Set Vars
months = calendar.month_abbr[1:12]



t_points = rd.get_point_type_dataset("t")
extent = [
                hgrid.x.min() - 2,
                hgrid.x.max() + 2,
                hgrid.y.min() - 2,
                hgrid.y.max() + 2,
            ]

var_config = {
    "ssh":{
        "glorys_var": "zos",
        "cesm_var": "SSH",
        "output_var": "ssh",
        "vmin" : -1.2,
        "vmax" : 1.2,
        "diff_vmin" : -1,
        "diff_vmax" : 1 ,
    },
    "mlotst":{
        "glorys_var": "mlotst",
        "cesm_var": "mlotst",
        "output_var": "mlotst",
        "vmin" : 0,
        "vmax" : 300,
        "diff_vmin" : -100,
        "diff_vmax" : 100,
    }
}
monthly_stats = {}
# diffs = xr.Dataset()

for output_var in ["mlotst"]:
    print(output_var)
    # diffs[output_var] = xr.zeros_like(cesm_monthly_means[var_config[output_var]["cesm_var"]])
    # for i, month in enumerate(months):
    #     # Get the data slice for the month
    #     cesm_month = cesm_monthly_means[var_config[output_var]["cesm_var"]][i]
    #     glorys_month = glorys_monthly_means[var_config[output_var]["glorys_var"]][i,t_points.t_points_y.values, t_points.t_points_x.values]
    #     # Rename glorys_month dims to xh, yh
    #     renamed_glorys= (glorys_month.rename({"nyp":"yh","nxp":"xh"}))
    #     diffs[output_var][i] = renamed_glorys - cesm_month
    monthly_stats[output_var] = {}
    for i, month in enumerate(months):
        print(month)
        # Get the data slice for the month
        cesm_month = cesm_monthly_means[var_config[output_var]["cesm_var"]][i]
        glorys_month = glorys_monthly_means[var_config[output_var]["glorys_var"]][i,t_points.t_points_y.values, t_points.t_points_x.values]
        # Calculate stats
        # cesm_max = cesm_month.max().compute().values.item()
        # cesm_min = cesm_month.min().compute().values.item()
        with ProgressBar():
            cesm_avg = cesm_month.weighted(rd.dataset.area).mean().compute().values.item()
            print(cesm_avg)
        
        print("Glorys")
        # Calculate stats for GLORYS
        # glorys_max = glorys_month.max().compute().values.item()
        # glorys_min = glorys_month.min().compute().values.item()
        with ProgressBar():
            glorys_avg = glorys_month.weighted(rd.dataset.area).mean().compute().values.item()
            print(glorys_avg)
        
        print("Diffs")
        # Calculate stats for DIFF
        # diff_max = diffs[output_var][i].max().compute().values.item()
        # diff_min = diffs[output_var][i].min().compute().values.item()
        with ProgressBar(): 
            diff_avg = diffs[output_var][i].weighted(rd.dataset.area).mean().compute().values.item()
            print(diff_avg)
        
        # Store stats in the dictionary
        monthly_stats[output_var][i] = {
            "cesm": {"min": 0, "max": 0, "average": cesm_avg},
            "glorys": {"min": 0, "max": 0, "average": glorys_avg},
            "diff": {"min": 0, "max": 0, "average": diff_avg},
        }

import json
with open("monthly_stats_averages_mlotst.json", "w") as f:
    json.dump(monthly_stats, f, indent = 4)