from datetime import datetime
import pandas as pd

participants_header = [
    "participant_id",  # This is the participant_id from the BIDS/MIDS standard (sub-<participant_id>)
    "participant_pseudo_id",  # This is the participant_pseudo_id from the PatientID (participant_id)
    "gender",  # This is the gender of the participant
    "patient_birthday",  # This is the patient's birthday
    "age",  # this is the list of ages of the participant in the sessions
    "modalities",  # This is the list of modalities used in the sessions
    "body_part_examined",  # This is the list of body parts examined in the sessions
    
]

session_header = [
    "session_id",  # This is the session_id from the BIDS/MIDS standard (ses-<session_id>)
    "session_pseudo_id",  # This is the session_pseudo_id from the PatientID (session_id)
    "session_date_time",  # This is the acquisition date time of the session
    "age",  # this is the age of the participant in the session
]

def get_session_row(fileset, subject, session):
    session_row = fileset.find_values(
        ["StudyDate", "StudyTime", "PatientBirthDate"],
        fileset.find(PatientID=subject, StudyID=session),
        load=True,
    )
    session_row["session_id"] = f"sub-{session}"
    session_row["session_pseudo_id"] = session
    date_time = session_row["StudyDate"][0] + session_row["StudyTime"][0]
    if "." not in date_time:
        date_time += ".000000"
    session_row["session_date_time"] = [date_time]
    session_row.pop("StudyDate")
    session_row.pop("StudyTime")

    print(session_row["session_date_time"])
    session_row["session_date_time"] = [
        datetime.strptime(s, "%Y%m%d%H%M%S.%f")
        for s in session_row["session_date_time"]
    ][0]
    session_row["PatientBirthDate"] = datetime.strptime(
        session_row["PatientBirthDate"][0], "%Y%m%d"
    )
    patient_age = (
        session_row["session_date_time"] - session_row["PatientBirthDate"]
    ).days // 365.25
    session_row["PatientBirthDate"] = session_row["PatientBirthDate"].strftime(
        "%Y-%m-%d"
    )
    session_row["session_date_time"] = session_row[
        "session_date_time"
    ].isoformat()
    session_row["age"] = patient_age
    
    return session_row

def get_participant_row(participant, fileset, subject, bodypart, patient_birthday):
    participant["participant_id"] = f"sub-{subject}"
    participant["participant_pseudo_id"] = subject
    participant["age"] = list(set(participant["age"]))
    participant.update(
        fileset.find_values(
            ["Modality", "BodyPartExamined", "PatientSex"],
            fileset.find(PatientID=subject),
            load=True,
        )
    )
    participant["gender"] = list(set(participant.pop("PatientSex")))[0]
    if len(participant["BodyPartExamined"]) == 0:
        participant["BodyPartExamined"] = [bodypart]
    participant["patient_birthday"] = patient_birthday
    participant["modalities"] = participant.pop("Modality")
    participant["body_part_examined"] = participant.pop("BodyPartExamined")
    return participant


def save_session_tsv(sessions, mids_path, subject):
    session_tsv = mids_path.joinpath(f"sub-{subject}", f"sub-{subject}_sessions.tsv")
    df = pd.DataFrame(sessions)[session_header]
    df = df.sort_values('session_date_time', ascending=False)
    session_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(session_tsv, sep="\t", index=False)


def save_participant_tsv(participants, mids_path):
    participant_tsv = mids_path.joinpath("participants.tsv")
    df = pd.DataFrame(participants)[participants_header]
    df = df.sort_values('participant_id', ascending=False)
    participant_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(participant_tsv, sep="\t", index=False)

def save_scans_tsv(scans, mids_path, subject, session):
    scan_tsv = mids_path.joinpath(
        f"sub-{subject}",
        f"ses-{session}",
        f"sub-{subject}_ses-{session}_scans.tsv",
    )
    df = pd.DataFrame(scans)
    df = df.sort_values('scan_file', ascending=False)
    scan_tsv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(scan_tsv, sep="\t", index=False)