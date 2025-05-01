import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from regional_mom6 import regridding as rgd

def plot_regridding_snapshot( raw_ds, regridded_ds, weights, raw_lon_name = "TLONG", raw_lat_name = "TLAT", regrid_lon_name = "lon", regrid_lat_name = "lat", raw_var_name = "DIC", regrid_var_name = "DIC", extent = [-83,-78,53.8,55]):
    cols = weights.col.values

    source_points_used_lon = raw_ds[raw_lon_name].values.flatten()[cols-1]
    source_points_used_lat = raw_ds[raw_lat_name].values.flatten()[cols-1]

    # Clean NaN lons as a random point
    lons_raw = np.where(np.isfinite(raw_ds[raw_lon_name]), raw_ds[raw_lon_name], -180)
    lats_raw = np.where(np.isfinite(raw_ds[raw_lat_name]), raw_ds[raw_lat_name], 90)


    # Generate Plt
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, fc="lightgray")
    ax.coastlines(resolution="10m")
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = gl.right_labels = False
    # Plot Raw Vals
    ax.scatter(lons_raw, lats_raw, c=~np.isnan(raw_ds[raw_var_name][0,0]),cmap ="bwr",s = 2, label = "Source Points with or without Data (Red/Blue)", transform=ccrs.PlateCarree())
    # Plot regridded vals
    ax.scatter(regridded_ds[regrid_lon_name],regridded_ds[regrid_lat_name],c = ~np.isnan(regridded_ds[regrid_var_name][0,0]), s=13, marker='x',cmap = "bwr", label = "Destination Points with or without Data (Red/Blue)", transform=ccrs.PlateCarree())

    #Plot source points for bilinear regridding
    sc = ax.scatter(source_points_used_lon, source_points_used_lat, c=weights.S, cmap='inferno', s=10, transform=ccrs.PlateCarree(), label = "Source Points w/ Regridding Weights")

    ax.legend(loc="upper left", fontsize="small")
    return fig

def regridding_point_analysis(raw_ds, regridded_ds, weights, points, raw_lon_name = "TLONG", raw_lat_name = "TLAT", regrid_lon_name = "lon", regrid_lat_name = "lat", raw_var_name = "DIC", regrid_var_name = "DIC"):

    
    # Setup Figure   
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, fc="lightgray")
    ax.coastlines(resolution="10m")
    min_lon = 1000
    max_lon = -1000
    min_lat = 1000
    max_lat = -1000

    # Iterate through points
    for point_index in points:
        indexes = np.where(weights.row == point_index)
        source_indexes = weights.col[indexes]
        if len(source_indexes) == 0:
            #print(f"Point index {point_index} not found in weights.")
            continue

        # Find Source Point Indexes
        source_points_used_lon = raw_ds[raw_lon_name].values.flatten()[source_indexes-1]
        source_points_used_lat = raw_ds[raw_lat_name].values.flatten()[source_indexes-1]

        # Find min/max for extent
        if source_points_used_lon.min()< min_lon: 
            min_lon = source_points_used_lon.min()
        if source_points_used_lon.max() > max_lon:
            max_lon = source_points_used_lon.max()
        if source_points_used_lat.min() < min_lat:
            min_lat = source_points_used_lat.min()
        if source_points_used_lat.max() > max_lat:
            max_lat = source_points_used_lat.max()
        
        # Plot Source Points
        sc = ax.scatter(source_points_used_lon, source_points_used_lat, c=weights.S[indexes], s=10, transform=ccrs.PlateCarree(), label = "Source Points")

        # Get Source & Dest Vals
        source_point_vals = raw_ds[raw_var_name][0,0].values.flatten()[source_indexes]      
        dest_point_vals = regridded_ds[regrid_var_name][0,0].values[point_index]

        # Plot Stats
        print("Point Index:", point_index, "Latitude:", regridded_ds[regrid_lat_name][point_index].values, "Longitude:", regridded_ds[regrid_lon_name][point_index].values, "is: ", dest_point_vals, "from #Nans in Source Point Values:", len(np.where(np.isnan(source_point_vals))[0]))
        
        # Plot Destination Point
        dest = ax.scatter(regridded_ds[regrid_lon_name][point_index], regridded_ds[regrid_lat_name][point_index].values, c='red', s=10, transform=ccrs.PlateCarree(), marker = "x", label = "Destination Points")
    
    # Plot the entire source field
    source_points_used_lon = np.where(np.isfinite(raw_ds[raw_lon_name]), raw_ds[raw_lon_name], -180)
    source_points_used_lat = np.where(np.isfinite(raw_ds[raw_lat_name]), raw_ds[raw_lat_name], -90)
    ax.scatter(source_points_used_lon, source_points_used_lat, c=raw_ds.DIC[0,0], cmap='viridis', s= 1)

    # Set extent and legend
    ax.set_extent([min_lon-1,max_lon+1,min_lat-1,max_lat+1], crs=ccrs.PlateCarree())
    ax.legend(loc="upper left", fontsize="small")


