import logging
from pathlib import Path
from typing import Tuple

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

        pass
