import re
from dcm2mids.procedures import Procedures
import SimpleITK as sitk


# TODO: generate medata from dicom files
# TODO: classify image type
# TODO: convert to nifti
# TODO: rename nifti file to BIDS/MIDS standard
#
class ProceduresVisibleLight(Procedures):
    def __init__(self, mids_path, bodypart, use_bodypart, use_viewposition):
        super().__init__(mids_path, bodypart, use_bodypart, use_viewposition)
    

    def classify_image_type(self, instance):
        print(instance)
        if instance.Modality in ["OP", "SC", "XC", "OT"]:
            self.scans_header = [
            'ScanFile',
            'BodyPart',
            'SeriesNumber',
            'AccessionNumber',
            'Manufacturer',
            'ManufacturerModelName',
            'Modality',
            'Columns',
            'Rows',
            'PhotometricInterpretation',
            'Laterality',
            ]
            return ("op", ("mim-light", "op"))
        if instance.Modality in ["BF", "SM"]:
            self.scans_header = [
                'ScanFile',
                'BodyPart',
                'SeriesNumber',
                'AccessionNumber',
                'Manufacturer',
                'ManufacturerModelName',
                'Modality',
                'Columns',
                'Rows',
                'PhotometricInterpretation',
                'ImagedVolumeHeight',
                'ImagedVolumeWeight'
            ]
            return ("BF", ("micr",))
        

    
    def get_name(self, dataset, modality, mim):
        
        
        sub = f"sub-{dataset.PatientID}" 
        ses = f"ses-{dataset.StudyID}" 
        run = f"run-{dataset.SeriesNumber}" if dataset.data_element("SeriesNumber") else ""
        if self.use_bodypart:
            bp = f"bp-{dataset.BodyPartExamined}" if "BodyPartExamined" in dataset else f"bp-{self.bodypart}"
        else:
            bp = ""
        lat = f"lat-{dataset.Laterality}" if dataset.data_element("Laterality") else ""
        vp = "" # f"vp-{dataset.data_element('ViewPosition')}" if dataset.data_element("ViewPosition") else ""
        chunk = f"chunk-{dataset.InstanceNumber}" if dataset.data_element("InstanceNumber") and self.use_chunk  else ""
        mod = modality
        return(
            self.mids_path.joinpath(sub, ses, *mim, "_".join([part for part in [sub, ses, run, bp, lat, vp, chunk, mod] if part != ''])),
            self.mids_path.joinpath(sub,ses)
        )
        
    def convert_to_image(self, instance, file_path_mids):
        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        image = sitk.ReadImage(instance.path)
        sitk.WriteImage(image, file_path_mids)
        
    def get_scan_metadata(self, dataset, file_path_mids):
        subs = lambda s: re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
        return {
            subs(key):value
            for key, value in zip(
                self.scans_header,
                [
                    str(file_path_mids.with_suffix(".png")),
                    dataset.BodyPartExamined if "BodyPartExamined" in dataset else self.bodypart, 
                    *[(dataset[i].value if i in dataset else "n/a") for i in self.scans_header[2:]],
                ]
            )
        }
        

    def run(self, instance_list: list):
        self.use_chunk = len(instance_list) > 1
        list_scan_metadata = []
        for _, instance in sorted(instance_list, key=lambda x: x[0]):
            print(instance)
            dataset=instance.load()
            modality, mim = self.classify_image_type(instance)
            file_path_mids, session_absolute_path_mids = self.get_name(dataset, modality, mim)
            self.convert_to_image(instance, file_path_mids.with_suffix(".png"))
            self.convert_to_jsonfile(dataset, file_path_mids.with_suffix(".json"))
            file_path_relative_mids = file_path_mids.relative_to(session_absolute_path_mids).with_suffix(".png")
            list_scan_metadata.append(self.get_scan_metadata(dataset, file_path_relative_mids))
        return list_scan_metadata
