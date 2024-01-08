import dicom2nifti as d2n
from abc import ABC, abstractmethod


class Procedures(ABC):
    def __int__(self):
        pass

    @abstractmethod
    def control_session_image(self):
        pass

    @abstractmethod
    def get_name(self):
        pass