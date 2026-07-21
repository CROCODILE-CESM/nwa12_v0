import xarray as xr
print("Start")
# Open the dataset, chunking as needed
dataset = xr.open_mfdataset(
    "/glade/derecho/scratch/manishrv/archive/gustavo-glorys-2/ocn/hist/gustavo-glorys-2.mom6.h.native.2000*.nc",
)

# Subset the variables you're interested in
subset = dataset[["mlotst", "SSH"]]  # Replace 'variable1' and 'variable2' with the actual variable names
print("Save")
# Save the subset to a new NetCDF file
subset.to_netcdf("/glade/u/home/manishrv/documents/croc/dev/gustavo_glorys/cesm_important_2d_fields.nc")
print("End")