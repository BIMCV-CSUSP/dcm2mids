from pathlib import Path
from typing import Union

from pydicom.fileset import FileSet
from pydicom.dataset import Dataset
# TODO: Add the logic to create the MIDS directory structure.
def create_mids_directory(
    fileset: FileSet, mids_path: Union[Path, str], bodypart: str
) -> None:
    """Create the MIDS directory structure."""
    
    
    for subject in fileset.find_values("PatientID"):
        print(f"{subject=}")
        for session in fileset.find_values("StudyID", fileset.find(PatientID=subject)):
            print(f" {session=}")
            for scan in fileset.find_values(
                "SeriesNumber", fileset.find(PatientID=subject, StudyID=session)
            ):
                print(f"  {scan=}")
                instance_list = []
                for instance in fileset.find(
                    PatientID=subject, StudyID=session, SeriesNumber=scan
                ):
                    instance_list.append(( instance))
                if instance_list[0].Modality == "MR":
                    print(instance_list[0].path)
                    pass
                if instance_list[0].Modality in ["CR", "DX", "CT", "PT"]:
                    print(instance_list[0].path)
                    pass
                if instance_list[0].Modality in ["OP", "SC", "XC", "OT", "SM"]:
                    print(instance_list[0].path)
                    pass
# TODO: Add the logic to create the TSV files.

def dictify(ds: Dataset) -> dict:
    """Turn a pydicom Dataset into a dict with keys derived from the Element names."""
    output = dict()
    for elem in ds:
        if elem.VR != "SQ":
            output[elem.name] = str(elem.value)
        else:
            output[elem.name] = [dictify(item) for item in elem]
    return output