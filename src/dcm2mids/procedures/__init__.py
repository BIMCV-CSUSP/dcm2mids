import json
from abc import ABC, abstractmethod
from pathlib import Path

from .dictify import dictify


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

    def convert_to_jsonfile(self, dataset, file_path_mids):
        json_dict = dictify(dataset)
        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path_mids, "w") as f:
            json.dump(json_dict, f, indent=4)

    @abstractmethod
    def run(self):
        pass
