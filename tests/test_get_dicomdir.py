from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

import pytest
from pydicom.data import get_testdata_file
from pydicom.fileset import FileSet

from dcm2mids.get_dicomdir import get_dicomdir

TEST_DICOMDIR = Path(get_testdata_file("DICOMDIR")).parent
TEST_CT_DICOM = Path(get_testdata_file("CT_small.dcm"))
TEST_MR_DICOM = Path(get_testdata_file("MR_small.dcm"))


@pytest.fixture
def tmp_path():
    tmp = TemporaryDirectory()
    tmp_path = Path(tmp.name)
    copyfile(TEST_CT_DICOM, tmp_path / TEST_CT_DICOM.name)
    copyfile(TEST_MR_DICOM, tmp_path / TEST_MR_DICOM.name)
    yield tmp_path
    tmp.cleanup()

def test_get_dicomdir_with_existing_dicomdir():
    # Call the get_dicomdir function
    result = get_dicomdir(TEST_DICOMDIR)

    # Assert that the result is a FileSet object
    assert isinstance(result, FileSet)

    # Assert that the FileSet is not empty
    assert len(result) > 0


def test_get_dicomdir_with_invalid_argument():
    # Call the get_dicomdir function with an invalid argument
    with pytest.raises(TypeError):
        get_dicomdir(5)


def test_get_dicomdir_with_no_dicomdir(tmp_path):
    # Call the get_dicomdir function
    result = get_dicomdir(tmp_path)

    # Assert that the result is a FileSet object
    assert isinstance(result, FileSet)

    # Assert that the FileSet contains the DICOM files
    assert len(result) == 2


def test_get_dicomdir_with_nonexistent_folder():
    # Call the get_dicomdir function with a nonexistent folder
    with pytest.raises(FileNotFoundError):
        get_dicomdir("/path/to/nonexistent/folder")
