from dataclasses import dataclass


@dataclass(slots=True)
class User:
    """ Class that defines User objects for GitLab users"""

    id: str
    name: str
    username: str
    state: str
    web_url: bool


def create_from_dict(user_dict: dict) -> User:
    """ Create a User object from a dict response from the GitLab API

    Args:
        user_dict: dict/JSON format data from GitLab API
    Returns:
        A new User object
    """

    return User(
        id=user_dict.get('id'),
        name=user_dict.get('name'),
        username=user_dict.get('username'),
        state=user_dict.get('state'),
        web_url=user_dict.get('web_url')
    )
