import logging
from datetime import datetime
from pathlib import Path
from typing import Union

from pydicom.fileset import FileSet

from .generate_tsvs import *
from .procedures import *

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
    mids_path = Path(mids_path)
    participants = []
    for subject in fileset.find_values("PatientID", load=True):
        logger.debug("Subject: %s", subject)
        participant = {}
        sessions = []
        for session in fileset.find_values("StudyID", fileset.find(PatientID=subject, load=True), load=True):
            logger.debug("Session: %s", session)
            scans = []
            for scan in fileset.find_values(
                "SeriesNumber", fileset.find(PatientID=subject, StudyID=session, load=True), load=True
            ):
                logger.debug("Scan: %s", scan)
                instance_list = fileset.find(
                    PatientID=subject, StudyID=session, SeriesNumber=scan,
                    load=True
                )
                instance_list = sorted(
                    instance_list, key=lambda x: int(x.InstanceNumber)
                )
                logger.debug("Number of instances: %d", len(instance_list))
                modality = instance_list[0].Modality
                if modality == "MR":
                    scans_row = MagneticResonanceProcedures(
                        mids_path, bodypart, use_bodypart, use_viewposition
                    ).run(instance_list)
                if modality in ["CR", "DX"]:
                    scans_row = ConventionalRadiologyProcedures(
                        mids_path, bodypart, use_bodypart, use_viewposition
                    ).run(instance_list)
                if modality in ["CT", "PT"]:
                    scans_row = TomographyProcedures(
                        mids_path,  bodypart, use_bodypart, use_viewposition
                    ).run(instance_list)
                if modality in ["OP", "SC", "XC", "OT"]:
                    scans_row = OphthalmographyProcedures(
                        mids_path, bodypart, use_bodypart, use_viewposition
                    ).run(instance_list)
                if modality in ["SM", "BF"]:
                    scans_row = MicroscopyProcedures(
                        mids_path, bodypart, use_bodypart, use_viewposition
                    ).run(instance_list)
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
                participant["ages"] = []
            participant["ages"].append(patient_age)
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
