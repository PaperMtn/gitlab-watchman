from dataclasses import dataclass

from . import user


@dataclass
class Namespace(object):
    id: str
    name: str
    path: str
    kind: str
    full_path: str
    parent_id: str
    web_url: str
    members: list[user.User] or None
    owner: user.User or None


@dataclass
class Project(object):
    """ Class that defines User objects for GitLab projects"""

    __slots__ = [
        'id',
        'description',
        'name',
        'name_with_namespace',
        'path',
        'path_with_namespace',
        'created_at',
        'web_url',
        'last_activity_at',
        'namespace',
    ]

    id: str
    description: str
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    created_at: str
    web_url: user.User
    last_activity_at: str
    namespace: Namespace


def create_from_dict(project_dict: dict) -> Project:
    """ Create a Project object from a dict response from the GitLab API

    Args:
        project_dict: dict/JSON format data from GitLab API
    Returns:
        A new Project object
    """

    project_object = Project(
        id=project_dict.get('id'),
        description=project_dict.get('description'),
        name=project_dict.get('name'),
        name_with_namespace=project_dict.get('name_with_namespace'),
        path=project_dict.get('path'),
        created_at=project_dict.get('created_at'),
        path_with_namespace=project_dict.get('path_with_namespace'),
        web_url=project_dict.get('web_url'),
        last_activity_at=project_dict.get('last_activity_at'),
        namespace=Namespace(
            id=project_dict.get('namespace').get('id'),
            name=project_dict.get('namespace').get('name'),
            path=project_dict.get('namespace').get('path'),
            kind=project_dict.get('namespace').get('kind'),
            full_path=project_dict.get('namespace').get('full_path'),
            parent_id=project_dict.get('namespace').get('parent_id'),
            web_url=project_dict.get('namespace').get('web_url'),
            members=[],
            owner=[]
        )
    )

    return project_object
