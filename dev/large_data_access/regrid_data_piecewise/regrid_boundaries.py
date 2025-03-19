import regional_mom6 as rm6
from pathlib import Path
from CrocoDash import utils
from CrocoDash.data_access.large_data_workflow.utils import load_config
import re
import os
from collections import defaultdict
from datetime import datetime
import xarray as xr

logger = utils.setup_logger(__name__)


def parse_dataset_folder(
    folder: str | Path, input_dataset_regex: str, date_format: str
):
    """
    Parse the input dataset folder and parse file names into categories based on boundary and date
    """
    # Dictionary to store boundary info
    boundary_file_list = defaultdict(list)

    # Regex Pattern for the dataset
    pattern = re.compile(input_dataset_regex)

    # Iterate through the folder provided for dataset files
    for file in os.listdir(folder):

        # Get File Path
        file_path = os.path.join(folder, file)

        # Check if file matches
        match = pattern.match(file)
        if match:

            # Extract information
            boundary, start_date, end_date = match.groups()

            # Convert dates to datetime objects
            start_date = datetime.strptime(start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)

            # Append (file path, start date, end date)
            boundary_file_list[boundary].append((start_date, end_date, file_path))

    # Sort the date ranges for each boundary
    for boundary in boundary_file_list:
        boundary_file_list[boundary].sort()

    return boundary_file_list


def regrid_dataset_piecewise(
    folder: str | Path,
    input_dataset_regex: str,
    date_format: str,
    start_date: str,
    end_date: str,
    hgrid: str | Path,
    dataset_varnames: dict,
    output_folder: str | Path,
    boundary_number_conversion: dict,
):
    """
    Find the required files
    """
    logger.info("Parsing Raw Data Folder")
    # Parse data folder and find required files
    start_date = datetime.strptime(start_date, date_format)
    end_date = datetime.strptime(end_date, date_format)
    boundary_file_list = parse_dataset_folder(folder, input_dataset_regex, date_format)

    if boundary_list == None:
        boundary_list = boundary_file_list.keys()

    for boundary in boundary_list:
        if boundary not in boundary_number_conversion:
            logger.error(
                f"Boundary '{boundary}' not found in the boundary_number_conversion. We need the boundary_number_conversion for all boundaries to identify what number to label each segment."
            )
            return

    matching_files = defaultdict(list)
    for boundary in boundary_list:
        for file_start, file_end, file_path in boundary_file_list[boundary]:
            if file_start <= end_date and file_end >= start_date:
                matching_files[boundary].append((file_start, file_end, file_path))

    logger.info("Setting up required information")
    # Setup required information for regridding

    # Read in hgrid
    hgrid = xr.open_dataset(hgrid)

    # Set up required information
    expt = rm6.experiment.create_empty()
    expt.hgrid = hgrid
    expt.mom_input_dir = Path(output_folder)
    expt.date_range = [start_date, None]

    logger.info("Starting regridding")
    # Do Regridding
    for boundary in matching_files.keys():
        for file_start, file_end, file_path in matching_files[boundary]:
            file_path = Path(file_path)
            expt.setup_single_boundary(
                file_path,
                dataset_varnames,
                boundary,
                boundary_number_conversion[boundary],
            )
            break
    logger.info("Finished regridding")
    return


def main():
    config = load_config(
        "/glade/u/home/manishrv/documents/croc/dev/large_data_access/regrid_data_piecewise/config.json"
    )
    regrid_dataset_piecewise(
        config["paths"]["raw_dataset_path"],
        config["raw_file_regex"]["raw_dataset_pattern"],
        config["dates"]["format"],
        config["dates"]["start"],
        config["dates"]["end"],
        config["paths"]["hgrid_path"],
        config["varnames"],
        config["paths"]["output_path"],
        config["boundary_number_conversion"],
    )
    return


if __name__ == "__main__":
    main()
