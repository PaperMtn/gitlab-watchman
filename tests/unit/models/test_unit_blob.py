from gitlab_watchman.models import blob

from fixtures import (
    GitLabMockData,
    mock_blob
)


def test_blob_initialisation(mock_blob):
    # Test that the Blob object is of the correct type
    assert isinstance(mock_blob, blob.Blob)

    # Test that the Blob object has the correct attributes
    assert mock_blob.id == GitLabMockData.MOCK_BLOB_DICT.get('id')
    assert mock_blob.basename == GitLabMockData.MOCK_BLOB_DICT.get('basename')
    assert mock_blob.data == GitLabMockData.MOCK_BLOB_DICT.get('data')
    assert mock_blob.path == GitLabMockData.MOCK_BLOB_DICT.get('path')
    assert mock_blob.filename == GitLabMockData.MOCK_BLOB_DICT.get('filename')
    assert mock_blob.ref == GitLabMockData.MOCK_BLOB_DICT.get('ref')
    assert mock_blob.project_id == GitLabMockData.MOCK_BLOB_DICT.get('project_id')


def test_blob_missing_fields():
    # Create dict with missing fields
    blob_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "basename": "ed899a2f4b5",
    }
    blob_object = blob.create_from_dict(blob_dict)
    # Test that the Blob object is of the correct type
    assert isinstance(blob_object, blob.Blob)

    # Test that the Blob object has the correct attributes
    assert blob_object.id == blob_dict.get('id')
    assert blob_object.basename == blob_dict.get('basename')
    assert blob_object.data is None
    assert blob_object.path is None
    assert blob_object.filename is None
    assert blob_object.ref is None
    assert blob_object.project_id is None
