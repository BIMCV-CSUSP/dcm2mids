import pytest
from pathlib import Path
from pydicom.data import get_testdata_file
from pydicom.fileset import FileSet
from dcm2mids.get_dicomdir import get_dicomdir

TEST_FILE = Path(get_testdata_file("DICOMDIR")).parent

def test_get_dicomdir_with_existing_dicomdir():
    # Call the get_dicomdir function
    result = get_dicomdir(TEST_FILE)

    # Assert that the result is a FileSet object
    assert isinstance(result, FileSet)

    # Assert that the FileSet is not empty
    assert len(result.find()) > 0

def test_get_dicomdir_with_invalid_argument():
    # Call the get_dicomdir function with an invalid argument
    with pytest.raises(TypeError):
        get_dicomdir(5)

# def test_get_dicomdir_with_no_dicomdir(tmp_path):
#     # Create a temporary folder
#     input_folder = tmp_path / "input"
#     input_folder.mkdir()

#     # Create some DICOM files
#     dicom_file1 = input_folder / "file1.dcm"
#     dicom_file1.touch()

#     dicom_file2 = input_folder / "file2.dcm"
#     dicom_file2.touch()

#     # Call the get_dicomdir function
#     result = get_dicomdir.get_dicomdir(input_folder)

#     # Assert that the result is a FileSet object
#     assert isinstance(result, get_dicomdir.FileSet)

#     # Assert that the FileSet contains the DICOM files
#     assert dicom_file1 in result
#     assert dicom_file2 in result

def test_get_dicomdir_with_nonexistent_folder():
    # Call the get_dicomdir function with a nonexistent folder
    with pytest.raises(FileNotFoundError):
        get_dicomdir("/path/to/nonexistent/folder")