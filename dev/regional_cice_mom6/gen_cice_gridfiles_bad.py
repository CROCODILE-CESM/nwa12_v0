import numpy as np
import xarray as xr
import struct
import os
from CrocoDash.grid import Grid
# Input file paths
in_vgrid_path = "/glade/derecho/scratch/manishrv/pan_artic_files_kate/vgrid_75_2m.nc"
in_topo_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/ocean_topog_cice_test_1_eaf771.nc"
in_supergrid_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/ocean_hgrid_cice_test_1_eaf771.nc"

# Output binary file paths
out_hgrid_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/cice_hgrid.ieeer8"
out_topo_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/cice_topo.ieeei4"

# Load NetCDF files
vgrid_ds = xr.open_dataset(in_vgrid_path)
topo_ds = xr.open_dataset(in_topo_path)
supergrid_ds = Grid.from_supergrid(in_supergrid_path)

# Get sizes
depth_array = topo_ds['depth'].values
ny, nx = depth_array.shape

dz = vgrid_ds['dz'].values
ndepth = dz.size

# Compute cumulative depth levels
depths = np.cumsum(dz)

# Compute kmt
kmt = np.full((ny, nx), ndepth, dtype=np.int32)
for j in range(ny):
    for i in range(nx):
        topo_depth = depth_array[j, i]
        for k in range(ndepth):
            if topo_depth < depths[k]:
                kmt[j, i] = k
                break

# Convert to radians
dtr = np.pi / 180.0

ulat = dtr * supergrid_ds.qlat.isel(nyp=slice(1, ny+1), nxp=slice(1, nx+1)).values
ulon = dtr * supergrid_ds.qlon.isel(nyp=slice(1, ny+1), nxp=slice(1, nx+1)).values
htn = 100.0 * supergrid_ds.dxCv.values
hte = 100.0 * supergrid_ds.dyCu.values
hus = 100.0 * supergrid_ds.dxCu.values
huw = 100.0 * supergrid_ds.dyCv.values
angle = dtr * supergrid_ds.angle.values

print(f"htn max: {np.max(htn)}, min: {np.min(htn)}")
print(f"hte max: {np.max(hte)}, min: {np.min(hte)}")

# Write binary files in big endian format
def write_binary_file(filename, array, dtype='f8'):
    if os.path.exists(filename):
        os.remove(filename)

    if dtype == 'f8':
        fmt = ">d"  # IEEE double precision, big endian
    elif dtype == 'i4':
        fmt = ">i"  # IEEE 32-bit integer, big endian
    else:
        raise ValueError("Unsupported dtype")

    with open(filename, 'wb') as f:
        flat_array = array.flatten()
        for val in flat_array:
            f.write(struct.pack(fmt, val))

write_binary_file(out_topo_path, kmt, dtype='i4')
write_binary_file(out_hgrid_path, ulat, dtype='f8')
write_binary_file(out_hgrid_path, ulon, dtype='f8')
write_binary_file(out_hgrid_path, htn, dtype='f8')
write_binary_file(out_hgrid_path, hte, dtype='f8')
write_binary_file(out_hgrid_path, hus, dtype='f8')
write_binary_file(out_hgrid_path, huw, dtype='f8')
write_binary_file(out_hgrid_path, angle, dtype='f8')
