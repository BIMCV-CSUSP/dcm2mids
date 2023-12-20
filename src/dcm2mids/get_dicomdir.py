from pathlib import Path
from typing import Union

from pydicom import dcmread
from pydicom.fileset import FileSet


def get_dicomdir(input_folder: Union[Path, str]) -> FileSet:
    """
    Get the DICOMDIR file from the input folder.
    """
    if not isinstance(input_folder, Path):
        try:
            input_folder = Path(input_folder)
        except TypeError:
            raise TypeError(
                f"Input folder must be a Path object or a string. Got {type(input_folder)} instead."
            )
    if not input_folder.exists():
        raise FileNotFoundError(f"Input folder {input_folder} does not exist.")
    dicomdir = input_folder / "DICOMDIR"
    if dicomdir.exists():  # If DICOMDIR exists, we will use it to get the DICOM str.
        ds = dcmread(dicomdir)
        fs = FileSet(ds)
    else:  # If DICOMDIR does not exist, we will search for DICOM files in the input folder.
        fs = FileSet()
        for file in dicomdir.glob("*.dcm"):
            fs.add(file)
    return fs
