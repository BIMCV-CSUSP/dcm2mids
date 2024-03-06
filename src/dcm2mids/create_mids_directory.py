import logging
from datetime import datetime
from pathlib import Path
from typing import Union

from pydicom.fileset import FileSet

from .generate_tsvs import (
    get_participant_row,
    get_session_row,
    save_participant_tsv,
    save_scans_tsv,
    save_session_tsv,
)
from .procedures.magnetic_resonance.magnetic_resonance_procedure import (
    MagneticResonanceProcedures,
)
from .procedures.visible_light.visible_light_procedure import VisibleLightProcedures

logger = logging.getLogger(__name__)


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

    use_bodypart = len(fileset.find_values("BodyPartExamined", load=True)) > 1
    logger.debug("`BodyPartExamined` tag: %s", use_bodypart)
    use_viewposition = len(fileset.find_values("ViewPosition", load=True)) > 1
    logger.debug("`ViewPosition` tag: %s", use_bodypart)
    #  procedure_MR = ProceduresMagneticResonance(mids_path, bodypart)
    mids_path = Path(mids_path)
    procedure_VL = VisibleLightProcedures(
        mids_path, bodypart, use_bodypart, use_viewposition
    )
    participants = []
    for subject in fileset.find_values("PatientID"):
        logger.info("Subject: %s", subject)
        participant = {}
        sessions = []
        for session in fileset.find_values("StudyID", fileset.find(PatientID=subject)):
            logger.info("Session: %s", session)
            scans = []
            for scan in fileset.find_values(
                "SeriesNumber", fileset.find(PatientID=subject, StudyID=session)
            ):
                logger.info("Scan: %s", scan)
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
                    pass
                if instance_list[0][1].Modality in ["OP", "SC", "XC", "OT", "SM", "BF"]:
                    scans_row = procedure_VL.run(instance_list)
                scans.extend(scans_row)
            save_scans_tsv(scans, mids_path, subject, session)  # type: ignore
            logger.debug(
                "%d scans created from session %s in subject %s.",
                len(scans),
                session,
                subject,
            )
            session_row = get_session_row(fileset, subject, session)  # type: ignore
            patient_age = session_row["age"]
            if "age" not in participant:
                participant["age"] = []
            participant["age"].append(patient_age)
            participant_birthday = session_row.pop("PatientBirthDate")
            sessions.append(session_row)
        save_session_tsv(sessions, mids_path, subject)  # type: ignore
        logger.debug(
            "%d sessions created from subject %s.",
            len(sessions),
            subject,
        )
        participant = get_participant_row(
            participant, fileset, subject, bodypart, participant_birthday  # type: ignore
        )
        participants.append(participant)
    save_participant_tsv(participants, mids_path)
    logger.debug("%d participants processed.", len(participants))
