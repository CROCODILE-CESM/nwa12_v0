#!/bin/bash

# Set the input and output folders
input_folder="/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/processed_interpolated_filled_data"       # Replace with your folder path
output_folder="/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/date_break"    # Replace with your output folder path
mkdir -p "$output_folder"  # Create the output folder if it doesn't exist

# Loop over all NetCDF files in the input folder
for file in "$input_folder"/*.nc; do
    filename=$(basename "$file")
    output_file="$output_folder/$filename"

    echo "Processing: $file -> $output_file"

    # Modify time units and calendar
    ncap2 -O -s 'time@units="days since 2000-01-01 00:00:00.000000"' "$file" "$output_file"

    echo "Saved: $output_file"
done

echo "All files processed successfully."
