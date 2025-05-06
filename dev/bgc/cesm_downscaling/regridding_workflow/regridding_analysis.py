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
        raw_data_source_points_lat = self.raw_ds[self.raw_lat_name].values.flatten()[
            source_point
        ]
        raw_data_source_points_lon = self.raw_ds[self.raw_lon_name].values.flatten()[
            source_point
        ]
        return raw_data_source_points_lat, raw_data_source_points_lon

    def dest_index_to_lat_lon(self, dest_point):
        raw_data_dest_points_lat = self.regrid_ds[
            self.regrid_lat_name
        ].values.flatten()[dest_point]
        raw_data_dest_points_lon = self.regrid_ds[
            self.regrid_lon_name
        ].values.flatten()[dest_point]
        return raw_data_dest_points_lat, raw_data_dest_points_lon
    
    def source_index_to_val(self, source_point):
        return self.raw_ds[self.raw_var_name].values.flatten()[source_point]
    def dest_index_to_val(self, dest_point):
        return self.regrid_ds[self.regrid_var_name].values.flatten()[dest_point]


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
        output_indexes = []
        for i in range(dest_nans.shape[0]):
            if dest_nans[i] and topo.point_is_ocean(
                lon=self.regridded_ds[self.regrid_lon_name][i],
                lat=self.regridded_ds[self.regrid_lat_name][i],
            ):
                output_indexes.append(i)


        return output_indexes

    def check_source_points_on_dest_nans_over_ocean(
        self, topo, level=0, include_zeros=False
    ):
        dest_nan_list = self.find_dest_nan_indexes_over_ocean(
            topo, level, include_zeros
        )

        for i in dest_nan_list:
            if type(i) == tuple:
                raise NotImplementedError()
            else:
                source_points = self.dest_to_source(i)
                vals = self.source_index_to_val(source_points) 
                print(
                    f"Source points involved in NaN dest point {i} are: {source_points}. The NaN source point are {vals}"
                )

