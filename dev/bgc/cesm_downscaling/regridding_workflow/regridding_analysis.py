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
    def source_lat_lons(self):
        raw_data_source_points_lat = self.raw_ds[self.raw_lat_name].values.flatten()[
            self.source_indexes
        ]
        raw_data_source_points_lon = self.raw_ds[self.raw_lon_name].values.flatten()[
            self.source_indexes
        ]
        return raw_data_source_points_lat, raw_data_source_points_lon

    @property
    def dest_lat_lons(self):
        regridded_data_dest_points_lat = self.regridded_ds[
            self.regrid_lat_name
        ].values.flatten()[self.dest_indexes]
        regridded_data_dest_points_lon = self.regridded_ds[
            self.regrid_lon_name
        ].values.flatten()[self.dest_indexes]

        return regridded_data_dest_points_lat, regridded_data_dest_points_lon

    @property
    def unincluded_dest_points(self):
        return [
            i
            for i in range(len(self.regridded_ds[self.regrid_lon_name]))
            if i not in self.dest_indexes
        ]  # These become zeroes

    def source_to_dest(self, source_point):
        return self.weights.row[np.where(self.weights.col == (source_point + 1))] - 1

    def dest_to_source(self, dest_point):
        return self.weights.col[np.where(self.weights.row == (dest_point + 1))] - 1

    def find_source_nans(self, surface = True):
        """
        Calculate the masks for the regridding process. Steps:
        1.  Find indexes of all source points that are NaN in all 4 dimensions, publish report
        2. Verify the destination points are similarly NaN, and find if other points are also Nan, publish report
        3. Using the topo masks, identify which dest points are okay to be NaN and which aren't. Publish report
        4. From unicluded dest points, make sure those all fall in the mask area, publish report.
        """
        if surface:
            nan_locs =  self.raw_ds[self.raw_var_name][0,0].isnull()

        else:
            nan_locs = self.raw_ds[self.raw_var_name][0].isnull()

    def find_dest_nans(self, surface = True):
        if surface:
            nan_locs =  self.regridded_ds[self.regrid_var_name][0,0].isnull()

        else:
            nan_locs = self.regridded_ds[self.regrid_var_name][0].isnull()

    def get_dest_mask(self, topo: Topo, direction):

        if direction == "north":
            q = topo.qmask[-1,:]
            alt = topo.vmask[-1,:]
        elif direction == "south":
            q = topo.qmask[0,:]
            alt = topo.vmask[0,:]
        elif direction == "west":
            q = topo.qmask[:,0]
            alt = topo.umask[:,0]
        elif direction == "east":
            q = topo.qmask[:,-1]
            alt = topo.umask[:,-1]

        combined_mask = np.empty(q.size + alt.size, dtype=q.dtype)
        combined_mask[0::2] = q  # Fill even indices with q
        combined_mask[1::2] = alt  # Fill odd indices with alt

        return combined_mask




    
