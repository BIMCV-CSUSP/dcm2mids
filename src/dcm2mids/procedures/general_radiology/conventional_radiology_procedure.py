import logging
from pathlib import Path
from typing import Tuple

from pydicom.fileset import FileInstance

from ..procedures import Procedures

logger = logging.getLogger("dcm2mids").getChild("conventional_radiology_procedure")

bids_bp = ["head", "brain", "skull"]

class ConventionalRadiologyProcedures(Procedures):
    """Conversion logic for General Radiologic Imaging procedures."""

    def __init__(
        self,
        mids_path: Path,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        super().__init__(mids_path, modality, bodypart, use_bodypart, use_viewposition)
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
            self.modality = pet if modality == "PT" else "ct"
            self.bodypart = bodypart
            self.use_bodypart = use_bodypart
            self.use_viewposition = use_viewposition
            self.pathfile = mids_path.joinpath(self.modality if self.bodypart in bids_bp else self.bodypart)

        pass
