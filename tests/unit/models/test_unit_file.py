from gitlab_watchman.models import file

from fixtures import (
    GitLabMockData,
    mock_file
)


def test_file_initialisation(mock_file):
    # Test that the File object is of the correct type
    assert isinstance(mock_file, file.File)

    # Test that the File object has the correct attributes
    assert mock_file.file_name == GitLabMockData.MOCK_FILE_DICT.get('file_name')
    assert mock_file.file_path == GitLabMockData.MOCK_FILE_DICT.get('file_path')
    assert mock_file.size == GitLabMockData.MOCK_FILE_DICT.get('size')
    assert mock_file.encoding == GitLabMockData.MOCK_FILE_DICT.get('encoding')
    assert mock_file.ref == GitLabMockData.MOCK_FILE_DICT.get('ref')
    assert mock_file.commit_id == GitLabMockData.MOCK_FILE_DICT.get('commit_id')
    assert mock_file.last_commit_id == GitLabMockData.MOCK_FILE_DICT.get('last_commit_id')


def test_file_missing_fields():
    # Create dict with missing fields
    file_dict = {
        "file_name": "my_file.txt",
        "size": "10",
    }
    file_object = file.create_from_dict(file_dict)
    # Test that the File object is of the correct type
    assert isinstance(file_object, file.File)

    # Test that the File object has the correct attributes
    assert file_object.file_name == file_dict.get('file_name')
    assert file_object.file_path is None
    assert file_object.size == file_dict.get('size')
    assert file_object.encoding is None
    assert file_object.ref is None
    assert file_object.commit_id is None
    assert file_object.last_commit_id is None