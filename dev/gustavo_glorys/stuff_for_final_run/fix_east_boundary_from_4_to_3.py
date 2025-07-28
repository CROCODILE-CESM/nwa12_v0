import xarray as xr

input_file = "/glade/derecho/scratch/manishrv/croc_input/gustavo.glorys.3/ocnice/forcing_obc_segment_004.nc"
output_file = "/glade/derecho/scratch/manishrv/croc_input/gustavo.glorys.3/ocnice/forcing_obc_segment_003.nc"

# Open with full decoding
ds = xr.open_dataset(input_file, chunks={})


# 1. Rename dimensions
rename_dims = {dim: dim.replace("004", "003") for dim in ds.dims if "004" in dim}
ds_new = ds.rename(rename_dims)

# 2. Rename variables
rename_vars = {var: var.replace("004", "003") for var in ds.data_vars if "004" in var}
ds_new = ds_new.rename(rename_vars)

# 3. Fix variable attributes
for var in ds_new.variables:
    new_attrs = {}
    for attr_name, attr_val in ds_new[var].attrs.items():
        if isinstance(attr_val, str):
            new_attrs[attr_name] = attr_val.replace("004", "003")
        else:
            new_attrs[attr_name] = attr_val
    ds_new[var].attrs = new_attrs

# 4. Fix global attributes
new_global_attrs = {}
for attr_name, attr_val in ds_new.attrs.items():
    if isinstance(attr_val, str):
        new_global_attrs[attr_name] = attr_val.replace("004", "003")
    else:
        new_global_attrs[attr_name] = attr_val
ds_new.attrs = new_global_attrs
VALID_KEYS = {
    '_FillValue', 'compression', 'zlib', 'least_significant_digit', 'dtype',
    'chunksizes', 'shuffle', 'contiguous', 'fletcher32', 'complevel'
}
encoding = {}
for var in ds_new.data_vars:
    # Recover old variable name in original file
    old_var = var.replace("003", "004") if var.endswith("003") else var

    if old_var in ds.variables:
        # Get original encoding
        enc_old = ds[old_var].encoding.copy()

        # Clean invalid keys
        enc_clean = {k: v for k, v in enc_old.items() if k in VALID_KEYS}

        # Replace any dimension suffixes in chunksizes if needed
        if 'chunksizes' in enc_clean and enc_clean['chunksizes'] is not None:
            enc_clean['chunksizes'] = tuple(
                [int(str(dim).replace("004", "003")) for dim in enc_clean['chunksizes']]
            )

        encoding[var] = enc_clean

# Save new NetCDF
ds_new.to_netcdf(output_file, encoding=encoding)
