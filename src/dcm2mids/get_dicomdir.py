from pathlib import Path
from typing import Union

from pydicom import dcmread
from pydicom.fileset import FileSet
from tqdm import tqdm


def get_dicomdir(input_dir: Union[Path, str]) -> FileSet:
    """
    Get the DICOM structure from the input directory.

    :param input_dir: The input directory as a Path object or a string.
    :type input_dir: Union[pathlib.Path, str]
    :raises TypeError: If the input_dir is not a Path object or a string.
    :raises FileNotFoundError: If the input_dir does not exist or is not a directory.
    :return: A FileSet object containing the DICOM files from the input directory.
    :rtype: pydicom.fileset.FileSet
    """
    if not isinstance(input_dir, Path):
        try:
            input_dir = Path(input_dir)
        except TypeError:
            raise TypeError(
                f"Input dir must be a Path object or a string. Got {type(input_dir)} instead."
            )
    if not input_dir.exists():
        raise FileNotFoundError(f"{input_dir} does not exist.")
    dicomdir = input_dir / "DICOMDIR"
    if (
        dicomdir.exists()
    ):  # If DICOMDIR exists, we will use it to get the DICOM structure.
        ds = dcmread(dicomdir)
        fs = FileSet(ds)
    elif (
        input_dir.is_dir()
    ):  # If DICOMDIR does not exist, we will search for DICOM files in the input dir.
        fs = FileSet()
        for filename in tqdm(input_dir.rglob("*.dcm")):
            ds = dcmread(filename)
            if not ds.StudyID:
                ds.StudyID = ds.AccessionNumber
            fs.add(ds)
    else:
        raise NotADirectoryError(f"{input_dir} is not a directory.")
    if len(fs) == 0:
        raise RuntimeError(f"No DICOM files found in {input_dir}.")
    return fs
