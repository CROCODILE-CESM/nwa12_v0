from CrocoDash.grid import Grid
print("Start Grid")
grid = Grid(
  resolution = 0.1,
  xstart = 278.0,
  lenx = 30.0,
  ystart = 7.0,
  leny = 30.0,
  name = "panama1",
)

from CrocoDash.topo import Topo
from pathlib import Path

topo = Topo(
    grid = grid,
    min_depth = 9.5,
)
bathymetry_path="/glade/work/altuntas/croc/input/GEBCO_2024_coarse_x4.nc"
bathymetry_path="/glade/derecho/scratch/manishrv/ice/croc/gebco/GEBCO_2024.nc"
zarr_path= Path("/glade/u/home/manishrv/scratch/ice/croc/zarr/gebco/GEBCO_2024.zarr")

topo.interpolate_from_file(
    file_path = bathymetry_path,
    longitude_coordinate_name="lon",
    latitude_coordinate_name="lat",
    vertical_coordinate_name="elevation"
)