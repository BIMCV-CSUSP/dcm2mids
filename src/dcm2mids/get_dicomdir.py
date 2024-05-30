import logging
from pathlib import Path
from typing import Union
from datetime import datetime

from pydicom import dcmread
from pydicom.fileset import FileSet

logger = logging.getLogger(__name__)


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
        input_dir = Path(input_dir)
    if not input_dir.exists():
        logger.error("%s does not exist.", input_dir)
        raise FileNotFoundError(f"{input_dir} does not exist.")
    dicomdir = input_dir / "DICOMDIR"
    if (
        dicomdir.exists()
    ):  # If DICOMDIR exists, we will use it to get the DICOM structure.
        logger.info("DICOMDIR file found")
        ds = dcmread(dicomdir)
        fs = FileSet(ds)
    elif (
        input_dir.is_dir()
    ):  # If DICOMDIR does not exist, we will search for DICOM files in the input dir.
        fs = FileSet()
        logger.info(
            "DICOMDIR file not found. Listing all `.dcm` files on the directory."
        )
        suffix = "*.[dD][cC][mM]"
        for filename in input_dir.rglob(suffix):
            ds = dcmread(filename)
            if not ds.StudyID:
                logger.warning(
                    "`StudyID` tag not found for file %s. `AccessionNumber` will be used instead.",
                    filename,
                )
                ds.StudyID = ds.AccessionNumber
            if not ds.StudyTime:
                logger.warning(
                    "`StudyTime` tag not found for file %s. Time part of `AdquisitionDateTime` will be used instead.",
                    filename,
                )
                ds.StudyTime = datetime.strptime(
                    ds.AcquisitionDateTime[:14], "%Y%m%d%H%M%S"
                ).strftime("%H%M%S")
            if not ds.SeriesNumber:
                logger.warning(
                    "`SeriesNumber` tag not found for file %s. Time part of `InstanceNumber` will be used instead.",
                    filename,
                )
                ds.SeriesNumber = ds.InstanceNumber
            # try:

            fs.add(ds)
            # except ValueError as e:
            #     print(e)
            #     continue

    else:
        logger.error("%s is not a directory.", input_dir)
        raise NotADirectoryError(f"{input_dir} is not a directory.")
    if len(fs) == 0:
        logger.error("No DICOMDIR/DICOM files found in %s.", input_dir)
        raise RuntimeError(f"No DICOM files found in {input_dir}.")
    logger.info("FileSet has %d elements", len(fs))
    return fs
