from pathlib import Path
from typing import List, Tuple

import SimpleITK as sitk
from pydicom import Dataset
from pydicom.fileset import FileInstance

from .. import Procedures


# TODO: generate medata from dicom files
# TODO: classify image type
# TODO: convert to nifti
# TODO: rename nifti file to BIDS/MIDS standard
#
class ProceduresVisibleLight(Procedures):
    """Conversion logic for Visible Light Imaging procedures."""

    def __init__(
        self,
        mids_path: Path,
        bodypart: str,
        use_bodypart: bool,
        use_viewposition: bool,
    ):
        super().__init__(mids_path, bodypart, use_bodypart, use_viewposition)
        self.reset()

    def reset(self):
        self.dicom_dict = {}

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
        print(instance)
        if instance.Modality in ["OP", "SC", "XC", "OT"]:
            return ("op", ("mim-light", "op"))
        if instance.Modality in ["BF", "SM"]:
            return ("BF", ("micr",))
        return ("", tuple())

    def get_name(self, dataset: Dataset, modality: str, mim: Tuple[str, ...]) -> Path:
        """
        Generates a name for the image based on its metadata.

        :param dataset: The dataset containing the image metadata.
        :type dataset: pydicom.Dataset
        :param modality: The modality of the image.
        :type modality: str
        :param mim: A tuple of labels to be included in the filepath.
        :type mim: tuple[str, ...]
        :returns: A Path object representing the generated name.
        :rtype: pathlib.Path
        """

        sub = f"sub-{dataset.PatientID}"
        ses = f"ses-{dataset.StudyID}"
        run = (
            f"run-{dataset.SeriesNumber}"
            if dataset.data_element("SeriesNumber")
            else ""
        )
        if self.use_bodypart:
            bp = (
                f"bp-{dataset.BodyPartExamined}"
                if dataset.data_element("BodyPartExamined")
                else f"bp-{self.bodypart}"
            )
        else:
            bp = ""
        lat = f"lat-{dataset.Laterality}" if dataset.data_element("Laterality") else ""
        vp = ""  # f"vp-{dataset.data_element('ViewPosition')}" if dataset.data_element("ViewPosition") else ""
        chunk = (
            f"chunk-{dataset.InstanceNumber}"
            if dataset.data_element("InstanceNumber") and self.use_chunk
            else ""
        )
        mod = modality
        return self.mids_path.joinpath(
            sub,
            ses,
            *mim,
            "_".join(
                [
                    part
                    for part in [sub, ses, run, bp, lat, vp, chunk, mod]
                    if part != ""
                ]
            ),
        )

    def convert_to_image(self, instance: FileInstance, file_path_mids: Path):
        """
        Converts a DICOM to an image.

        :param instance: The DICOM image instance.
        :type instance: pydicom.fileset.FileInstance
        :param file_path_mids: The path where the converted image will be saved.
        :type file_path_mids: pathlib.Path
        """

        file_path_mids.parent.mkdir(parents=True, exist_ok=True)
        image = sitk.ReadImage(instance.path)
        sitk.WriteImage(image, file_path_mids)

    def run(self, instance_list: List[Tuple[int, FileInstance]]):
        """
        Runs the image conversion pipeline on a list of instances.

        :param instance_list: A list of tuples containing the instance number and the DICOM instance.
        :type instance_list: list[uuple[int, pydicom.fileset.FileInstance]]
        """

        self.use_chunk = len(instance_list) > 1
        for _, instance in sorted(instance_list, key=lambda x: x[0]):
            print(instance)
            dataset = instance.load()
            modality, mim = self.classify_image_type(instance)
            file_path_mids = self.get_name(dataset, modality, mim)
            print(instance.path, file_path_mids)
            self.convert_to_image(instance, file_path_mids.with_suffix(".png"))
            self.convert_to_jsonfile(dataset, file_path_mids.with_suffix(".json"))
