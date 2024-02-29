from pathlib import Path
from typing import Union

from .procedures.magnetic_resonance.magnetic_resonance_procedure import (
    ProceduresMagneticResonance,
)
from .procedures.visible_light.visible_light_procedure import ProceduresVisibleLight
from pydicom.fileset import FileSet


# TODO: Add the logic to create the MIDS directory structure.
def create_mids_directory(
    fileset: FileSet, mids_path: Union[Path, str], bodypart: str
) -> None:
    """Create the MIDS directory structure."""
    use_bodypart = len(fileset.find_values("BodyPartExamined")) > 1  ### []
    use_viewposition = len(fileset.find_values("ViewPosition")) > 1  ### []
    procedure_MR = ProceduresMagneticResonance(mids_path, bodypart)
    procedure_VL = ProceduresVisibleLight(mids_path, bodypart)

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
                    try:
                        instance_number = int(instance.InstanceNumber)
                    except (AttributeError, ValueError):
                        instance_number = -1
                    instance_list.append((instance_number, instance))

                if instance_list[0][1].Modality == "MR":
                    procedure_MR.run(instance_list)
                    pass
                if instance_list[0][1].Modality in ["CR", "DX", "CT", "PT"]:

                    pass
                if instance_list[0][1].Modality in ["OP", "SC", "XC", "OT", "SM", "BF"]:
                    procedure_VL.run(instance_list)

                    pass


# TODO: Add the logic to create the TSV files.
