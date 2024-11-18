from gitlab_watchman.models import group
from gitlab_watchman.utils import convert_to_utc_datetime

from fixtures import (
    GitLabMockData,
    mock_group
)


def test_group_initialisation(mock_group):
    # Test that the Group object is of the correct type
    assert isinstance(mock_group, group.Group)

    # Test that the Group object has the correct attributes
    assert mock_group.id == GitLabMockData.MOCK_GROUP_DICT.get('id')
    assert mock_group.name == GitLabMockData.MOCK_GROUP_DICT.get('name')
    assert mock_group.path == GitLabMockData.MOCK_GROUP_DICT.get('path')
    assert mock_group.description == GitLabMockData.MOCK_GROUP_DICT.get('description')
    assert mock_group.visibility == GitLabMockData.MOCK_GROUP_DICT.get('visibility')
    assert mock_group.require_two_factor_authentication == GitLabMockData.MOCK_GROUP_DICT.get('require_two_factor_authentication')
    assert mock_group.two_factor_grace_period == GitLabMockData.MOCK_GROUP_DICT.get('two_factor_grace_period')
    assert mock_group.auto_devops_enabled == GitLabMockData.MOCK_GROUP_DICT.get('auto_devops_enabled')
    assert mock_group.emails_disabled == GitLabMockData.MOCK_GROUP_DICT.get('emails_disabled')
    assert mock_group.request_access_enabled == GitLabMockData.MOCK_GROUP_DICT.get('request_access_enabled')
    assert mock_group.full_name == GitLabMockData.MOCK_GROUP_DICT.get('full_name')
    assert mock_group.full_path == GitLabMockData.MOCK_GROUP_DICT.get('full_path')
    assert mock_group.created_at == convert_to_utc_datetime(GitLabMockData.MOCK_GROUP_DICT.get('created_at'))
    assert mock_group.web_url == GitLabMockData.MOCK_GROUP_DICT.get('web_url')
    assert mock_group.ip_restriction_ranges == GitLabMockData.MOCK_GROUP_DICT.get('ip_restriction_ranges')


def test_group_missing_fields():
    # Create dict with missing fields
    group_dict = {
        "id": "ed899a2f4b50b4370feeea94676502b42383c746",
        "name": "my_group",
    }
    group_object = group.create_from_dict(group_dict)
    # Test that the Group object is of the correct type
    assert isinstance(group_object, group.Group)

    # Test that the Group object has the correct attributes
    assert group_object.id == group_dict.get('id')
    assert group_object.name == group_dict.get('name')
    assert group_object.path is None
    assert group_object.description is None
    assert group_object.visibility is None
    assert group_object.require_two_factor_authentication is None
    assert group_object.two_factor_grace_period is None
    assert group_object.auto_devops_enabled is None
    assert group_object.emails_disabled is None
    assert group_object.request_access_enabled is None
    assert group_object.full_name is None
    assert group_object.full_path is None
    assert group_object.created_at is None
    assert group_object.web_url is None
    assert group_object.ip_restriction_ranges is None