from gitlab_watchman.models import merge_request, user
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_merge_request
)


def test_merge_request_initialisation(mock_merge_request):
    # Test that the MergeRequest object is of the correct type
    assert isinstance(mock_merge_request, merge_request.MergeRequest)

    # Test that the MergeRequest object has the correct attributes
    assert mock_merge_request.id == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('id')
    assert mock_merge_request.iid == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('iid')
    assert mock_merge_request.project_id == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('project_id')
    assert mock_merge_request.title == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('title')
    assert mock_merge_request.description == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('description')
    assert mock_merge_request.state == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('state')
    assert mock_merge_request.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('created_at'))
    assert mock_merge_request.updated_at == convert_to_utc_datetime(GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('updated_at'))
    assert mock_merge_request.merged_by is None
    assert mock_merge_request.merged_at == convert_to_utc_datetime(GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('merged_at'))
    assert mock_merge_request.target_branch == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('target_branch')
    assert mock_merge_request.source_branch == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('source_branch')
    assert isinstance(mock_merge_request.author, user.User)
    assert mock_merge_request.source_project_id == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('source_project_id')
    assert mock_merge_request.target_project_id == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('target_project_id')
    assert mock_merge_request.merge_status == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('merge_status')
    assert mock_merge_request.web_url == GitLabMockData.MOCK_MERGE_REQUEST_DICT.get('web_url')


def test_merge_request_missing_fields():
    # Create dict with missing fields
    merge_request_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "iid": "1",
    }
    merge_request_object = merge_request.create_from_dict(merge_request_dict)
    # Test that the MergeRequest object is of the correct type
    assert isinstance(merge_request_object, merge_request.MergeRequest)

    # Test that the MergeRequest object has the correct attributes
    assert merge_request_object.id == merge_request_dict.get('id')
    assert merge_request_object.iid == merge_request_dict.get('iid')
    assert merge_request_object.project_id is None
    assert merge_request_object.title is None
    assert merge_request_object.description is None
    assert merge_request_object.state is None
    assert merge_request_object.created_at is None
    assert merge_request_object.updated_at is None
    assert merge_request_object.merged_by is None
    assert merge_request_object.merged_at is None
    assert merge_request_object.target_branch is None
    assert merge_request_object.source_branch is None
    assert merge_request_object.author is None
    assert merge_request_object.source_project_id is None
    assert merge_request_object.target_project_id is None
    assert merge_request_object.merge_status is None
    assert merge_request_object.web_url is None


def test_initialisation_with_merged_by_user(mock_merge_request):
    # Create dict and add merged_by user
    merge_request_dict = GitLabMockData.MOCK_MERGE_REQUEST_DICT.copy()
    merge_request_dict['merged_by'] = {
            "id": 1,
            "name": "Administrator",
            "username": "root",
            "state": "active",
            "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
            "web_url": "http://localhost:3000/root"
        }
    merge_request_object = merge_request.create_from_dict(merge_request_dict)

    # Test that the MergeRequest object is of the correct type
    assert isinstance(merge_request_object, merge_request.MergeRequest)

    # Test that the MergeRequest object has the correct attributes
    assert isinstance(merge_request_object.merged_by, user.User)

    # Test that the User object is of the correct type
    assert merge_request_object.merged_by.id == 1
    assert merge_request_object.merged_by.name == 'Administrator'
    assert merge_request_object.merged_by.username == 'root'
    assert merge_request_object.merged_by.state == 'active'
    assert merge_request_object.merged_by.web_url == 'http://localhost:3000/root'
