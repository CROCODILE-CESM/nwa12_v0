import os
import sys
import xarray as xr
import subprocess
import numpy as np
import json


def ncdiff_files(file1, file2, output_dir):
    command = (
        "ncdiff "
        + file1
        + " "
        + file2
        + " -O "
        + os.path.join(
            output_dir, os.path.basename(file2).replace(".nc", "") + "_ncdiff_diff.nc"
        )
    )
    activate_command = f"{command}"
    print(command)
    subprocess.run(activate_command, shell=True)


def ncompare_files(file1, file2, output_dir):
    command = (
        "ncompare "
        + file1
        + " "
        + file2
        + " --file-text "
        + os.path.join(
            output_dir,
            os.path.basename(file2).replace(".nc", "") + "_ncompare_diff.txt",
        )
    )
    print(command)
    activate_command = f"{command}"
    subprocess.run(activate_command, shell=True)


def compare_netcdf_with_xarray(file1, file2, output_dir):
    ds1 = xr.open_dataset(file1)
    ds2 = xr.open_dataset(file2)
    # Initialize empty dictionary to store differences
    differences = {"global_attributes": [], "dimensions": [], "variables": []}

    # Compare global attributes
    for attr in ds1.attrs:
        if attr not in ds2.attrs:
            differences["global_attributes"].append(
                f"Attribute {attr} missing in second dataset."
            )
        elif ds1.attrs[attr] != ds2.attrs[attr]:
            differences["global_attributes"].append(
                f"Global attribute '{attr}' differs: {ds1.attrs[attr]} vs {ds2.attrs[attr]}"
            )

    # Check for extra attributes in ds2
    for attr in ds2.attrs:
        if attr not in ds1.attrs:
            differences["global_attributes"].append(
                f"Attribute {attr} missing in first dataset."
            )

    # Compare dimensions
    if ds1.dims != ds2.dims:
        differences["dimensions"].append(f"Dimensions differ: {ds1.dims} vs {ds2.dims}")

    # Compare variables
    for var in ds1.data_vars:
        if var not in ds2.data_vars:
            differences["variables"].append(
                f"Variable {var} missing in second dataset."
            )
            continue

        # Check variable attributes
        for attr in ds1[var].attrs:
            if attr not in ds2[var].attrs:
                differences["variables"].append(
                    f"Attribute '{attr}' for variable '{var}' missing in second dataset."
                )
            elif ds1[var].attrs[attr] != ds2[var].attrs[attr]:
                differences["variables"].append(
                    f"Variable '{var}' attribute '{attr}' differs: {ds1[var].attrs[attr]} vs {ds2[var].attrs[attr]}"
                )

        # Check data values
        if not np.allclose(ds1[var].values, ds2[var].values, rtol=1e-3, atol=1e-3):
            differences["variables"].append(f"Data for variable '{var}' differs.")

    # Check for extra variables in ds2
    for var in ds2.data_vars:
        if var not in ds1.data_vars:
            differences["variables"].append(f"Variable {var} missing in first dataset.")

    # Output results
    if not any(differences.values()):
        print("The datasets are identical within the specified tolerance.")
    else:
        print("Differences found:")
        for category, diff_list in differences.items():
            if diff_list:
                print(f"\n{category.capitalize()}:")
                for diff in diff_list:
                    print(f" - {diff}")
    ds1.close()
    ds2.close()
    with open(
        os.path.join(
            output_dir, os.path.basename(file2).replace(".nc", "") + "_python_diff.json"
        ),
        "w",
    ) as json_file:
        json.dump(differences, json_file, indent=4)

    return differences


def run_comparison(dir1, dir2, case_name):
    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))
    common_files = files1.intersection(files2)

    all_match = True
    for file in common_files:
        if not file.endswith(".nc"):
            continue
        file1 = os.path.join(dir1, file)
        file2 = os.path.join(dir2, file)
        output_dir = "testing_diffs/" + case_name
        os.makedirs(output_dir, exist_ok=True)
        ncompare_files(file1, file2, output_dir)
        ncdiff_files(file1, file2, output_dir)
        print(
            "Xarray Comparison:", compare_netcdf_with_xarray(file1, file2, output_dir)
        )

    return all_match


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python test_regrid_velocity_and_tracers.py <dir1> <dir2> <case_name>"
        )
        sys.exit(1)

    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    case_name = sys.argv[3]

    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        print("Both arguments must be directories.")
        sys.exit(1)

    run_comparison(dir1, dir2, case_name)
