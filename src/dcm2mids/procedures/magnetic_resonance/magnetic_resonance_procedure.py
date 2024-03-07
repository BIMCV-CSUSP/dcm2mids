import logging

from dcm2mids.procedures.dictify import dictify

from ..procedures import Procedures

logger = logging.getLogger("dcm2mids").getChild("magnetic_resonance_procedure")


class MagneticResonanceProcedures(Procedures):
    def __init__(self, mids_path, bodypart):
        super().__init__(mids_path, bodypart)
        self.reset()

    def reset(self):
        self.dicom_dict = {}

    def generate_metadata(self, instance_list: list):
        """Generate metadata from dicom files."""
        dicom_jsons = []
        ordered_instance_list = [
            instance[1] for instance in sorted(instance_list, key=lambda x: x[0])
        ]
        for instance in ordered_instance_list:
            dicom_jsons.append(dictify(instance.load()))
        for item in zip(*[items for items in [json.items() for json in dicom_jsons]]):
            values = [i[1] for i in item]
            print(values)
            if len(set(values)) == 1:
                dicom_dict[item[0][0]] = item[0][1]
            else:
                dicom_dict[item[0][0]] = values
            print(dicom_dict[item[0][0]])

    def classify_image_type(self):
        pass

    def control_session_image(self):
        pass

    def get_name(self):
        pass

    def run(self, instance_list: list):
        self.generate_metadata(instance_list)
        self.classify_image_type()
        self.control_session_image()
        self.get_name()
