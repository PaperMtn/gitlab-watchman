from gitlab_watchman.models import milestone
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_milestone
)


def test_milestone_initialisation(mock_milestone):
    # Test that the Milestone object is of the correct type
    assert isinstance(mock_milestone, milestone.Milestone)

    # Test that the Milestone object has the correct attributes
    assert mock_milestone.id == GitLabMockData.MOCK_MILESTONE_DICT.get('id')
    assert mock_milestone.iid == GitLabMockData.MOCK_MILESTONE_DICT.get('iid')
    assert mock_milestone.project_id == GitLabMockData.MOCK_MILESTONE_DICT.get('project_id')
    assert mock_milestone.title == GitLabMockData.MOCK_MILESTONE_DICT.get('title')
    assert mock_milestone.description == GitLabMockData.MOCK_MILESTONE_DICT.get('description')
    assert mock_milestone.state == GitLabMockData.MOCK_MILESTONE_DICT.get('state')
    assert mock_milestone.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_MILESTONE_DICT.get('created_at'))
    assert mock_milestone.updated_at == convert_to_utc_datetime(GitLabMockData.MOCK_MILESTONE_DICT.get('updated_at'))
    assert mock_milestone.due_date == convert_to_utc_datetime(GitLabMockData.MOCK_MILESTONE_DICT.get('due_date'))
    assert mock_milestone.start_date == convert_to_utc_datetime(GitLabMockData.MOCK_MILESTONE_DICT.get('start_date'))
    assert mock_milestone.expired == GitLabMockData.MOCK_MILESTONE_DICT.get('expired')
    assert mock_milestone.web_url == GitLabMockData.MOCK_MILESTONE_DICT.get('web_url')


def test_milestone_missing_fields():
    # Create dict with missing fields
    milestone_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "iid": "1",
    }
    milestone_object = milestone.create_from_dict(milestone_dict)
    # Test that the Milestone object is of the correct type
    assert isinstance(milestone_object, milestone.Milestone)

    # Test that the Milestone object has the correct attributes
    assert milestone_object.id == milestone_dict.get('id')
    assert milestone_object.iid == milestone_dict.get('iid')
    assert milestone_object.project_id is None
    assert milestone_object.title is None
    assert milestone_object.description is None
    assert milestone_object.state is None
    assert milestone_object.created_at is None
    assert milestone_object.updated_at is None
    assert milestone_object.due_date is None
    assert milestone_object.start_date is None
    assert milestone_object.expired is None
    assert milestone_object.web_url is None