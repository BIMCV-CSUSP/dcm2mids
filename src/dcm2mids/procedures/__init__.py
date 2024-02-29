
from abc import ABC, abstractmethod

from dcm2mids.procedures.dictify import dictify
import json

class Procedures(ABC):
    def __init__(self, mids_path, bodypart, use_bodypart, use_viewposition):
        
        self.mids_path = mids_path
        self.bodypart = bodypart
        self.use_bodypart = use_bodypart
        self.use_viewposition = use_viewposition
        self.chunk : bool
        

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