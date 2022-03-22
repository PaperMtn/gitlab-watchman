from dataclasses import dataclass

@dataclass
class Commit(object):
    """ Class that defines File objects for GitLab files"""

    __slots__ = [
        'id',
        'created_at',
        'title',
        'message',
        'author_name',
        'author_email',
        'authored_date',
        'committer_name',
        'committer_email',
        'committed_date',
        'web_url',
        'status',
        'project_id'
    ]

    id: str
    created_at: str
    title: str
    message: str
    author_name: str
    author_email: str
    authored_date: str
    committer_name: str
    committer_email: str
    committed_date: str
    web_url: str
    status: str
    project_id: str


def create_from_dict(commit_dict: dict) -> Commit:
    """ Create a Commit object from a dict response from the GitLab API

    Args:
        commit_dict: dict/JSON format data from GitLab API
    Returns:
        A new Note object
    """

    commit_object = Commit(
        id=commit_dict.get('id'),
        created_at=commit_dict.get('created_at'),
        title=commit_dict.get('title'),
        message=commit_dict.get('message'),
        author_name=commit_dict.get('author_name'),
        author_email=commit_dict.get('author_email'),
        authored_date=commit_dict.get('authored_date'),
        committer_name=commit_dict.get('committer_name'),
        committed_date=commit_dict.get('committed_date'),
        committer_email=commit_dict.get('committer_email'),
        web_url=commit_dict.get('web_url'),
        status=commit_dict.get('status'),
        project_id=commit_dict.get('project_id')
    )

    return commit_object
