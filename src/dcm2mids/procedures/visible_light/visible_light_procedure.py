from dcm2mids.procedures import Procedures



# TODO: generate medata from dicom files
# TODO: classify image type
# TODO: convert to nifti
# TODO: rename nifti file to BIDS/MIDS standard
#
class ProceduresVisibleLight(Procedures):
    def __init__(self, mids_path, bodypart):
        super().__init__(mids_path, bodypart)
        self.reset()

    def reset(self):
        self.dicom_dict = {}

    # def generate_metadata(self, instance: list):
    #     """Generate metadata from dicom files."""
        
    #     dictify(instance.load())
    #     if len(dicom_jsons) == 1:
    #         return dicom_jsons[0]

    #     else:
    #         return self.merge_dicom_jsons(dicom_jsons)

    # def merge_dicom_jsons(self, dicom_jsons: list):
    #     for item in zip(*[items for items in [json.items() for json in dicom_jsons]]):
    #         values = [i[1] for i in item]
    #         if len(set(values)) == 1:
    #             self.dicom_dict[item[0][0]] = item[0][1]
    #         else:
    #             self.dicom_dict[item[0][0]] = values
    #         print(self.dicom_dict[item[0][0]])

    def classify_image_type(self, instance):
        print(instance)
        if instance.Modality in ["OP", "SC", "XC", "OT"]:
            return ("op", ("mim-light", "op"))
        if instance.Modality in ["BF", "SM"]:
            return ("BF", ("micr",))
        

    
    def get_name(self, instance, modality, mim):
        
        
        sub = f"sub-{instance.PatientID}" 
        ses = f"ses-{instance.StudyID}" 
        run = f"run-{instance.data_element('SeriesNumber')}" if instance.data_element("SeriesNumber") else ""
        bp = f"bp-{instance.data_element('BodyPartExamined')}" if instance.data_element("BodyPartExamined") else f"bp-{self.bodypart}"
        lat = f"lat-{instance.data_element('Laterality')}" if instance.data_element("Laterality") else ""
        vp = "" # f"vp-{instance.data_element('ViewPosition')}" if instance.data_element("ViewPosition") else ""
        chunk = f"chunk-{instance.data_element('InstanceNumber')}" if instance.data_element("InstanceNumber") and len(instance_list)>1  else ""
        mod = modality
        return(
            self.mids_path.joinpath(sub, ses, *mim, "_".join([part for part in [sub, ses, run, bp, lat, vp, chunk, mod] if part != '']))
        )
        
    def convert_to_image(self, image_array, file_path_mids):
        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        try:
            sitk.WriteImage(image_array, file_path_mids)
        except RuntimeError:
            print(f"error to convert: {name_list}")
        
    
    def convert_to_jsonfile(self, dataset, file_path_mids):
        json_dict = dictify(dataset)
        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path_mids, "w") as f:
            json.dump(json_dict, f, indent=4)
        


    def run(self, instance_list: list):
        print(instance_list[0])
        for _, instance in sorted(instance_list, key=lambda x: x[0]):
            print(instance)
            dataset=instance.load()
            
            modality, mim = self.classify_image_type(instance)
            file_path_mids = self.get_name(instance, modality, mim)
            print(instance.path, file_path_mids)
            self.convert_to_image(dataset.pixel_array, file_path_mids.with_suffix(".nii.gz"))
            self.convert_to_jsonfile(dataset, file_path_mids.with_suffix(".json"))
