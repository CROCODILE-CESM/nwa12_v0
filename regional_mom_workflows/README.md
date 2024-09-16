# Regional MOM6 Workflows

This is to be a description of Fred's work used in Gustavo & Mikes builds and Ashley's Regional MOM6 Package. There's a few things to consider about setting up MOM in regional mode and its integrations with CESM, and in a few ways it looks like the workflows diverge. Here's to writing up a cleaner workflow of not just the grid generation, but the setup of the CESM cases.

## Grid Generation

### Fred's Work
1.  Load the GFDL NWA12 Supergrid
2. Find the extents of that grid
3. Load the global MOM6 Supergrid, Topo, and Land-Sea Mask
4. Cut the global supergrid to the regional extents
5. Make sure the number of cells works well with MPI (not a prime number, etc). 
6. Save the supergrid
7. Cut the global mask and topo file to the regional domain by using our new supergrid dimensions
8. **Fill the mask with locations (like the Pacific and areas of Canada) that we don't want in the regional domain**
9. Save those files

### Ashley's Work
1. Load the GFDL NWA12 Supergrid
2. Find the extents of that grid
3. Create h & vgrid from scratch
4. Read GLORYS data, cut out bathmetry based on extents, and fill lakes



### Differences and Discussion
It looks like Ashley's work creates the grids from scratch, while Fred's work comes from the other side and subsets a global grid. To combine the best of both worlds, here are some discussion points we probably could tackle to create a neat workflow:
1. Decide from which direction to create regional grids (subset global or generate from scratch)
2. Implement tool to trim grid size to a easily divisible number for Supercomputer nodes/MPI 
3. Implement tool to mask out water we don't want, like the Pacific.


## Boundary Conditions Generation


### Fred's Work
1. Read in grid files and GLORYS data
2. Get Coordinate Extents
3. Read GLORYS data (from RDA), regrid it
4. Get Boundary Data and Save to NetCDF
5. Save Raw Data
6. Format & Export to NetCDF
### Ashley's Work
1. Get coordinate extents from earlier
2. Directly subset GLORYS data using the Copernicus Marine API
3. ....

### Differences and Discussion
The way Ashley has done this is pretty similar to the way Fred does it with a few differences. To combine the best of both worlds, here are some discussion points we could tackle to create a neat workflow:
1. Where should we get GLORYS data from? Are there advantages in gatehring data directly from Copernicus Marine? 
    - Ashley's OBC is much faster than using the RDA w/ Fred's code and is (currently) more publicly accessible, but adds additional dependencies on an API that doesn't always work and comes with its own difficulties. 
2. ...

## CESM Setup

### Fred's (and Mike and Gustavo's) Work
1. Create an ESMF Mesh Grid file called NWA12_grid with mosaic2mom6.py (I think? It seems very different).
2. Change CCS Config to get an NWA12 grid file
3. Generate MOM Config Files in SourceMods
4. Make XML changes for the following processes
    1. 

### Ashley's Work
1.  Using Visual Case Gen, setup a general CESM case with every component turning off (but MOM) with a data atmosphere and generic grid.
2. Copy MOM config files (input, override, diag_table, input.nml) into SourceMods
3. Override MOM config files (MOM_override) to point to the input directories with the correct number of cells in the x and y directions
4. (Remnant from RM6) Remove references to MOM_layout in input.nml b/c RM6 uses it for standalone MOM and the CESM handles it instead
5. (Remnant from RM6) Move forcing files to the general input directory
6. Create ESMF grid
7. Make XML Changes (see cesm_tools.py) for the following proceses:
    - Set number of OCN cells in the x and y direction
    - Make MOM6 dynamic_symmetric
    - Point toward esmf_mesh file in ocn (and ice, though maybe not needed) for the mask mesh/grid + general domain
    - Set Start Date

### Differences and Discussion
 To combine the best of both worlds, here are some discussion points we could tackle to create a neat workflow:
1. The creation of the ESMF grid file is similar to Fred's mosaic2mom6 python script

## General Discussion Points
- Can we (or should we) use MOM6_Bathy?





