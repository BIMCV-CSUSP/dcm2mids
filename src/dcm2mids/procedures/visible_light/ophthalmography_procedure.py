import logging
import re
from pathlib import Path
from typing import List, Tuple

import SimpleITK as sitk
from pydicom import Dataset
from pydicom.fileset import FileInstance

from ..procedures import Procedures

logger = logging.getLogger("dcm2mids").getChild("ophthalmography_procedure")


class OphthalmographyProcedures(Procedures):
    """Conversion logic for Visible Light Imaging procedures."""

    def __init__(
        self,
        mids_path: Path,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        super().__init__(mids_path, bodypart, use_bodypart, use_viewposition)

    def classify_image_type(
        self, instance: FileInstance
    ) -> Tuple[str, Tuple[str, ...]]:
        """
        Classifies an image based on its modality.

        :param instance: The instance to be classified.
        :type instance: pydicom.fileset.FileInstance
        :returns: A tuple containing the image type and a tuple of labels for that type.
        :rtype: tuple[str, tuple[str, ...]]
        """

        logger.debug("Processing instance %s", instance.path)
        logger.debug("Instance modality: %s", instance.Modality)
        if instance.Modality in ["OP", "SC", "XC", "OT"]:
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
                "Laterality",
            ]
            return ("op", ("mim-light", "op"))
        if instance.Modality in ["BF", "SM"]:
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
                "NumberOfFrames"
            ]
            return ("BF", ("micr",))
        return ("", tuple())

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
        vp = ""  # f"vp-{dataset.data_element('ViewPosition')}" if dataset.data_element("ViewPosition") else ""
        chunk = (
            f"chunk-{dataset.InstanceNumber}"
            if dataset.data_element("InstanceNumber") and self.use_chunk
            else ""
        )
        mod = modality
        filename = "_".join(
            [part for part in [sub, ses, run, bp, lat, vp, chunk, mod] if part != ""]
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
        image = sitk.ReadImage(instance.path)
        sitk.WriteImage(image, file_path_mids)

    def get_scan_metadata(self, dataset, file_path_mids):
        subs = lambda s: re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
        return {
            subs(key): value
            for key, value in zip(
                self.scans_header,
                [
                    str(file_path_mids.with_suffix(".png")),
                    (
                        dataset.BodyPartExamined
                        if "BodyPartExamined" in dataset
                        else self.bodypart
                    ),
                    *[
                        (dataset[i].value if i in dataset else "n/a")
                        for i in self.scans_header[2:]
                    ],
                ],
            )
        }

    def run(self, instance_list: List[FileInstance]):
        """
        Runs the image conversion pipeline on a list of instances.

        :param instance_list: A list of tuples containing the instance number and the DICOM instance.
        :type instance_list: list[uuple[int, pydicom.fileset.FileInstance]]
        """

        self.use_chunk = len(instance_list) > 1
        list_scan_metadata = []
        for instance in instance_list:
            dataset = instance.load()
            modality, mim = self.classify_image_type(instance)
            file_path_mids, session_absolute_path_mids = self.get_name(
                dataset, modality, mim
            )
            self.convert_to_image(instance, file_path_mids.with_suffix(".png"))
            self.convert_to_jsonfile(dataset, file_path_mids.with_suffix(".json"))
            file_path_relative_mids = file_path_mids.relative_to(
                session_absolute_path_mids
            ).with_suffix(".png")
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
