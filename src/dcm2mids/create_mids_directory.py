from datetime import datetime
from pathlib import Path
from typing import Union

from .generate_tsvs import (
    get_participant_row, 
    get_session_row, 
    save_session_tsv, 
    save_participant_tsv, 
    save_scans_tsv
)
from .procedures.magnetic_resonance.magnetic_resonance_procedure import (
    ProceduresMagneticResonance,
)
from .procedures.visible_light.visible_light_procedure import (
    ProceduresVisibleLight
)
from pydicom.fileset import FileSet



session_header = [
    "session_id",  # This is the session_id from the BIDS/MIDS standard (ses-<session_id>)
    "session_pseudo_id",  # This is the session_pseudo_id from the PatientID (session_id)
    "session_date_time",  # This is the acquisition date time of the session
    "age",  # this is the age of the participant in the session
]

sessions_keys = ["StudyID", "AcquisitionDateTime"]


# TODO: Add the logic to create the MIDS directory structure.
def create_mids_directory(
    fileset: FileSet, mids_path: Union[Path, str], bodypart: str
) -> None:
    """Create the MIDS directory structure."""
    use_bodypart = len(fileset.find_values("BodyPartExamined")) > 1  ### []
    use_viewposition = len(fileset.find_values("ViewPosition")) > 1  ### []
    # procedure_MR = ProceduresMagneticResonance(mids_path, bodypart)
    procedure_VL = ProceduresVisibleLight(
        mids_path, bodypart, use_bodypart, use_viewposition
    )
    participants = []
    for subject in fileset.find_values("PatientID"):
        participant = {}
        sessions = []
        for session in fileset.find_values("StudyID", fileset.find(PatientID=subject)):
            scans = []
            for scan in fileset.find_values(
                "SeriesNumber", fileset.find(PatientID=subject, StudyID=session)
            ):
                # data[subject][session][scan] = data[subject][session].get(scan, {})
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
                    # procedure_MR.run(instance_list)
                    pass
                if instance_list[0][1].Modality in ["CR", "DX", "CT", "PT"]:

                    pass
                if instance_list[0][1].Modality in ["OP", "SC", "XC", "OT", "SM", "BF"]:
                    scans_row = procedure_VL.run(instance_list)
                scans.extend(scans_row)
            save_scans_tsv(scans, mids_path, subject, session)
            session_row = get_session_row(fileset, subject, session)    
            patient_age = session_row["age"]
            if "age" not in participant:
                participant["age"] = []
            participant["age"].append(patient_age)
            patient_birthday = session_row.pop("PatientBirthDate")
            sessions.append(session_row)

            print(f"{scans=}")
        save_session_tsv(sessions, mids_path, subject)
        participant = get_participant_row(participant, fileset, subject, bodypart, patient_birthday)
        

        participants.append(participant)

    save_participant_tsv(participants, mids_path)
    print(f"{participants=}")


