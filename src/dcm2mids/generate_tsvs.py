import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd
from pydicom.fileset import FileSet

logger = logging.getLogger("dcm2mids").getChild("generate_tsvs")

participants_header = [
    "participant_id",  # This is the participant_id from the BIDS/MIDS standard (sub-<participant_id>)
    "participant_pseudo_id",  # This is the participant_pseudo_id from the PatientID (participant_id)
    "sex",  # This is the gender of the participant
    "participant_birthday",  # This is the patient's birthday
    "ages",  # This is the list of ages of the participant in the sessions
    "modalities",  # This is the list of modalities used in the sessions
    "body_parts_examined",  # This is the list of body parts examined in the sessions
]

session_header = [
    "session_id",  # This is the session_id from the BIDS/MIDS standard (ses-<session_id>)
    "session_pseudo_id",  # This is the session_pseudo_id from the PatientID (session_id)
    "acq_time",  # This is the acquisition date time of the session
    "age",  # this is the age of the participant in the session
]


def get_session_row(fileset: FileSet, subject: str, session: str) -> Dict[str, str]:
    """
    Generate a row for the Sessions TSV file.

    :param fileset: The FileSet to search for the subject and session.
    :type fileset: pydicom.fileset.FileSet
    :param subject: The ID of the subject this session belongs to.
    :type subject: str
    :param session: The ID of the session.
    :type session: str
    :return: A dictionary containing the session row data.
    :rtype: dict
    """

    session_row = fileset.find_values(
        ["StudyDate", "StudyTime", "AcquisitionDateTime", "AcquisitionDate", "AcquisitionTime", "PatientBirthDate"],
        fileset.find(PatientID=subject, StudyID=session),
        load=True,
    )
    session_row["session_id"] = f"sub-{session}"
    session_row["session_pseudo_id"] = session
    logger.debug("AcquisitionDateTime: %s", session_row.get("AcquisitionDateTime"))
    logger.debug("AcquisitionDate: %s", session_row.get("AcquisitionDate"))
    logger.debug("AcquisitionTime: %s", session_row.get("AcquisitionTime"))
    logger.debug("StudyDate: %s", session_row.get("StudyDate"))
    logger.debug("StudyTime: %s", session_row.get("StudyTime"))

    date_time = session_row["StudyDate"][0] + session_row["StudyTime"][0]
    if "." not in date_time:
        date_time += ".000000"
    session_row["session_date_time"] = [date_time]
    session_row.pop("StudyDate")
    session_row.pop("StudyTime")
    session_row["session_date_time"] = [
        datetime.strptime(s, "%Y%m%d%H%M%S.%f")
        for s in session_row["session_date_time"]
    ][0]
    if session_row.get("PatientBirthDate")[0]:

        session_row["PatientBirthDate"] = datetime.strptime(
            session_row["PatientBirthDate"][0], "%Y%m%d"
        )
        patient_age = (
            session_row["session_date_time"] - session_row["PatientBirthDate"]
        ).days // 365.25

        session_row["PatientBirthDate"] = session_row["PatientBirthDate"].strftime(
            "%Y-%m-%d"
        )
    else:
        session_row["PatientBirthDate"] = "n/a"
        patient_age = "n/a"
    
    session_row["acq_time"] = session_row["session_date_time"].isoformat()
    session_row["age"] = patient_age

    return session_row


def get_participant_row(
    participant: Dict[str, Union[str, list]],
    fileset: FileSet,
    subject: str,
    bodypart: str,
    participant_birthday: str,
) -> Dict[str, Union[str, list]]:
    """
    Generate a row for the Participants TSV file.

    :param participant: A dictionary with participant data.
    :type participant: dict
    :param fileset: The FileSet to search for the subject and session.
    :type fileset: pydicom.fileset.FileSet
    :param subject: The ID of the subject this session belongs to.
    :type subject: str
    :param bodypart: The bodypart(s) contained in the dataset for this participant.
    :type bodypart: str
    :param participant_birthday: The participant's birthday.
    :type participant_birthday: str
    :return: A dictionary containing the participant row data.
    :rtype: dict
    """

    participant["participant_id"] = f"sub-{subject}"
    participant["participant_pseudo_id"] = subject
    participant["ages"] = list(set(participant["ages"]))
    participant.update(
        fileset.find_values(
            ["Modality", "BodyPartExamined", "PatientSex"],
            fileset.find(PatientID=subject),
            load=True,
        )
    )
    participant["sex"] = list(set(participant.pop("PatientSex")))[0]
    if len(participant["BodyPartExamined"]) == 0:
        participant["BodyPartExamined"] = [bodypart]
    participant["participant_birthday"] = participant_birthday
    participant["modalities"] = participant.pop("Modality")
    participant["body_parts_examined"] = participant.pop("BodyPartExamined")
    return participant


def save_session_tsv(sessions: List[Dict[str, str]], mids_path: Path, subject: str):
    """
    Save the sessions for a given subject to a TSV file in the MIDS directory.

    :param sessions: The list of sessions to save.
    :type sessions: list[dict]
    :param mids_path: The path to the MIDS directory.
    :type mids_path: pathlib.Path
    :param subject: The ID of the subject for which to save the sessions.
    :type subject: str
    """

    session_tsv = mids_path.joinpath(f"sub-{subject}", f"sub-{subject}_sessions.tsv")
    df = pd.DataFrame(sessions)[session_header]
    df = df.sort_values("acq_time", ascending=False)  # type: ignore
    session_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(session_tsv, sep="\t", index=False)


def save_participant_tsv(
    participants: List[Dict[str, Union[str, list]]], mids_path: Path
):
    """
    Save the participants to a TSV file in the MIDS directory.

    :param participants: The list of participants to save.
    :type participants: List[Dict]
    :param mids_path: The path to the MIDS directory.
    :type mids_path: Path
    """

    participant_tsv = mids_path.joinpath("participants.tsv")
    df = pd.DataFrame(participants)[participants_header]
    df = df.sort_values("participant_id", ascending=False)  # type: ignore
    participant_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(participant_tsv, sep="\t", index=False)


def save_scans_tsv(
    scans: List[Dict[str, str]], mids_path: Path, subject: str, session: str
):
    """
    Save the scans for a given subject and session to a TSV file in the MIDS directory.

    :param scans: The list of scans to save.
    :type scans: List[Dict]
    :param mids_path: The path to the MIDS directory.
    :type mids_path: Path
    :param subject: The ID of the subject for which to save the scans.
    :type subject: str
    :param session: The ID of the session for which to save the scans.
    :type session: str
    """

    scan_tsv = mids_path.joinpath(
        f"sub-{subject}",
        f"ses-{session}",
        f"sub-{subject}_ses-{session}_scans.tsv",
    )
    df = pd.DataFrame(scans)
    df = df.sort_values("scan_file", ascending=False)
    scan_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(scan_tsv, sep="\t", index=False)
