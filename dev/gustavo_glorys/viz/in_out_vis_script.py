import xarray as xr
boxes_cesm = {
    "in": {
        "lon_min": -70,
        "lon_max": -35,
        "lat_min": 0,
        "lat_max": 15,
    },
    "out": {
        "lon_min": -63,
        "lon_max": -30,
        "lat_min": 40,
        "lat_max": 64,
    },
}
boxes_glorys = {
    "in": {
        "lon_min": -70,
        "lon_max": -35,
        "lat_min": 0,
        "lat_max": 15,
    },
    "out": {
        "lon_min": -63,
        "lon_max": -30,
        "lat_min": 40,
        "lat_max": 64,
    },
}

cesm_surface_data = xr.open_mfdataset("/glade/u/home/manishrv/scratch/archive/gustavo-glorys-2/ocn/hist/*sfc*")
glorys_daily_data = xr.open_mfdataset("/glade/campaign/collections/rda/data/d010049/2000/mercatorglorys12v1_gl12_mean_20000*.nc")
box = "out"
lon_min = boxes_cesm[box]["lon_min"]
lon_max = boxes_cesm[box]["lon_max"]
lat_min = boxes_cesm[box]["lat_min"]
lat_max = boxes_cesm[box]["lat_max"]

# Subset the suface data

cesm_surface_data_box = (cesm_surface_data.sel(xh=slice(lon_min, lon_max), yh=slice(lat_min, lat_max)))[["SSH"]]
lon_min = boxes_glorys[box]["lon_min"]
lon_max = boxes_glorys[box]["lon_max"]
lat_min = boxes_glorys[box]["lat_min"]
lat_max = boxes_glorys[box]["lat_max"]
glorys_daily_data_box = (glorys_daily_data.sel(longitude=slice(lon_min, lon_max), latitude=slice(lat_min, lat_max)))[["zos"]]
# glorys_daily_data_box["so"] = glorys_daily_data_box["so"][:,0]

cesm_surface_data_box.to_netcdf(f"/glade/u/home/manishrv/scratch/temp/cesm_surface_data_ssh_large_{box}.nc")
glorys_daily_data_box.to_netcdf(f"/glade/u/home/manishrv/scratch/temp/glorys_daily_data_ssh_large_{box}.nc")
