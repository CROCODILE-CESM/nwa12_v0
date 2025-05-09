import xarray as xr
import numpy as np
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from CrocoDash.topo import Topo


class RegriddingAnalysis:
    """
    Class to analyze the regridding process.
    """

    def __init__(
        self,
        raw_ds,
        regridded_ds,
        weights,
        *,
        raw_lon_name="TLONG",
        raw_lat_name="TLAT",
        regrid_lon_name="lon",
        regrid_lat_name="lat",
        raw_var_name="DIC",
        regrid_var_name="DIC",
    ):
        """
        Initialize the RegriddingAnalysis class.

        Parameters
        ----------
        raw_ds : xarray.Dataset
            The original dataset. (Must be of the form time, depth, lat, lon)
        regridded_ds : xarray.Dataset
            The regridded dataset. (Must be of the form time, depth, lat, lon)
        weights : xarray.DataArray
            The weights used for regridding.
        raw_lon_name : str, optional
            The name of the longitude variable in the original dataset (default is "TLONG").
        raw_lat_name : str, optional
            The name of the latitude variable in the original dataset (default is "TLAT").
        regrid_lon_name : str, optional
            The name of the longitude variable in the regridded dataset (default is "lon").
        regrid_lat_name : str, optional
            The name of the latitude variable in the regridded dataset (default is "lat").
        raw_var_name : str, optional
            The name of the variable in the original dataset (default is "DIC").
        regrid_var_name : str, optional
            The name of the variable in the regridded dataset (default is "DIC").
        """
        self.raw_ds = raw_ds
        self.regridded_ds = regridded_ds
        self.weights = weights
        self.raw_lon_name = raw_lon_name
        self.raw_lat_name = raw_lat_name
        self.regrid_lon_name = regrid_lon_name
        self.regrid_lat_name = regrid_lat_name
        self.raw_var_name = raw_var_name
        self.regrid_var_name = regrid_var_name

    def generate_figure_background(self, extent=[-180, 180, -90, 90]):
        """
        Generate a default figure for the regridding analysis.
        """
        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent(extent, crs=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND, fc="lightgray")
        ax.coastlines(resolution="10m")
        gl = ax.gridlines(
            draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--"
        )
        gl.top_labels = gl.right_labels = False
        return fig,ax

    @property
    def source_indexes(self):
        """
        Get the indexes of the source points in the original dataset.
        """
        return self.weights.col.values - 1

    @property
    def dest_indexes(self):
        """
        Get the indexes of the destination points in the regridded dataset.
        """
        return self.weights.row.values - 1

    @property
    def unincluded_dest_points(self):
        return [
            i
            for i in range(len(self.regridded_ds[self.regrid_lon_name]))
            if i not in self.dest_indexes
        ]  # These become zeroes

    def source_index_to_lat_lon(self, source_point):
        raw_data_source_points_lat = self.raw_ds[self.raw_lat_name].values.ravel()[
            source_point
        ]
        raw_data_source_points_lon = self.raw_ds[self.raw_lon_name].values.ravel()[
            source_point
        ]
        return raw_data_source_points_lat, raw_data_source_points_lon

    def dest_index_to_lat_lon(self, dest_point):
        raw_data_dest_points_lat = self.regrid_ds[
            self.regrid_lat_name
        ].values.ravel()[dest_point]
        raw_data_dest_points_lon = self.regrid_ds[
            self.regrid_lon_name
        ].values.ravel()[dest_point]
        return raw_data_dest_points_lat, raw_data_dest_points_lon
    
    def source_index_to_val(self, source_points,level=0):
        unraveled = np.unravel_index(source_points, self.raw_ds[self.raw_var_name][0][level].shape)
        vals = []
        for i in range(unraveled[0].shape[0]):
            val = self.raw_ds[self.raw_var_name][0,level,unraveled[0][i],unraveled[1][i]].item()
            vals.append(val)
        return vals
    def dest_index_to_val(self, dest_point):
        return self.regrid_ds[self.regrid_var_name].values.ravel()[dest_point]
    def source_to_dest(self, source_point):
        return self.weights.row[np.where(self.weights.col == (source_point + 1))] - 1

    def dest_to_source(self, dest_point):
        return self.weights.col[np.where(self.weights.row == (dest_point + 1))] - 1

    def find_source_nans(self, level=0, include_zeros=False):
        vals = self.raw_ds[self.raw_var_name][0, level]


        if include_zeros:
            res = vals.is_null() | (vals == 0)
        else:
            res = vals.is_null()

        return res

    def find_dest_nans(self, level=0, include_zeros=False):

        vals = self.regridded_ds[self.regrid_var_name][0, level]

        if include_zeros:
            res = vals.is_null() | (vals == 0)
        else:
            res = vals.isnull()

        return res

    def find_dest_nan_indexes_over_ocean(self, topo, level=0, include_zeros=False):
        """
        Find Destination NaNs over ocean
        """

        # Filter dest_nans to ones on our destination
        dest_nans = self.find_dest_nans(level=level, include_zeros=include_zeros)
        where_nan = np.where(dest_nans)[0]
        is_ocean = topo.point_is_ocean(
                lons=self.regridded_ds[self.regrid_lon_name][where_nan].values,
                lats=self.regridded_ds[self.regrid_lat_name][where_nan].values,
            )
        return where_nan[np.where(is_ocean)[0]]



    def check_source_points_on_dest_nans_over_ocean(
        self, topo, level=0, include_zeros=False
    ):
        dest_nan_list = self.find_dest_nan_indexes_over_ocean(
            topo, level, include_zeros
        )
        report = {}
        for i in dest_nan_list:
            if type(i) == tuple:
                raise NotImplementedError()
            else:
                source_points = self.dest_to_source(i)
                vals = self.source_index_to_val(source_points,level) 
                report[i] = {
                    "dest_point":i,
                    "source_points":source_points,
                    "source_vals":vals
                }
        return report
    
    def generate_boundary_dest_mask(self, topo):
        mask = topo.point_is_ocean(lats = self.regridded_ds[self.regrid_lat_name].values, lons = self.regridded_ds[self.regrid_lon_name].values)
        return mask
    def generate_source_mask(self):
        return  xr.where(~np.isnan(self.raw_ds[self.raw_var_name][0,0]), 1, 0)
    
    def plot_regridding_information(self,extent,topo,plot_source_issues = True, level = 0):
        fig,ax = self.generate_figure_background(extent)
        ax.scatter(self.regridded_ds[self.regrid_lon_name], self.regridded_ds[self.regrid_lat_name].values,c = ~np.isnan(self.regridded_ds[self.regrid_var_name][0,level]), s=13, marker='x',cmap = "bwr", label = "Destination Points with or without Data (Red/Blue)", transform=ccrs.PlateCarree())
        ax.scatter(topo._grid.qlon, topo._grid.qlat, c="orange", s=topo.qmask, transform=ccrs.PlateCarree(), label="Wet Q Points")
        ax.scatter(topo._grid.vlon, topo._grid.vlat, c="orange", s=topo.vmask, transform=ccrs.PlateCarree(), label="Wet V Points")
        ax.scatter(topo._grid.ulon, topo._grid.ulat, c="orange", s=topo.umask, transform=ccrs.PlateCarree(), label="Wet U Points")
        ax.scatter(topo._grid.tlon, topo._grid.tlat, c="orange", s=topo.tmask, transform=ccrs.PlateCarree(), label="Wet T Points")
        if plot_source_issues:
            report = self.check_source_points_on_dest_nans_over_ocean(topo, level = level)
            lon = []
            lat = []
            val = []
            for key in report:
                s = report[key]["source_points"]
                lat_part,lon_part = self.source_index_to_lat_lon(s)

                val_part = self.source_index_to_val(s)
                lon.extend(lon_part)
                lat.extend(lat_part)
                val.extend(val_part)
            # Mask for valid and invalid values
            lon = np.array(lon)
            lat = np.array(lat)
            valid = ~np.isnan(val)
            invalid = np.isnan(val)
            # Scatter valid (red)
            ax.scatter(lon[valid], lat[valid], c="red", s=10, transform=ccrs.PlateCarree(), label="Source Points with value")

            # Scatter invalid (blue)
            ax.scatter(lon[invalid], lat[invalid], c="blue", s=10, transform=ccrs.PlateCarree(), label="Source Points no value")

        ax.legend( fontsize="small")

        



