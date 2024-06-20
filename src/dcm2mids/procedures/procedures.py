import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from pydicom import Dataset

from .dictify import dictify

logger = logging.getLogger("dcm2mids").getChild("procedures")
class Procedures(ABC):
    def __init__(
        self,
        mids_path: Path,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        self.mids_path = mids_path
        self.bodypart = bodypart
        self.use_bodypart = use_bodypart
        self.use_viewposition = use_viewposition
        self.use_chunk: bool

    # @abstractmethod
    # def control_session_image(self):
    #     pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def run(self):
        pass
    
    @staticmethod
    def convert_to_jsonfile(dataset: Dataset, file_path_mids: Path):
        """
        Convert a dataset to a JSON file.

        :param dataset: The dataset to be converted.
        :type dataset: pydicom.Dataset
        :param file_path_mids: The path to the JSON file where the data will be saved.
        :type file_path_mids: pathlib.Path
        :return: None
        :rtype: None
        """
        json_dict = dictify(dataset)
        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path_mids, "w") as f:
            json.dump(json_dict, f, indent=4)

    
