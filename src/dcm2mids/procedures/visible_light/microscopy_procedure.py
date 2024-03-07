import logging
from pathlib import Path
from shutil import copyfile
from typing import Dict, List, Tuple

from pydicom import Dataset
from pydicom.fileset import FileInstance

from ..procedures import Procedures
from ..utils import *

logger = logging.getLogger("dcm2mids").getChild("microscopy_procedure")


class MicroscopyProcedures(Procedures):
    """Conversion logic for Microscopy procedures."""

    def __init__(
        self,
        mids_path: Path,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        super().__init__(mids_path, bodypart, use_bodypart, use_viewposition)
        self.extension = ".dcm"
        self.modality = "BF"
        self.mim = ("micr",)
        self.scans_header = [
            "ScanFile",
            "BodyPart",
            "SeriesNumber",
            "AccessionNumber",
            "Manufacturer",
            "ManufacturerModelName",
            "Modality",
            "Columns",
            "Rows",
            "PhotometricInterpretation",
            "ImagedVolumeHeight",
            "ImagedVolumeWeight",
        ]

    def get_name(
        self, dataset: Dataset, modality: str, mim: Tuple[str, ...]
    ) -> Tuple[Path, Path]:
        """
        Generates a name for the image based on its metadata.

        :param dataset: The dataset containing the image metadata.
        :type dataset: pydicom.Dataset
        :param modality: The modality of the image.
        :type modality: str
        :param mim: A tuple of labels to be included in the filepath.
        :type mim: tuple[str, ...]
        :returns: A Path object representing the generated name.
        :rtype: pathlib.Path
        """

        sub = f"sub-{dataset.PatientID}"
        ses = f"ses-{dataset.StudyID}"
        run = (
            f"run-{dataset.SeriesNumber}"
            if dataset.data_element("SeriesNumber")
            else ""
        )
        if self.use_bodypart:
            bp = (
                f"bp-{dataset.BodyPartExamined}"
                if "BodyPartExamined" in dataset
                else f"bp-{self.bodypart}"
            )
        else:
            bp = ""
        lat = f"lat-{dataset.Laterality}" if dataset.data_element("Laterality") else ""
        chunk = (
            f"chunk-{dataset.InstanceNumber}"
            if dataset.data_element("InstanceNumber") and self.use_chunk
            else ""
        )
        mod = modality
        filename = "_".join(
            [part for part in [sub, ses, run, bp, lat, chunk, mod] if part != ""]
        )
        return (
            self.mids_path.joinpath(sub, ses, *mim, filename),
            self.mids_path.joinpath(sub, ses),
        )

    def convert_to_image(self, instance: FileInstance, file_path_mids: Path):
        """
        Converts a DICOM to an image.

        :param instance: The DICOM image instance.
        :type instance: pydicom.fileset.FileInstance
        :param file_path_mids: The path where the converted image will be saved.
        :type file_path_mids: pathlib.Path
        """
        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        copyfile(instance.path, file_path_mids)

    def get_scan_metadata(
        self, dataset: Dataset, file_path_mids: Path
    ) -> Dict[str, str]:
        """
        Extracts metadata from a scan and returns it in a dictionary.

        :param dataset: The dataset to extract metadata from.
        :type dataset: pydicom.Dataset
        :param file_path_mids: The path where to save the image file.
        :type file_path_mids: pathlib.Path
        :return: A dictionary containing the extracted metadata.
        :rtype: dict
        """

        bodypart = (
            dataset.BodyPartExamined if "BodyPartExamined" in dataset else self.bodypart
        )
        tag_values = [
            (dataset[i].value if i in dataset else "n/a") for i in self.scans_header[2:]
        ]
        header_values = [
            str(file_path_mids.with_suffix(self.extension)),
            bodypart,
            *tag_values,
        ]
        return {
            pascal_to_snake_case(key): value
            for key, value in zip(
                self.scans_header,
                header_values,
            )
        }

    def run(self, instance_list: List[FileInstance]) -> List[Dict[str, str]]:
        """
        Runs the image conversion pipeline on a list of instances.

        :param instance_list: A list of tuples containing the instance number and the DICOM instance.
        :type instance_list: list[uuple[int, pydicom.fileset.FileInstance]]
        """

        self.use_chunk = len(instance_list) > 1
        list_scan_metadata = []
        for instance in instance_list:
            logger.debug("Processing instance %s", instance.path)
            dataset = instance.load()
            file_path_mids, session_absolute_path_mids = self.get_name(
                dataset, self.modality, self.mim
            )
            self.convert_to_image(instance, file_path_mids.with_suffix(self.extension))
            self.convert_to_jsonfile(dataset, file_path_mids.with_suffix(".json"))
            file_path_relative_mids = file_path_mids.relative_to(
                session_absolute_path_mids
            ).with_suffix(self.extension)
            list_scan_metadata.append(
                self.get_scan_metadata(dataset, file_path_relative_mids)
            )
            logger.info(
                "Successfully processed instance %s",
                instance.path,
            )
            logger.info(
                "Saved to %s",
                file_path_relative_mids.stem,
            )
        return list_scan_metadata
