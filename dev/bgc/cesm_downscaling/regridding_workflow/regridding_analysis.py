import xarray as xr
import numpy as np
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


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
            The original dataset.
        regridded_ds : xarray.Dataset
            The regridded dataset.
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

    def calculate_useful_indexes(self):
        """
        Calculate info for the regridding process.
        """

        # Get All Points
        self.source_point_indexes = self.weights.col.values - 1
        self.raw_data_source_points_lat = self.raw_ds[self.raw_lat_name].flatten()[
            self.source_point_indexes
        ]
        self.raw_data_source_points_lon = self.raw_ds[self.raw_lon_name].flatten()[
            self.source_point_indexes
        ]
        self.dest_point_indexes = np.unique(self.weights.row.values - 1)
        self.regridded_data_dest_points_lat = self.regridded_ds[
            self.regrid_lat_name
        ].flatten()[self.dest_point_indexes]
        self.regridded_data_dest_points_lon = self.regridded_ds[
            self.regrid_lon_name
        ].flatten()[self.dest_point_indexes]

        # Get it in term of dest points (which are 1-D)
        self.dest_to_source = {}

        for i in self.dest_point_indexes:
            indexes = np.where(self.weights.row == (i + 1))
            source_indexes = self.weights.col[indexes]
            self.dest_to_source[i] = source_indexes

        self.source_to_dest = {}

        for i in self.source_point_indexes:
            index = np.where(self.weights.col == (i + 1))
            dest_index = self.weights.row[index]
            self.source_to_dest[i] = dest_index

        self.unincluded_dest_points = [i for i in range( len(self.regridded_ds[self.regrid_lon_name])) if i not in self.dest_point_indexes]  # These become zeroes

        
