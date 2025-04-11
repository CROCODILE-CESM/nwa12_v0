#!/bin/bash

# Define input and output folders
INPUT_FOLDER="/glade/u/home/manishrv/documents/croc/dev/bgc/cesm_downscaling/date_break"
OUTPUT_FOLDER="/glade/u/home/manishrv/scratch/croc_input/nwa_in_crocesm/ocnice"


# Ensure input folder exists
if [ ! -d "$INPUT_FOLDER" ]; then
    echo "Error: Input folder '$INPUT_FOLDER' does not exist."
    exit 1
fi

# Ensure output folder exists, create if not
mkdir -p "$OUTPUT_FOLDER"

# Extract unique suffixes (e.g., 001.nc, 002.nc, etc.)
SUFFIXES=$(ls "$INPUT_FOLDER"/*.nc 2>/dev/null | awk -F_ '{print $NF}' | sort -u)

# Check if there are any NetCDF files
if [ -z "$SUFFIXES" ]; then
    echo "Error: No NetCDF files found in '$INPUT_FOLDER'."
    exit 1
fi

# Loop through each suffix and merge files by adding variables
for SUFFIX in $SUFFIXES; do
    FILES=("$INPUT_FOLDER"/*_"$SUFFIX")

    # Check if files exist for the suffix
    if [ ${#FILES[@]} -gt 0 ]; then
        OUTPUT_FILE="$OUTPUT_FOLDER/merged_$SUFFIX"
        echo "Merging files ending with $SUFFIX into $OUTPUT_FILE..."
        
        # Start with the first file as the base
        cp "${FILES[0]}" "$OUTPUT_FILE"
        
        # Append variables from the rest of the files
        for ((i=1; i<${#FILES[@]}; i++)); do
            echo "Adding variables from ${FILES[i]}..."
            ncks -A "${FILES[i]}" "$OUTPUT_FILE"
        done

        # Check if merge was successful
        if [ $? -eq 0 ]; then
            echo "Merged successfully: $OUTPUT_FILE"
        else
            echo "Error: Merge failed for suffix $SUFFIX"
        fi
    fi
done

echo "All merging operations completed!"
