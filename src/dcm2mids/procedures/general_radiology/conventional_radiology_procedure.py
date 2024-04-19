import logging
from pathlib import Path
from typing import Tuple, List
from pydicom import Dataset

from pydicom.fileset import FileInstance

from ..procedures import Procedures

logger = logging.getLogger("dcm2mids").getChild("conventional_radiology_procedure")

bids_bp = ["head", "brain", "skull"]

class ConventionalRadiologyProcedures(Procedures):
    """Conversion logic for General Radiologic Imaging procedures."""

    def __init__(
        self,
        mids_path: Path,
        modality: str,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        super().__init__(mids_path, modality, bodypart, use_bodypart, use_viewposition)
        self.scans_header = [
                "Filename",
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
        self.modality = modality.lower()
        self.bodypart = bodypart
        self.use_bodypart = use_bodypart
        self.use_viewposition = use_viewposition
        self.mim = "mim-rx" if self.bodypart in bids_bp else ""
        self.bids_folder = modality.lower()
        self.extension = ".png"

    def get_name(self, dataset: Dataset) -> Tuple[Path, Path]:
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
        if self.use_viewposition:
            
            vp = (
                f"vp-{convert_orientation_2D(dataset.data_element('ImageOrientationPatient'))}"
                if dataset.data_element("ImageOrientationPatient")
                else ""
            )
        else:
            vp = ""
        
        chunk = (
            f"chunk-{dataset.InstanceNumber}"
            if dataset.data_element("InstanceNumber") and self.use_chunk
            else ""
        )
        mod = self.modality
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
            logger.info(
                "Successfully processed instance %s",
                instance.path,
            )
            logger.info(
                "Saved to %s",
                file_path_relative_mids.stem,
            )
        return list_scan_metadata

def convert_orientation_2D(orientation):
    mapping = {
        "1\\0\\0\\0\\1\\0": "AP",  # Anterior-Posterior
        "0\\1\\0\\0\\0\\-1": "PA",  # Posterior-Anterior
        "1\\0\\0\\0\\0\\-1": "LAT",  # Lateral
        "1\\0\\0\\0\\1\\1": "OB",  # Oblique
        # Add more mappings as needed
    }
    return mapping.get(orientation, "Unknown")

def convert_orientation(orientation):
    mapping = {
        "1\\0\\0\\0\\1\\0": ("Sag", "LAS"),  # Left-Anterior-Superior
        "0\\1\\0\\0\\0\\-1": ("Cor", "RAS"),  # Right-Anterior-Superior
        "1\\0\\0\\0\\0\\-1": ("Ax", "PAS"),  # Posterior-Anterior-Superior
        # Add more mappings as needed
    }
    return mapping.get(orientation, ("Unknown", "Unknown"))
def convert_orientation_full(orientation):
    mapping = {
        "1\\0\\0\\0\\1\\0": ("Sag", "LAS"),  # Left-Anterior-Superior
        "0\\1\\0\\0\\0\\-1": ("Cor", "RAS"),  # Right-Anterior-Superior
        "1\\0\\0\\0\\0\\-1": ("Ax", "PAS"),  # Posterior-Anterior-Superior
        "0\\0\\-1\\1\\0\\0": ("Ax", "RSP"),  # Right-Superior-Posterior
        "0\\0\\1\\1\\0\\0": ("Ax", "RIP"),  # Right-Inferior-Posterior
        "0\\0\\1\\0\\1\\0": ("Cor", "ASP"),  # Anterior-Superior-Posterior
        "0\\0\\-1\\0\\1\\0": ("Cor", "AIP"),  # Anterior-Inferior-Posterior
        "1\\0\\0\\0\\0\\1": ("Sag", "LAP"),  # Left-Anterior-Posterior
        "1\\0\\0\\0\\0\\-1": ("Sag", "LIP"),  # Left-Inferior-Posterior
        # Add more mappings as needed
    }
    return mapping.get(orientation, ("Unknown", "Unknown"))