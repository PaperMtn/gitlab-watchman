from gitlab_watchman.models import commit
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_commit
)


def test_commit_initialisation(mock_commit):
    # Test that the Conversation object is of the correct type
    assert isinstance(mock_commit, commit.Commit)

    # Test that the Conversation object has the correct attributes
    assert mock_commit.id == GitLabMockData.MOCK_COMMIT_DICT.get('id')
    assert mock_commit.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_COMMIT_DICT.get('created_at'))
    assert mock_commit.title == GitLabMockData.MOCK_COMMIT_DICT.get('title')
    assert mock_commit.message == GitLabMockData.MOCK_COMMIT_DICT.get('message')
    assert mock_commit.author_name == GitLabMockData.MOCK_COMMIT_DICT.get('author_name')
    assert mock_commit.author_email == GitLabMockData.MOCK_COMMIT_DICT.get('author_email')
    assert mock_commit.authored_date == convert_to_utc_datetime(GitLabMockData.MOCK_COMMIT_DICT.get('authored_date'))
    assert mock_commit.committer_name == GitLabMockData.MOCK_COMMIT_DICT.get('committer_name')
    assert mock_commit.committer_email == GitLabMockData.MOCK_COMMIT_DICT.get('committer_email')
    assert mock_commit.committed_date == convert_to_utc_datetime(GitLabMockData.MOCK_COMMIT_DICT.get('committed_date'))
    assert mock_commit.web_url == GitLabMockData.MOCK_COMMIT_DICT.get('web_url')
    assert mock_commit.status == GitLabMockData.MOCK_COMMIT_DICT.get('status')
    assert mock_commit.project_id == GitLabMockData.MOCK_COMMIT_DICT.get('project_id')


def test_commit_missing_fields():
    # Create dict with missing fields
    commit_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "short_id": "ed899a2f4b5",
    }
    commit_object = commit.create_from_dict(commit_dict)
    # Test that the Conversation object is of the correct type
    assert isinstance(commit_object, commit.Commit)

    # Test that the Conversation object has the correct attributes
    assert commit_object.id == commit_dict.get('id')
    assert commit_object.created_at is None
    assert commit_object.title is None
    assert commit_object.message is None
    assert commit_object.author_name is None
    assert commit_object.author_email is None
    assert commit_object.authored_date is None
    assert commit_object.committer_name is None
    assert commit_object.committer_email is None
    assert commit_object.committed_date is None
    assert commit_object.web_url is None
    assert commit_object.status is None
    assert commit_object.project_id is None
