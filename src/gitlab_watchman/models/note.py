from dataclasses import dataclass
from datetime import datetime

from gitlab_watchman.models import user
from gitlab_watchman.utils import convert_to_utc_datetime


@dataclass(slots=True)
class Note(object):
    """ Class that defines User objects for GitLab notes"""

    id: str
    type: str
    body: str
    attachment: str or bool
    author: user.User
    created_at: datetime | None
    updated_at: datetime | None
    system: str
    noteable_id: str
    noteable_type: str
    commit_id: str
    resolvable: bool
    resolved_by: user.User
    resolved_at: datetime | None
    confidential: str
    noteable_iid: str
    command_changes: str


def create_from_dict(note_dict: dict) -> Note:
    """ Create a Note object from a dict response from the GitLab API

    Args:
        note_dict: dict/JSON format data from GitLab API
    Returns:
        A new Note object
    """
    if note_dict.get('resolved_by'):
        resolved_by = user.create_from_dict(note_dict.get('resolved_by', {}))
    else:
        resolved_by = None

    if note_dict.get('author'):
        author = user.create_from_dict(note_dict.get('author', {}))
    else:
        author = None

    return Note(
        id=note_dict.get('id'),
        type=note_dict.get('type'),
        body=note_dict.get('body'),
        attachment=note_dict.get('attachment'),
        author=author,
        created_at=convert_to_utc_datetime(note_dict.get('created_at')),
        updated_at=convert_to_utc_datetime(note_dict.get('updated_at')),
        system=note_dict.get('system'),
        noteable_id=note_dict.get('noteable_id'),
        noteable_type=note_dict.get('noteable_type'),
        commit_id=note_dict.get('commit_id'),
        resolvable=note_dict.get('resolvable'),
        resolved_by=resolved_by,
        resolved_at=convert_to_utc_datetime(note_dict.get('resolved_at')),
        confidential=note_dict.get('confidential'),
        noteable_iid=note_dict.get('noteable_iid'),
        command_changes=note_dict.get('command_changes'),
    )
