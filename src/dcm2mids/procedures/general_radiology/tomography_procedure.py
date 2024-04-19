import logging
from pathlib import Path
from typing import List, Tuple

from pydicom import Dataset
from pydicom.fileset import FileInstance

from ..procedures import Procedures

logger = logging.getLogger("dcm2mids").getChild("tomography_procedure")


class TomographyProcedures(Procedures):
    """Conversion logic for General Radiologic Imaging procedures."""

    def __init__(
        self,
        mids_path: Path,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        super().__init__(mids_path, bodypart, use_bodypart, use_viewposition)
        self.scans_header = [
                'Filename',
                'BodyPart',
                'ViewPosition',
                'SeriesNumber',
                'AccessionNumber',
                'Manufacturer',
                'ManufacturerModelName',
                'Modality',
                'Columns',
                'Rows',
                'PhotometricInterpretation',
                'Laterality',
                'KVP',
                'Exposure',
                'ExposureTime',
                'XRayTubeCurrent'
            ]

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
        if instance.Modality in ["CR", "DX"]:
            self.scans_header = [
                "Filename",
                "BodyPart",
                "ViewPosition",
                "SeriesNumber",
                "AccessionNumber",
                "Manufacturer",
                "ManufacturerModelName",
                "Modality",
                "Columns",
                "Rows",
                "PhotometricInterpretation",
                "Laterality",
                "KVP",
                "Exposure",
                "ExposureTime",
                "XRayTubeCurrent",
            ]
            return (
                instance.Modality.lower(),
                (
                    (instance.Modality.lower(),)
                    if self.bodypart in ["head", "brain", "skull"]
                    else (
                        "mim-rx",
                        instance.Modality.lower(),
                    )
                ),
                ".png",
            )

        if instance.Modality in ["CT"]:
            self.scans_header = [
                "ScanFile",
                "BodyPart",
                "ViewPosition",
                "SeriesNumber",
                "AccessionNumber",
                "Manufacturer",
                "ManufacturerModelName",
                "Modality",
                "Columns",
                "Rows",
                "PhotometricInterpretation",
                "Laterality",
                "KVP",
                "Exposure" "ExposureTime",
                "XRayTubeCurrent",
                "DataCollectionDiameter",
                "ReconstructionDiameter",
                "SliceThickness",
                "ConvolutionKernel",
                "ReconstructionAlgorithm",
                "DistanceSourceToDetector" "Image Orientation",
                "SmallestImagePixelValue",
                "LargestImagePixelValue",
                "WindowCenter",
                "WindowWidth",
            ]
            return (
                instance.Modality.lower(),
                (
                    (instance.Modality.lower(),)
                    if self.bodypart in ["head", "brain", "skull"]
                    else (
                        "mim-rx",
                        instance.Modality.lower(),
                    )
                ),
                ".nii.gz",
            )
        return ("", tuple(), "")

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
        vp = (
            f"vp-{convert_orientation(dataset.data_element('ImageOrientationPatient'))[0]}"
            if dataset.data_element("ImageOrientationPatient")
            else ""
        )
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
        if "".join(file_path_mids.suffixes) == ".nii.gz":
            pass
        else:
            file_path_mids.parent.mkdir(parents=True, exist_ok=True)
            image = sitk.ReadImage(instance.path)
            sitk.WriteImage(image, file_path_mids)


def run(self, instance_list: List[Tuple[int, FileInstance]]):
    """
    Runs the image conversion pipeline on a list of instances.

    :param instance_list: A list of tuples containing the instance number and the DICOM instance.
    :type instance_list: list[uuple[int, pydicom.fileset.FileInstance]]
    """

    self.use_chunk = len(instance_list) > 1
    list_scan_metadata = []
    for _, instance in sorted(instance_list, key=lambda x: x[0]):
        print(instance)
        dataset = instance.load()
        modality, mim, ext = self.classify_image_type(instance)
        file_path_mids, session_absolute_path_mids = self.get_name(
            dataset, modality, mim
        )

        self.convert_to_image(instance, file_path_mids.with_suffix(ext))
        self.convert_to_jsonfile(dataset, file_path_mids.with_suffix(".json"))
        file_path_relative_mids = file_path_mids.relative_to(
            session_absolute_path_mids
        ).with_suffix(".png")
        list_scan_metadata.append(
            self.get_scan_metadata(dataset, file_path_relative_mids)
        )
    return list_scan_metadata


def convert_orientation(orientation):
    mapping = {
        "1\\0\\0\\0\\1\\0": ("Sag", "LAS"),  # Left-Anterior-Superior
        "0\\1\\0\\0\\0\\-1": ("Cor", "RAS"),  # Right-Anterior-Superior
        "1\\0\\0\\0\\0\\-1": ("Ax", "PAS"),  # Posterior-Anterior-Superior
        # Add more mappings as needed
    }
    return mapping.get(orientation, ("Unknown", "Unknown"))
