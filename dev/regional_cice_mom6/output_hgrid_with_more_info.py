import xarray as xr
from CrocoDash.grid import Grid

in_supergrid_path = "/glade/derecho/scratch/manishrv/croc_input/cice.test.1/ocnice/ocean_hgrid_cice_test_1_eaf771.nc"

supergrid_ds = Grid.from_supergrid(in_supergrid_path)
out_hgrid_path = "/glade/u/home/manishrv/documents/croc/dev/regional_cice_mom6/hgrid_adj.nc"
output_hgrid = xr.Dataset()
output_hgrid['qlat'] = supergrid_ds.qlat
output_hgrid['qlon'] = supergrid_ds.qlon
output_hgrid['dxCv'] = supergrid_ds.dxCv
output_hgrid['dyCu'] = supergrid_ds.dyCu
output_hgrid['dxCu'] = supergrid_ds.dxCu
output_hgrid['dyCv'] = supergrid_ds.dyCv
output_hgrid['angle'] = supergrid_ds.angle
output_hgrid.to_netcdf(out_hgrid_path)