from dataclasses import dataclass

@dataclass
class File(object):
    """ Class that defines File objects for GitLab files"""

    __slots__ = [
        'file_name',
        'file_path',
        'size',
        'encoding',
        'ref',
        'blob_id',
        'commit_id',
        'last_commit_id',
        'content'
    ]

    file_name: str
    file_path: str
    size: str
    encoding: str
    ref: str
    commit_id: str
    last_commit_id: str
    content: str


def create_from_dict(file_dict: dict) -> File:
    """ Create a File object from a dict response from the GitLab API

    Args:
        file_dict: dict/JSON format data from GitLab API
    Returns:
        A new Note object
    """

    file_object = File(
        file_name=file_dict.get('file_name'),
        file_path=file_dict.get('file_path'),
        size=file_dict.get('size'),
        encoding=file_dict.get('encoding'),
        ref=file_dict.get('ref'),
        commit_id=file_dict.get('commit_id'),
        last_commit_id=file_dict.get('last_commit_id'),
        content=file_dict.get('content')
    )

    return file_object
