import os
from pathlib import Path
import CrocoDash as cd

def main():
    expt = cd.driver.CrocoDashDriver.create_experiment_from_config("/glade/u/home/manishrv/documents/nwa12_0.1/mom_run/gfdl_copy.3.n3b/config.json")
    glorys_path = os.path.join("/","glade","derecho","scratch","manishrv","gfdl_copy.1.n3b_inputs","glorys" )
    # Define a mapping from the GLORYS variables and dimensions to the MOM6 ones
    ocean_varnames = {"time": "time",
                  "yh": "latitude",
                  "xh": "longitude",
                  "zl": "depth",
                  "eta": "zos",
                  "u": "uo",
                  "v": "vo",
                  "tracers": {"salt": "so", "temp": "thetao"}
                  }

    # Set up the initial condition
    expt.setup_initial_condition(
        Path(glorys_path) / "ic_unprocessed.nc", # directory where the unprocessed initial condition is stored, as defined earlier
        ocean_varnames,
        arakawa_grid="A"
        )    

    # Set up the four boundary conditions. Remember that in the glorys_path, we have four boundary files names north_unprocessed.nc etc. 
    # expt.setup_ocean_state_boundaries(
    #         Path(glorys_path),
    #         ocean_varnames,
    #         arakawa_grid = "A"
    #         )

if __name__ == "__main__":
    print("Test")
    main()