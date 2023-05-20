from dataclasses import dataclass


@dataclass(slots=True)
class File(object):
    """ Class that defines File objects for GitLab files"""

    file_name: str
    file_path: str
    size: str
    encoding: str
    ref: str
    commit_id: str
    last_commit_id: str


def create_from_dict(file_dict: dict) -> File:
    """ Create a File object from a dict response from the GitLab API

    Args:
        file_dict: dict/JSON format data from GitLab API
    Returns:
        A new Note object
    """

    return File(
        file_name=file_dict.get('file_name'),
        file_path=file_dict.get('file_path'),
        size=file_dict.get('size'),
        encoding=file_dict.get('encoding'),
        ref=file_dict.get('ref'),
        commit_id=file_dict.get('commit_id'),
        last_commit_id=file_dict.get('last_commit_id'),
    )
