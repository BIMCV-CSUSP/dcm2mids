import logging
from pathlib import Path
from typing import List, Union
from datetime import datetime

from pydicom import dcmread
from pydicom.fileset import FileSet

logger = logging.getLogger(__name__)


def get_dicomdir(input_dir: Union[Path, str], exclude_paths: List[Union[Path, str]] = None) -> FileSet:
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
    if exclude_paths is not None:
        exclude_paths = [Path(p) if not isinstance(p, Path) else p for p in exclude_paths]
    
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
            
            
            if exclude_paths and any(filename.is_relative_to(exclude_path) for exclude_path in exclude_paths): continue
            ds = dcmread(filename)
            txt_file = filename.parent / "note.txt"
            txt_content = ""
            if txt_file.exists():
                with txt_file.open('r') as file:
                    txt_content = file.read()
            if txt_content == "": txt_content = "n/a"
            
            # Reserve a private tag block
            private_creator_tag = 0x000b  # (gggg,00XX) for reserving block
            block = ds.private_block(private_creator_tag, 'Note', create=True)

            # Define the private tag (for example, in the reserved block)
            private_tag = 0x10  # (gggg,xxYY) where xxYY is within the reserved block

            # Add the private tag with VR (e.g., LO for Long String) and value
            block.add_new(private_tag, 'LO', txt_content)
            ds.add_new
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
                    "`SeriesNumber` tag not found for file %s. `InstanceNumber` will be used instead.",
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
