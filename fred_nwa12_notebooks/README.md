# Generating the NWA12 Grid and Boundary Condition Files
This folder contains the original workflow to create the NWA12 regional grid and boundary conditions (Created by Fred C). In it, we create the supergrid, topography, and mask files for the region, NWA12 and then create the boundary conditions with the GLORYS dataset. Please see below for both the file structure, with information about each file, and the workflow for these were generated.

## File Structure & Information
This section introduces the folders and file structures of the original NWA12 grid/obc generation. Please see below for details.
### Folders
1. `input_files`: Where the output grid files are outputted
2. `plots`: Where output plots are outputted
3. `obc_glorys`: Folder where all boundary conditions are generated

### Files
1. `ncar_NWA12.ipynb`: Creates the NWA12 supergrid, mask, and topo files into `input_files`
2. `mosaic2mom6.py`: Merges the output from `ncar_NWA12.ipynb` into one `NWA12_grid.nc` file into the `input_files` folder, with additional grid formatting.
3. `plot_NWA12.ipynb`: Plots different variables from `NWA12_grid.nc` and saves to the `plots` folder.
4. `obc_glorys/gen_nwa12_obc_from_glorys.ipynb`: Generates all boundary condition files
5. `obc_glorys/check_nwa12_obc_from_glorys.ipynb`: Checks the generated boundary conditions
6. `obc_glorys/batch_gen_nwa12_obc_from_glorys.sh`: Submits the `en_nwa12_obc_from_glorys.ipynb` notebook to casper (it takes a while)
7. `obc_glorys/mom6_OBC_routines.py`: Utils

## Workflow
1. Install conda environment from `environment.yml`
2. Run the `ncar_NWA12.ipynb` notebook. In it, we: 
    1.  Load the GFDL NWA12 Supergrid
    2. Find the extents of that grid
    3. Load the global MOM6 Supergrid, Topo, and Land-Sea Mask
    4. Cut the global supergrid to the regional extents
    5. Make sure the number of cells works well with MPI (not a prime number, etc). 
    6. Save the supergrid
    7. Cut the global mask and topo file to the regional domain by using our new supergrid dimensions
    8. Fill the mask with locations (like the Pacific and areas of Canada) that we don't want in the regional domain
    9. Save those files
3. Run the `mosaic2mom6.py`. In it, we:
    1. Read the output files from the previous step
    2. Find the necessary variables
    3. Find the necessary grid information and store it in variables
    4. Add it to the general netCDF file
    5. Save it
4. Run the `plot_NWA12.ipynb` file. See the plots folder for more information.
5. That's it for the grid files. Now we open the obc_glorys folder to create the boundary conditions.
6. Run `obc_glorys/check_nwa12_obc_from_glorys.ipynb`. In it, we:
    1. Read in grid files and GLORYS data
    2. Get Coordinate Extents
    3. Read GLORYS data, regrid it, Get Boundary Data and Save to NetCDF
    4. Save Raw Data
    5. Format & Export to NetCDF
7. Submit the actual notebook (starts with gen) with all the data to Casper using `obc_glorys/batch_gen_nwa12_obc_from_glorys.sh`
8. Apply to CESM Run

## Tool Creation
This section discusses converting this workflow into a tool leveraging similar tools like regional-mom6.

1. Create the rectangle grid using regional-mom6
2. Check grid numbers being a good divisible number 
3. Apply masking for the Pacific & Canada using available tools
4. Generating OBC - Compare Processes