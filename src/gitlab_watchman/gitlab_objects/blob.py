from dataclasses import dataclass


@dataclass
class Blob(object):
    """ Class that defines Blob objects for GitLab blobs"""

    __slots__ = [
        'basename',
        'data',
        'path',
        'filename',
        'id',
        'ref',
        'project_id'
    ]

    basename: str
    data: str
    path: str
    filename: str
    id: str
    ref: str
    project_id: str


def create_from_dict(blob_dict: dict) -> Blob:
    """ Create a Blob object from a dict response from the GitLab API

    Args:
        blob_dict: dict/JSON format data from GitLab API
    Returns:
        A new Blob object
    """

    blob_object = Blob(
        id=blob_dict.get('id'),
        basename=blob_dict.get('basename'),
        data=blob_dict.get('data'),
        path=blob_dict.get('path'),
        filename=blob_dict.get('filename'),
        ref=blob_dict.get('ref'),
        project_id=blob_dict.get('project_id')
    )

    return blob_object
