import os
import xarray as xr
import re
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Start File")
# Path to the directory containing the segmented folders
base_dir = "/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/fix/rm6_output"  # Change this to your actual path

desired_start_date =  datetime.strptime('2000-01-01', "%Y-%m-%d")
desired_end_date =  datetime.strptime('2005-12-31', "%Y-%m-%d")
# Find and sort folders based on the start date
folders = []
for f in os.listdir(base_dir):
    start_date_str, end_date_str = f.split('_to_')
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    if desired_start_date <= start_date <= desired_end_date or desired_start_date <= end_date <= desired_end_date:
            folders.append((start_date, end_date, f))

# Sort folders by extracted start date
folders.sort()  # Sorts by the datetime object

# Define segments to merge
segments = [ "forcing_obc_segment_001", "forcing_obc_segment_002", "forcing_obc_segment_003"]

# Dictionary to store datasets for each segment
segment_files = {seg: [] for seg in segments}

# Collect files for each segment
for _,_, folder in folders:  # Now sorted by start date
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        for seg in segments:
            file_path = os.path.join(folder_path, f"{seg}.nc")
            if os.path.exists(file_path):
                segment_files[seg].append(file_path)

# Merge and save output for each segment
output_dir = "/glade/u/home/manishrv/scratch/inputs_rm6/nwa_twenty_year/merged_rm6_output"
os.makedirs(output_dir, exist_ok=True)
for seg, files in segment_files.items():
    logger.info(f"Start Merge: {seg}")
    if files:
        logger.info(f"Open Datasets")
        datasets = [xr.open_dataset(f) for f in files]
        logger.info(f"Merge Datasets")
        merged = xr.concat(datasets, dim="time")  # Ensure time is concatenated properly
        output_path = os.path.join(output_dir, f"{seg}_{folders[0][0].strftime('%Y-%m-%d')}_to_{folders[-1][1].strftime('%Y-%m-%d')}.nc")
        merged.to_netcdf(output_path, format="netcdf4")
        logger.info(f"Saved: {output_path}")
        # Close datasets
        for ds in datasets:
            ds.close()
