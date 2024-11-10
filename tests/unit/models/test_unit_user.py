from gitlab_watchman.models import user

from fixtures import (
    GitLabMockData,
    mock_user
)


def test_user_initialisation(mock_user):
    # Test that the User object is of the correct type
    assert isinstance(mock_user, user.User)

    # Test that the User object has the correct attributes
    assert mock_user.id == GitLabMockData.MOCK_USER_DICT.get('id')
    assert mock_user.name == GitLabMockData.MOCK_USER_DICT.get('name')
    assert mock_user.username == GitLabMockData.MOCK_USER_DICT.get('username')
    assert mock_user.state == GitLabMockData.MOCK_USER_DICT.get('state')
    assert mock_user.web_url == GitLabMockData.MOCK_USER_DICT.get('web_url')


def test_user_missing_fields():
    # Create a user object with missing fields
    user_dict = {
        "id": "1",
        "name": "Test user",
    }

    # Test that the User object is of the correct type
    assert isinstance(user.create_from_dict(user_dict), user.User)

    # Test that the User object has the correct attributes
    assert user.create_from_dict(user_dict).id == user_dict.get('id')
    assert user.create_from_dict(user_dict).name == user_dict.get('name')
    assert user.create_from_dict(user_dict).username is None
    assert user.create_from_dict(user_dict).state is None
    assert user.create_from_dict(user_dict).web_url is None
