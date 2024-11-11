from dataclasses import dataclass
from datetime import datetime

from gitlab_watchman.utils import convert_to_utc_datetime


@dataclass(slots=True)
class Commit(object):
    """ Class that defines File objects for GitLab files"""

    id: str
    created_at: datetime | None
    title: str
    message: str
    author_name: str
    author_email: str
    authored_date: datetime | None
    committer_name: str
    committer_email: str
    committed_date: datetime | None
    web_url: str
    status: str
    project_id: str


def create_from_dict(commit_dict: dict) -> Commit:
    """ Create a Commit object from a dict response from the GitLab API

    Args:
        commit_dict: dict/JSON format data from GitLab API
    Returns:
        A new Commit object
    """

    return Commit(
        id=commit_dict.get('id'),
        created_at=convert_to_utc_datetime(commit_dict.get('created_at')),
        title=commit_dict.get('title'),
        message=commit_dict.get('message'),
        author_name=commit_dict.get('author_name'),
        author_email=commit_dict.get('author_email'),
        authored_date=convert_to_utc_datetime(commit_dict.get('authored_date')),
        committer_name=commit_dict.get('committer_name'),
        committed_date=convert_to_utc_datetime(commit_dict.get('committed_date')),
        committer_email=commit_dict.get('committer_email'),
        web_url=commit_dict.get('web_url'),
        status=commit_dict.get('status'),
        project_id=commit_dict.get('project_id')
    )
