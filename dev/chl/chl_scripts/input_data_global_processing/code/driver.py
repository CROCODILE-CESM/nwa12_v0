import combine_seawifs
import create_seawifs_mask
import CrocoDash.raw_data_access.driver as dv
from pathlib import Path
import subprocess
def main(path):

    # # Access raw data
    # print("Accessing raw data")
    # pfr = dv.ProductFunctionRegistry()
    # pfr.load_functions()
    # pfr.functions["SEAWIFS"]["get_global_seawifs_script_for_cli"](
    #             "UNUSED",
    #             "UNUSED",
    #             "UNUSED",
    #             "UNUSED",
    #             "UNUSED",
    #             path,
    #             "UNUSED",
    #             "manishvenu"
    #         )
    
    # # Run the script
    # subprocess.run(
    #     [
    #         path / "get_seawifs_data.sh",
    #     ]
    # )
    # # Create SEAWIFS mask
    # print("Creating SEAWIFS mask")
    # create_seawifs_mask.create_seawifs_mask(path)

    # Combine SEAWIFS data
    print("Combining SEAWIFS data")
    combine_seawifs.combine_seawifs(path)

if __name__ == "__main__":
    script_dir = Path(__file__).parent.parent
    path = script_dir / "data"
    main(path)



