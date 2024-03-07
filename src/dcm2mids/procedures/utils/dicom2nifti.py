from pathlib import Path
from typing import Union


def dicom2nifti(
    json_files: Union[str, Path, list], path_to_save: Union[str, Path]
) -> Path:
    folder_nifti = folder_json.parent.parent.joinpath("LOCAL_NIFTI", "files")
    folder_nifti.mkdir(parents=True, exist_ok=True)
    d2n.convert_directory(str(folder_json), str(folder_nifti))
    shutil.copy2(str(folder_json.joinpath("bids.json")), str(folder_nifti.parent))
    if folder_json.joinpath("note.txt").exists():
        shutil.copy2(str(folder_json.joinpath("note.txt")), str(folder_nifti.parent))
    return folder_nifti.parent
