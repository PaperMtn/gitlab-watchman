from dataclasses import dataclass

from src.gitlab_watchman.gitlab_objects import user


@dataclass
class Issue(object):
    """ Class that defines Issues objects for GitLab issues"""

    __slots__ = [
        'id',
        'iid',
        'project_id',
        'title',
        'description',
        'state',
        'created_at',
        'updated_at',
        'closed_at',
        'closed_by',
        'author',
        'type',
        'author',
        'confidential',
        'web_url'
    ]

    id: str
    iid: str
    project_id: str
    title: str
    description: str
    state: str
    created_at: str
    updated_at: str
    closed_by: user.User
    closed_at: str
    author: str
    type: str
    author: user.User
    confidential: str
    web_url: str


def create_from_dict(issue_dict: dict) -> Issue:
    """ Create a Issue object from a dict response from the GitLab API

    Args:
        issue_dict: dict/JSON format data from GitLab API
    Returns:
        A new MergeRequest object
    """
    if issue_dict.get('closed_by'):
        closed_by = user.create_from_dict(issue_dict.get('closed_by'))
    else:
        closed_by = None

    issue_object = Issue(
        id=issue_dict.get('id'),
        iid=issue_dict.get('iid'),
        project_id=issue_dict.get('project_id'),
        title=issue_dict.get('title'),
        description=issue_dict.get('description'),
        state=issue_dict.get('state'),
        created_at=issue_dict.get('created_at'),
        updated_at=issue_dict.get('updated_at'),
        closed_by=closed_by,
        closed_at=issue_dict.get('closed_at'),
        type=issue_dict.get('type'),
        author=user.create_from_dict(issue_dict.get('author')),
        confidential=issue_dict.get('confidential'),
        web_url=issue_dict.get('web_url'),
    )

    return issue_object
