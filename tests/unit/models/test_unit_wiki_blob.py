from gitlab_watchman.models import wiki_blob
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_wiki_blob
)


def test_wiki_blob_initialisation(mock_wiki_blob):
    # Test that the WikiBlob object is of the correct type
    assert isinstance(mock_wiki_blob, wiki_blob.WikiBlob)

    # Test that the WikiBlob object has the correct attributes
    assert mock_wiki_blob.id == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('id')
    assert mock_wiki_blob.basename == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('basename')
    assert mock_wiki_blob.data == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('data')
    assert mock_wiki_blob.path == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('path')
    assert mock_wiki_blob.filename == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('filename')
    assert mock_wiki_blob.ref == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('ref')
    assert mock_wiki_blob.project_id == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('project_id')
    assert mock_wiki_blob.group_id == GitLabMockData.MOCK_WIKI_BLOB_DICT.get('group_id')


def test_wiki_blob_missing_fields():
    # Create dict with missing fields
    wiki_blob_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "basename": "ed899a2f4b5",
    }
    wiki_blob_object = wiki_blob.create_from_dict(wiki_blob_dict)
    # Test that the WikiBlob object is of the correct type
    assert isinstance(wiki_blob_object, wiki_blob.WikiBlob)

    # Test that the WikiBlob object has the correct attributes
    assert wiki_blob_object.id == wiki_blob_dict.get('id')
    assert wiki_blob_object.basename == wiki_blob_dict.get('basename')
    assert wiki_blob_object.data is None
    assert wiki_blob_object.path is None
    assert wiki_blob_object.filename is None
    assert wiki_blob_object.ref is None
    assert wiki_blob_object.project_id is None
    assert wiki_blob_object.group_id is None
