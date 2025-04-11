import os
import xarray as xr
print("Starting")
# Define input and output folders
input_folder="/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/date_break"
output_folder="/glade/u/home/manishrv/scratch/croc_input/nwa_in_crocesm/ocnice"


# Get all unique suffixes (e.g., 001.nc, 002.nc, etc.)
files = [f for f in os.listdir(input_folder) if f.endswith('.nc')]
suffixes = sorted(set(f.split('_')[-1] for f in files))

# Loop through each suffix and merge the corresponding files
for suffix in suffixes:
    # Get all files with the same suffix
    files_to_merge = [os.path.join(input_folder, f) for f in files if f.endswith(f"_{suffix}")]
    print("Opening")
    # Open all matching files as xarray datasets
    datasets = [xr.open_dataset(f) for f in files_to_merge]
    
    print("Merging")
    # Merge the datasets by adding variables (along existing dimensions)
    merged_dataset = xr.merge(datasets)
    
    # Define output file path
    output_file = os.path.join(output_folder, f"marbl_bgc_{suffix}")
    
    # Save the merged dataset to a new NetCDF file
    merged_dataset.to_netcdf(output_file)
    
    print(f"Merged {len(datasets)} files for suffix '{suffix}' into {output_file}")

print("All merging operations completed!")
