from dataclasses import dataclass


@dataclass(slots=True)
class WikiBlob:
    """ Class that defines WikiBlob objects for GitLab blobs"""

    basename: str
    data: str
    path: str
    filename: str
    id: str
    ref: str
    project_id: str | None
    group_id: str | None


def create_from_dict(blob_dict: dict) -> WikiBlob:
    """ Create a WikiBlob object from a dict response from the GitLab API

    Args:
        blob_dict: dict/JSON format data from GitLab API
    Returns:
        A new WikiBlob object
    """

    return WikiBlob(
        id=blob_dict.get('id'),
        basename=blob_dict.get('basename'),
        data=blob_dict.get('data'),
        path=blob_dict.get('path'),
        filename=blob_dict.get('filename'),
        ref=blob_dict.get('ref'),
        project_id=blob_dict.get('project_id'),
        group_id=blob_dict.get('group_id', None)
    )