def plot_region_mask(ocean_static, hgrid, extent = [-62,-60,56,57]):

    # Get points of arakawa c grid from hgrid
    t_points = rgd.get_hgrid_arakawa_c_points(hgrid, "t")
    v_points = rgd.get_hgrid_arakawa_c_points(hgrid, "v")
    u_points = rgd.get_hgrid_arakawa_c_points(hgrid, "u")
    q_points = rgd.get_hgrid_arakawa_c_points(hgrid, "q")

    # Put in Ocean Static
    ocean_static["tlon"] = (("yh","xh"),(t_points.tlon.values))
    ocean_static["tlat"] = (("yh","xh"),(t_points.tlat.values))
    ocean_static["ulon"] = (("yh","xq"),(u_points.ulon.values))
    ocean_static["ulat"] = (("yh","xq"),(u_points.ulat.values))
    ocean_static["qlon"] = (("yq","xq"),(q_points.qlon.values))
    ocean_static["qlat"] = (("yq","xq"),(q_points.qlat.values))
    ocean_static["vlon"] = (("yq","xh"),(v_points.vlon.values))
    ocean_static["vlat"] = (("yq","xh"),(v_points.vlat.values))

    # Create filter masks
    filter_mask_t = ocean_static["wet"] == 0
    filter_mask_c = ocean_static["wet_c"] == 0
    filter_mask_v = ocean_static["wet_v"] == 0
    filter_mask_u = ocean_static["wet_u"] == 0

    # Plot mask!
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, fc="lightgray")
    ax.coastlines(resolution="10m")
    ax.set_extent([-62,-60,56,57], crs=ccrs.PlateCarree())
    ax.scatter(hgrid.x, hgrid.y, c="gray", s=0.1, transform=ccrs.PlateCarree(), label="Hgrid Points")

    ax.scatter(ocean_static.tlon.values[filter_mask_t], ocean_static.tlat.values[filter_mask_t], c="blue", s=5, transform=ccrs.PlateCarree(), label="T Points")
    ax.scatter(ocean_static.qlon.values[filter_mask_c], ocean_static.qlat.values[filter_mask_c], c="green", s=5, transform=ccrs.PlateCarree(), label="Q Points")
    ax.scatter(ocean_static.vlon.values[filter_mask_v], ocean_static.vlat.values[filter_mask_v], c="red", s=5, transform=ccrs.PlateCarree(), label="V Points")
    ax.scatter(ocean_static.ulon.values[filter_mask_u], ocean_static.ulat.values[filter_mask_u], c="orange", s=5, transform=ccrs.PlateCarree(), label="U Points")

    ax.legend(loc="upper right", fontsize="small")
    ax.set_title("Land Points")
    return fig

def plot_boundary_mask(ocean_static, hgrid,regridded_ds, regrid_lon_name = "lon", regrid_lat_name = "lat", regrid_var_name = "DIC"):
    
        # Get points of arakawa c grid from hgrid
        t_points = rgd.get_hgrid_arakawa_c_points(hgrid, "t")
        v_points = rgd.get_hgrid_arakawa_c_points(hgrid, "v")
        u_points = rgd.get_hgrid_arakawa_c_points(hgrid, "u")
        q_points = rgd.get_hgrid_arakawa_c_points(hgrid, "q")

        # Put in Ocean Static
        ocean_static["tlon"] = (("yh","xh"),(t_points.tlon.values))
        ocean_static["tlat"] = (("yh","xh"),(t_points.tlat.values))
        ocean_static["ulon"] = (("yh","xq"),(u_points.ulon.values))
        ocean_static["ulat"] = (("yh","xq"),(u_points.ulat.values))
        ocean_static["qlon"] = (("yq","xq"),(q_points.qlon.values))
        ocean_static["qlat"] = (("yq","xq"),(q_points.qlat.values))
        ocean_static["vlon"] = (("yq","xh"),(v_points.vlon.values))
        ocean_static["vlat"] = (("yq","xh"),(v_points.vlat.values))
        ocean_static = ocean_static.isel(yq=[-1,-2],yh=[-1,-2])
        # Create filter masks
        filter_mask_t = ocean_static["wet"] == 0
        filter_mask_c = ocean_static["wet_c"] == 0
        filter_mask_v = ocean_static["wet_v"] == 0
        filter_mask_u = ocean_static["wet_u"] == 0

        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([-63,-60,56,57], crs=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND, fc="lightgray")
        ax.coastlines(resolution="10m")
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = gl.right_labels = False

        # Plot regridded vals
        ax.scatter(regridded_ds[regrid_lon_name], regridded_ds[regrid_lat_name].values,c = ~np.isnan(regridded_ds[regrid_var_name][0,0]), s=13, marker='x',cmap = "bwr", label = "Destination Points with or without Data (Red/Blue)", transform=ccrs.PlateCarree())

        #Plot source points for bilinear regridding
        ax.scatter(ocean_static.qlon.values[~filter_mask_c], ocean_static.qlat.values[~filter_mask_c], c="green", s=5, transform=ccrs.PlateCarree(), label="Wet Q Points")
        ax.scatter(ocean_static.vlon.values[~filter_mask_v], ocean_static.vlat.values[~filter_mask_v], c="orange", s=5, transform=ccrs.PlateCarree(), label="Wet V Points")

        # Plot the scatter regridded
        ax.legend(loc="upper left", fontsize="small")
        return fig