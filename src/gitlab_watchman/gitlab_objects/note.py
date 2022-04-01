from dataclasses import dataclass

from . import user


@dataclass
class Note(object):
    """ Class that defines User objects for GitLab notes"""

    __slots__ = [
        'id',
        'type',
        'body',
        'attachment',
        'author',
        'created_at',
        'updated_at',
        'system',
        'noteable_id',
        'noteable_type',
        'commit_id',
        'resolvable',
        'resolved',
        'resolved_by',
        'resolved_at',
        'confidential',
        'noteable_iid',
        'command_changes'
    ]

    id: str
    type: str
    body: str
    attachment: str or bool
    author: user.User
    created_at: str
    updated_at: str
    system: str
    noteable_id: str
    noteable_type: str
    commit_id: str
    resolvable: bool
    resolved_by: user.User
    resolved_at: str
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

    note_object = Note(
        id=note_dict.get('id'),
        type=note_dict.get('type'),
        body=note_dict.get('body'),
        attachment=note_dict.get('attachment'),
        author=user.create_from_dict(note_dict.get('author', {})),
        created_at=note_dict.get('created_at'),
        updated_at=note_dict.get('updated_at'),
        system=note_dict.get('system'),
        noteable_id=note_dict.get('noteable_id'),
        noteable_type=note_dict.get('noteable_type'),
        commit_id=note_dict.get('commit_id'),
        resolvable=note_dict.get('resolvable'),
        resolved_by=resolved_by,
        resolved_at=note_dict.get('resolved_at'),
        confidential=note_dict.get('confidential'),
        noteable_iid=note_dict.get('noteable_iid'),
        command_changes=note_dict.get('command_changes'),
    )

    return note_object
