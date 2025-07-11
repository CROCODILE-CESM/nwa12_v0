from regional_mom6 import MOM_parameter_tools as mpt
from pathlib import Path

def main():
    gustavo = mpt.read_MOM_file_as_dict(Path("MOM_parameter_doc.all"),"/glade/u/home/manishrv/scratch/calgulf.2/run")
    new_default = mpt.read_MOM_file_as_dict(Path("MOM_parameter_doc.all"),"/glade/u/home/manishrv/scratch/calgulf.tm1/run")
    for key in gustavo:
        if key == "original" or key == "filename":
            continue
        if key in new_default:
            if gustavo[key]["value"]!=new_default[key]["value"]:
                print("Difference!",key,gustavo[key]["value"], new_default[key]["value"])
        else:
            print("Key missing in default", key)
            

if __name__ == "__main__":
    main()