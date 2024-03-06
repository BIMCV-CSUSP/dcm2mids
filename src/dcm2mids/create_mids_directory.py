from datetime import datetime
from pathlib import Path
from typing import Union

from pydicom.fileset import FileSet

from dcm2mids.procedures.general_radiology import general_radiology_procedure

from .generate_tsvs import (
    get_participant_row,
    get_session_row,
    save_participant_tsv,
    save_scans_tsv,
    save_session_tsv,
)
from .procedures.magnetic_resonance.magnetic_resonance_procedure import (
    MagneticResonanceProcedures
)
from .procedures.visible_light.visible_light_procedure import (
    VisibleLightProcedures
)

# TODO: Add the logic to create the MIDS directory structure.
def create_mids_directory(
    fileset: FileSet, mids_path: Union[Path, str], bodypart: str
) -> None:
    """
    Create the MIDS directory structure for a given file set and body  part.

    :param fileset: The FileSet object containing the data to be processed.
    :type fileset: pydicom.fileset.FileSet
    :param mids_path: The path to the MIDS directory where the data will be stored.
    :type mids_path: Union[pathlib.Path, str]
    :param bodypart: The body part to be processed (e.g., "head", "neck", etc.).
    :type bodypart: str
    :return: None
    :rtype: None
    """

    use_bodypart = len(fileset.find_values("BodyPartExamined")) > 1  ### []
    use_viewposition = len(fileset.find_values("ViewPosition")) > 1  ### []
    #  procedure_MR = ProceduresMagneticResonance(mids_path, bodypart)
    mids_path = Path(mids_path)
    procedure_VL = VisibleLightProcedures(
        mids_path, bodypart, use_bodypart, use_viewposition
    )
    procedure_RX = general_radiology_procedure(mids_path, bodypart)
    participants = []
    for subject in fileset.find_values("PatientID"):
        participant = {}
        sessions = []
        for session in fileset.find_values("StudyID", fileset.find(PatientID=subject)):
            scans = []
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
                    pass
                if instance_list[0][1].Modality in ["CR", "DX", "CT", "PT"]:
                    scans_row = procedure_RX.run(instance_list)
                    
                if instance_list[0][1].Modality in ["OP", "SC", "XC", "OT", "SM", "BF"]:
                    scans_row = procedure_VL.run(instance_list)
                scans.extend(scans_row)
            save_scans_tsv(scans, mids_path, subject, session)  # type: ignore
            session_row = get_session_row(fileset, subject, session)  # type: ignore
            patient_age = session_row["age"]
            if "age" not in participant:
                participant["age"] = []
            participant["age"].append(patient_age)
            participant_birthday = session_row.pop("PatientBirthDate")
            sessions.append(session_row)
            print(f"{scans=}")
        save_session_tsv(sessions, mids_path, subject)  # type: ignore
        participant = get_participant_row(
            participant, fileset, subject, bodypart, participant_birthday  # type: ignore
        )
        participants.append(participant)
    save_participant_tsv(participants, mids_path)
    print(f"{participants=}")
