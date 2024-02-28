
from abc import ABC, abstractmethod


class Procedures(ABC):
    def __init__(self, mids_path, bodypart):
        
        self.mids_path = mids_path
        self.bodypart = bodypart
        

    @abstractmethod
    def control_session_image(self):
        pass

    @abstractmethod
    def get_name(self):
        pass