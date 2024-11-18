from gitlab_watchman.models import issue, user
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_issue
)


def test_issue_initialisation(mock_issue):
    # Test that the Issue object is of the correct type
    assert isinstance(mock_issue, issue.Issue)

    # Test that the Issue object has the correct attributes
    assert mock_issue.id == GitLabMockData.MOCK_ISSUE_DICT.get('id')
    assert mock_issue.iid == GitLabMockData.MOCK_ISSUE_DICT.get('iid')
    assert mock_issue.project_id == GitLabMockData.MOCK_ISSUE_DICT.get('project_id')
    assert mock_issue.title == GitLabMockData.MOCK_ISSUE_DICT.get('title')
    assert mock_issue.description == GitLabMockData.MOCK_ISSUE_DICT.get('description')
    assert mock_issue.state == GitLabMockData.MOCK_ISSUE_DICT.get('state')
    assert mock_issue.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_ISSUE_DICT.get('created_at'))
    assert mock_issue.updated_at == convert_to_utc_datetime(GitLabMockData.MOCK_ISSUE_DICT.get('updated_at'))
    assert mock_issue.closed_by == user.create_from_dict(GitLabMockData.MOCK_ISSUE_DICT.get('closed_by'))
    assert mock_issue.closed_at == convert_to_utc_datetime(GitLabMockData.MOCK_ISSUE_DICT.get('closed_at'))
    assert mock_issue.type == GitLabMockData.MOCK_ISSUE_DICT.get('type')
    assert mock_issue.author == user.create_from_dict(
        GitLabMockData.MOCK_ISSUE_DICT.get('author')), GitLabMockData.MOCK_ISSUE_DICT.get('author')
    assert mock_issue.confidential == GitLabMockData.MOCK_ISSUE_DICT.get('confidential')
    assert mock_issue.web_url == GitLabMockData.MOCK_ISSUE_DICT.get('web_url')


def test_issues_missing_fields():
    # Create dict with missing fields
    issue_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "iid": "1",
    }
    issue_object = issue.create_from_dict(issue_dict)
    # Test that the Issue object is of the correct type
    assert isinstance(issue_object, issue.Issue)

    # Test that the Issue object has the correct attributes
    assert issue_object.id == issue_dict.get('id')
    assert issue_object.iid == issue_dict.get('iid')
    assert issue_object.project_id is None
    assert issue_object.title is None
    assert issue_object.description is None
    assert issue_object.state is None
    assert issue_object.created_at is None
    assert issue_object.updated_at is None
    assert issue_object.closed_by is None
    assert issue_object.closed_at is None
    assert issue_object.type is None
    assert issue_object.author is None
    assert issue_object.confidential is None
    assert issue_object.web_url is None


def test_issue_user_initialisation(mock_issue):
    # Test creating a user object with the response from the GitLab API

    # Test that the User object is of the correct type
    assert isinstance(mock_issue.author, user.User)

    # Test that the User object has the correct attributes
    assert mock_issue.author.id == GitLabMockData.MOCK_ISSUE_DICT.get('author').get('id')
    assert mock_issue.author.name == GitLabMockData.MOCK_ISSUE_DICT.get('author').get('name')
    assert mock_issue.author.username == GitLabMockData.MOCK_ISSUE_DICT.get('author').get('username')
    assert mock_issue.author.state == GitLabMockData.MOCK_ISSUE_DICT.get('author').get('state')
    assert mock_issue.author.web_url == GitLabMockData.MOCK_ISSUE_DICT.get('author').get('web_url')
